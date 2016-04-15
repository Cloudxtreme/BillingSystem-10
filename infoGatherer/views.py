import re
import os
import datetime
import subprocess
import json

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.views import login, logout, password_reset, password_reset_confirm, password_reset_done, password_reset_complete
from django.contrib.auth import authenticate
from django.core import serializers
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
    Payer, ReferringProvider, Provider, PROVIDER_ROLE_CHOICES, CPT,dx)
from accounting.models import *
from deepdiff import DeepDiff
from pprint import pprint
from accounts.models import *
from django.core.files.storage import FileSystemStorage
from displayContent.forms import DocumentForm
from django.core.files import File
from django.db.models import Q
import datetime

from base.models import ExtPythonSerializer


def TrackCharges(request):
    return render(request, 'track_charges.html')


@login_required
def view_audit_log(request):
    # History list
    history_list=["+","-"]

    # Get list of users
    users=User.objects.values_list('id', 'email')
    users=dict(users)

    # Referring provider audit
    rf1=[]
    rf2=[]
    rf3=[]
    rf_mod={}
    idList=ReferringProvider.history.values_list('id', flat=True)
    idList=set(idList)
    idList=list(idList)
    for idd in idList:
        content=ReferringProvider.history.filter(id=idd).filter(history_type="~").order_by('history_date').values()
        if(len(content)>1):
            for i in range(1,len(content)):
                temp={}
                # Put all useful information in temp
                temp["first_name"]=content[i]["first_name"]
                temp["last_name"]=content[i]["last_name"]
                helperAuditLog(content[i-1],content[i],temp,rf1,users,2,False)

        contentCreated=ReferringProvider.history.filter(id=idd).filter(history_type="+").values()
        if(len(contentCreated)>0 and len(content)>0):
            contentModified=content[0]
            temp={}
             # Put all useful information in temp]
            temp["first_name"]=contentModified["first_name"]
            temp["last_name"]=contentModified["last_name"]
            helperAuditLog(contentCreated[0],contentModified,temp,rf1,users,3,False)

    rf_mod["modified"]=rf1
    for symbol in history_list:
        hisNums=ReferringProvider.history.filter(history_type=symbol).values()
        if(symbol == "+"):
            for history in hisNums:
                temp={}
                temp["first_name"]=history["first_name"]
                temp["last_name"]=history["last_name"]
                helperAuditLog(None,history,temp,rf2,users,2,True)
            rf_mod["created"]=rf2
        elif(symbol=="-"):
            for history in hisNums:
                temp={}
                temp["first_name"]=history["first_name"]
                temp["last_name"]=history["last_name"]
                helperAuditLog(None,history,temp,rf3,users,2,True)
            rf_mod["deleted"]=rf3


    # DX audit
    dx1=[]
    dx2=[]
    dx3=[]
    dx_mod={}
    idList=dx.history.values_list('ICD_10', flat=True)
    idList=set(idList)
    idList=list(idList)
    for idd in idList:
        content=dx.history.filter(ICD_10=idd).filter(history_type="~").order_by('history_date').values()
        if(len(content)>1):
            for i in range(1,len(content)):
                temp={}
                # Put all useful information in temp
                temp["ICD_10"]=content[i]["ICD_10"]
                helperAuditLog(content[i-1],content[i],temp,dx1,users,2,False)

        contentCreated=dx.history.filter(ICD_10=idd).filter(history_type="+").values()
        if(len(contentCreated)>0 and len(content)>0):
            contentModified=content[0]
            temp={}
             # Put all useful information in temp]
            temp["ICD_10"]=contentModified["ICD_10"]
            helperAuditLog(contentCreated[0],contentModified,temp,dx1,users,3,False)

    dx_mod["modified"]=dx1
    for symbol in history_list:
        hisNums=dx.history.filter(history_type=symbol).values()
        if(symbol == "+"):
            for history in hisNums:
                temp={}
                temp["ICD_10"]=history["ICD_10"]
                helperAuditLog(None,history,temp,dx2,users,2,True)
            dx_mod["created"]=dx2
        elif (symbol == "-"):
            for history in hisNums:
                temp={}
                temp["ICD_10"]=history["ICD_10"]
                helperAuditLog(None,history,temp,dx3,users,2,True)
            dx_mod["deleted"]=dx3


    # CPT audit
    cpt1=[]
    cpt2=[]
    cpt3=[]
    cpt_mod={}
    idList=CPT.history.values_list('id', flat=True)
    idList=set(idList)
    idList=list(idList)
    for idd in idList:
        content=CPT.history.filter(id=idd).filter(history_type="~").order_by('history_date').values()
        if(len(content)>1):
            for i in range(1,len(content)):
                temp={}
                # Put all useful information in temp
                temp["cpt_code"]=content[i]["cpt_code"]
                temp["cpt_description"]=content[i]["cpt_description"]
                helperAuditLog(content[i-1],content[i],temp,cpt1,users,2,False)

        contentCreated=CPT.history.filter(id=idd).filter(history_type="+").values()
        if(len(contentCreated)>0 and len(content)>0):
            contentModified=content[0]
            temp={}
             # Put all useful information in temp
            temp["cpt_code"]=contentModified["cpt_code"]
            temp["cpt_description"]=contentModified["cpt_description"]
            helperAuditLog(contentCreated[0],contentModified,temp,cpt1,users,3,False)

    cpt_mod["modified"]=cpt1
    for symbol in history_list:
        hisNums=CPT.history.filter(history_type=symbol).values()
        if(symbol=="+"):
            for history in hisNums:
                temp={}
                temp["cpt_code"]=history["cpt_code"]
                temp["cpt_description"]=history["cpt_description"]
                helperAuditLog(None,history,temp,cpt2,users,2,True)
            cpt_mod["created"]=cpt2
        elif(symbol=="-"):
            for history in hisNums:
                temp={}
                temp["cpt_code"]=history["cpt_code"]
                temp["cpt_description"]=history["cpt_description"]
                helperAuditLog(None,history,temp,cpt3,users,2,True)
            cpt_mod["deleted"]=cpt3


    # Provider Audit
    provider1=[]
    provider2=[]
    provider3=[]
    provider_mod={}
    idList=Provider.history.values_list('id', flat=True)
    idList=set(idList)
    idList=list(idList)
    for idd in idList:
        content=Provider.history.filter(id=idd).filter(history_type="~").order_by('history_date').values()
        if(len(content)>1):
            for i in range(1,len(content)):
                temp={}
                # Put all useful information in temp
                temp["provider_name"]=content[i]["provider_name"]
                helperAuditLog(content[i-1],content[i],temp,provider1,users,2,False)

        contentCreated=Provider.history.filter(id=idd).filter(history_type="+").values()
        if(len(contentCreated)>0 and len(content)>0):
            contentModified=content[0]
            temp={}
             # Put all useful information in temp
            temp["provider_name"]=contentModified["provider_name"]
            helperAuditLog(contentCreated[0],contentModified,temp,provider1,users,3,False)

    provider_mod["modified"]=provider1
    for symbol in history_list:
        hisNums=Provider.history.filter(history_type=symbol).values()
        if(symbol == "+"):
            for history in hisNums:
                temp={}
                temp["provider_name"]=history["provider_name"]
                helperAuditLog(None,history,temp,provider2,users,2,True)
            provider_mod["created"]=provider2
        elif(symbol == "-"):
            for history in hisNums:
                temp={}
                temp["provider_name"]=history["provider_name"]
                helperAuditLog(None,history,temp,provider2,users,2,True)
            provider_mod["deleted"]=provider3

    # Insurance Audit
    ins1=[]
    ins2=[]
    ins3=[]
    ins_mod={}
    # Need to get history by code number
    codeNum=Insurance_Information.history.values_list('id', flat=True)
    codeNum=set(codeNum)
    codeNum=list(codeNum)
    for code in codeNum:
        content=Insurance_Information.history.filter(id=code).filter(history_type="~").order_by('history_date').values()
        # print content
        if(len(content)>1):
            for i in range(1,len(content)):
                temp={}
                # Put all useful information in temp
                person=Personal_Information.objects.filter(chart_no=content[i]["patient_id"]).values()[0]
                payer=Payer.objects.filter(code=content[i]["payer_id"]).values()[0]
                temp["patientname"]=person['last_name']+", "+person['first_name']
                temp["payername"]=payer['name']
                helperAuditLog(content[i-1],content[i],temp,ins1,users,2,False,True)

        contentCreated=Insurance_Information.history.filter(id=code).filter(history_type="+").values()
        if(len(contentCreated)>0 and len(content)>0):
            contentModified=content[0]
            temp={}
             # Put all useful information in temp
            person=Personal_Information.objects.filter(chart_no=contentModified["patient_id"]).values()[0]
            payer=Payer.objects.filter(code=contentModified["payer_id"]).values()[0]
            temp["patientname"]=person['last_name']+", "+person['first_name']
            temp["payername"]=payer['name']
            helperAuditLog(contentCreated[0],contentModified,temp,ins1,users,3,False,True)

    ins_mod["modified"]=ins1
    for symbol in history_list:
        hisNums=Insurance_Information.history.filter(history_type=symbol).values()
        if (symbol=="+"):
            for history in hisNums:
                temp={}
                person=Personal_Information.objects.filter(chart_no=history["patient_id"]).values()[0]
                payer=Payer.objects.filter(code=history["payer_id"]).values()[0]
                temp["patientname"]=person['last_name']+", "+person['first_name']
                temp["payername"]=payer['name']
                helperAuditLog(None,history,temp,ins2,users,2,True)
            ins_mod["created"]=ins2
        elif (symbol=="-"):
            for history in hisNums:
                temp={}
                person=Personal_Information.objects.filter(chart_no=history["patient_id"]).values()[0]
                payer=Payer.objects.filter(code=history["payer_id"]).values()[0]
                temp["patientname"]=person['last_name']+", "+person['first_name']
                temp["payername"]=payer['name']
                helperAuditLog(None,history,temp,ins2,users,2,True)
            ins_mod["deleted"]=ins3

    # Payer Audit
    payer1=[]
    payer2=[]
    payer3=[]
    payer_mod={}
    # Need to get history by code number
    codeNum=Payer.history.values_list('code', flat=True)
    codeNum=set(codeNum)
    codeNum=list(codeNum)
    for code in codeNum:
        content=Payer.history.filter(code=code).filter(history_type="~").order_by('history_date').values()
        if(len(content)>1):
            for i in range(1,len(content)):
                temp={}
                # Put all useful information in temp
                temp["name"]=content[i]["name"]
                helperAuditLog(content[i-1],content[i],temp,payer1,users,2,False)

        contentCreated=Payer.history.filter(code=code).filter(history_type="+").values()
        if(len(contentCreated)>0 and len(content)>0):
            contentModified=content[0]
            temp={}
             # Put all useful information in temp
            temp["name"]=contentModified["name"]
            helperAuditLog(contentCreated[0],contentModified,temp,payer1,users,3,False)

    payer_mod["modified"]=payer1
    for symbol in history_list:
        hisNums=Payer.history.filter(history_type=symbol).values()
        if (symbol=="+"):
            for history in hisNums:
                temp={}
                temp["name"]=history["name"]
                helperAuditLog(None,history,temp,payer2,users,2,True)
            payer_mod["created"]=payer2
        elif (symbol=="-"):
            for history in hisNums:
                temp={}
                temp["name"]=history["name"]
                helperAuditLog(None,history,temp,payer3,users,2,True)
            payer_mod["deleted"]=payer3

    # free variables
    content = None

    # Patient Audit
    pat1=[]
    pat2=[]
    pat3=[]
    pat_mod={}
    # Audit : Modified
    charNums=Personal_Information.history.values_list('chart_no', flat=True)
    charNums=set(charNums)
    charNums=list(charNums)
    for chart_no in charNums:
        content=Personal_Information.history.filter(chart_no=chart_no).filter(history_type="~").order_by('history_date').values()
        if(len(content)>1):
            for i in range(1,len(content)):
                temp={}
                # Put all useful information in temp
                temp["first_name"]=content[i]["first_name"]
                temp["last_name"]=content[i]["last_name"]
                helperAuditLog(content[i-1],content[i],temp,pat1,users,2,False)


        contentCreated=Personal_Information.history.filter(chart_no=chart_no).filter(history_type="+").values()
        if(len(contentCreated)>0 and len(content)>0):
            contentModified=content[0]
            temp={}
             # Put all useful information in temp
            temp["first_name"]=contentModified["first_name"]
            temp["last_name"]=contentModified["last_name"]
            helperAuditLog(contentCreated[0],contentModified,temp,pat1,users,3,False)

    pat_mod["modified"]=pat1
    for symbol in history_list:
        hisNums=Personal_Information.history.filter(history_type=symbol).values()
        if (symbol=="+"):
            for history in hisNums:
                temp={}
                temp["first_name"]=history["first_name"]
                temp["last_name"]=history["last_name"]
                helperAuditLog(None,history,temp,pat2,users,2,True)
            pat_mod["created"]=pat2
        elif (symbol=="-"):
            for history in hisNums:
                temp={}
                temp["first_name"]=history["first_name"]
                temp["last_name"]=history["last_name"]
                helperAuditLog(None,history,temp,pat3,users,2,True)
            pat_mod["deleted"]=pat3

    return render(request, 'auditlog.html',{
        'pat_mod':pat_mod,
        'payer_mod' : payer_mod,
        'insurance_mod' : ins_mod,
        'provider_mod' : provider_mod,
        'cpt_mod' : cpt_mod,
        'dx_mod' : dx_mod,
        'rp_mod' :rf_mod,
        'display' : 'payer' if 'payer' in request.GET else 'insurance' if 'insurance' in request.GET else 'provider' if 'provider' in request.GET else 'cpt' if 'cpt' in request.GET else 'dx' if 'dx' in request.GET else 'rp' if 'rp' in request.GET else 'patient' ,
        'display_rows_m': request.GET['num_m'] if 'num_m' in request.GET and request.GET['num_m'] else '10' ,
        'typemcd' : request.GET['typemcd'] if 'typemcd' in request.GET else 'mod' ,
        'search' : request.GET['search'] if 'search' in request.GET and request.GET['search'] else ""
    })


