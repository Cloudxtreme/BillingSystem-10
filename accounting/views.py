from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

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
        AppliedPayment.objects.create(**form.cleaned_data)
        return redirect(reverse('dashboard:dashboard'))

    return render(request, 'accounting/payment/apply.html', {'form': form})