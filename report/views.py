from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone

from datetime import datetime, timedelta
from decimal import *
from xlwt import Workbook
import datetime
import pytz
import xlwt
import time
from dateutil import tz

from infoGatherer.models import *
from accounting.models import *
from dashboard.models import Notes
from .models import *


@login_required
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

    from win32com import client
    from django.conf import settings
    import pythoncom

    pythoncom.CoInitialize()
    excel = None
    wb = None
    try:
        # Prepare excel template
        excel = client.Dispatch("Excel.Application")
        templateDir = settings.BASE_DIR + "\\templates\\report"
        wb = excel.Workbooks.Open(templateDir + "\\statement.xlsx")
        ws = wb.Worksheets("statement")

        # Write data
        ws.Range("F1").Value = billing_provider.provider_name.upper()
        ws.Range("F2").Value = billing_provider.provider_address.upper()
        ws.Range("F3").Value = "%s %s %s" % (
                billing_provider.provider_city.upper(),
                billing_provider.provider_state.upper(),
                billing_provider.provider_zip)

        ws.Range("A5").Value = ws.Range("A5").Value + \
                " " + billing_provider.provider_phone.upper()
        ws.Range("A6").Value = ws.Range("A6").Value + \
                " " + patient.full_name.upper()

        ws.Range("AM6").Value = today.strftime("%m/%d/%y")
        ws.Range("BN6").Value = patient.chart_no

        ws.Range("F10").Value = patient.full_name.upper()
        ws.Range("F11").Value = patient.address.upper()
        ws.Range("F12").Value = "%s %s %s" % (
                patient.city.upper(),
                patient.state.upper(),
                patient.zip)

        ws.Range("BA10").Value = ws.Range("F1").Value
        ws.Range("BA11").Value = ws.Range("F2").Value
        ws.Range("BA12").Value = ws.Range("F3").Value

        ws.Range("L18").Value = ws.Range("F10").Value
        ws.Range("AV18").Value = ws.Range("BN6").Value

        line = 19
        for claim in claims:
            ws.Range("A%s" % line).Value = claim.created.strftime("%m/%d/%y")
            ws.Range("L%s" % line).Value = claim.rendering_provider\
                    .provider_name.upper()
            ws.Range("AF%s" % line).Value = claim.total_charge
            ws.Range("AL%s" % line).Value = claim.ins_adjustment_per_claim
            ws.Range("AV%s" % line).Value = claim.ins_pmnt_per_claim
            ws.Range("BC%s" % line).Value = claim.pat_responsible_per_claim
            ws.Range("BJ%s" % line).Value = claim.pat_pmnt_per_claim
            ws.Range("BT%s" % line).Value = claim.total_balance

            line += 1
            for procedure in claim.procedure_set.all():
                ws.Range("A%s" % line).Value = procedure.date_of_service.strftime("%m/%d/%y")
                ws.Range("F%s" % line).Value = procedure.cpt.cpt_code
                ws.Range("L%s" % line).Value = procedure.cpt.cpt_description.upper()
                ws.Range("AF%s" % line).Value = procedure.ins_total_charge
                ws.Range("AL%s" % line).Value = procedure.ins_total_adjustment
                ws.Range("AV%s" % line).Value = procedure.ins_total_pymt

                line += 1
                for charge in procedure.charge_set.all():
                    if charge.payer_type == "Patient":
                        ws.Range("L%s" % line).Value = charge.resp_type.upper()
                        ws.Range("BC%s" % line).Value = charge.amount
                        line += 1

        ws.Range("AV55").Value = total_ins_pymt
        ws.Range("BJ55").Value = total_pat_pymt

        ws.Range("P57").Value = aging.get("i_m1")
        ws.Range("Y57").Value = aging.get("i_m2")
        ws.Range("AH57").Value = aging.get("i_m3")
        ws.Range("AQ57").Value = aging.get("i_m4")
        ws.Range("AZ57").Value = aging.get("i_m5")
        ws.Range("BH57").Value = aging.get("i_t")

        ws.Range("P58").Value = aging.get("p_m1")
        ws.Range("Y58").Value = aging.get("p_m2")
        ws.Range("AH58").Value = aging.get("p_m3")
        ws.Range("AQ58").Value = aging.get("p_m4")
        ws.Range("AZ58").Value = aging.get("p_m5")
        ws.Range("BH58").Value = aging.get("p_t")

        ws.Range("BA6").Value = aging.get("total")
        ws.Range("BT17").Value = aging.get("total")
        ws.Range("BT55").Value = aging.get("total")
        ws.Range("BT60").Value = aging.get("total")

        # Save as PDF format
        file_url = "\\temp\\statement.pdf"
        wb.ExportAsFixedFormat(0, settings.BASE_DIR + file_url)

        # fileStorage = FileSystemStorage()
        # fileStorage.file_permissions_mode = 0744
        # f = open('output.pdf', 'rb+')
        # myfile = File(f)
        # name = fileStorage.get_available_name(str(claim_id)+".pdf")
        # fileStorage.save(name, myfile)
        # today = datetime.datetime.now()
        # today_path = today.strftime("%Y/%m/%d")
        # newdoc = Document.objects.create(claim=claim, docfile='media/documents/'+today_path+"/"+name)

        try:
            with transaction.atomic():
                sh = StatementHistory.objects.create(
                        created_by=request.user)

                s = Statement.objects.create(
                        statementHistory=sh,
                        patient=patient,
                        balance=aging.get("total"),
                        url=file_url)
        except IntegrityError:
            print 'IntegrityError has occured.'

    except Exception, e:
        print "Error occurs during saving statement report"
        print e
    finally:
        if wb is not None:
            wb.Close(False)
        if excel is not None:
            excel.Application.Quit()

    return render(request, "report/statement.html", {
        "patient": patient,
        "billing_provider": billing_provider,
        "claims": claims,
        "aging": aging,
        "today": today,
        "total_ins_pymt": total_ins_pymt,
        "total_pat_pymt": total_pat_pymt,
    })

