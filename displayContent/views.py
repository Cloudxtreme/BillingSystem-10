from functools import partial, wraps

from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Sum, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone
from fdfgen import forge_fdf
from django.http.response import HttpResponseBadRequest
import re
from datetime import datetime, timedelta
from decimal import *
import os
import subprocess
import json
from .models import *
from accounting.models import *
from accounting.forms import NoteForm
from infoGatherer.models import Personal_Information, Payer, Insurance_Information
from base.models import ExtPythonSerializer
from shutil import copyfile


def generate_statement(request, chart):
    # get all claims

    return HttpResponse("<html>This is sparta!</html>")


def view_dashboard(request):
    return render(request, 'displayContent/dashboard.html')

def view_claims(request, chart):
    """
    Renders the /patient/<no>/claimhistory webpage. Information is used for claim detals and claim searches (go to url).
    """
    patient_info=Personal_Information.objects.filter(pk=chart).values()
    claimSearches=Claim.objects.filter(patient_id=chart).order_by('-created')
    if len(patient_info)>0:
        claimValues=[]
        claimValues=claimSearches.values()[:]

        for claim, claimValue in zip(claimSearches, claimValues):
            claimValue["pk"]=claim.pk
            claimValue["total_charge"]=claim.total_charge
            claimValue["ins_pmnt"]=claim.ins_pmnt_per_claim
            claimValue["ins_adjustment"]=claim.ins_adjustment_per_claim
            claimValue["pat_responsible"]=claim.pat_responsible_per_claim
            claimValue["pat_pmnt"]=claim.pat_pmnt_per_claim
            claimValue["inc_balance"]=Decimal(claim.total_charge)-Decimal(claim.ins_pmnt_per_claim+claim.ins_adjustment_per_claim)
            claimValue["total_balance"]=claimValue["inc_balance"]+(claim.pat_responsible_per_claim-claim.pat_pmnt_per_claim)

        return render(request, 'displayContent/patient/claim.html',{
            'claimSearches' : claimValues,
            'patient_info' : patient_info[0],
            'note_form': NoteForm(request.POST or None),
        })
    else:
        return render(request, 'displayContent/patient/NotExist.html', {
            'info' : "(404) Sorry! This patientID doesn't exisit in the database."
            })

