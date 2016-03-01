from django.forms import ModelForm
from infoGatherer.models import Personal_Information, Guarantor_Information, Insurance_Information
from django import forms
from django.forms import extras
from infoGatherer.models import PostAd, ReferringProvider, dx, Provider, CPT
from infoGatherer.models import Personal_Information, Payer
from localflavor.us.forms import USZipCodeField, USStateSelect, USPhoneNumberField, USStateField
from localflavor.us.us_states import STATE_CHOICES
import datetime


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

class PostAdForm(forms.ModelForm):  
    error_css_class = 'error'

    #Get entries from databse
    patient_list = Personal_Information.objects.order_by('first_name')


    CUSTOM_STATE_CHOICES = list(STATE_CHOICES)
    CUSTOM_STATE_CHOICES.insert(0, ('', '---------'))


    pat_id = forms.ModelMultipleChoiceField(queryset=Personal_Information.objects.all())
    insured_id = forms.ModelMultipleChoiceField(queryset=Personal_Information.objects.all())
    other_insured_id = forms.ModelMultipleChoiceField(queryset=Personal_Information.objects.all())
    payer_id = forms.ModelMultipleChoiceField(queryset=Payer.objects.all())


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
    pat_birth_date = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'}))
    pat_sex = forms.ChoiceField(choices=SEX)
    pat_relationship_insured = forms.ChoiceField(choices=REL_INSUR, required=False)
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
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': ''})
    )
    insured_birth_date = forms.DateField(widget=forms.DateInput())
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


    # Diagnosis section
    ICD_10_1 = forms.CharField(max_length=8)
    ICD_10_2 = forms.CharField(max_length=8, required=False)
    ICD_10_3 = forms.CharField(max_length=8, required=False)
    ICD_10_4 = forms.CharField(max_length=8, required=False)
    ICD_10_5 = forms.CharField(max_length=8, required=False)
    ICD_10_6 = forms.CharField(max_length=8, required=False)
    ICD_10_7 = forms.CharField(max_length=8, required=False)
    ICD_10_8 = forms.CharField(max_length=8, required=False)
    ICD_10_9 = forms.CharField(max_length=8, required=False)
    ICD_10_10 = forms.CharField(max_length=8, required=False)


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


    # Procedure section
    dx_pt_s1_1 = forms.ChoiceField(choices=DX_PT)
    dx_pt_s1_2 = forms.ChoiceField(choices=DX_PT)
    dx_pt_s1_3 = forms.ChoiceField(choices=DX_PT)
    dx_pt_s1_4 = forms.ChoiceField(choices=DX_PT)


    class Meta:
        model = PostAd
        fields = '__all__'



class ProcedureForm(forms.Form):
    def __init__(self, lines, *args, **kwargs):
        super(ProcedureForm, self).__init__(*args, **kwargs)
        for i in xrange(lines):
            if i == 1:
                cpt_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'CPT/HCPCS code'}))
            else:
                cpt_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'CPT/HCPCS code'}))

            for j in xrange(4):
                self.fields['dx_pt_%d' % (j+1)] = forms.ChoiceField(choices=DX_PT)


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

