from django import forms
from django.utils.translation import ugettext_lazy as _

class Sign_In_Form(forms.Form):
    """
    Sign In form
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}),
        label='Email Address'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label='Password'
    )

    class Meta:
        fields = ['email', 'password']