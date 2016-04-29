from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone

from datetime import datetime, timedelta
from decimal import *
from xlwt import Workbook
import datetime
import pytz
from pytz import timezone
import xlwt
import time
from dateutil import tz
from .forms import *
from django.db.models import Q

from infoGatherer.models import *
from accounting.models import *
from dashboard.models import Notes


def statment_create(request):
    patient_id = request.GET.get("patient")
    patient = get_object_or_404(Personal_Information, pk=patient_id)

    billing_provider_id = request.GET.get("billing")
    try:
        billing_provider = Provider.objects.get(pk=billing_provider_id)
    except:
        billing_provider = Provider.objects.get(provider_name__icontains="XENON HEALTH")

    # Calculate total ins pymt and pat pymt
    total_ins_pymt = 0
    total_pat_pymt = 0
    claims = patient.patient.all()
    for claim in claims:
        total_ins_pymt += claim.ins_pmnt_per_claim
        total_pat_pymt += claim.pat_pmnt_per_claim

    # Prepare aging table
    today = timezone.now().date()
    m1_time = today - timedelta(days=30)
    m2_time = today - timedelta(days=60)
    m3_time = today - timedelta(days=90)
    m4_time = today - timedelta(days=120)

    Q1 = Q(created__gte=m1_time)
    Q2 = Q(Q(created__lt=m1_time) & Q(created__gte=m2_time))
    Q3 = Q(Q(created__lt=m2_time) & Q(created__gte=m3_time))
    Q4 = Q(Q(created__lt=m3_time) & Q(created__gte=m4_time))
    Q5 = Q(Q(created__lt=m4_time))

    charges = Charge.objects.filter(procedure__claim__patient=patient)
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

    return render(request, "report/statement.html", {
        "patient": patient,
        "billing_provider": billing_provider,
        "claims": claims,
        "aging": aging,
        "today": timezone.now(),
        "total_ins_pymt": total_ins_pymt,
        "total_pat_pymt": total_pat_pymt,
    })

def index(request):
    return render(request, "report/statement.html")

def report_search(request):
    str_form = SearchTransactionReport(request.POST or None)

    if request.method == 'POST' and str_form.is_valid():
        cleaned_data = str_form.cleaned_data
        reporttype = cleaned_data.get('reporttype')
        startdate = cleaned_data.get('startdate')
        enddate = cleaned_data.get('enddate')
        renderingprovider = cleaned_data.get('renderingprovider')
        locationprovider = cleaned_data.get('locationprovider')

        # utc=pytz.utc

        # from_dos = datetime.datetime.combine(startdate, datetime.time())
        from_dos = str(startdate)+" 00:00:00"
        from_dos = datetime.datetime.strptime(from_dos, "%Y-%m-%d %H:%M:%S")
        from_dos = pytz.timezone('UTC').localize(from_dos)
        # to_dos = datetime.datetime.combine(enddate, datetime.time())
        to_dos = str(enddate)+" 23:59:59"
        to_dos = datetime.datetime.strptime(to_dos, "%Y-%m-%d %H:%M:%S")
        to_dos = pytz.timezone('UTC').localize(to_dos)

        # Transaction report without payments!
        if(reporttype=="1"):
            return TransactionReport(from_dos, to_dos, renderingprovider, locationprovider)

        elif(reporttype=="2"):
            return TransactionReportPayment(from_dos, to_dos, renderingprovider, locationprovider)

        return render(request, "report/report_search.html", {'form': str_form})

    return render(request, "report/report_search.html", {'form': str_form})