def statment_read(request, statement):
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

def index(request):
    return render(request, "report/statement.html")

def report_search(request):
    return render(request, "report/report_search.html")
    return HttpResponse("<html>To do!</html>")

def TransactionReportPayment(request):
    utc=pytz.utc
    from_dos = datetime.datetime(2016, 04, 18, 0, 0,0,0,utc)
    to_dos = datetime.datetime(2016, 04, 28, 0,0,0,0,utc)

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

    # alignment and border
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_LEFT

    borderT1 = xlwt.Borders()
    borderT1.down = xlwt.Borders.THIN

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
    font.height = 240
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
    sheet1.write(3, 0, label = '', style=style1)
    
    sheet1.write(3, 1, label = 'Patient', style=style1)
    sheet1.write(3, 2, label = 'Chart No', style=style1)
    sheet1.write(3, 3, label = 'Claim id', style=style1)
    sheet1.write(3, 4, label = 'Date', style=style1)
    sheet1.write(3, 5, label = 'Provider', style=style1)
    sheet1.write(3, 6, label = 'POS', style=style1)
    sheet1.write(3, 7, label = 'Diagnosis', style=style1)
    sheet1.write(3, 8, label = 'TX Code', style=style1)
    sheet1.write(3, 9, label = 'Amount', style=style1)

    # filtering the information!
    claim = Claim.objects.filter(created__range=(from_dos, to_dos)).order_by('patient').all()
    # setting base line number
    line=5
    patient_old_no=""
    total_charge=Decimal("0.00")
    total_ins=Decimal("0.00")
    total_pat=Decimal("0.00")
    total_pat_paid=Decimal("0.00")
    total_adj=Decimal("0.00")
    for cl in claim:
        # procedure
        pro=cl.procedure_set.all()
        # patient
        patient=cl.patient.get_full_name()
        if(patient_old_no!=cl.patient_id):
            sheet1.write(line, 1, label = patient, style=style2)
            sheet1.write(line, 2, label = cl.patient_id, style=style7)
        patient_old_no=cl.patient_id
        for procedure in pro:
            sheet1.write(line, 3, label = cl.id,style=style7)
            sheet1.write(line, 4, label = str(procedure.date_of_service), style=style2)
            sheet1.write(line, 5, label = procedure.rendering_provider.provider_name, style=style2)
            sheet1.write(line, 6, label = procedure.claim.location_provider.place_of_service, style=style2)
            sheet1.write(line, 7, label = procedure.diag , style=style2)
            sheet1.write(line, 8, label = procedure.cpt.cpt_code, style=style2)
            sheet1.write(line, 9, label = str(Decimal(procedure.ins_total_charge)), style=style2)
            total_charge=total_charge+Decimal(procedure.ins_total_charge)
            char=procedure.charge_set.all()
            anytrue=False
            pat_tot=Decimal("0.00")
            for charge in char:
                if(charge.payer_type=='Patient'):
                    if(charge.resp_type=='Co-pay'):
                        anytrue=True
                        line=line+1
                        sheet1.write(line, 8, label = 'Co-pay', style=style2)
                        sheet1.write(line, 9, label = str(Decimal(charge.amount)), style=style2)
                        sheet1.write(line, 4, label = str((charge.created.astimezone(tz.tzlocal()))).split(" ")[0], style=style2)
                        pat_tot=pat_tot+Decimal(charge.amount)
                    if(charge.resp_type=='Deductible'):
                        anytrue=True
                        line=line+1
                        sheet1.write(line, 8, label = 'Deductable', style=style2)
                        sheet1.write(line, 9, label = str(Decimal(charge.amount)), style=style2)
                        sheet1.write(line, 4, label = str((charge.created.astimezone(tz.tzlocal()))).split(" ")[0], style=style2)
                        pat_tot=pat_tot+Decimal(charge.amount)
                    if(charge.resp_type=='Other PR'):
                        anytrue=True
                        line=line+1
                        sheet1.write(line, 8, label = 'Other PR', style=style2)
                        sheet1.write(line, 9, label = str(Decimal(charge.amount)), style=style2)
                        sheet1.write(line, 4, label = str((charge.created.astimezone(tz.tzlocal()))).split(" ")[0], style=style2)
                        pat_tot=pat_tot+Decimal(charge.amount)
            if(anytrue):
                line=line+1
                sheet1.write(line, 8, label = 'Pat Balance', style=style2)
                sheet1.write(line, 9, label = str(Decimal(procedure.patient_balance)), style=style2)
                total_pat_paid=total_pat_paid+pat_tot-Decimal(procedure.patient_balance)   
            total_pat=total_pat+pat_tot                 
            # ins
            line=line+1
            sheet1.write(line, 8, label = 'Ins. Paid', style=style2)
            sheet1.write(line, 9, label = str(Decimal(procedure.ins_total_pymt)), style=style2)
            total_ins=total_ins+Decimal(procedure.ins_total_pymt)
            line=line+1
            sheet1.write(line, 8, label = 'Ins. Adjustment', style=style2)
            sheet1.write(line, 9, label = str(Decimal(procedure.ins_total_adjustment)), style=style2)
            total_adj=total_adj+Decimal(procedure.ins_total_adjustment)
            line=line+1

    line=line+5
    sheet1.write(line, 5, label = 'All Provider - All Location', style=style6)

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


