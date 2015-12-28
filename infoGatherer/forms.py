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
        
class InsuranceForm(ModelForm):
    class Meta:
        model = Insurance_Information
        fields = '__all__'
        
class ClaimForm(ModelForm):
    pass