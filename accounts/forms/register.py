from django import forms
from accounts.models import User
from django.utils.translation import ugettext_lazy as _

class Registration_Form(forms.ModelForm):
    """
    Form for registering a new account
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}),
        label='Email Address'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password Confirmation'}),
        label='Password Confirmation'
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match na ja')

        return password2

    def save(self, commit=True):
        user = super(Registration_Form, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()

        return user