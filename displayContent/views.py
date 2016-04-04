from django.shortcuts import *
from functools import partial, wraps
from django.shortcuts import *
from django.core import serializers
from django.db.models import Sum
from datetime import datetime
from .models import *
from infoGatherer.models import Personal_Information, Payer, Insurance_Information
from accounting.models import *
from accounting.forms import NoteForm
from django.http import JsonResponse
from base.models import ExtPythonSerializer
import re
from decimal import *


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
        return HttpResponse("<html><h2>The patientID doesn't exist in the database.</h2></html>")

def view_patient(request, chart):
    """Page to view info about patients and goto the claims"""

    patient = get_object_or_404(Personal_Information, pk=chart)

    # Insurance information
    insur_q_set = patient.insurance_information_set.all()

    # # Primary Insurance
    # primary_insurance = insur_q_set.filter(level='primary').values()[0] if insur_q_set.filter(level='primary').exists() else []
    # if len(primary_insurance) > 0:
    #     primary_insurance_payer=Payer.objects.filter(pk=primary_insurance["payer_id"]).values()[0]
    # else:
    #     primary_insurance_payer=[]

    # # Secondary Insurance
    # secondary_insurance=insur_q_set.filter(level='secondary').values()[0] if insur_q_set.filter(level='secondary').exists() else []
    # if(len(secondary_insurance) >0):
    #     secondary_insurance_payer=Payer.objects.filter(pk=secondary_insurance["payer_id"]).values()[0]
    # else:
    #     secondary_insurance_payer=[]

    # # Tertiary Insurance
    # tertiary_insurance=insur_q_set.filter(level='tertiary').values()[0] if insur_q_set.filter(level='tertiary').exists() else []
    # if(len(tertiary_insurance) >0):
    #     tertiary_insurance_payer=Payer.objects.filter(pk=tertiary_insurance["payer_id"]).values()[0]
    # else:
    #     tertiary_insurance_payer=[]


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

    return render(request, 'displayContent/patient/chart.html', {
            'patient': patient,
            'primary_insur': primary_insur,
            'secondary_insur': secondary_insur,
            'tertiary_insur':tertiary_insur})

def payment_details(request, claim_id):
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
                props=['id', 'get_patient_insurance', ],
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
