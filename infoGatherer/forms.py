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

class PostAdForm(forms.ModelForm):  
    error_css_class = 'error'

    patient_list = Personal_Information.objects.order_by('first_name')
    category = forms.ModelChoiceField(queryset=patient_list, empty_label="(Select Name)" )

    class Meta:
        model = PostAd
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'What\'s your name?'}),
            'email': forms.TextInput(attrs={'placeholder': 'john@example.com'}),
            'gist': forms.TextInput(attrs={'placeholder': 'In a few words, I\'m looking for/to...'}),
            'expire': forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'})
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