def TransactionReport(request):
    utc=pytz.utc
    from_dos = datetime.datetime(2016, 04, 8, 0, 0,0,0,utc)
    to_dos = datetime.datetime(2016, 04, 23, 0,0,0,0,utc)

    # dictionaries to count number of entries in it
    dic_pat={}
    dic_provider={}
    dic_code={}

    #keeping track pf total charge
    sum_charge=Decimal(0)
    sum_unit_total=Decimal(0)
    # Writing into excel workbook
    wb = Workbook()
    sheet1 = wb.add_sheet('Transaction Report')

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

    sheet1.write(0, 0, label = 'Transaction Report', style = style)
    sheet1.write(0, 7, label = 'Report Date:', style=style2)
    sheet1.write(0, 8, label = str(datetime.datetime.now()).split(" ")[0],style=style2)
    sheet1.write(1, 7, label = 'Date Span:',style=style2)
    sheet1.write(1, 8, label = str(from_dos).split(" ")[0] +" to "+ str(to_dos).split(" ")[0],style=style2)
    sheet1.write(3, 0, label = '', style=style1)

    sheet1.write(3, 1, label = 'Patient', style=style1)
    sheet1.write(3, 2, label = 'Chart No', style=style1)
    sheet1.write(3, 3, label = 'Provider', style=style1)
    sheet1.write(3, 4, label = 'Code [Modifiers]', style=style1)
    sheet1.write(3, 5, label = 'Procedure Code Description', style=style1)
    sheet1.write(3, 6, label = 'DOS', style=style1)
    sheet1.write(3, 7, label = 'Created Date', style=style1)
    sheet1.write(3, 8, label = 'Units', style=style1)
    sheet1.write(3, 9, label = 'Charges', style=style1)

    # filtering the information!
    claim = Claim.objects.filter(created__range=(from_dos, to_dos)).all()
    # setting base line number
    line=5
    for cl in claim:
        dic_pro_claim={}
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
            sheet1.write(line, 2, label = cl.patient_id, style=style2)
            sheet1.write(line, 3, label = procedure.rendering_provider.provider_name, style=style2)
            sheet1.write(line, 4, label = procedure.cpt.cpt_code, style=style2)
            sheet1.write(line, 5, label = procedure.cpt.cpt_description, style=style2)
            sheet1.write(line, 6, label = str(procedure.date_of_service), style=style2)
            sheet1.write(line, 7, label = str(procedure.created), style=style2)
            sheet1.write(line, 8, label = str(Decimal(procedure.unit)), style=style2)
            sheet1.write(line, 9, label = str(Decimal(procedure.ins_total_charge)), style=style2)
            # summing up charges
            sum_charge=sum_charge+Decimal(procedure.ins_total_charge)
            sum_claim=sum_claim+Decimal(procedure.ins_total_charge)
            sum_unit=sum_unit+Decimal(procedure.unit)
            #entering into dictionary
            dic_pat[str(cl.patient_id)]=1
            dic_provider[str(procedure.rendering_provider.provider_name)]=1
            dic_code[str(procedure.cpt.cpt_code)]=1
            dic_pro_claim[str(procedure.rendering_provider.provider_name)]=1
            dic_cpt_claim[str(procedure.cpt.cpt_code)]=1
            line=line+1
        sum_unit_total=sum_unit_total+sum_unit
        # border
        sheet1.write(line, 1, label = '', style=style3)
        sheet1.write(line, 2, label = '', style=style3)
        sheet1.write(line, 3, label = len(dic_pro_claim), style=style3)
        sheet1.write(line, 4, label = len(dic_cpt_claim), style=style3)
        sheet1.write(line, 5, label = '', style=style3)
        sheet1.write(line, 6, label = '', style=style3)
        sheet1.write(line, 7, label = '', style=style3)
        sheet1.write(line, 8, label = str(sum_unit), style=style3)
        sheet1.write(line, 9, label = str(sum_claim), style=style3)

    # writing totals
    sheet1.write(4, 1, label = 'Total', style=style1)
    sheet1.write(4, 2, label = str(len(dic_pat)), style=style1)
    sheet1.write(4, 3, label = str(len(dic_provider)), style=style1)
    sheet1.write(4, 4, label = str(len(dic_code)), style=style1)
    sheet1.write(4, 5, label = '', style=style1)
    sheet1.write(4, 6, label = '', style=style1)
    sheet1.write(4, 7, label = '', style=style1)
    sheet1.write(4, 8, label = str(Decimal(sum_unit_total)), style=style1)
    sheet1.write(4, 9, label = str(Decimal(sum_charge)) , style=style1)

    # saving the report
    wb.save('transactionreport.xls')
    return HttpResponse(open('transactionreport.xls','rb+').read(),
        content_type='application/vnd.ms-excel')
