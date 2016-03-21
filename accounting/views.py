from django.shortcuts import render, redirect, get_list_or_404
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.db.models import Sum

from datetime import datetime

from .models import *
from .forms import *


def payment_create(request):
    form = PaymentMakeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        Payment.objects.create(**form.cleaned_data)
        return redirect(reverse('dashboard:dashboard'))

    return render(request, 'accounting/payment/create.html', {'form': form})

def payment_apply(request):
    form = PaymentApplyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        data['adjustment'] = data.get('adjustment') or 0

        AppliedPayment.objects.create(**data)
        return redirect(reverse('dashboard:dashboard'))

    return render(request, 'accounting/payment/apply.html', {'form': form})

def api_search_payment(request):
    if request.method == 'POST':
        post_data = request.POST
        payment = Payment.objects.filter(
            id__contains=post_data.get('payment_id') or '',
            amount__icontains=post_data.get('amount') or '',
        )

        if post_data.get('check_number'):
            payment = payment.filter(check_number__icontains=post_data.get('check_number'))
        if post_data.get('insurance_name'):
            payment = payment.filter(payer_insurance__name__icontains=post_data.get('insurance_name'))
        if post_data.get('last_name'):
            payment = payment.filter(payer_patient__last_name__icontains=post_data.get('last_name'))
        if post_data.get('first_name'):
            payment = payment.filter(payer_patient__first_name__icontains=post_data.get('first_name'))

        se = serializers.serialize('python', payment, use_natural_foreign_keys=True)

        # Add extra field "unapplied amount" into serialized string
        payment = payment.annotate(s=Sum('appliedpayment__amount'))
        for i, s in enumerate(se):  
            if s.items()[1][1] == payment[i].pk:
                s.items()[2][1]['unapplied_amount'] = payment[i].amount - (payment[i].s or 0)
            else:
                print 'Payment query set and serialized list are not in the same order'

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

def api_search_applied_payment(request):
    if request.method == 'POST':
        post_data = request.POST

        # Get all procedures of the claim
        procedure = Procedure.objects.filter(claim=post_data.get('claim_id'))
        p_list = serializers.serialize('python', procedure, use_natural_foreign_keys=True)

        # Get applied payment
        c = Claim.objects.get(pk=post_data.get('claim_id'))
        ap = c.appliedpayment_set.all()
        ap_list = serializers.serialize('python', ap, use_natural_foreign_keys=True)

        # Calculate amount of unapplied payment
        payment = Payment.objects.get(pk=post_data.get('payment_id'))
        payment_amount = payment.amount
        applied_amount = payment.appliedpayment_set.all().aggregate(s=Sum('amount')).get('s')
        unapplied_amount = payment_amount - applied_amount

        data = dict(
            procedure=p_list,
            applied_payment=ap_list,
            unapplied_amount=unapplied_amount
        )
        return JsonResponse(data=data, safe=False)
    else:
        return JsonResponse(dict(), safe=False)
