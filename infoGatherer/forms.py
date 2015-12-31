from django.forms import ModelForm
from infoGatherer.models import Personal_Information, Guarantor_Information, Insurance_Information

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