def helperAuditLog(content1,content2,temp,dic,users,changingKeys,createdelete, *optional):
    temp["history_type"]=content2["history_type"]
    temp["history_date"]=content2["history_date"]
    temp["history_id"]=content2["history_id"]
    if(content2["history_user_id"] is not None):
        temp["history_user_id"]=users[content2["history_user_id"]]
    else:
        temp["history_user_id"]="None"

    if createdelete==False:
        diff=DeepDiff(content1,content2)['values_changed']
        if(changingKeys==2):
            alwaysChangingKeys=["root['history_id']", "root['history_date']"]
        else:
            alwaysChangingKeys=["root['history_id']", "root['history_date']", "root['history_type']"]

        if (len(optional)>0):
            for k, v in diff.iteritems():
                if (k not in alwaysChangingKeys):
                    # Put change in temp
                    temp["change"]=k[k.find("['")+1:k.find("']")][1:]
                    if(temp["change"]=="patient_id"):
                        person0=Personal_Information.objects.filter(chart_no=v["oldvalue"]).values()[0]
                        person1=Personal_Information.objects.filter(chart_no=v["newvalue"]).values()[0]
                        temp["oldvalue"]=person0['last_name']+", "+person0['first_name']
                        temp["newvalue"]=person1['last_name']+", "+person1['first_name']
                    elif(temp["change"]=="payer_id"):
                        temp["oldvalue"]=Payer.objects.filter(code=v["oldvalue"]).values()[0]['name']
                        temp["newvalue"]=Payer.objects.filter(code=v["newvalue"]).values()[0]['name']
                    else:
                        temp["oldvalue"]=v["oldvalue"]
                        temp["newvalue"]=v["newvalue"]
                    dic.append(temp)
        else:
            for k, v in diff.iteritems():
                if (k not in alwaysChangingKeys):
                    # Put change in temp
                    temp["change"]=k[k.find("['")+1:k.find("']")][1:]
                    temp["oldvalue"]=v["oldvalue"]
                    temp["newvalue"]=v["newvalue"]
                    dic.append(temp)
    elif createdelete==True:
        temp["change"]=""
        temp["oldvalue"]=""
        temp["newvalue"]=""
        dic.append(temp)

