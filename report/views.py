from django.shortcuts import *
from django.db.models import Q
from django.utils import timezone

from datetime import datetime, timedelta
from decimal import *

from infoGatherer.models import *
from accounting.models import *


from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dashboard.models import Notes
from django.http.response import HttpResponseBadRequest
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers
import xlwt
from xlwt import Workbook
import time
from datetime import date



def statment_create(request):
    patient_id = request.GET.get("patient")
    patient = get_object_or_404(Personal_Information, pk=patient_id)

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
        "claims": patient.patient.all(),
        "aging": aging,
        "today": today,
    })

def index(request):
    return render(request, "report/statement.html")


def TransactionReport(request):
    # Writing into excel workbook

    wb = Workbook()
    sheet1 = wb.add_sheet('Transaction Report')

    # Set wedth of columns
    sheet1.col(0).width = 1000
    sheet1.col(1).width = 5000
    sheet1.col(2).width = 2500
    sheet1.col(3).width = 5000
    sheet1.col(4).width = 5000
    sheet1.col(5).width = 8000
    sheet1.col(6).width = 5000
    sheet1.col(7).width = 5000

    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = True
    font.height = 240
    style.font = font
    sheet1.write(0, 0, label = 'Transaction Report', style = style)

    sheet1.write(0, 7, label = 'Report Date:')
    sheet1.write(1, 7, label = 'Date Span:')

    style1 = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Verdana'
    font.bold = True
    font.height = 160
    style1.font = font
    sheet1.write(4, 1, label = 'Patient', style=style1)
    sheet1.write(4, 2, label = 'Chart No', style=style1)
    sheet1.write(4, 3, label = 'Provider', style=style1)
    sheet1.write(4, 4, label = 'Code [Modifiers]', style=style1)
    sheet1.write(4, 5, label = 'Procedure Code Description', style=style1)
    sheet1.write(4, 6, label = 'DOS', style=style1)
    sheet1.write(4, 7, label = 'Created Date', style=style1)
    sheet1.write(4, 8, label = 'Units', style=style1)
    sheet1.write(4, 9, label = 'Charges', style=style1)

    # filtering the information!

    from_dos = datetime.date(2016, 04, 1)
    to_dos = datetime.date(2007, 04, 12)

    claim=Claim.objects.filter(created__gte(from_dos),created__lte(to_dos))


    # saving the report
    wb.save('xlwt_example.xls')
    return HttpResponse("<html>This is transaction reports!</html>")
