from django.forms import ModelForm
from infoGatherer.models import Personal_Information, Guarantor_Information, Insurance_Information
from django import forms
from django.forms import extras
from infoGatherer.models import PostAd, ReferringProvider, dx, Provider, CPT
from infoGatherer.models import Personal_Information, Payer
from localflavor.us.forms import USZipCodeField, USStateSelect, USPhoneNumberField, USStateField
from localflavor.us.us_states import STATE_CHOICES
import datetime
from django.forms.utils import ErrorList
from django.conf import settings
from .models import (HEALTHPLAN, SEX, PAT_RELA_TO_INSURED, DX_PT, UNIT)


FORMAT_DATE = settings.CONFIG.get('format').get('date')
DEFAULT_NONE_POLICY = settings.CONFIG.get('default').get('none_policy')


class CptForms(forms.ModelForm):
    cpt_charge = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Charges ($)'}))
    cpt_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'CPT/HCPCS code'}))
    cpt_description=forms.CharField(required=False)
    class Meta:
        model = CPT
        fields = '__all__'
        widgets = {}

class OtherProviderForm(ModelForm):
    provider_name=forms.CharField(required=False)
    role=forms.CharField(required=False)
    class Meta:
        model = Provider
        fields = '__all__'

class ReferringProviderForm(ModelForm):
    last_name=forms.CharField(required=False)

    class Meta:
        model = ReferringProvider
        fields = '__all__'

class dxForm(ModelForm):
    ICD_10 = forms.CharField(required=False)
    description = forms.CharField(required=False)
    class Meta:
        model = dx
        fields = '__all__'

