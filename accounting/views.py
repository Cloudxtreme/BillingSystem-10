from functools import partial, wraps

from django.shortcuts import *
from django.contrib import messages
from django.core import serializers
from django.core.urlresolvers import reverse
from django.forms import formset_factory
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.db import IntegrityError, transaction
from django.http.response import HttpResponseBadRequest
from django.utils import timezone

from datetime import datetime
from decimal import Decimal

from .models import *
from .forms import *
from base.models import ExtPythonSerializer

def claim_summary(request):

    summary = Claim.objects.values()
    summary = list(summary)
    for c, b in zip(Claim.objects.all(),summary):
        b['pat_name'] = c.patient.full_name

    for c, b in zip(Claim.objects.all(),summary):
        b['user'] = c.user.first_name+"("+c.user.email+")"

    return render(request, 'accounting/claim/summary.html' ,{
        'summary': summary
    })

def gross_payment_summary(request):
    # get data from accounting_claim : claim_id, created data, patient_id
    dic=[]
    idList=Claim.objects.values_list('id', flat=True)
    for claim_id in idList:
        temp={}
        temp["claimId"]=claim_id

        claimRow=Claim.objects.filter(id=claim_id).values()[0]
        dateCreated=claimRow["created"]
        patientId=claimRow["patient_id"]
        temp["dateCreated"]=dateCreated
        temp["patientId"]=patientId

        # get patient_name from patient table through id
        patientRow=Personal_Information.objects.filter(chart_no=patientId).values()[0]
        patientName=patientRow['last_name']+", "+patientRow['first_name']
        temp["patientName"]=patientName

        # get total charge from accounting_procedure (add ammount for same claim id)
        # get sum od ammounts for same claim id from accounting_appliedpayment
        # get total adjustments -- create another column --
        procedures=Procedure.objects.filter(claim_id=claim_id)
        totalCharge = Decimal('0.00')
        totalAppliedAmnt = Decimal('0.00')
        totalAdjustments = Decimal('0.00')
        for procedure in procedures:
            charges = procedure.charge_set.all()
            for c in charges:
                totalCharge += c.amount
                totalAppliedAmnt += (Apply.objects.filter(charge=c.pk)\
                        .aggregate(Sum('amount'))\
                        .get('amount__sum') or 0)
                totalAdjustments += (Apply.objects.filter(charge=c.pk)\
                        .aggregate(Sum('adjustment'))\
                        .get('adjustment__sum') or 0)
        temp["totalCharge"] = totalCharge
        temp["totalAppliedAmnt"] = totalAppliedAmnt
        temp["totalAdjustments"] = totalAdjustments
        temp["balance"] = totalCharge - (totalAppliedAmnt+totalAdjustments)
        dic.append(temp)
    return render(request, 'accounting/payment/accounts_summary.html', {'summary': dic})

def payment_create(request):
    claim_id = request.GET.get("claim")
    initial = None
    if claim_id:
        claim = get_object_or_404(Claim, pk=claim_id)
        initial = dict(
            billing_provider=claim.billing_provider,
            rendering_provider=claim.rendering_provider,
            payer_type="Patient",
            payer_patient=claim.patient)

    if request.method == "GET" and initial:
        form = PaymentMakeForm(initial=initial)
    else:
        form = PaymentMakeForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        Payment.objects.create(user=request.user, **form.cleaned_data)
        return redirect(reverse('dashboard:dashboard'))
    return render(request, 'accounting/payment/create.html', {'form': form})

def payment_apply_read(request):
    pcs_form = PaymentClaimSearchForm(request.POST or None)

    if request.method == 'POST' and pcs_form.is_valid():
        cleaned_data = pcs_form.cleaned_data
        search_type = cleaned_data.get('search_type')

        if search_type == 'create_patient_charge':
            location = 'accounting:charge_patient_create'
        else:
            location = 'accounting:payment_apply_create'

        return redirect(reverse(location, kwargs={
                'payment_id': cleaned_data.get('payment'),
                'claim_id': cleaned_data.get('claim')}))

    context = {
        'pcs_form': pcs_form,
    }

    return render(request, 'accounting/apply/read.html', context)

