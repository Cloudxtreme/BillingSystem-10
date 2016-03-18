from django.shortcuts import render, redirect, get_list_or_404
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import JsonResponse

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

        s = serializers.serialize('python', payment, use_natural_foreign_keys=True)
        return JsonResponse(data=s, safe=False)
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


# def get_make_claim_extra_context(request):
#     p_set = Personal_Information.objects.values('chart_no', 'first_name', 'last_name', 'address', 'city').order_by('first_name')
#     context = {'patients': list(p_set),}
#     return JsonResponse(data=context);

# def get_json_personal_info(request):
#     personal_q_set = Personal_Information.objects.filter(pk=request.POST['personal_chart_no'])
#     context = {"personal_information": list(personal_q_set.values()),}
#     return JsonResponse(data=context)

# def get_json_personal_and_insurance_info(request):
#     personal_set = Personal_Information.objects.filter(pk=request.POST['personal_chart_no'])
#     insurance_set = personal_set[0].insurance_information_set.all().select_related("payer")
#     i_set_dict = insurance_set.values()
#     i_set = [i for i in i_set_dict]

#     for i in range(len(i_set)):
#         i_set[i]["payer"] = model_to_dict(insurance_set[i].payer)

#     context = {
#         "personal_information": list(personal_set.values()),
#         "insurance_list": i_set,
#     }

#     return JsonResponse(data=context);

# def get_json_physician_info(request):
#     phy_q_set = ReferringProvider.objects.all()
#     context = {"physicians": list(phy_q_set.values()),}
#     return JsonResponse(data=context)

# def get_json_provider_info(request):
#     context = {}
#     for choice in PROVIDER_ROLE_CHOICES:
#         key = choice[0]
#         value = choice[1]
#         provider_q_set = Provider.objects.filter(role=key)
#         context[value] = list(provider_q_set.values())
    
#     return JsonResponse(data=context)