def TransactionReportPayment(from_dos, to_dos, renderingprovider, locationprovider ):
    # utc=pytz.utc
    # from_dos = datetime.datetime(2016, 04, 18, 0, 0,0,0,utc)
    # to_dos = datetime.datetime(2016, 04, 28, 0,0,0,0,utc)
    wb = Workbook()
    sheet1 = wb.add_sheet('Transaction Report Payment')
    # Set wedth of columns
    sheet1.col(0).width = 1000
    sheet1.col(1).width = 5000
    sheet1.col(2).width = 2500
    sheet1.col(3).width = 5000
    sheet1.col(4).width = 5000
    sheet1.col(5).width = 5500
    sheet1.col(6).width = 5000
    sheet1.col(7).width = 5000
    sheet1.col(8).width = 5000
    sheet1.col(9).width = 5000
    sheet1.col(10).width = 5000
    # alignment and border
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_LEFT
    borderT1 = xlwt.Borders()
    borderT1.top = xlwt.Borders.THIN
    borderT2 = xlwt.Borders()
    borderT2.top = xlwt.Borders.THIN
    borderT2.bottom = xlwt.Borders.THIN
    # styles
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = True
    font.height = 240
    style.font = font

    style1 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = True
    font.height = 160
    style1.borders = borderT1
    style1.font = font

    style8 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = False
    font.height = 160
    style8.borders = borderT1
    style8.font = font

    style0 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = True
    font.height = 160
    style0.borders = borderT2
    style0.font = font

    style2 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = False
    font.height = 160
    style2.font = font

    style7 = xlwt.XFStyle()
    font = xlwt.Font()
    style7.alignment = alignment
    font.name = 'Verdana'
    font.bold = False
    font.height = 160
    style7.font = font

    style77 = xlwt.XFStyle()
    font = xlwt.Font()
    style77.alignment = alignment
    font.name = 'Verdana'
    font.bold = False
    font.height = 160
    style77.borders = borderT1
    style77.font = font

    style4 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = True
    font.height = 160
    style4.font = font

    style6 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = True
    font.height = 200
    style6.font = font

    style5 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = False
    font.height = 200
    style5.font = font

    sheet1.write(0, 0, label = 'Transaction Report With Payment Details', style = style)
    sheet1.write(0, 7, label = 'Report Date:', style=style2)
    sheet1.write(0, 8, label = str(datetime.datetime.now()).split(" ")[0],style=style2)
    sheet1.write(1, 7, label = 'Date Span:',style=style2)
    sheet1.write(1, 8, label = str(from_dos).split(" ")[0] +" to "+ str(to_dos).split(" ")[0],style=style2)
    sheet1.write(3, 0, label = '', style=style0)
    sheet1.write(3, 1, label = 'Patient', style=style0)
    sheet1.write(3, 2, label = 'Chart No', style=style0)
    sheet1.write(3, 3, label = 'Claim id', style=style0)
    sheet1.write(3, 4, label = 'Date', style=style0)
    sheet1.write(3, 5, label = 'Rendering Provider', style=style0)
    sheet1.write(3, 6, label = 'Location Provider', style=style0)
    sheet1.write(3, 7, label = 'POS', style=style0)
    sheet1.write(3, 8, label = 'Diagnosis', style=style0)
    sheet1.write(3, 9, label = 'TX Code', style=style0)
    sheet1.write(3, 10, label = 'Amount', style=style0)
    # filtering the information!
    claim = Claim.objects.filter(created__range=(from_dos, to_dos))
    if(renderingprovider is not None):
        claim = claim.filter(rendering_provider=renderingprovider)
    if(locationprovider is not None):
        claim = claim.filter(location_provider=locationprovider)
    claim=claim.order_by('patient')
    # setting base line number
    line=4
    patient_old_no=""
    total_charge=Decimal("0.00")
    total_ins=Decimal("0.00")
    total_pat=Decimal("0.00")
    total_pat_paid=Decimal("0.00")
    total_adj=Decimal("0.00")
    for cl in claim:
        first=True
        # procedure
        pro=cl.procedure_set.all()
        # patient
        patient=cl.patient.get_full_name()
        if(patient_old_no!=cl.patient_id):
            sheet1.write(line, 1, label = patient, style=style8)
            sheet1.write(line, 2, label = cl.patient_id, style=style77)
        else:
            first=False
        patient_old_no=cl.patient_id
        
        for procedure in pro:
            if(first==True):
                sheet1.write(line, 3, label = cl.id,style=style77)
                sheet1.write(line, 4, label = str(procedure.date_of_service), style=style8)
                sheet1.write(line, 5, label = procedure.rendering_provider.provider_name, style=style8)
                sheet1.write(line, 6, label = cl.location_provider.provider_name, style=style8)
                sheet1.write(line, 7, label = procedure.claim.location_provider.place_of_service, style=style8)
                sheet1.write(line, 8, label = procedure.diag , style=style8)
                sheet1.write(line, 9, label = procedure.cpt.cpt_code, style=style8)
                sheet1.write(line, 10, label = str(Decimal(procedure.ins_total_charge)), style=style8)
                first=False
            else:
                sheet1.write(line, 3, label = cl.id,style=style7)
                sheet1.write(line, 4, label = str(procedure.date_of_service), style=style2)
                sheet1.write(line, 5, label = procedure.rendering_provider.provider_name, style=style2)
                sheet1.write(line, 6, label = cl.location_provider.provider_name, style=style2)
                sheet1.write(line, 7, label = procedure.claim.location_provider.place_of_service, style=style2)
                sheet1.write(line, 8, label = procedure.diag , style=style2)
                sheet1.write(line, 9, label = procedure.cpt.cpt_code, style=style2)
                sheet1.write(line, 10, label = str(Decimal(procedure.ins_total_charge)), style=style2)
            total_charge=total_charge+Decimal(procedure.ins_total_charge)
            char=procedure.charge_set.all()
            anytrue=False
            pat_tot=Decimal("0.00")
            for charge in char:
                if(charge.payer_type=='Patient'):
                    if(charge.resp_type=='Co-pay'):
                        anytrue=True
                        line=line+1
                        sheet1.write(line, 9, label = 'Co-pay', style=style2)
                        sheet1.write(line, 10, label = str(Decimal(charge.amount)), style=style2)
                        sheet1.write(line, 4, label = str((charge.created.astimezone(tz.tzlocal()))).split(" ")[0], style=style2)
                        pat_tot=pat_tot+Decimal(charge.amount)
                    if(charge.resp_type=='Deductible'):
                        anytrue=True
                        line=line+1
                        sheet1.write(line, 9, label = 'Deductable', style=style2)
                        sheet1.write(line, 10, label = str(Decimal(charge.amount)), style=style2)
                        sheet1.write(line, 4, label = str((charge.created.astimezone(tz.tzlocal()))).split(" ")[0], style=style2)
                        pat_tot=pat_tot+Decimal(charge.amount)
                    if(charge.resp_type=='Other PR'):
                        anytrue=True
                        line=line+1
                        sheet1.write(line, 9, label = 'Other PR', style=style2)
                        sheet1.write(line, 10, label = str(Decimal(charge.amount)), style=style2)
                        sheet1.write(line, 4, label = str((charge.created.astimezone(tz.tzlocal()))).split(" ")[0], style=style2)
                        pat_tot=pat_tot+Decimal(charge.amount)
            if(anytrue):
                line=line+1
                sheet1.write(line, 9, label = 'Pat Balance', style=style2)
                sheet1.write(line, 10, label = str(Decimal(procedure.patient_balance)), style=style2)
                total_pat_paid=total_pat_paid+pat_tot-Decimal(procedure.patient_balance)   
            total_pat=total_pat+pat_tot                 
            # ins
            line=line+1
            sheet1.write(line, 9, label = 'Ins. Paid', style=style2)
            sheet1.write(line, 10, label = str(Decimal(procedure.ins_total_pymt)), style=style2)
            total_ins=total_ins+Decimal(procedure.ins_total_pymt)
            line=line+1
            sheet1.write(line, 9, label = 'Ins. Adjustment', style=style2)
            sheet1.write(line, 10, label = str(Decimal(procedure.ins_total_adjustment)), style=style2)
            total_adj=total_adj+Decimal(procedure.ins_total_adjustment)
            line=line+1

    # writing totals
    sheet1.write(line, 1, label = '', style=style1)
    sheet1.write(line, 2, label = '', style=style1)
    sheet1.write(line, 3, label = '', style=style1)
    sheet1.write(line, 4, label = '', style=style1)
    sheet1.write(line, 5, label = '', style=style1)
    sheet1.write(line, 6, label = '', style=style1)
    sheet1.write(line, 7, label = '', style=style1)
    sheet1.write(line, 8, label = '', style=style1)
    sheet1.write(line, 9, label = '', style=style1)
    sheet1.write(line, 10, label = '', style=style1)

    line=line+5
    loc_ref=""
    if(renderingprovider is not None):
        loc_ref="Rendering Provider: "+str(renderingprovider.provider_name)
    else:
        loc_ref="All Provider"
    loc_ref=loc_ref+" - "
    if(locationprovider is not None):
        loc_ref=loc_ref+"Location Provider: "+str(locationprovider.provider_name)
    else:
        loc_ref=loc_ref+"All Location"
    sheet1.write(line, 5, label = loc_ref, style=style6)
    #chargers
    line=line+1
    sheet1.write(line, 4, label = 'Charges', style=style5)
    sheet1.write(line, 5, label = 'Insurance', style=style5)
    sheet1.write(line, 6, label = str(total_charge), style=style5)
    line=line+1
    sheet1.write(line, 5, label = 'Patient', style=style5)
    sheet1.write(line, 6, label = str(total_pat), style=style5)
    # payments
    line=line+2
    sheet1.write(line, 4, label = 'Payments', style=style5)
    sheet1.write(line, 5, label = 'Insurance', style=style5)
    sheet1.write(line, 6, label = str(total_ins), style=style5)   
    line=line+1
    sheet1.write(line, 5, label = 'Patient', style=style5)
    sheet1.write(line, 6, label = str(total_pat_paid), style=style5)  
    line=line+2
    sheet1.write(line, 4, label = 'Adjustments', style=style5)
    sheet1.write(line, 5, label = 'Insurance', style=style5)
    sheet1.write(line, 6, label = str(total_adj), style=style5)
    # saving the report
    wb.save('transactionreportpayment.xls')
    return HttpResponse(open('transactionreportpayment.xls','rb+').read(),
        content_type='application/vnd.ms-excel')
    # return HttpResponse("<html>To do!</html>")