@login_required
def PostAdPage(request):
    loop_times= xrange(12)
    dx_pt_range = [chr(i + ord('A')) for i in range(0,12)]

    form=PostAdForm(loop_times, request.POST or None)

    if 'pat_name' in request.POST and request.POST['pat_name']:
        if form.is_valid() :
            payer = Payer.objects.get(pk=request.POST['payer_id'])
            patient = Personal_Information.objects.get(pk=request.POST['pat_id'])
            insured = Personal_Information.objects.get(pk=request.POST['insured_id'])

            if(request.POST['other_insured_id']):
                other_insured = Personal_Information.objects.get(pk=request.POST['other_insured_id'])
            else:
                other_insured = None

            referring_provider = ReferringProvider.objects.get(pk=request.POST['referring_provider_id'])
            rendering_provider = Provider.objects.get(pk=request.POST['rendering_provider_id'])
            location_provider = Provider.objects.get(pk=request.POST['location_provider_id'])
            billing_provider = Provider.objects.get(pk=request.POST['billing_provider_id'])

            claim = Claim.objects.create(
                payer=payer,
                patient=patient,
                patient_dob=patient.dob,
                insured=insured,
                insured_dob=insured.dob,
                other_insured=other_insured,
                referring_provider=referring_provider,
                referring_provider_npi=referring_provider.NPI,
                rendering_provider=rendering_provider,
                rendering_provider_npi=rendering_provider.npi,
                location_provider=location_provider,
                location_provider_npi=location_provider.npi,
                billing_provider=billing_provider,
                billing_provider_npi=billing_provider.npi,
                user=request.user,
            );

            for i in xrange(1, form.rows+1):
                if(form.cleaned_data.get('cpt_code_%s' % i)):
                    cpt_code = form.cleaned_data.get('cpt_code_%s' % i)
                    cpt = CPT.objects.get(cpt_code=cpt_code)
                    amount = form.cleaned_data.get('total_%s' % i)
                    date_of_service = form.cleaned_data.get('service_start_date_%s' % i)
                    if(cpt and amount):
                        procedure = Procedure.objects.create(
                            claim=claim,
                            rendering_provider=rendering_provider,
                            cpt=cpt,
                            date_of_service=date_of_service,
                        )

                        charge = Charge.objects.create(
                                procedure=procedure,
                                payer_type='Insurance',
                                amount=amount,
                                created=claim.created)

            var = print_form(request.POST);

            # copy the saved file into media directory
            save_file_to_media(claim.pk)
            return var
        else:
           print form.errors

    return render(request, 'post_ad.html', {
        'dx_pt_range': dx_pt_range,
        'loop_times' : loop_times,
        'form': form,
    })