def view_patient(request, chart):
    """Page to view info about patients and goto the claims"""

    patient = get_object_or_404(Personal_Information, pk=chart)
    # Primary insurance and payer
    try:
        primary_insur = Insurance_Information.objects.get(
                patient=chart,
                level='primary')
    except Insurance_Information.DoesNotExist:
        primary_insur = None

    # Secondary insurance and payer
    try:
        secondary_insur = Insurance_Information.objects.get(
                patient=chart,
                level='secondary')
    except Insurance_Information.DoesNotExist:
        secondary_insur = None

    if secondary_insur:
        secondary_payer = secondary_insur.payer
    else:
        secondary_payer = None

    # Tertiary insurance and payer
    try:
        tertiary_insur = Insurance_Information.objects.get(
                patient=chart,
                level='tertiary')
    except Insurance_Information.DoesNotExist:
        tertiary_insur = None

    if tertiary_insur:
        tertiary_payer = tertiary_insur.payer
    else:
        tertiary_payer = None

    today = timezone.now()
    m1_time = today - timedelta(days=30)
    m2_time = today - timedelta(days=60)
    m3_time = today - timedelta(days=90)
    m4_time = today - timedelta(days=120)

    Q1 = Q(created__gte=m1_time)
    Q2 = Q(Q(created__lt=m1_time) & Q(created__gte=m2_time))
    Q3 = Q(Q(created__lt=m2_time) & Q(created__gte=m3_time))
    Q4 = Q(Q(created__lt=m3_time) & Q(created__gte=m4_time))
    Q5 = Q(Q(created__lt=m4_time))

    charges = Charge.objects.filter(procedure__claim__patient=chart)
    ins_charges = charges.filter(payer_type="Insurance")
    pat_charges = charges.filter(payer_type="Patient")

    ins_c_age = [ins_charges.filter(Q1),
            ins_charges.filter(Q2),
            ins_charges.filter(Q3),
            ins_charges.filter(Q4),
            ins_charges.filter(Q5)]

    pat_c_age = [pat_charges.filter(Q1),
            pat_charges.filter(Q2),
            pat_charges.filter(Q3),
            pat_charges.filter(Q4),
            pat_charges.filter(Q5)]

    ins_t_age = [Decimal("0.00") for i in range(5)]
    for i, charges in enumerate(ins_c_age):
        for charge in charges:
            ins_t_age[i] += charge.balance

    pat_t_age = [Decimal("0.00") for i in range(5)]
    for i, charges in enumerate(pat_c_age):
        for charge in charges:
            pat_t_age[i] += charge.balance

    aging = dict(
            i_m1=ins_t_age[0],
            i_m2=ins_t_age[1],
            i_m3=ins_t_age[2],
            i_m4=ins_t_age[3],
            i_m5=ins_t_age[4],
            p_m1=pat_t_age[0],
            p_m2=pat_t_age[1],
            p_m3=pat_t_age[2],
            p_m4=pat_t_age[3],
            p_m5=pat_t_age[4],
            i_t=sum(ins_t_age),
            p_t=sum(pat_t_age),
            m1_t=ins_t_age[0] + pat_t_age[0],
            m2_t=ins_t_age[1] + pat_t_age[1],
            m3_t=ins_t_age[2] + pat_t_age[2],
            m4_t=ins_t_age[3] + pat_t_age[3],
            m5_t=ins_t_age[4] + pat_t_age[4],
            total=sum(ins_t_age) + sum(pat_t_age))

    return render(request, 'displayContent/patient/chart.html', {
            "today": today,
            'patient': patient,
            'primary_insur': primary_insur,
            'secondary_insur': secondary_insur,
            'tertiary_insur':tertiary_insur,
            "aging": aging})

def payment_details(request):
    claim_id = request.GET.get('claim_id')
    claim = get_object_or_404(Claim, pk=claim_id)

    # Group relevant payments
    applies = Apply.objects.filter(charge__procedure__claim=claim)
    p = dict()
    for a in applies:
        p[a.payment] = a.payment
    payments = [v for k,v in p.iteritems()]

    # Group relevant procedures
    charges = Charge.objects.filter(procedure__claim=claim)
    c_proc = dict()
    for c in charges:
        if c_proc.get(c.procedure) is None:
            c_proc[c.procedure] = dict()
            c_proc[c.procedure]['Insurance'] = []
            c_proc[c.procedure]['Patient'] = []

        c_proc[c.procedure][c.payer_type].append(c)


    return render(request, 'displayContent/patient/payment_details.html', {
        'payments': payments,
        'c_proc': c_proc})

