from django.forms import ModelForm
from infoGatherer.models import Personal_Information, Guarantor_Information, Insurance_Information
from django import forms  
from infoGatherer.models import PostAd, ReferringProvider, dx, Provider, CPT
from infoGatherer.models import Personal_Information, Payer


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
    ('M', 'Male'),
    ('F', 'Female'),
)
REL_INSUR = (  
    ('Self', 'Self'),
    ('Spouse', 'Spouse'),
    ('Child', 'Child'),
    ('Other', 'Other'),
)

class CptForms(forms.ModelForm):
    cpt_charge = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Charges ($)'}))
    cpt_code = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'CPT/HCPCS code'}))
    class Meta:
        model = CPT
        fields = '__all__'
        widgets = {}

class OtherProviderForm(ModelForm):
    class Meta:
        model = Provider
        fields = '__all__'


class BillingProviderForm(forms.Form):
    billing_provider_name = forms.CharField()
    # location_provider_name = Provider.provider_name
    # rendering_provider_name = Provider.provider_name

    class Meta:
        fields = ['billing_provider_name',]


class ReferringProviderForm(ModelForm):
    class Meta:
        model = ReferringProvider
        fields = '__all__'

class dxForm(ModelForm):
    class Meta:
        model = dx
        fields = '__all__'

class PostAdForm(forms.ModelForm):  
    error_css_class = 'error'

    #Get entries from databse
    patient_list = Personal_Information.objects.order_by('first_name')
    
    #Health Plan
    health_plan = forms.ChoiceField(choices=HEALTHPLAN, required=False )

    #Patient Info.
    #pat_name = forms.ModelChoiceField(queryset=patient_list, empty_label="(Select Name)" )
    pat_sex = forms.ChoiceField(choices=SEX, required=False )
    pat_relationship=forms.ChoiceField(choices=REL_INSUR, required=False )
    pat_relation_emp = forms.BooleanField(initial=False)
    pat_relation_other_accident =forms.BooleanField(initial=False)
    pat_relation_auto_accident = forms.BooleanField(initial=False)

    #Insured's Info
    insured_sex = forms.ChoiceField(choices=SEX, required=False )
    insured_other_benifit_plan=forms.BooleanField(initial=False)
    
    # Not required fields
    insured_name=forms.CharField(required=False)
    pat_other_insured_name=forms.CharField(required=False)
    pat_other_insured_policy=forms.CharField(required=False)
    pat_reservednucc1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '8'}))
    pat_reservednucc2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '9 (b)'}))
    pat_reservednucc3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '9 (c)'}))
    pat_insuranceplanname = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '9 (d)'}))
    other_cliam_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '11 (b)'}))

    pat_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Patient\'s name'}))
    birth_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'}))
    insured_idnumber = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': ''}))
    insured_streetaddress = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'No,. Street'}))
    insured_city = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    insured_state = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'State'}))
    insured_zip = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Zip'}))
    insured_telephone = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone No.'}))
    pat_auto_accident_state = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'State'}))
    claim_codes = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '10 (d)'}))
    insured_other_insured_policy = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': ''}))
    insured_plan_name_program = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '11 (c)'}))
    payer_num = forms.CharField(required=False)
    payer_name = forms.CharField(required=False)
    payer_address = forms.CharField(required=False)
    

    class Meta:
        model = PostAd
        fields = '__all__'

        widgets = {
            'insured_birth_date': forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'}),
            'pat_streetaddress': forms.TextInput(attrs={'placeholder': 'No,. Street'}),
            'pat_city': forms.TextInput(attrs={'placeholder': 'City'}),
            'pat_state': forms.TextInput(attrs={'placeholder': 'State'}),
            'pat_zip': forms.TextInput(attrs={'placeholder': 'Zip'}),
            'pat_telephone': forms.TextInput(attrs={'placeholder': 'Phone No.'}),
            
        }



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

