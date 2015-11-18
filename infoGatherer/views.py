from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.contrib.auth.views import login, logout, password_reset,\
    password_reset_confirm, password_reset_done, password_reset_complete
from django.contrib.auth import authenticate
from django.template.context import RequestContext
from infoGatherer.models import Guarantor_Information, Insurance_Information, Personal_Information, Payer 
from django.contrib.auth.decorators import login_required

actions = {'I':'Created','U':'Changed','D':'Deleted'}

def index(request):
    return HttpResponse("Welcome")

@login_required(login_url='/info/login/')
def admin_log(request):
    #Each Table's Log
    print '\nPersonal Information'
    for p in Personal_Information.audit_log.all().order_by('-action_date'):
        print 'For Patient: ',p.chart_no, ' ',p .first_name, ' ', p.last_name
   
    print '\nInsurance Information'
    for i in Insurance_Information.audit_log.all().order_by('insurance_id','action_date'):
        print 'Insurance: ',i.insurance_id, i.payer.name
        print 'For Pateint: ',i.patient.chart_no, i.patient.first_name, ' ', i.patient.last_name
        print actions.get(i.action_type), i.action_user, 'on', i.action_date
        print ''
    
    return HttpResponse("Welcome")
    
def user_login(request):
    username = ''
    password = ''
    state = ''
    status_code = ''    
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                status_code = 1
                state = 'You have successfully Logged In'
            else:
                state = 'Your account has been deactivated'
        else:
            state = 'Invalid Login Details'
      
    #return render_to_response('login.html',{'state':state,'status_code':status_code,'username':username},context_instance=RequestContext(request))    
    return login(request, template_name='login.html',extra_context={'state':state,'status_code':status_code})

def user_logout(request, *args, **kwargs):
    user = request.user
    return logout(request, *args, **kwargs)
    #return render_to_response('logout.html',context_instance=RequestContext(request))
    
def user_password_reset(request):
    print 'pwd reset'
    return password_reset(request, is_admin_site=False, template_name='password_reset_form.html', 
                          email_template_name='password_reset_email.html',post_reset_redirect='/info/user/password/reset/done/',)

def user_password_reset_done(request):
    print 'pwd reset done'
    return password_reset_done(request,template_name='password_reset_done.html',)

def user_password_reset_confirm(request,*args,**kwargs):
    print 'pwd reset confirm'
    return password_reset_confirm(request,template_name='password_reset_confirm.html',post_reset_redirect='/info/user/password/done/',)

def user_password_reset_complete(request):
    print 'pwd reset complete'
    return password_reset_complete(request,template_name='password_reset_complete.html',)