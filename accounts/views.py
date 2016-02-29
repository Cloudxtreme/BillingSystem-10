from django.shortcuts import render, redirect
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_reset as auth_password_reset, password_reset_confirm as auth_password_reset_confirm

from accounts.forms import Registration_Form, Sign_In_Form, Password_Reset_Form, Set_Password_Form


def index(request):
    return redirect(reverse('accounts:sign_in'))

def sign_in(request):
    """
    Render user's sign-in page and authenticate credential
    """
    form = Sign_In_Form(request.POST or None)
    if form.is_valid():
        user = auth.authenticate(
            email = request.POST.get('email'),
            password = request.POST.get('password'),
        )

        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect(request.GET.get('next', reverse('dashboard:dashboard')))
        else:
            return render(request, 'accounts/failure.html')

    return render(request, 'accounts/sign_in.html', {'form': form})

def sign_out(request):
    auth.logout(request)
    return redirect(reverse('accounts:sign_in'))

@login_required
def success(request):
    return render(request, 'accounts/success.html')

def password_reset_confirm(request, uidb64=None, token=None):
    return auth_password_reset_confirm(
        request,
        template_name = 'accounts/password_reset_confirm.html',
        uidb64 = uidb64,
        token = token,
        post_reset_redirect = reverse('accounts:sign_in'),
        set_password_form = Set_Password_Form,
    )

def password_reset(request):
    return auth_password_reset(
        request,
        template_name = 'accounts/password_reset.html',
        email_template_name = 'accounts/password_reset_email.html',
        html_email_template_name = 'accounts/password_reset_email.html',
        subject_template_name = 'accounts/password_reset_email_subject.txt',
        post_reset_redirect = reverse('accounts:sign_in'),
        password_reset_form = Password_Reset_Form,
    )

@login_required
def register(request):
    form = Registration_Form(data=request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.is_staff = True;
        user.is_superuser = True;
        user.save()
        return redirect(reverse('accounts:success'))

    return render(request, 'accounts/register.html', {'form': form})