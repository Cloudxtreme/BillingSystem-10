import re
import os
import datetime
import subprocess
import json

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.views import login, logout, password_reset, password_reset_confirm, password_reset_done, password_reset_complete
from django.contrib.auth import authenticate
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.forms import formset_factory
from django.views.generic import FormView
from django.template.loader import get_template
from django.forms.models import model_to_dict
from fdfgen import forge_fdf
from infoGatherer.forms import (
    PostAdForm, PatientForm, GuarantorForm, InsuranceForm,
    ReferringProviderForm, dxForm, OtherProviderForm, CptForms)
from infoGatherer.models import (
    PostAd, Guarantor_Information, Insurance_Information, Personal_Information,
    Payer, ReferringProvider, Provider, PROVIDER_ROLE_CHOICES, CPT)
from deepdiff import DeepDiff
from pprint import pprint
from accounts.models import *

def TrackCharges(request):
    return render(request, 'track_charges.html')

def view_audit_log(request):

    # Get list of users
    users=User.objects.values_list('id', 'email')
    users=dict(users)
    # send list of dictionaries
    list_dic=[]

    # Get history by chart_num (id for patients)
    charNums=Personal_Information.history.filter(history_type="~").values_list('chart_no', flat=True)
    charNums=set(charNums)
    charNums=list(charNums)
    for chart_no in charNums:
        content=Personal_Information.history.filter(chart_no=chart_no).filter(history_type="~").order_by('history_type','history_date').values()
        if(len(content)>1):
            for i in range(1,len(content)):
                # counter=0
                d1=content[i-1]
                d2=content[i]
                diff=DeepDiff(d1,d2)['values_changed']
                alwaysChangingKeys=["root['history_id']", "root['history_date']"]
                # print diff
                for k, v in diff.iteritems():
                    if (k not in alwaysChangingKeys):
                        temp={}
                        # Put all useful information in temp
                        temp["first_name"]=content[i]["first_name"]
                        temp["last_name"]=content[i]["last_name"]
                        temp["history_type"]=content[i]["history_type"]
                        temp["history_user_id"]=users[content[i]["history_user_id"]]
                        temp["history_date"]=content[i]["history_date"]
                        temp["history_id"]=content[i]["history_id"]
                        # Put change in temp
                        temp["change"]=k[k.find("['")+1:k.find("']")][1:]
                        temp["oldvalue"]=v["oldvalue"]
                        temp["newvalue"]=v["newvalue"]
                        list_dic.append(temp)

    print list_dic
    return render(request, 'auditlog.html',{'info': list_dic})

def getDiff():

    return True

@login_required
def PostAdPage(request):
    loop_times= xrange(12)
    dx_pt_range = [chr(i + ord('A')) for i in range(0,12)]

    form=PostAdForm(loop_times, request.GET or None)

    if 'pat_name' in request.GET and request.GET['pat_name']:
        if form.is_valid() :
            var = print_form(request.GET);
            return var
        else:
           print form.errors

    return render(request, 'post_ad.html', {
        'dx_pt_range': dx_pt_range,
        'loop_times' : loop_times,
        'form': form,
    })

def get_make_claim_extra_context(request):
    p_set = Personal_Information.objects.values('chart_no', 'first_name', 'last_name', 'address', 'city').order_by('first_name')
    context = {'patients': list(p_set),}
    return JsonResponse(data=context);

def get_json_personal_info(request):
    personal_q_set = Personal_Information.objects.filter(pk=request.POST['personal_chart_no'])
    context = {"personal_information": list(personal_q_set.values()),}
    return JsonResponse(data=context)

def get_json_personal_and_insurance_info(request):
    personal_set = Personal_Information.objects.filter(pk=request.POST['personal_chart_no'])
    insurance_set = personal_set[0].insurance_information_set.all().select_related("payer")
    i_set_dict = insurance_set.values()
    i_set = [i for i in i_set_dict]

    for i in range(len(i_set)):
        i_set[i]["payer"] = model_to_dict(insurance_set[i].payer)

    context = {
        "personal_information": list(personal_set.values()),
        "insurance_list": i_set,
    }

    return JsonResponse(data=context);

def get_json_physician_info(request):
    phy_q_set = ReferringProvider.objects.all()
    context = {"physicians": list(phy_q_set.values()),}
    return JsonResponse(data=context)

def get_json_provider_info(request):
    context = {}
    for choice in PROVIDER_ROLE_CHOICES:
        key = choice[0]
        value = choice[1]
        provider_q_set = Provider.objects.filter(role=key)
        context[value] = list(provider_q_set.values())
    
    return JsonResponse(data=context)

def get_json_cpt(request):
    cpt_q_set = CPT.objects.all()
    context = {'cpts': list(cpt_q_set.values()),}
    return JsonResponse(data=context)

def view_in_between(request):
    return render(request, 'test.html')


def search_form(request):
    return render(request, 'test.html')

