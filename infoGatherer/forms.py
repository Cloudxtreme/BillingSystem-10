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


"""
CATEGORIES = (
    ('LAB', 'labor'),
    ('CAR', 'cars'),
    ('TRU', 'trucks'),
    ('WRI', 'writing'),
)
"""
HEALTHPLAN = (
    ('Medicare', 'Medicare'),
    ('Medicaid', 'Medicaid'),
    ('Tricare', 'Tricare'),
    ('Champva', 'Champva'),
    ('GroupHealthPlan', 'GroupHealthPlan'),
    ('FECA_Blk_Lung', 'FECA Blk Lung'),
    ('Other', 'Other'),
)
SEX = (
    ('', '-----'),
    ('M', 'Male'),
    ('F', 'Female'),
)
REL_INSUR = (  
    ('Self', 'Self'),
    ('Spouse', 'Spouse'),
    ('Child', 'Child'),
    ('Other', 'Other'),
)
DX_PT = (
    ('', '---'),
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
    ('F', 'F'),
    ('G', 'G'),
    ('H', 'H'),
    ('I', 'I'),
    ('J', 'J'),
    ('K', 'K'),
    ('L', 'L'),
)
UNIT = (  
    ('ME', 'Milligram'),
    ('F2', 'International Unit'),
    ('GR', 'Gram'),
    ('ML', 'Milliliter'),
    ('UN', 'Unit'),
)


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

    #Get entries from databse
    patient_list = Personal_Information.objects.order_by('first_name')


    # Customize state options to start with not select
    CUSTOM_STATE_CHOICES = list(STATE_CHOICES)
    CUSTOM_STATE_CHOICES.insert(0, ('', 'Choose state'))


    # Id hidden fields to link records in the database
    pat_id = forms.ModelChoiceField(queryset=Personal_Information.objects.all(), widget=forms.HiddenInput())
    insured_id = forms.ModelChoiceField(queryset=Personal_Information.objects.all(), widget=forms.HiddenInput())
    other_insured_id = forms.ModelChoiceField(required=False, queryset=Personal_Information.objects.all(), widget=forms.HiddenInput())
    payer_id = forms.ModelChoiceField(queryset=Payer.objects.all(), widget=forms.HiddenInput())


    # Payer section
    health_plan = forms.ChoiceField(choices=HEALTHPLAN, required=False)
    payer_num = forms.CharField()
    payer_name = forms.CharField()
    payer_address = forms.CharField()
    

    # Patient section
    pat_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name, First Name, Middle Initial'}),
    )
    pat_streetaddress = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'No., Street'}),
    )
    pat_city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'City'}),
    )
    pat_state = USStateField(widget=forms.Select(choices=CUSTOM_STATE_CHOICES))
    pat_zip = USZipCodeField(widget=forms.TextInput(attrs={'placeholder': 'Zip'}))
    pat_telephone = USPhoneNumberField()
    pat_birth_date = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'MM/DD/YYYY'}))
    pat_sex = forms.ChoiceField(choices=SEX)
    pat_relationship_insured = forms.ChoiceField(choices=REL_INSUR)
    pat_relation_emp = forms.BooleanField(initial=False, required=False)
    pat_relation_other_accident =forms.BooleanField(initial=False, required=False)
    pat_relation_auto_accident = forms.BooleanField(initial=False, required=False)
    pat_auto_accident_state = USStateField(required=False, widget=forms.Select(choices=CUSTOM_STATE_CHOICES))


    # Insured section (id is id field in database whereas idnumber is number on insurance card)
    insured_idnumber = forms.CharField(max_length=255)
    insured_name = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name, First Name, Middle Initial'}),
    )
    insured_streetaddress = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'No., Street'}),
    )
    insured_city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'City'}),
    )
    insured_state = USStateField(widget=forms.Select(choices=CUSTOM_STATE_CHOICES))
    insured_zip = USZipCodeField(widget=forms.TextInput(attrs={'placeholder': 'Zip'}))
    insured_telephone = USPhoneNumberField()
    insured_policy = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': '', 'value': 'None'})
    )
    insured_birth_date = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'MM/DD/YYYY'}))
    insured_sex = forms.ChoiceField(choices=SEX)


    # Other insured section
    insured_other_benifit_plan = forms.BooleanField(initial=False, required=False)
    pat_other_insured_name = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name, First Name, Middle Initial'}),
    )
    pat_other_insured_policy = forms.CharField(required=False)


    # Not required fields
    pat_reservednucc1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '8'}))
    pat_reservednucc2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '9 (b)'}))
    pat_reservednucc3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '9 (c)'}))
    other_insured_insur_plan_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '9 (d)'}))
    claim_codes = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '10 (d)'}))
    other_cliam_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '11 (b)'}))    
    insured_insur_plan_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '11 (c)'}))


    # Physician section
    referring_name = forms.CharField(max_length=255)
    NPI = forms.CharField(max_length=15)


    # Provider section
    billing_provider_name = forms.CharField(max_length=100)
    billing_provider_address = forms.CharField(max_length=255)
    billing_provider_telephone = USPhoneNumberField()
    billing_provider_npi = forms.CharField(max_length=15)
    
    location_provider_name = forms.CharField(max_length=100)
    location_provider_address = forms.CharField(max_length=255)
    location_provider_npi = forms.CharField(max_length=15)
    
    rendering_provider_name = forms.CharField(max_length=100)
    rendering_provider_npi = forms.CharField(max_length=15)


    # Procedure section will be in separate form


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
            self.fields['cpt_code_%s' % i] = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'CPT/HCPCS code'}))
            self.fields['service_start_date_%s' % i] = forms.DateField(required=False, widget=forms.DateInput(attrs={
                'class': 'dateValidation',
                'placeholder': 'MM/DD/YYYY',
            }))
            self.fields['place_of_service_%s' % i] = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Place of Service'}))
            self.fields['emg_%s' % i] = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'EMG'}))
            self.fields['cpt_charge_%s' % i] = forms.FloatField(required=False, widget=forms.NumberInput(attrs={
                'placeholder': 'Charges ($)',
                'step': '0.01'
            }))
            self.fields['note_%s' % i] = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Note'}))
            self.fields['total_%s' % i] = forms.FloatField(widget=forms.NumberInput(attrs={
                'value': 0,
                'readonly': True,
            }))

            for j in xrange(1, self.columns+1):
                self.fields['dx_pt_s%s_%s' % (j, i)] = forms.ChoiceField(required=False, choices=DX_PT, widget=forms.Select(attrs={'class': 'dropValidation'}))
                self.fields['mod_%s_%s' % ( chr(ord('a')+j-1), i )] = forms.CharField(
                    required=False,
                    widget=forms.TextInput(attrs={'placeholder': 'Mod ' + chr(ord('A')+j-1)})
                )

            # Calculator option
            self.fields['start_time_%s' % i] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-small'}))
            self.fields['end_time_%s' % i] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-small'}))
            self.fields['base_units_%s' % i] = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'value': 5}))
            self.fields['time_units_%s' % i] = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'readonly': True}))
            self.fields['fees_%s' % i] = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
            
            # Drug information option
            self.fields['proc_code_%s' % i] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-small'}))
            self.fields['ndc_%s' % i] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-small'}))
            self.fields['qty_%s' % i] = forms.FloatField(required=False, widget=forms.NumberInput(attrs={
                'step': '0.01',
                'min': 0,
                'class': 'input-small',
            }))
            self.fields['unit_%s' % i] = forms.ChoiceField(choices=UNIT)


    def is_valid(self):
        valid = super(PostAdForm, self).is_valid()
        if not valid:
            valid = False

        for i in xrange(1, self.lines+1):
            if self.cleaned_data['start_time_%s' % i] and not self.cleaned_data['end_time_%s' % i]:
                self._errors['end_time_%s' % i] = ErrorList(['There is start period but not end period.'])
                valid = False
            if not self.cleaned_data['start_time_%s' % i] and self.cleaned_data['end_time_%s' % i]:
                self._errors['start_time_%s' % i] = ErrorList(['There is end period but not start period.'])
                valid = False

            for j in xrange(1, self.columns+1):
                if self.cleaned_data['dx_pt_s1_%s' % i]:
                    char = self.cleaned_data['dx_pt_s%s_%s' % (j, i)]
                    num = ord(char.upper()) - ord('A') + 1
                    if not self.cleaned_data['ICD_10_%s' % num]:
                        self.error['ICD_10_%s' % num] = ErrorList(['Diagnonsis pointer points to empty element in CPT list'])
                        valid = False


        if self.cleaned_data['pat_relation_auto_accident'] == True and not self.cleaned_data['pat_auto_accident_state']:
            self._errors['pat_auto_accident_state'] = ErrorList(['Auto accident must select state.'])
            valid = False

        if not self.cleaned_data['insured_policy']:
            self.cleaned_data['insured_policy'] = 'None'


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

