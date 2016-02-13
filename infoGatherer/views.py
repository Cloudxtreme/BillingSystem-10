from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.views import login, logout, password_reset,\
    password_reset_confirm, password_reset_done, password_reset_complete
from django.contrib.auth import authenticate
from django.template.context import RequestContext
from infoGatherer.models import PostAd, Guarantor_Information, Insurance_Information, Personal_Information, Payer
from django.contrib.auth.decorators import login_required
from infoGatherer.forms import PostAdForm, PatientForm, GuarantorForm, InsuranceForm
import re
from django.shortcuts import redirect
from django.forms import formset_factory
from fdfgen import forge_fdf
import os
import datetime
import subprocess
from django.views.generic import FormView
from django.template.loader import get_template
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers

# New Stuff

def PostAdPage(request):

    form=PostAdForm()
    if request.method == 'POST':
        var=print_form(True);
        return var
    return render(request, 'post_ad.html', {'form': form})

        
def get_make_claim_extra_context(request):
    p_set = Personal_Information.objects.values('chart_no', 'first_name', 'last_name').order_by('first_name')
    extra_context = {
        'patient_list': list(p_set),
    }

    return JsonResponse(data=json.dumps(extra_context), safe=False);

def get_json_personal_information(request):
    personal_set = Personal_Information.objects.filter(pk=request.POST['personal_chart_no'])

    insurance_set = personal_set[0].insurance_information_set.all()

    payer_code_list = [i.payer.code for i in insurance_set]
    payer_set = Payer.objects.filter(code__in=payer_code_list)

    content = {
        "personal_information": list(personal_set.values()),
        "payer_list": list(payer_set.values()),
    }

    return JsonResponse(data=json.dumps(content, cls=DjangoJSONEncoder), safe=False);

def view_in_between(request):
    return render(request, 'test.html')


def search_form(request):
    #return HttpResponse("Welcome")
    #now = datetime.datetime.now()
    return render(request, 'test.html')

def print_form(bar):
    fields = [('2','1168 W 35th St'), ('10','2138809466'), ('11','Ekasit Ja')]
    fdf = forge_fdf("",fields,[],[],[])
    fdf_file = open("data.fdf","w")
    fdf_file.write(fdf)
    fdf_file.close()
    #process = subprocess.Popen(['pdftk', 'CMS1500.pdf', 'fill_form','data.fdf','output','output.pdf'])
    #r = subprocess.call("pdftk CMS1500.pdf fill_form data.fdf output output.pdf",Shell=True)
    os.system('pdftk CMS1500.pdf fill_form data.fdf output output.pdf')
    with open('output.pdf', 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
        return response
    pdf.closed
    os.remove('data.fdf')
    return True
    
    
    

#Old Stuff
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

# def user_password_reset(request):
#     print 'pwd reset'
#     return password_reset(request, is_admin_site=False, template_name='password_reset_form.html',
#                           email_template_name='password_reset_email.html',post_reset_redirect='/info/user/password/reset/done/',)
#
# def user_password_reset_done(request):
#     print 'pwd reset done'
#     return password_reset_done(request,template_name='password_reset_done.html',)
#
# def user_password_reset_confirm(request,*args,**kwargs):
#     print 'pwd reset confirm'
#     return password_reset_confirm(request,template_name='password_reset_confirm.html',post_reset_redirect='/info/user/password/done/',)
#
# def user_password_reset_complete(request):
#     print 'pwd reset complete'
#     return password_reset_complete(request,template_name='password_reset_complete.html',)

@login_required(login_url='/info/login/')
def get_patient_info(request, who=''):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        request_type = request.POST['submit']
        # create a form instance and populate it with data from the request:
        form = PatientForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            if request_type != "Update":
                form.save()
                patient = Personal_Information.objects.all().order_by('-pk')[0]
                url = '/info/insurance/'+str(patient.pk)
                return redirect(url)
    # if a GET (or any other method) we'll create a blank form
    else:
        context = dict()
        if who == 'all':
            context['all_patients'] = Personal_Information.objects.all()
            return render(request, 'all_patients.html', context)

        elif re.match(r'\d+', who):
            if Personal_Information.objects.get(pk=who):
                patient = Personal_Information.objects.filter(pk=who).values()[0]
                guarantor = Guarantor_Information.objects.filter(patient=who).values()
                insurance = Insurance_Information.objects.filter(patient=who).values()

                #context['patient'] = patient#.get_data() #converting to dictionary - order is lost
                #context['guarantor'] = guarantor
                #context['insurance'] = insurance


                p_form = PatientForm(initial = patient)
                #g_form = GuarantorForm(initial = guarantor)

#                 InsuranceFormSet = formset_factory(InsuranceForm)
#                 i_formSet = InsuranceFormSet()
#                 for each in i_formSet:
#                     print (each.as_table())

                i_form = []

                for each in insurance:
                    payer_id = each['payer_id']
                    payer_name = Payer.objects.filter(pk=payer_id).values()[0]['name']
                    i_form.append(InsuranceForm(initial = each))

                return render(request, 'patient.html', {'p_form':p_form, 'i_form':i_form})
        else:
            form = PatientForm()

    return render(request, 'patient.html', {'form': form})

@login_required(login_url='/info/login/')
def get_insurance_info(request, id=''):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = InsuranceForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            form.save()
            patient = Personal_Information.objects.get(pk=id)
            url = '/info/guarantor/'+str(patient.pk)
            return redirect(url)
            #return HttpResponse('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        patient = Personal_Information.objects.get(pk=id)
        form = InsuranceForm(initial={'patient': patient})

    return render(request, 'insurance.html', {'form': form})

@login_required(login_url='/info/login/')
def get_guarantor_info(request, id=''):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = GuarantorForm(request.POST)

#         if form['relation'].value() == "Self":
#             print "relation is self"
#             #print(form)
#             patient = Personal_Information.objects.get(pk=id)
#             print(form['first_name'].value())
#             form['first_name'].value = patient.first_name
#             form['first_name'].set
#             print(form['first_name'].value())
#             form['middle_name'].value = patient.middle_name
#             form['last_name'].value = patient.last_name
#             form['dob'].value = patient.dob
#             form['sex'].value = patient.sex
#             #form['country'].value = patient.country
#             form['ssn'].value = patient.ssn
#             form['address'].value = patient.address
#             form['city'].value = patient.city
#             form['state'].value = patient.state
#             form['zip'].value = patient.zip
#             form['home_phone'].value = patient.home_phone
#                 #print(form)
#             form.save()

#         else:
            # check whether it's valid:
#         if form.is_valid():
#             print "valid"
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
        form.save()
        url = '/info/login/'
        return redirect(url)

    # if a GET (or any other method) we'll create a blank form
    else:
        patient = Personal_Information.objects.get(pk=id)
        form = GuarantorForm(initial={'patient': patient})

    return render(request, 'guarantor.html', {'form': form})