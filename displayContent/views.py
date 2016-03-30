from django.shortcuts import render
from functools import partial, wraps
from django.shortcuts import *
from django.core import serializers
from django.db.models import Sum
from datetime import datetime
from .models import *
from infoGatherer.models import Personal_Information, Payer
from django.http import JsonResponse
from base.models import ExtPythonSerializer
import re


def view_dashboard(request):
    return render(request, 'displayContent/dashboard.html')

def view_claims(request):
    return render(request, 'displayContent/patient/claim.html')


def view_patient(request):
    m = re.search('.*patient\/([0-9]+)\/.*', str(request))
    chart=m.group(1)

    obj=Personal_Information.objects.filter(pk=chart)
    patient_info=obj.values()

    if(len(patient_info)>0):
        # Insurance
        insurance_obj=obj[0].insurance_information_set.all()

        # Primary Insurance
        primary_insurance=insurance_obj.filter(level='primary').values()[0] if insurance_obj.filter(level='primary').exists() else []
        print len(primary_insurance)
        if(len(primary_insurance) >0):
            primary_insurance_payer=Payer.objects.filter(pk=primary_insurance["payer_id"]).values()[0]
        else:
            primary_insurance_payer=[]

        # Secondary Insurance
        secondary_insurance=insurance_obj.filter(level='secondary').values()[0] if insurance_obj.filter(level='secondary').exists() else []
        if(len(secondary_insurance) >0):
            secondary_insurance_payer=Payer.objects.filter(pk=secondary_insurance["payer_id"]).values()[0]
        else:
            secondary_insurance_payer=[]

        # Tertiary Insurance
        tertiary_insurance=insurance_obj.filter(level='tertiary').values()[0] if insurance_obj.filter(level='tertiary').exists() else []
        if(len(tertiary_insurance) >0):
            tertiary_insurance_payer=Payer.objects.filter(pk=tertiary_insurance["payer_id"]).values()[0]
        else:
            tertiary_insurance_payer=[]


        return render(request, 'displayContent/patient/chart.html', 
            {
                'patient_info': patient_info[0],

                'primary_insurance': primary_insurance,
                'primary_insurance_payer':primary_insurance_payer,

                'secondary_insurance': secondary_insurance,
                'secondary_insurance_payer':secondary_insurance_payer,

                'tertiary_insurance': tertiary_insurance,
                'tertiary_insurance_payer':tertiary_insurance_payer,

            }
        )
    else:
        return JsonResponse([], safe=False)

def api_search_patient(request):
    if request.method == 'POST':
        post_data = request.POST
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
        # print se
        return JsonResponse(data=se, safe=False)
    else:
        # print "456"
        return JsonResponse([], safe=False)