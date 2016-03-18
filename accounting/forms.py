import datetime

from django import forms
from django.forms import ModelForm
from django.forms.utils import ErrorList
from django.conf import settings

from localflavor.us.forms import USZipCodeField, USStateSelect, USPhoneNumberField, USStateField
from localflavor.us.us_states import STATE_CHOICES

from .models import *
from base.models import MAX_DIGITS, DECIMAL_PLACES


class PaymentMakeForm(forms.ModelForm):
    class Meta:
        model = Payment
        exclude = ['modified']

    def is_valid(self):
        valid = super(PaymentMakeForm, self).is_valid()
        data = self.cleaned_data

        if not valid:
            valid = False

        if data.get('payer_type') == 'Insurance' and data.get('payer_insurance') is None:
            valid = False
            self.add_error('payer_insurance', ErrorList(['Payer insurance is required for payer type insurance']))
        elif data.get('payer_type') == 'Patient' and data.get('payer_patient') is None:
            valid = False
            self.add_error('payer_patient', ErrorList(['Payer patient is required for payer type patient']))

        if data.get('payment_method') == 'Check' and not data.get('check_number'):
            valid = False
            self.add_error('check_number', ErrorList(['Check number is required for payment method check']))

        return valid


class PaymentApplyForm(forms.Form):
    # payment = forms.ModelChoiceField(queryset=Payment.objects.all())
    # claim = forms.ModelChoiceField(queryset=Claim.objects.all())
    procedure = forms.ModelChoiceField(queryset=Procedure.objects.all())
    amount = forms.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, min_value=0)
    adjustment = forms.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, required=False)

    payment = forms.CharField(required=True)
    claim = forms.CharField(required=True)
