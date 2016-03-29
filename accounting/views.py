from functools import partial, wraps

from django.shortcuts import *
from django.core import serializers
from django.core.urlresolvers import reverse
from django.forms import formset_factory
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models import Q

from datetime import datetime

from .models import *
from .forms import *
from base.models import ExtPythonSerializer


def payment_summary(request):
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
        procedureList=Procedure.objects.filter(claim_id=claim_id).values()
        totalCharge=0
        totalAppliedAmnt=0
        totalAdjustments=0
        for procedure in procedureList:
            totalCharge=totalCharge+procedure['charge']
            totalAppliedAmnt=totalAppliedAmnt+(AppliedPayment.objects.filter(procedure_id=procedure['id']).all().aggregate(Sum('amount'))['amount__sum'] or 0)
            totalAdjustments=totalAdjustments+(AppliedPayment.objects.filter(procedure_id=procedure['id']).all().aggregate(Sum('adjustment'))['adjustment__sum'] or 0)
        temp["totalCharge"]=totalCharge
        temp["totalAppliedAmnt"]=totalAppliedAmnt
        temp["totalAdjustments"]=totalAdjustments
        temp["balance"]=totalCharge-totalAppliedAmnt+totalAdjustments
        dic.append(temp)
    return render(request, 'accounting/payment/accounts_summary.html', {'summary': dic})

def payment_create(request):
    form = PaymentMakeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        Payment.objects.create(**form.cleaned_data)
        return redirect(reverse('dashboard:dashboard'))
    return render(request, 'accounting/payment/create.html', {'form': form})

def payment_apply_read(request):
    form = PaymentApplyReadForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data

        return redirect(reverse('accounting:payment_apply_create', kwargs={
            'payment_id': data.get('payment'),
            'claim_id': data.get('claim'),
        }))

    context = {
        'form': form,
    }

    return render(request, 'accounting/payment/apply_read.html', context)

def payment_apply_create(request, payment_id, claim_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    claim = get_object_or_404(Claim, pk=claim_id)

    PaymentApplyFormSet = formset_factory(
        wraps(PaymentApplyCreateForm)\
            (partial(
                PaymentApplyCreateForm,
                claim_id=claim_id,
                payment_id=payment_id
            )),
        formset=BasePaymentApplyCreateFormSet,
        extra=0,
    )

    procedures = Procedure.objects.filter(claim=claim_id)
    apply_data = [{
        'procedure': p.pk,
        'date_of_service': p.date_of_service,
        'cpt_code_text': p.cpt.cpt_code,
        'charge': p.charge,
        'balance': p.balance,
    } for p in procedures]

    PatientChargeFormSet = formset_factory(
            wraps(PatientChargeForm)\
                (partial(
                    PatientChargeForm,
                    claim_id=claim_id)),
            extra=0)
    PatientAppliedPaymentFormSet = formset_factory(
            PatientAppliedPaymentForm,
            extra=len(apply_data))

    if request.method == 'POST':
        apply_formset = PaymentApplyFormSet(request.POST)
        if apply_formset.is_valid():
            new_applied = []
            for apply_form in apply_formset:
                data = apply_form.cleaned_data
                amount = data.get('amount')
                adjustment = data.get('adjustment')

                if amount is not None or \
                    adjustment is not None:

                    new_applied.append(AppliedPayment(**data))

            AppliedPayment.objects.bulk_create(new_applied)

            return redirect(reverse('accounting:payment_apply_create', kwargs={
                'payment_id': payment_id,
                'claim_id': claim_id,
            }))

    else:
        apply_formset = PaymentApplyFormSet(initial=apply_data)
        charge_formset = PatientChargeFormSet(initial=apply_data)
        patient_apply_formset = PatientAppliedPaymentFormSet()


    print '--------------------------------------------------------------------------------'
    print charge_formset[0]
    print '--------------------------------------------------------------------------------'

    context = {
        'payment': payment,
        'claim': claim,
        'apply_formset': apply_formset,
        'apply_data': apply_data,
        'charge_formset': charge_formset,
        'patient_apply_formset': patient_apply_formset,
    }

    return render(request, 'accounting/payment/apply_create.html', context)

def apply_create(request, payment_id, claim_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    claim = get_object_or_404(Claim, pk=claim_id)

    ApplyFormSet = formset_factory(
        wraps(ApplyForm)(partial(ApplyForm, claim_id=claim_id)),
        formset=BasePaymentApplyCreateFormSet,
        extra=0,
    )

    charges = Charge.objects.filter(procedure__claim=claim_id)
    apply_data = [{
        'charge': c.pk,
        'date_of_service': c.procedure.date_of_service,
        'cpt_code_text': c.procedure.cpt.cpt_code,
        'charge_amount': c.amount,
        'balance': c.balance,
    } for c in charges]

    if request.method == 'POST':
        apply_formset = ApplyFormSet(request.POST)
        if apply_formset.is_valid():
            new_applies = []
            for apply_form in apply_formset:
                cleaned_data = apply_form.cleaned_data
                amount = cleaned_data.get('amount')
                adjustment = cleaned_data.get('adjustment')

                if amount is not None or adjustment is not None:
                    new_applies.append(Apply(**cleaned_data))

            Apply.objects.bulk_create(new_applies)

            if payment.payer_type == 'Insurance':
                return redirect(reverse('accounting:payment_apply_create',
                        kwargs={
                            'payment_id': payment_id,
                            'claim_id': claim_id}))
    else:
        apply_formset = ApplyFormSet(initial=apply_data)

    return render(request, 'accounting/payment/apply_create.html', {
            'payment': payment,
            'claim': claim,
            'apply_formset': apply_formset,
            'apply_data': apply_data})


###############################################################################
# API function for ajax call from front end page
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
            dob = datetime.datetime.strptime(post_data.get('dob'), '%m/%d/%Y')
            claim = claim.filter(patient__dob=dob.strftime('%Y-%m-%d'))

        s = serializers.serialize('python', claim, use_natural_foreign_keys=True)
        return JsonResponse(data=s, safe=False)
    else:
        return JsonResponse([], safe=False)
