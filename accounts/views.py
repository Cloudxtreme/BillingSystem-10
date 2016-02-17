from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.urlresolvers import reverse

from accounts.forms import Registration_Form, Sign_In_Form

# Create your views here.
def sign_in(request):
    if request.method == 'POST':

        form = Sign_In_Form(request.POST or None)
        if form.is_valid():

            user = auth.authenticate(
                email=request.POST.get('email', ""),
                password=request.POST.get('password', ""),
            )


            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    # return redirect('/')
                    return success(request)
            else:
                return render(request, 'accounts/failure.html')
    else:
        form = Sign_In_Form()

    return render(request, 'accounts/sign_in.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = Registration_Form(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse('accounts:sign_in'))
    else:
        form = Registration_Form()

    return render(request, 'accounts/register.html', {'form': form})

def sign_out(request):
    auth.logout(request)
    return redirect(reverse('accounts:sign_in'))

def success(request):
    return render(request, 'accounts/success.html')