def TransactionReport(from_dos, to_dos, renderingprovider, locationprovider):
    # dictionaries to count number of entries in it
    dic_pat={}
    dic_provider={}
    dic_loc={}
    dic_code={}
    #keeping track pf total charge
    sum_charge=Decimal(0)
    sum_unit_total=Decimal(0)
    # Writing into excel workbook
    wb = Workbook()
    sheet1 = wb.add_sheet('Transaction Report')
    # set alignment
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_LEFT
    # set border
    borderT1 = xlwt.Borders()
    borderT1.top = xlwt.Borders.THIN
    borderT2 = xlwt.Borders()
    borderT2.top = xlwt.Borders.THIN
    #color
    shadedFill = xlwt.Pattern()
    shadedFill.pattern = xlwt.Pattern.SOLID_PATTERN
    shadedFill.pattern_fore_colour = 0x16 # 25% Grey
    shadedFill.pattern_back_colour = 0x08 # Black
    # Set wedth of columns
    sheet1.col(0).width = 1000
    sheet1.col(1).width = 5000
    sheet1.col(2).width = 2500
    sheet1.col(3).width = 5000
    sheet1.col(4).width = 5000
    sheet1.col(5).width = 8000
    sheet1.col(6).width = 5000
    sheet1.col(7).width = 5000
    sheet1.col(8).width = 5000
    sheet1.col(9).width = 5000
    sheet1.col(10).width = 5000

    # creating styles
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = True
    font.height = 240
    style.font = font

    style2 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = False
    font.height = 160
    style2.font = font

    style3 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = False
    font.height = 160
    style3.borders = borderT1
    style3.font = font

    style4 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = True
    font.height = 160
    style4.font = font

    style1 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = True
    font.height = 160
    style1.borders = borderT2
    style1.font = font

    style7 = xlwt.XFStyle()
    font = xlwt.Font()
    style7.alignment = alignment
    font.name = 'Verdana'
    font.bold = False
    font.height = 160
    style7.font = font

    sheet1.write(0, 0, label = 'Transaction Report', style = style)
    sheet1.write(0, 7, label = 'Report Date:', style=style2)
    sheet1.write(0, 8, label = str(datetime.datetime.now()).split(" ")[0],style=style2)
    sheet1.write(1, 7, label = 'Date Span:',style=style2)
    sheet1.write(1, 8, label = str(from_dos).split(" ")[0] +" to "+ str(to_dos).split(" ")[0],style=style2)
    sheet1.write(3, 0, label = '', style=style1)
    sheet1.write(3, 1, label = 'Patient', style=style1)
    sheet1.write(3, 2, label = 'Chart No', style=style1)
    sheet1.write(3, 3, label = 'Rendering Provider', style=style1)
    sheet1.write(3, 4, label = 'Location Provider', style=style1)
    sheet1.write(3, 5, label = 'Code [Modifiers]', style=style1)
    sheet1.write(3, 6, label = 'Procedure Code Description', style=style1)
    sheet1.write(3, 7, label = 'DOS', style=style1)
    sheet1.write(3, 8, label = 'Created Date', style=style1)
    sheet1.write(3, 9, label = 'Units', style=style1)
    sheet1.write(3, 10, label = 'Charges', style=style1)
    # filtering the information!
    claim = Claim.objects.filter(created__range=(from_dos, to_dos))
    if(renderingprovider is not None):
        claim = claim.filter(rendering_provider=renderingprovider)
    if(locationprovider is not None):
        claim = claim.filter(location_provider=locationprovider)
    # setting base line number
    line=5
    for cl in claim:
        dic_pro_claim={}
        dic_loc_claim={}
        dic_cpt_claim={}
        sum_claim=Decimal(0)
        sum_unit=Decimal(0)
        # procedure
        pro=cl.procedure_set.all()
        # patient
        patient=cl.patient.get_full_name()
        line=line+1
        # New line
        sheet1.write(line, 0, label = cl.patient.\
                        last_name+", "+cl.patient.\
                        first_name+"("+str(cl.patient.dob)+")", style=style4)
        line=line+1
        for procedure in pro:
            sheet1.write(line, 1, label = patient, style=style2)
            sheet1.write(line, 2, label = cl.patient_id, style=style7)
            sheet1.write(line, 3, label = procedure.rendering_provider.provider_name, style=style2)
            sheet1.write(line, 4, label = cl.location_provider.provider_name, style=style2)
            sheet1.write(line, 5, label = procedure.cpt.cpt_code, style=style2)
            sheet1.write(line, 6, label = procedure.cpt.cpt_description, style=style2)
            sheet1.write(line, 7, label = str(procedure.date_of_service), style=style2)
            sheet1.write(line, 8, label = str(procedure.created), style=style2)
            sheet1.write(line, 9, label = str(Decimal(procedure.unit)), style=style2)
            sheet1.write(line, 10, label = str(Decimal(procedure.ins_total_charge)), style=style2)
            # summing up charges
            sum_charge=sum_charge+Decimal(procedure.ins_total_charge)
            sum_claim=sum_claim+Decimal(procedure.ins_total_charge)
            sum_unit=sum_unit+Decimal(procedure.unit)
            #entering into dictionary
            dic_pat[str(cl.patient_id)]=1
            dic_provider[str(procedure.rendering_provider.provider_name)]=1
            dic_loc[str(cl.location_provider.provider_name)]=1
            dic_code[str(procedure.cpt.cpt_code)]=1
            dic_pro_claim[str(procedure.rendering_provider.provider_name)]=1
            dic_loc_claim[str(cl.location_provider.provider_name)]=1
            dic_cpt_claim[str(procedure.cpt.cpt_code)]=1
            line=line+1
        sum_unit_total=sum_unit_total+sum_unit
        # border
        sheet1.write(line, 1, label = '', style=style3)
        sheet1.write(line, 2, label = '', style=style3)
        sheet1.write(line, 3, label = len(dic_pro_claim), style=style3)
        sheet1.write(line, 4, label = len(dic_loc_claim), style=style3)
        sheet1.write(line, 5, label = len(dic_cpt_claim), style=style3)
        sheet1.write(line, 6, label = '', style=style3)
        sheet1.write(line, 7, label = '', style=style3)
        sheet1.write(line, 8, label = '', style=style3)
        sheet1.write(line, 9, label = str(sum_unit), style=style3)
        sheet1.write(line, 10, label = str(sum_claim), style=style3)
    # writing totals
    sheet1.write(4, 1, label = 'Total', style=style1)
    sheet1.write(4, 2, label = str(len(dic_pat)), style=style1)
    sheet1.write(4, 3, label = str(len(dic_provider)), style=style1)
    sheet1.write(4, 4, label = str(len(dic_loc)), style=style1)
    sheet1.write(4, 5, label = str(len(dic_code)), style=style1)
    sheet1.write(4, 6, label = '', style=style1)
    sheet1.write(4, 7, label = '', style=style1)
    sheet1.write(4, 8, label = '', style=style1)
    sheet1.write(4, 9, label = str(Decimal(sum_unit_total)), style=style1)
    sheet1.write(4, 10, label = str(Decimal(sum_charge)) , style=style1)
    # saving the report
    wb.save('transactionreport.xls')
    return HttpResponse(open('transactionreport.xls','rb+').read(),
        content_type='application/vnd.ms-excel')