def apply_create(request, payment_id, claim_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    claim = get_object_or_404(Claim, pk=claim_id)

    pcs_form = PaymentClaimSearchForm(initial={
            'payment': payment_id,
            'claim': claim_id})

    ApplyFormSet = formset_factory(
        wraps(ApplyForm)(partial(ApplyForm,
            claim_id=claim_id,
            payment_id=payment_id,)),
        formset=BaseApplyFormSet,
        extra=0,
    )

    charges = Charge.objects.filter(
            procedure__claim=claim_id,
            payer_type=payment.payer_type)

    other_charges = Charge.objects.filter(
            procedure__claim=claim_id)\
            .exclude(payer_type=payment.payer_type)

    apply_data = [{
        'charge': c.pk,
        'date_of_service': c.procedure.date_of_service,
        'cpt_code_text': c.procedure.cpt.cpt_code,
        'charge_amount': c.amount,
        'balance': c.balance,
        'resp_type': c.resp_type,
    } for c in charges]

    other_apply_data = [{
        'charge': c.pk,
        'date_of_service': c.procedure.date_of_service,
        'cpt_code_text': c.procedure.cpt.cpt_code,
        'charge_amount': c.amount,
        'balance': c.balance,
        'resp_type': c.resp_type,
    } for c in other_charges]

    notes = claim.note_set.all();

    if request.method == 'POST':
        apply_formset = ApplyFormSet(request.POST)
        if apply_formset.is_valid():
            new_applies = []
            total_amount = Decimal('0.00')
            n = timezone.now()

            for apply_form in apply_formset:
                cleaned_data = apply_form.cleaned_data
                amount = cleaned_data.get('amount')
                adjustment = cleaned_data.get('adjustment')

                if (payment.payer_type == 'Insurance' and \
                        (amount is not None or adjustment is not None)) or \
                        (payment.payer_type == 'Patient' and \
                        amount is not None):
                    new_applies.append(Apply(
                            user=request.user,
                            created=n,
                            **cleaned_data))
                    total_amount += amount

            Apply.objects.bulk_create(new_applies)
            messages.add_message(request, messages.SUCCESS,
                    "$%s from Payment ID: \"%s\" has been applied." % \
                    (total_amount, payment_id))

            return redirect(reverse('accounting:payment_apply_create',
                    kwargs={
                        'payment_id': payment_id,
                        'claim_id': claim_id}))
    else:
        apply_formset = ApplyFormSet(initial=apply_data)

    return render(request, 'accounting/apply/create.html', {
            'pcs_form': pcs_form,
            'payment': payment,
            'claim': claim,
            'apply_formset': apply_formset,
            'apply_data': apply_data,
            'other_apply_data': other_apply_data,
            'notes': notes})

def charge_patient_create(request, payment_id, claim_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    claim = get_object_or_404(Claim, pk=claim_id)

    pcs_form = PaymentClaimSearchForm(initial={
            'payment': payment_id,
            'claim': claim_id})

    PCFormSet = formset_factory(
            wraps(PatientChargeForm)
                (partial(PatientChargeForm,
                    claim_id=claim_id)),
            formset=BasePatientChargeFormSet,
            extra=1)

    pc_formset = PCFormSet(request.POST or None)

    if request.method == 'POST' and pc_formset.is_valid():
        try:
            with transaction.atomic():
                for pc_form in pc_formset:
                    cleaned_data = pc_form.cleaned_data

                    procedure = cleaned_data.get('procedure')
                    payment = cleaned_data.get('payment')
                    charge_amount = cleaned_data.get('charge_amount')
                    resp_type = cleaned_data.get('resp_type')
                    apply_amount = cleaned_data.get('apply_amount')
                    reference = cleaned_data.get('reference')

                    if procedure and payment and \
                            charge_amount and resp_type:
                        charge = Charge.objects.create(
                                procedure=procedure,
                                payer_type='Patient',
                                amount=charge_amount,
                                resp_type=resp_type)

                        if payment.payer_type == 'Patient' and apply_amount:
                            Apply.objects.create(
                                    payment=payment,
                                    charge=charge,
                                    amount=apply_amount,
                                    adjustment=None,
                                    reference=reference)

            return redirect(reverse('accounting:payment_apply_create',
                    kwargs={
                        'payment_id': payment_id,
                        'claim_id': claim_id}))
        except IntegrityError:
            print 'IntegrityError has occured.'

    return render(request, 'accounting/charge/patient_create.html', {
            'pcs_form': pcs_form,
            'payment': payment,
            'claim': claim,
            'pc_formset': pc_formset})


###############################################################################
# API function
###############################################################################
def api_search_payment(request):
    if request.method == 'POST':
        post_data = request.POST
        payment = Payment.objects.filter(
            id__contains=post_data.get('payment_id') or '',
            amount__icontains=post_data.get('amount') or '',
        )

        if post_data.get('check_number'):
            payment = payment.filter(
                    check_number__icontains=post_data.get('check_number'))

        insurance_name = post_data.get('insurance_name')
        last_name = post_data.get('last_name')
        first_name = post_data.get('first_name')

        if len(insurance_name) == 0:
            insurance_name = None
        if len(last_name) == 0:
            last_name = None
        if len(first_name) == 0:
            first_name = None

        insurance_kwargs = dict()
        if insurance_name is not None:
            insurance_kwargs['payer_insurance__name__icontains'] = insurance_name
        patient_kwargs = dict()
        if last_name is not None:
            patient_kwargs['payer_patient__last_name__icontains'] = last_name
        if first_name is not None:
            patient_kwargs['payer_patient__first_name__icontains'] = first_name

        if insurance_name is None:
            payment = payment.filter(Q(**patient_kwargs))
        elif last_name is None and first_name is None:
            payment = payment.filter(Q(**insurance_kwargs))
        else:
            payment = payment.filter(
                Q(**insurance_kwargs) | \
                Q(**patient_kwargs)
            )

        se = ExtPythonSerializer().serialize(
            payment,
            props=['unapplied_amount',],
            use_natural_foreign_keys=True
        )

        return JsonResponse(data=se, safe=False)
    else:
        return JsonResponse([], safe=False)

def api_search_claim(request):
    if request.method == 'POST':
        post_data = request.POST
        claim = Claim.objects.filter(
            id__contains=post_data.get('claim_id') or '',
            patient__first_name__icontains=post_data.get('first_name') or '',
            patient__last_name__icontains=post_data.get('last_name') or '',
        )

        if post_data.get('dob'):
            dob = datetime.strptime(post_data.get('dob'), '%m/%d/%Y')
            claim = claim.filter(patient__dob=dob.strftime('%Y-%m-%d'))

        s = serializers.serialize('python', claim, use_natural_foreign_keys=True)
        return JsonResponse(data=s, safe=False)
    else:
        return JsonResponse([], safe=False)

def api_create_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            Note.objects.create(
                    author=request.user,
                    **cleaned_data)

            return JsonResponse('', safe=False)

    return HttpResponseBadRequest('', content_type='application/json')