def open_pdf(request, yr, mo, da, claim):
    try:
        with open('media/documents/'+yr+"/"+mo+"/"+da+"/"+claim+".pdf", 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename=some_file.pdf'
            return response
        pdf.closed
    except Exception as e:
        return render(request, 'displayContent/patient/NotExist.html', {
            'info' : "(404) Sorry! This claim that you're trying to open doesn't exisit in the file system."
            })


###############################################################################
# API function
###############################################################################
@login_required
def helper_trasnfer_pdf_content(file_path, request):
    count=1
    name=""
    val=""
    fields=[]
    pdf_transfer="pdf_transfer"
    try:
        temp_path = "temp/" + str(request.user.pk)
        data_file_path = os.path.join(temp_path, "data.fdf")
        temp_output_file_path = os.path.join(temp_path, "output_blank.pdf")
        temp_pdf_transfer = os.path.join(temp_path, "pdf_transfer.txt")
        ori_form_file_path = "blank.pdf"
        temp_form_file_path = os.path.join(temp_path, ori_form_file_path)
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)

        copyfile(ori_form_file_path, temp_form_file_path)

        os.system('pdftk '+file_path+' dump_data_fields output '+temp_pdf_transfer)
        with open(temp_pdf_transfer,"rb") as f:
            for line in f:
                if(len(line.split("---"))==1):
                    if(len(line.split("FieldName:"))>1):
                        name=line.split("FieldName:")[1].split("\n")[0]
                    elif (len(line.split("FieldValue:"))>1):
                        val=line.split("FieldValue:")[1].split("\n")[0]
                else:
                    fields.append((name.strip(), val.strip()))
                    name=""
                    val=""
                count=count+1

        # Transfer PDF content
        fdf = forge_fdf("",fields,[],[],[])
        fdf_file = open(data_file_path,"w")
        fdf_file.write(fdf)
        fdf_file.close()

        os.system('pdftk %s fill_form %s output %s' % \
                (temp_form_file_path, data_file_path, temp_output_file_path))

        with open(temp_output_file_path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename=some_file.pdf'
            pdf.closed
            res=response
        os.remove(temp_pdf_transfer)
        os.remove(temp_output_file_path)
        os.remove(data_file_path)
        os.remove(temp_form_file_path)
        return res
    except:
        return HttpResponseBadRequest('[]', content_type='application/json')

@login_required
def api_get_blank_claim(request,yr,mo,da,claim):
    if request.method == 'GET' and 'make' in request.GET :
        url=yr+"/"+mo+"/"+da+"/"+claim+".pdf"
        var = helper_trasnfer_pdf_content("media/documents/"+url, request)
        return var

    return HttpResponseBadRequest('[]', content_type='application/json')


def api_search_patient(request):
    if request.method == 'POST':
        post_data = request.POST

        if post_data.get('options')=="Claim":
            claim = Claim.objects.filter(pk__icontains=post_data.get('claim_id') or '')
            se = ExtPythonSerializer().serialize(
                claim,
                props=['id', 'get_patient_insurance', 'get_patient_ssn', 'get_patient_home_phone',  ],
                use_natural_foreign_keys=True
            )
            return JsonResponse(data=se, safe=False)
        else:
            patient = Personal_Information.objects.filter(
                first_name__icontains=post_data.get('first_name') or '',
                last_name__icontains=post_data.get('last_name') or '',
            )
            if post_data.get('dob'):
                patient = patient.filter(dob=post_data.get('dob'))
            if post_data.get('phone'):
                patient = patient.filter(home_phone__icontains=post_data.get('phone'))
            if post_data.get('ssn'):
                patient = patient.filter(ssn__icontains=post_data.get('ssn'))
            if post_data.get('chart_no'):
                patient = patient.filter(chart_no__icontains=post_data.get('chart_no'))
            se = ExtPythonSerializer().serialize(
                patient,
                props=['chart_no','get_primary_insurane',],
                use_natural_foreign_keys=True
            )
            return JsonResponse(data=se, safe=False)
    else:
        return JsonResponse([], safe=False)

def api_view_claim(request):
    """
    Renders the /patient/<no>/claimhistory webpage. Information is
    used for claim detals and claim searches (go to url).
    """
    claim = get_object_or_404(Claim, pk=request.GET.get('claim_id'))
    notes = claim.note_set.all();
    n = serializers.serialize('python', notes, use_natural_foreign_keys=True)
    c = ExtPythonSerializer().serialize(
            claim,
            props=[
                    'total_charge',
                    'ins_pmnt_per_claim',
                    'ins_adjustment_per_claim',
                    'ins_balance',
                    'pat_responsible_per_claim',
                    'pat_pmnt_per_claim',
                    'total_balance'])
    s = dict(claim=c, notes=n)
    return JsonResponse(data=s, safe=False)
