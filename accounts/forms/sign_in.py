from django import forms
from django.utils.translation import ugettext_lazy as _

class Sign_In_Form(forms.Form):
    """
    Sign In form
    """
    email = forms.EmailField(
        widget = forms.EmailInput(
            attrs = {
                'placeholder': 'Email Address',
                'class': 'form-control',
                'required': True,
                'autofocus': True,
            }
        ),
        label = ''
    )
    password = forms.CharField(
        widget = forms.PasswordInput(
            attrs = {
                'placeholder': 'Password',
                'class': 'form-control',
                'required': True,
            }
        ),
        label = ''
    )

    class Meta:
        fields = ['email', 'password']