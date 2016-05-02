from django.shortcuts import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone

from datetime import datetime, timedelta
from decimal import *
from xlwt import Workbook
import os
import pytz
from pytz import timezone
import xlwt
import time
from dateutil import tz
from win32com import client
import pythoncom
from shutil import copyfile

from infoGatherer.models import *
from accounting.models import *
from dashboard.models import Notes
from .models import *
from .forms import *


@login_required
def statement_create(request, patient_id, today_page):
    patient = get_object_or_404(Personal_Information, pk=patient_id)
    d = datetime.strptime(today_page, "%m-%d-%Y")

    sh = statement_generate(
            request=request,
            today_page=d,
            patients=[patient])
    if sh is not None:
        ss = sh.statement_set.all()
        return redirect(reverse('report:statement_file_read',
                        kwargs={'statement_id': ss[0].pk}))

    messages.add_message(request, messages.WARNING,
            "There is no claim from this patient to create statement.")
    return redirect(reverse('displayContent:view_patient',
            kwargs={'chart': patient_id}))

@login_required
def statement_generate(
        request,
        today_page,
        billing_provider=None,
        rendering_provider=None,
        patients=None,
        min_balance=None,
        max_balance=None,
        message=""):

    # Get default billing provider if it is not provided
    if billing_provider is None or \
            type(billing_provider) != Provider or \
            billing_provider.role != "Billing":
        billing_provider = Provider.objects.get(
                provider_name__icontains="XENON HEALTH")

    # rendering_provider option will filter claims to retrieve
    # only those relate to this rendering doctor.  Set it to
    # None to indicate that any provider is fine.
    if type(rendering_provider) != Provider or \
            rendering_provider.role != "Rendering":
        rendering_provider = None

    # Check if patients is a collection of personal_information
    # or not.  If not, generate report for all patients
    if type(patients) != list and \
            type(patients) != tuple and \
            type(patients) != QuerySet:
        patients = Personal_Information.objects.all()
    elif len(patients) > 0:
        for patient in patients:
            if type(patient) != Personal_Information:
                patients = Personal_Information.objects.all()
                break
    else:
        patients = Personal_Information.objects.all()

    # Prepare time condition for aging table
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

    # These COM extension should be launch just once
    pythoncom.CoInitialize()
    excel = client.Dispatch("Excel.Application")

    # Create Statement history record to group all reports created
    # at the time user clicks
    sh = StatementHistory.objects.create(created_by=request.user)

    gen_report = 0
    for patient in patients:
        # Calculate total ins pymt and pat pymt
        total_ins_pymt = 0
        total_pat_pymt = 0

        if rendering_provider is not None:
            claims = patient.patient.filter(
                    rendering_provider=rendering_provider)
            # Exclude charges not related to rendering provider
            charges = Charge.objects.filter(
                    procedure__claim__patient=patient,
                    procedure__claim__rendering_provider=rendering_provider)
        else:
            claims = patient.patient.all()
            charges = Charge.objects.filter(procedure__claim__patient=patient)

        # No need to do anything if we don't
        # capture any claim from here
        if len(claims) < 1:
            continue

        for claim in claims:
            total_ins_pymt += claim.ins_pmnt_per_claim
            total_pat_pymt += claim.pat_pmnt_per_claim

        # Prepare aging table
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

        # If total balance of that patient doesn't match min or max
        # balance, do not generate report
        if min_balance is not None:
            if aging.get("total") < min_balance:
                continue
        if max_balance is not None:
            if aging.get("total") > max_balance:
                continue

        # Begin writing Excel template
        wb = None
        try:
            # Copy template to temp folder of that user beforehand
            temp_path = "temp/" + str(request.user.pk)
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)

            src_template = "templates/report/statement.xlsx"
            des_template = temp_path + "/statement.xlsx"
            copyfile(src_template, des_template)

            # Prepare excel template

            template_path = os.path.join(settings.BASE_DIR, des_template)
            wb = excel.Workbooks.Open(template_path)
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

            ws.Range("AM6").Value = today_page.strftime("%m/%d/%y")
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

                ws.Range("A%s" % line).Font.Bold = True
                ws.Range("L%s" % line).Font.Bold = True
                ws.Range("AF%s" % line).Font.Bold = True
                ws.Range("AL%s" % line).Font.Bold = True
                ws.Range("AV%s" % line).Font.Bold = True
                ws.Range("BC%s" % line).Font.Bold = True
                ws.Range("BJ%s" % line).Font.Bold = True
                ws.Range("BT%s" % line).Font.Bold = True

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

            if len(message) > 0:
                ws.Range("A60").Value = message

            # Prepare path and filename for temp file
            temp_filename = "statement.pdf"
            temp_pdf_file_path = os.path.join(temp_path, temp_filename)
            location = "documents/report/statement/" + today.strftime("%Y") + \
                    "/user_" + str(request.user.pk) + "/"

            # Save temp file as PDF format
            wb.ExportAsFixedFormat(0, os.path.join(
                    settings.BASE_DIR,
                    temp_pdf_file_path))

            # Save to permanent file with FileSystemStorage to use its
            # built-in auto-rename function
            fileStorage = FileSystemStorage(
                    location=os.path.join(settings.MEDIA_ROOT, location))
            fileStorage.file_permissions_mode = 0744
            temp_file = File(open(temp_pdf_file_path, 'rb+'))
            filename = fileStorage.save(
                    today.strftime("%m%d_%H%M%S_p_") + str(patient.pk) + ".pdf",
                    temp_file)

            # remove temp file
            temp_file.close()
            os.remove(temp_pdf_file_path)

            s = Statement.objects.create(
                    statement_history=sh,
                    patient=patient,
                    balance=aging.get("total"),
                    file=location + filename,
                    created=sh.created)

            gen_report += 1

        except Exception, e:
            print "Error occurs during saving statement report"
            print e
        finally:
            if wb is not None:
                wb.Close(False)
                os.remove(template_path)

    pythoncom.CoUninitialize()

    # Delete history object is we didn't create
    # any report for that group
    if gen_report < 1:
        sh.delete()
        return None
    else:
        return sh

