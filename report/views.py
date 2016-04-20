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

# from django.http import JsonResponse


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