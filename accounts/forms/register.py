from django import forms
from accounts.models import User
from django.utils.translation import ugettext_lazy as _

class Registration_Form(forms.ModelForm):
    """
    Form for registering a new account
    """
    email = forms.EmailField(widget=forms.TextInput, label="Email Address")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Password Confirmation")

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        return password2
    # def clean(self):
    #     """
    #     Verifies that the values entered into the password fields match

    #     NOTE: Errors here will appear in ``non_field_errors()`` because it applies to more than one field.
    #     """
    #     cleaned_data = super(RegistrationForm, self).clean()
    #     if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
    #         if self.cleaned_data['password1'] != self.cleaned_data['password2']:
    #             raise forms.ValidationError("Passwords don't match. Please enter both fields again.")
    #     return self.cleaned_data

    def save(self, commit=True):
        user = super(Registration_Form, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

        return user