def save_file_to_media(claim_id):
    claim = Claim.objects.get(pk=claim_id)
    fileStorage = FileSystemStorage()
    fileStorage.file_permissions_mode = 0744
    f = open('output.pdf', 'rb+')
    myfile = File(f)
    name=fileStorage.get_available_name(str(claim_id)+".pdf")
    fileStorage.save(name, myfile)
    today = datetime.datetime.now()
    today_path = today.strftime("%Y/%m/%d")
    newdoc = Document.objects.create(claim=claim, docfile='media/documents/'+today_path+"/"+name)

def get_make_claim_extra_context(request):
    p = Personal_Information.objects.all()
    se = ExtPythonSerializer().serialize(
            p,
            props=['format_name',])

    return JsonResponse(data=se, safe=False)

def get_json_personal_info(request):
    p = Personal_Information.objects.filter(pk=request.POST.get('personal_chart_no'))
    se = ExtPythonSerializer().serialize(
            p,
            props=['format_name',],
            use_natural_foreign_keys=True)

    return JsonResponse(data=se, safe=False)

def get_json_personal_and_insurance_info(request):
    p = Personal_Information.objects.filter(pk=request.POST.get('personal_chart_no'))
    se = ExtPythonSerializer().serialize(
            p,
            props=['format_name',],
            use_natural_foreign_keys=True)

    personal_set = Personal_Information.objects.filter(pk=request.POST['personal_chart_no'])
    insurance_set = personal_set[0].insurance_information_set.all().select_related("payer")
    i_set_dict = insurance_set.values()
    i_set = [i for i in i_set_dict]

    for i in range(len(i_set)):
        i_set[i]["payer"] = model_to_dict(insurance_set[i].payer)

    context = {
        "personal_information": se,
        "insurance_list": i_set,
    }

    return JsonResponse(data=context, safe=False)

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
    bar2={}
    for k, v in bar.items():
        bar2[k]=v.upper();

    bar=bar2;
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
    if(bar['pat_relationship_insured']=='SELF'):
        fields.append(('24',True))
    elif(bar['pat_relationship_insured']=='SPOUSE'):
        fields.append(('25',True))
    elif(bar['pat_relationship_insured']=='CHILD'):
        fields.append(('26',True))
    else:
        fields.append(('27',True))

    if('insured_other_benifit_plan' in bar):
        if(bar['insured_other_benifit_plan']=='ON'):
            fields.append(('64',True))
    else:
        fields.append(('65',True))

    if('pat_relation_emp' in bar):
        if(bar['pat_relation_emp']=='ON'):
            fields.append(('49',True))
    else:
        fields.append(('50',True))
    if('pat_relation_auto_accident' in bar):
        if(bar['pat_relation_auto_accident']=='ON'):
            fields.append(('51',True))
    else:
        fields.append(('52',True))
    if('pat_relation_other_accident' in bar):
        if(bar['pat_relation_other_accident']=='ON'):
            fields.append(('54',True))
    else:
        fields.append(('55',True))
    fields.append(('251',bar['pat_id']))

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
    fields.append(('269',n.upper()))
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
    fields.append(('262',n.upper()))

    # Rendering Provider
    rendering_p=Provider.objects.filter(provider_name=bar['rendering_provider_name']).values()[0]
    rp=rendering_p['provider_name'].split()
    if(len(rp)>1):
        fields.append(('260',rp[1].upper()+", "+rp[0].upper()))
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
    if(bar['health_plan']=='Medicare'.upper()):
        fields.append(('3',True))
    elif(bar['health_plan']=='Medicaid'.upper()):
        fields.append(('4',True))
    elif(bar['health_plan']=='Tricare'.upper()):
        fields.append(('5',True))
    elif(bar['health_plan']=='Champva'.upper()):
        fields.append(('6',True))
    elif(bar['health_plan']=='GroupHealthPlan'.upper()):
        fields.append(('7',True))
    elif(bar['health_plan']=='FECA_Blk_Lung'.upper()):
        fields.append(('8',True))
    elif(bar['health_plan']=='Other'.upper()):
        fields.append(('9',True))
    fields.append(('66','Signature on file'.upper()))
    fields.append(('68','Signature on file'.upper()))
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
            fields.append((str(116+(23*i-23)),year[2:]))

            fields.append((str(117+(23*i-23)),month))
            fields.append((str(118+(23*i-23)),day))
            fields.append((str(119+(23*i-23)),year[2:]))

        # EMG
        da=bar['emg_'+str(i)]
        fields.append((str(121+(23*i-23)),da))

        # CPT code and charge
        code=bar['cpt_code_'+str(i)]
        fields.append((str(122+(23*i-23)),code))
        if(len(code)>0):
            charge[i-1]=Decimal(bar['total_'+str(i)])
            fields.append((str(128+(23*i-23)),str(charge[i-1]).split(".")[0]))

            # Place of service
            da=bar['place_of_service_'+str(i)]
            fields.append((str(120+(23*i-23)),da))

            try:
                fields.append((str(129+(23*i-23)),str(charge[i-1]).split(".")[1]))
            except IndexError:
                fields.append((str(129+(23*i-23)),"00"))

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
    fields.append(('254',str(sum(charge)).split(".")[0]))
    try:
        fields.append(('255',str(sum(charge)).split(".")[1]))
    except IndexError:
        fields.append(('255',"00"))
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

@login_required
def api_read_dx(request):
    dxs = dx.objects.all()
    q = request.GET.get('q')

    if q:
        dxs = dxs.filter(Q(pk__icontains=q) | Q(description__icontains=q))

    dxs = dxs[:100]
    s = serializers.serialize('python', dxs)
    return JsonResponse(data=s, safe=False)
