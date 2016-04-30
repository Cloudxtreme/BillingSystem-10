from django import forms

from localflavor.us.forms import USZipCodeField, USStateSelect, USPhoneNumberField, USStateField
from localflavor.us.us_states import STATE_CHOICES

from .models import *
from base.models import BASE_DECIMAL
from infoGatherer.models import (
        Provider,)

REPORTS = (
    ('1', 'Transaction report without payment summary'),
    ('2', 'Transaction report with payment summary'),
)

class SearchTransactionReport(forms.Form):
    reporttype = forms.ChoiceField(choices=REPORTS)
    startdate = forms.DateField()
    enddate = forms.DateField()
    renderingprovider  = forms.ModelMultipleChoiceField(queryset=Provider.objects.filter(role="Rendering").all(), required=False,  widget=forms.SelectMultiple)
    locationprovider  = forms.ModelMultipleChoiceField(queryset=Provider.objects.filter(role="Location").all(), required=False,  widget=forms.SelectMultiple)

    def clean(self):
        cleaned_data = super(SearchTransactionReport, self).clean()
        reporttype = cleaned_data.get('reporttype')
        startdate = cleaned_data.get('startdate')
        enddate = cleaned_data.get('enddate')
