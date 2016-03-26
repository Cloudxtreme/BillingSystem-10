from django.shortcuts import render
from functools import partial, wraps
from django.shortcuts import *
from django.core import serializers
from django.db.models import Sum
from datetime import datetime
from .models import *
from infoGatherer.models import Personal_Information
from django.http import JsonResponse
from base.models import ExtPythonSerializer


def view_dashboard(request):
    return render(request, 'displayContent/dashboard.html')

def view_patient(request):
    return render(request, 'displayContent/patient/main.html')

def api_search_patient(request):
    if request.method == 'POST':
        post_data = request.POST
        patient = Personal_Information.objects.filter(
            first_name__icontains=post_data.get('first_name') or '',
            last_name__icontains=post_data.get('last_name') or '',
        )

        # if post_data.get('last_name'):
        #     patient = patient.filter(payer_patient__last_name__icontains=post_data.get('last_name'))
        # if post_data.get('first_name'):
        #     patient = patient.filter(payer_patient__first_name__icontains=post_data.get('first_name'))

        se = ExtPythonSerializer().serialize(
            patient,
            props=['chart_no',],
            use_natural_foreign_keys=True
        )
        # print se
        print "123"
        return JsonResponse(data=se, safe=False)
    else:
        print "456"
        return JsonResponse([], safe=False)