def print_form(bar):

    # Patient Information
    fields = [
        ('11',bar['pat_name']),
        ('18',bar['pat_streetaddress']),
        ('19',bar['pat_city']),
        ('20',bar['pat_state']),
        ('21',bar['pat_zip']),
        ('22',bar['pat_telephone'].split('-')[0]),
        ('23',bar['pat_telephone'].split('-')[1]+"-"+bar['pat_telephone'].split('-')[2])
    ]
    month, day, year = bar['pat_birth_date'].split('/')
    fields.append(('12', month))
    fields.append(('13', day))
    fields.append(('14', year))
    fields.append(('10',bar['insured_idnumber']))
    fields.append(('txt8',bar['pat_reservednucc1']))
    fields.append(('56_1',bar['claim_codes']))
    fields.append(('17_A','DN'))
    if(bar['pat_sex']=='M'):
        fields.append(('15',True))
    else:
        fields.append(('16',True))
    if(bar['pat_relationship_insured']=='Self'):
        fields.append(('24',True))
    elif(bar['pat_relationship_insured']=='Spouse'):
        fields.append(('25',True))
    elif(bar['pat_relationship_insured']=='Child'):
        fields.append(('26',True))
    else:
        fields.append(('27',True))

    if('insured_other_benifit_plan' in bar):
        if(bar['insured_other_benifit_plan']=='on'):
            fields.append(('64',True))
    else:
        fields.append(('65',True))

    if('pat_relation_emp' in bar):
        if(bar['pat_relation_emp']=='on'):
            fields.append(('49',True))
    else:
        fields.append(('50',True))
    if('pat_relation_auto_accident' in bar):
        if(bar['pat_relation_auto_accident']=='on'):
            fields.append(('51',True))
    else:
        fields.append(('52',True))
    if('pat_relation_other_accident' in bar):
        if(bar['pat_relation_other_accident']=='on'):
            fields.append(('54',True))
    else:
        fields.append(('55',True))
    
    # Payer Information
    fields.append(('2',bar['payer_name']+"\n"+bar['payer_address']))

    # Physician Information
    fields.append(('81',bar['referring_name']))
    fields.append(('84',bar['NPI']))
    fields.append(('93',True))
    fields.append(('94','0.00'))
    fields.append(('21_A','0'))
    fields.append(('95',bar['ICD_10_1']))
    fields.append(('96',bar['ICD_10_2']))
    fields.append(('97',bar['ICD_10_3']))
    fields.append(('98',bar['ICD_10_4']))
    fields.append(('99',bar['ICD_10_5']))
    fields.append(('100',bar['ICD_10_6']))
    fields.append(('101',bar['ICD_10_7']))
    fields.append(('102',bar['ICD_10_8']))
    fields.append(('103',bar['ICD_10_9']))
    fields.append(('104',bar['ICD_10_10']))
    fields.append(('105',bar['ICD_10_11']))
    fields.append(('106',bar['ICD_10_12']))

    # Providers
    # Billing provider
    bill_p=Provider.objects.filter(provider_name=bar['billing_provider_name']).values()[0]
    n="";
    fields.append(('272',bill_p['npi']))
    fields.append(('267',bill_p['provider_phone'].split('-')[0]))
    fields.append(('268',bill_p['provider_phone'].split('-')[1]+"-"+bill_p['provider_phone'].split('-')[2]))
    n=n+str(bill_p['provider_name'])
    n=n+" "+str(bill_p['provider_address'])
    n=n+" "+str(bill_p['provider_city'])
    n=n+" "+str(bill_p['provider_state'])
    n=n+" "+str(bill_p['provider_zip'])
    fields.append(('269',n))
    # Billing provider tax id
    fields.append(('248',bill_p['tax_id']))
    # Billing provider ssn and ein
    if(len(bill_p['provider_ssn'])!=0):
        fields.append(('249',True))
    
    if(len(bill_p['provider_ein'])!=0):
        fields.append(('250',True))
    


    # Location provider
    location_p=Provider.objects.filter(provider_name=bar['location_provider_name']).values()[0]
    n="";
    fields.append(('265',location_p['npi']))
    n=n+str(location_p['provider_name'])
    n=n+" "+str(location_p['provider_address'])
    n=n+" "+str(location_p['provider_city'])
    n=n+" "+str(location_p['provider_state'])
    n=n+" "+str(location_p['provider_zip'])
    fields.append(('262',n))

    # Rendering Provider
    rendering_p=Provider.objects.filter(provider_name=bar['rendering_provider_name']).values()[0]
    rp=rendering_p['provider_name'].split()
    if(len(rp)>1):
        fields.append(('260',rp[1]+", "+rp[0]))
    else:
        fields.append(('260',rendering_p['provider_name']))
    now = datetime.datetime.now()
    fields.append(('260A',str(now.month)+"|"+str(now.day)+"|"+str(now.year)))

	# Insured
    fields.append(('53',bar['pat_auto_accident_state']))
    fields.append(('42',bar['pat_reservednucc2']))
    fields.append(('47',bar['pat_reservednucc3']))
    fields.append(('48',bar['other_insured_insur_plan_name']))
    fields.append(('56',bar['claim_codes']))
    fields.append(('40',bar['pat_other_insured_name']))
    fields.append(('41',bar['pat_other_insured_policy']))
    fields.append(('17',bar['insured_name']))
    fields.append(('28',bar['insured_streetaddress']))
    fields.append(('29',bar['insured_city']))
    fields.append(('30',bar['insured_state']))
    fields.append(('31',bar['insured_zip']))
    fields.append(('32',bar['insured_telephone'].split('-')[0]))
    fields.append(('33',bar['insured_telephone'].split('-')[1]+"-"+bar['insured_telephone'].split('-')[2]))
    fields.append(('63',bar['insured_insur_plan_name'].split('-')[0]))

    if(bar['insured_sex']=='M'):
        fields.append(('60',True))
    else:
        fields.append(('61',True))

    month, day, year = bar['insured_birth_date'].split('/')
    fields.append(('57', month))
    fields.append(('58', day))
    fields.append(('59', year))

    fields.append(('56_2',bar['insured_policy']))
    fields.append(('62',bar['other_cliam_id']))

    # Health Plan and signatures
    if(bar['health_plan']=='Medicare'):
        fields.append(('3',True))
    elif(bar['health_plan']=='Medicaid'):
        fields.append(('4',True))
    elif(bar['health_plan']=='Tricare'):
        fields.append(('5',True))
    elif(bar['health_plan']=='Champva'):
        fields.append(('6',True))
    elif(bar['health_plan']=='GroupHealthPlan'):
        fields.append(('7',True))
    elif(bar['health_plan']=='FECA_Blk_Lung'):
        fields.append(('8',True))
    elif(bar['health_plan']=='Other'):
        fields.append(('9',True))
    fields.append(('66','Signature on file'))
    fields.append(('68','Signature on file'))
    now = datetime.datetime.now()
    fields.append(('67',str(now.month)+"|"+str(now.day)+"|"+str(now.year)))

    # Service Information
    npi=Provider.objects.filter(provider_name=bar['rendering_provider_name']).values()[0]
    rendering_p_npi=rendering_p['npi']
    charge=[0,0,0,0,0,0]
    for i in range(1,7):

        # date field
        # print ('service_start_date_'+str(i))
        # print bar['service_start_date_'+str(i)]
        if(len(bar['service_start_date_'+str(i)])!=0):
            da=bar['service_start_date_'+str(i)]
            # print (114+str(23*i-23))

            month, day, year = da.split('/')
            fields.append((str(114+(23*i-23)),month))
            fields.append((str(115+(23*i-23)),day))
            fields.append((str(116+(23*i-23)),year))

            fields.append((str(117+(23*i-23)),month))
            fields.append((str(118+(23*i-23)),day))
            fields.append((str(119+(23*i-23)),year))

        # Place of service
        da=bar['place_of_service_'+str(i)]
        fields.append((str(120+(23*i-23)),da))

        # EMG
        da=bar['emg_'+str(i)]
        fields.append((str(121+(23*i-23)),da))

        # CPT code and charge
        code=bar['cpt_code_'+str(i)]
        fields.append((str(122+(23*i-23)),code))
        if(len(code)>0):
            charge[i-1]=int(bar['total_'+str(i)])
            fields.append((str(128+(23*i-23)),charge[i-1]))

        # Modifiers
        fields.append((str(123+(23*i-23)),bar['mod_a_'+str(i)]))
        fields.append((str(124+(23*i-23)),bar['mod_b_'+str(i)]))
        fields.append((str(125+(23*i-23)),bar['mod_c_'+str(i)]))
        fields.append((str(126+(23*i-23)),bar['mod_d_'+str(i)]))

        # Diagnostic pointer
        diag=(bar['dx_pt_s1_'+str(i)] if bar['dx_pt_s1_'+str(i)]!='---' else '')+(bar['dx_pt_s2_'+str(i)] if bar['dx_pt_s2_'+str(i)]!='---' else '')+(bar['dx_pt_s3_'+str(i)] if bar['dx_pt_s3_'+str(i)]!='---' else '')+(bar['dx_pt_s4_'+str(i)] if bar['dx_pt_s4_'+str(i)]!='---' else '')
        fields.append((str(127+(23*i-23)),diag))

        # Note
        fields.append((str(110+(23*i-23)),bar['note_'+str(i)]))

        #Provider ID
        if(len(code)>0):
            fields.append((str(132+(23*i-23)),rendering_p_npi))

        #units
        if(len(bar['note_'+str(i)])>0):
            txt=bar['note_'+str(i)]
            if(txt.split()[0]=='START'):
                fields.append((str(130+(23*i-23)),txt.split()[7]))
            else:
                fields.append((str(130+(23*i-23)),txt.split()[2][-2:]))


    # Total charge
    fields.append(('254',sum(charge)))
    # Amount paid
    fields.append(('256','0.00'))
    # Accept assignment
    fields.append(('252',True))

    # PDF generation
    fdf = forge_fdf("",fields,[],[],[])
    fdf_file = open("data.fdf","w")
    fdf_file.write(fdf)
    fdf_file.close()
    os.system('pdftk CMS1500.pdf fill_form data.fdf output output.pdf')
    os.remove('data.fdf')
    with open('output.pdf', 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
        return response
    pdf.closed
    
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