def statement_read(request):
    today = timezone.now()
    shs = StatementHistory.objects.all().order_by("-created")

    form = StatementReportForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        cleaned_data = form.cleaned_data
        sh = statement_generate(
                request=request,
                today_page=cleaned_data.get("today"),
                billing_provider=cleaned_data.get("billing_provider"),
                rendering_provider=cleaned_data.get("rendering_provider"),
                patients=cleaned_data.get("patients"),
                min_balance=cleaned_data.get("min_balance"),
                max_balance=cleaned_data.get("max_balance"),
                message=cleaned_data.get("message"))

        if sh is not None:
            return redirect(reverse('report:statement_history_read',
                    kwargs={'history_id': sh.pk}))
        else:
            messages.add_message(request, messages.WARNING,
                    "No statement has been created due to given options")
            return redirect(reverse('report:statement_read'))

    return render(request, "report/statement.html", {
        "today": today,
        "shs": shs,
        "form": form})

def statement_history_read(request, history_id):
    ss = Statement.objects.filter(statement_history=history_id)

    return render(request, "report/statement_history.html", {
        "ss": ss})

def statement_file_read(request, statement_id):
    s = get_object_or_404(Statement, pk=statement_id)

    response = HttpResponse(s.file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=' + \
            os.path.basename(s.file.name)
    return response

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

        print renderingprovider

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

    if(len(renderingprovider)>0):
        matches = claim.filter(rendering_provider=renderingprovider[0])
        for renderingprovider in renderingprovider:
            matches = matches | claim.filter(rendering_provider=renderingprovider)
        claim = matches
        if(len(locationprovider)>0):
            matches2 = claim.filter(location_provider=locationprovider[0])
            for locationprovider in locationprovider:
                matches2 = matches2 | claim.filter(location_provider=locationprovider)
            claim =  matches2
    else:
        if(len(locationprovider)>0):
            matches2 = claim.filter(location_provider=locationprovider[0])
            for locationprovider in locationprovider:
                matches2 = matches2 | claim.filter(location_provider=locationprovider)
            claim =  matches2

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
    # if(renderingprovider is not None):
    #     loc_ref="Rendering Provider: "+str(renderingprovider.provider_name)
    # else:
    #     loc_ref="All Provider"
    # loc_ref=loc_ref+" - "
    # if(locationprovider is not None):
    #     loc_ref=loc_ref+"Location Provider: "+str(locationprovider.provider_name)
    # else:
    #     loc_ref=loc_ref+"All Location"
    loc_ref="All Location"
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

    if(len(renderingprovider)>0):
        matches = claim.filter(rendering_provider=renderingprovider[0])
        for renderingprovider in renderingprovider:
            matches = matches | claim.filter(rendering_provider=renderingprovider)
        claim = matches
        if(len(locationprovider)>0):
            matches2 = claim.filter(location_provider=locationprovider[0])
            for locationprovider in locationprovider:
                matches2 = matches2 | claim.filter(location_provider=locationprovider)
            claim =  matches2
    else:
        if(len(locationprovider)>0):
            matches2 = claim.filter(location_provider=locationprovider[0])
            for locationprovider in locationprovider:
                matches2 = matches2 | claim.filter(location_provider=locationprovider)
            claim =  matches2
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
