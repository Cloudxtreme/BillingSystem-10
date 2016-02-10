from django.forms import ModelForm
from infoGatherer.models import Personal_Information, Guarantor_Information, Insurance_Information
from django import forms  
from infoGatherer.models import PostAd
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


class PostAdForm(forms.ModelForm):  
    error_css_class = 'error'

    #Get entries from databse
    patient_list = Personal_Information.objects.order_by('first_name')
    
    #Health Plan
    health_plan = forms.ChoiceField(choices=HEALTHPLAN, required=True )

    #Patient Info.
    pat_name = forms.ModelChoiceField(queryset=patient_list, empty_label="(Select Name)" )
    pat_sex = forms.ChoiceField(choices=SEX, required=True )
    pat_relationship=forms.ChoiceField(choices=REL_INSUR, required=True )
    pat_relation_emp = forms.BooleanField(initial=False)
    pat_relation_other_accident =forms.BooleanField(initial=False)
    pat_relation_auto_accident = forms.BooleanField(initial=False)

    #Insured's Info
    insured_sex = forms.ChoiceField(choices=SEX, required=True )
    insured_other_benifit_plan=forms.BooleanField(initial=False)
    
    # Not required fields
    insured_name=forms.CharField(required=True)
    pat_other_insured_name=forms.CharField(required=False)
    pat_other_insured_policy=forms.CharField(required=False)
    pat_reservednucc1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '8'}))
    pat_reservednucc2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '9 (b)'}))
    pat_reservednucc3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '9 (c)'}))
    pat_insuranceplanname = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '9 (c)'}))
    other_cliam_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '11 (b)'}))
    
    class Meta:
        model = PostAd
        fields = '__all__'


        widgets = {
            'birth_date': forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'}),
            'insured_idnumber': forms.TextInput(attrs={'placeholder': ''}),
            'insured_streetaddress': forms.TextInput(attrs={'placeholder': 'No,. Street'}),
            'insured_city': forms.TextInput(attrs={'placeholder': 'City'}),
            'insured_state': forms.TextInput(attrs={'placeholder': 'State'}),
            'insured_zip': forms.TextInput(attrs={'placeholder': 'Zip'}),
            'insured_telephone': forms.TextInput(attrs={'placeholder': 'Phone No.'}),
            'insured_other_insured_policy': forms.TextInput(attrs={'placeholder': ''}),
            'insured_birth_date': forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'}),
            'insured_plan_name_program': forms.TextInput(attrs={'placeholder': '11 (c)'}),
            'claim_codes': forms.TextInput(attrs={'placeholder': '10 (d)'}),
            'pat_streetaddress': forms.TextInput(attrs={'placeholder': 'No,. Street'}),
            'pat_city': forms.TextInput(attrs={'placeholder': 'City'}),
            'pat_state': forms.TextInput(attrs={'placeholder': 'State'}),
            'pat_zip': forms.TextInput(attrs={'placeholder': 'Zip'}),
            'pat_telephone': forms.TextInput(attrs={'placeholder': 'Phone No.'}),
            'pat_auto_accident_state': forms.TextInput(attrs={'placeholder': 'State'}),
            'email': forms.TextInput(attrs={'placeholder': 'john@example.com'}),
            'gist': forms.TextInput(attrs={'placeholder': 'In a few words, I\'m looking for/to...'}),
            'expire': forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'}),
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

