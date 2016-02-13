from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

from infoGatherer.models import Personal_Information, Payer
from fdfgen import forge_fdf
import os, sys

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
    print >>sys.stderr, request.method
    print >>sys.stderr, request.POST['patient_chart_no']
    print >>sys.stderr,  request.POST['insured_chart_no']
    print >>sys.stderr,  request.POST['payer_code']


    if request.method == 'POST' and \
        request.POST['patient_chart_no'] and \
        request.POST['insured_chart_no'] and \
        request.POST['payer_code']:

        patient = get_object_or_404(Personal_Information, pk=request.POST['patient_chart_no'])
        insured = get_object_or_404(Personal_Information, pk=request.POST['insured_chart_no'])
        payer = get_object_or_404(Payer, pk=request.POST['payer_code'])
        fields = [
            ('2', payer.address),
            ('10', patient.first_name + ' ' + patient.last_name),
            ('11', insured.first_name + ' ' + insured.last_name),
        ]
        fdf = forge_fdf("",fields,[],[],[])
        fdf_file = open("data.fdf","w")
        fdf_file.write(fdf)
        fdf_file.close()

        os.system('pdftk CMS1500.pdf fill_form data.fdf output output.pdf')
        os.remove('data.fdf')

        with open('output.pdf', 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename=output.pdf'
            return response
        pdf.closed

    else:

        return render(request, 'claims/generateClaim.html')