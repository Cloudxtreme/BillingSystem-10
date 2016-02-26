from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

from infoGatherer.models import Personal_Information, Payer
from fdfgen import forge_fdf
import os

# Create your views here.
def index(request):
    return render(request, 'claims/index.html')

def createClaim(request):
    patient_list = Personal_Information.objects.order_by('first_name')
    payer_list = Payer.objects.order_by('name')
    context = {
        'patient_list': patient_list,
        'payer_list': payer_list,
    }

    return render(request, 'claims/createClaim.html', context)

def generateClaim(request):

    for k, v in request.POST.iteritems():
        print k + ' : ' + v

    return render(request, 'claims/createClaim.html')