from django import forms
from django.utils.translation import ugettext_lazy as _

class Sign_In_Form(forms.Form):
    """
    Sign In form
    """
    email = forms.EmailField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        fields = ["email", "password"]
        # widgets = {
        #     "email":  forms.EmailInput,
        #     "password": forms.PasswordInput,
        # }
        # labels = {
        #     "email":  _("Email Address"),
        #     "password": _("Password"),
        # }