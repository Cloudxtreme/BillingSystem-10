from functools import partial, wraps

from django.shortcuts import *
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone

import re
from datetime import datetime, timedelta
from decimal import *

from .models import *
from accounting.models import *
from accounting.forms import NoteForm
from infoGatherer.models import Personal_Information, Payer, Insurance_Information
from base.models import ExtPythonSerializer


def view_dashboard(request):
    return render(request, 'displayContent/dashboard.html')

def view_claims(request, chart):
    """
    Renders the /patient/<no>/claimhistory webpage. Information is used for claim detals and claim searches (go to url).
    """
    patient_info=Personal_Information.objects.filter(pk=chart).values()
    claimSearches=Claim.objects.filter(patient_id=chart)
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

    claim = Claim.objects.filter(patient=chart)
    today = timezone.now().date()
    m1_time = today - timedelta(days=30)
    m2_time = today - timedelta(days=60)
    m3_time = today - timedelta(days=90)
    m4_time = today - timedelta(days=120)
    m1_claim = claim.filter(created__gte=m1_time)
    m2_claim = claim.filter(created__lt=m1_time, created__gte=m2_time)
    m3_claim = claim.filter(created__lt=m2_time, created__gte=m3_time)
    m4_claim = claim.filter(created__lt=m3_time, created__gte=m4_time)
    m5_claim = claim.filter(created__lt=m4_time)

    print '\n\n\n',m1_claim,'\n\n\n'
    print '\n\n\n',m2_claim,'\n\n\n'
    print '\n\n\n',m3_claim,'\n\n\n'
    print '\n\n\n',m4_claim,'\n\n\n'
    print '\n\n\n',m5_claim,'\n\n\n'

    return render(request, 'displayContent/patient/chart.html', {
            'patient': patient,
            'primary_insur': primary_insur,
            'secondary_insur': secondary_insur,
            'tertiary_insur':tertiary_insur})

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
