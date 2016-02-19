from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from accounts.models import User
from django import forms
from django.contrib.auth import password_validation
from django.utils.translation import ugettext, ugettext_lazy as _


class UserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    def __init__(self, *args, **kargs):
        super(UserCreationForm, self).__init__(*args, **kargs)

    class Meta:
        model = User
        fields = ("email",)


class UserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    def __init__(self, *args, **kargs):
        super(UserChangeForm, self).__init__(*args, **kargs)

    class Meta:
        model = User
        fields = ('email',)


class Password_Reset_Form(PasswordResetForm):
    """
    Password reset form
    """
    email = forms.EmailField(
        widget = forms.EmailInput(
            attrs = {
                'placeholder': _('example@xenonhealth.com'),
                'class': 'form-control',
                'required': True,
                'autofocus': True,
            },
        ),
        label = '',
        max_length = 127,
    )


class Registration_Form(forms.ModelForm):
    """
    Form for registering a new account
    """
    email = forms.EmailField(
        widget = forms.EmailInput(
            attrs={
                'placeholder': _('Email Address'),
                'class': 'form-control',
                'required': True,
                'autofocus': True,
            }
        ),
        label = '',
        max_length = 127,
    )
    password1 = forms.CharField(
        widget= forms.PasswordInput(
            attrs = {
                'placeholder': _('Password'),
                'class': 'form-control',
                'required': True,
            },
        ),
        label=_(''),
        help_text=password_validation.password_validators_help_text_html()
    )
    password2 = forms.CharField(
        widget= forms.PasswordInput(
            attrs = {
                'placeholder': _('Password Confirmation'),
                'class': 'form-control',
                'required': True,
            },
        ),
        label=_(''),
        help_text=password_validation.password_validators_help_text_html()
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match')

        return password2

    def save(self, commit=True):
        user = super(Registration_Form, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()

        return user


class Set_Password_Form(SetPasswordForm):
    """
    Set password form for reset request
    """
    new_password1 = forms.CharField(
        widget= forms.PasswordInput(
            attrs = {
                'placeholder': _('Password'),
                'class': 'form-control',
                'required': True,
                'autofocus': True,
            },
        ),
        label=_(''),
        help_text=password_validation.password_validators_help_text_html()
    )
    new_password2 = forms.CharField(
        widget= forms.PasswordInput(
            attrs = {
                'placeholder': _('Password Confirmation'),
                'class': 'form-control',
                'required': True,
            },
        ),
        label=_(''),
        help_text=password_validation.password_validators_help_text_html()
    )


class Sign_In_Form(forms.Form):
    """
    Sign In form
    """
    email = forms.EmailField(
        widget = forms.EmailInput(
            attrs = {
                'placeholder': _('Email Address'),
                'class': 'form-control',
                'required': True,
                'autofocus': True,
            },
        ),
        label = '',
        max_length = 127,
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