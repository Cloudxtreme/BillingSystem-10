from django import forms

from localflavor.us.forms import USZipCodeField, USStateSelect, USPhoneNumberField, USStateField
from localflavor.us.us_states import STATE_CHOICES

from .models import *
from base.models import BASE_DECIMAL


class SearchTransactionReport(forms.Form):
    date = forms.CharField()
    name = forms.CharField()
    size = forms.CharField()

    def clean(self):
        cleaned_data = super(SearchTransactionReport, self).clean()
        payment_id = cleaned_data.get('date')
        claim_id = cleaned_data.get('name')
        search_type = cleaned_data.get('size')

        # try:
        #     payment = Payment.objects.get(pk=payment_id)
        #     # if search_type == 'create_patient_charge' and \
        #     #         payment.payer_type != 'Patient':
        #     #     self.add_error('payment',
        #     #             'Given payment is not payer type \"Patient\"')
        # except:
        #     self.add_error('payment', 'Payment with given ID does not exist')

        # try:
        #     Claim.objects.get(pk=claim_id)
        # except:
        #     self.add_error('claim', 'Claim with given ID does not exist')