class PostAdForm(forms.Form):
    error_css_class = 'error'
    # Customize state options to start with not select
    CUSTOM_STATE_CHOICES = list(STATE_CHOICES)
    CUSTOM_STATE_CHOICES.insert(0, ('', 'Choose state'))


    # Id hidden fields to link records in the database
    pat_id = forms.ModelChoiceField(queryset=Personal_Information.objects.all(), widget=forms.HiddenInput())
    insured_id = forms.ModelChoiceField(queryset=Personal_Information.objects.all(), widget=forms.HiddenInput())
    other_insured_id = forms.ModelChoiceField(required=False, queryset=Personal_Information.objects.all(), widget=forms.HiddenInput())
    payer_id = forms.ModelChoiceField(queryset=Payer.objects.all(), widget=forms.HiddenInput())


    # Payer section
    payer_num = forms.CharField(max_length=10)
    payer_name = forms.CharField(max_length=255)
    payer_address = forms.CharField(max_length=255)
    health_plan = forms.ChoiceField(choices=HEALTHPLAN)
    

    # Patient section
    pat_name = forms.CharField(max_length=255)
    pat_streetaddress = forms.CharField(max_length=255)
    pat_city = forms.CharField(max_length=50)
    pat_state = USStateField(widget=forms.Select(choices=CUSTOM_STATE_CHOICES))
    pat_zip = USZipCodeField()
    pat_telephone = USPhoneNumberField()
    pat_birth_date = forms.DateField()
    pat_sex = forms.ChoiceField(choices=SEX)
    pat_relationship_insured = forms.ChoiceField(choices=PAT_RELA_TO_INSURED)
    pat_relation_emp = forms.BooleanField(initial=False, required=False)
    pat_relation_other_accident =forms.BooleanField(initial=False, required=False)
    pat_relation_auto_accident = forms.BooleanField(initial=False, required=False)
    pat_auto_accident_state = USStateField(required=False, widget=forms.Select(choices=CUSTOM_STATE_CHOICES))


    # Insured section (id is id field in database whereas idnumber is number on insurance card)
    insured_idnumber = forms.CharField(max_length=255)
    insured_name = forms.CharField(max_length=255)
    insured_streetaddress = forms.CharField(max_length=255)
    insured_city = forms.CharField(max_length=50)
    insured_state = USStateField(widget=forms.Select(choices=CUSTOM_STATE_CHOICES))
    insured_zip = USZipCodeField()
    insured_telephone = USPhoneNumberField()
    insured_policy = forms.CharField(
        required=False,
        max_length=100,
        initial=DEFAULT_NONE_POLICY,
    )
    insured_birth_date = forms.DateField()
    insured_sex = forms.ChoiceField(choices=SEX)


    # Other insured section
    insured_other_benifit_plan = forms.BooleanField(initial=False, required=False)
    pat_other_insured_name = forms.CharField(required=False, max_length=255)
    pat_other_insured_policy = forms.CharField(required=False, max_length=100)


    # Not required fields
    pat_reservednucc1 = forms.CharField(max_length=100, required=False)
    pat_reservednucc2 = forms.CharField(max_length=100, required=False)
    pat_reservednucc3 = forms.CharField(max_length=100, required=False)
    other_insured_insur_plan_name = forms.CharField(max_length=100, required=False)
    claim_codes = forms.CharField(max_length=100, required=False)
    other_cliam_id = forms.CharField(max_length=100, required=False)
    insured_insur_plan_name = forms.CharField(max_length=100, required=False)


    # Physician section
    referring_name = forms.CharField(max_length=255)
    NPI = forms.CharField(max_length=15)


    # Provider section
    billing_provider_name = forms.CharField(max_length=255)
    billing_provider_address = forms.CharField(max_length=255)
    billing_provider_telephone = USPhoneNumberField()
    billing_provider_npi = forms.CharField(max_length=15)
    
    location_provider_name = forms.CharField(max_length=255)
    location_provider_address = forms.CharField(max_length=255)
    location_provider_npi = forms.CharField(max_length=15)
    
    rendering_provider_name = forms.CharField(max_length=255)
    rendering_provider_npi = forms.CharField(max_length=15)


    # Procedure section will be generated at runtime
    def __init__(self, loop_times, *args, **kwargs):
        super(PostAdForm, self).__init__(*args, **kwargs)
        self.dx_times = 12
        self.lines = 6
        self.columns = 4

        # Diagnosis section
        for i in loop_times:
            self.fields['ICD_10_%s' % (i+1)] = forms.CharField(max_length=8, required=False)

        # Procedure section
        for i in xrange(1, self.lines+1):
            self.fields['cpt_code_%s' % i] = forms.CharField(max_length=10, required=False)
            self.fields['service_start_date_%s' % i] = forms.DateField()
            self.fields['place_of_service_%s' % i] = forms.CharField(max_length=5)
            self.fields['emg_%s' % i] = forms.CharField(max_length=5, required=False)
            self.fields['cpt_charge_%s' % i] = forms.FloatField(required=False)
            self.fields['note_%s' % i] = forms.CharField(max_length=255, required=False)
            self.fields['total_%s' % i] = forms.FloatField(initial=0)

            for j in xrange(1, self.columns+1):
                self.fields['dx_pt_s%s_%s' % (j, i)] = forms.ChoiceField(required=False, choices=DX_PT)
                self.fields['mod_%s_%s' % ( chr(ord('a')+j-1), i )] = forms.CharField(max_length=5, required=False)

            # Calculator option
            self.fields['start_time_%s' % i] = forms.TimeField(required=False)
            self.fields['end_time_%s' % i] = forms.TimeField(required=False)
            self.fields['base_units_%s' % i] = forms.IntegerField(required=False, initial=5)
            self.fields['time_units_%s' % i] = forms.IntegerField(required=False)
            self.fields['fees_%s' % i] = forms.FloatField(required=False)
            
            # Drug information option
            self.fields['proc_code_%s' % i] = forms.CharField(max_length=100, required=False)
            self.fields['ndc_%s' % i] = forms.CharField(max_length=20, required=False)
            self.fields['qty_%s' % i] = forms.FloatField(required=False)
            self.fields['unit_%s' % i] = forms.ChoiceField(choices=UNIT)

    def is_valid(self):
        valid = super(PostAdForm, self).is_valid()
        if not valid:
            valid = False

        for i in xrange(1, self.lines+1):
            ### Pending - how to determine if it is calculator or drug information and this is displayed on the page ###
            # if self.cleaned_data['start_time_%s' % i] and not self.cleaned_data['end_time_%s' % i]:
            #     self._errors['end_time_%s' % i] = ErrorList(['There is start period but not end period.'])
            #     valid = False
            # if not self.cleaned_data['start_time_%s' % i] and self.cleaned_data['end_time_%s' % i]:
            #     self._errors['start_time_%s' % i] = ErrorList(['There is end period but not start period.'])
            #     valid = False

            for j in xrange(1, self.columns+1):
                if self.cleaned_data['dx_pt_s%s_%s' % (j, i)]:
                    char = self.cleaned_data['dx_pt_s%s_%s' % (j, i)]
                    num = ord(char.upper()) - ord('A') + 1
                    if not self.cleaned_data['ICD_10_%s' % num]:
                        self.error['ICD_10_%s' % num] = ErrorList(['Diagnosis pointer is pointing to empty element in Diagnosis List'])
                        valid = False

        if self.cleaned_data['pat_relation_auto_accident'] == True and not self.cleaned_data['pat_auto_accident_state']:
            self._errors['pat_auto_accident_state'] = ErrorList(['Auto accident must select state.'])
            valid = False

        if not self.cleaned_data['insured_policy']:
            self.cleaned_data['insured_policy'] = DEFAULT_NONE_POLICY

        if self.cleaned_data['pat_other_insured_name'] and not self.cleaned_data['pat_other_insured_policy']:
            self.cleaned_data['pat_other_insured_policy'] = DEFAULT_NONE_POLICY

        return valid


class PatientForm(ModelForm):
    class Meta:
        model = Personal_Information
        fields = '__all__'
        
class GuarantorForm(ModelForm):
    class Meta:
        model = Guarantor_Information
        fields = '__all__'
        
    def clean(self):
        cleaned_data = super(GuarantorForm, self).clean()
        rel = cleaned_data.get('relation')
        if rel == "Self":
            self['first_name'].required = False
            self['last_name'].required = False
            self['dob'].required = False
            self['address'].required = False
            self['city'].required = False
            self['zip'].required = False
            self['home_phone'].required = False
            
class InsuranceForm(ModelForm):
    class Meta:
        model = Insurance_Information
        fields = '__all__'


class ClaimForm(ModelForm):
    pass

