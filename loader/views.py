from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import render

from .forms import *

from win32com import client
import pythoncom
import os


@login_required
def loader_read(request):
    form = LoaderForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            # Copy uploaded file to temp folder
            # Create the folder if it doesn't exist
            temp_dir = os.path.join(
                    settings.BASE_DIR,
                    "temp",
                    str(request.user.pk))
            try:
                os.mkdir(temp_dir)
            except:
                pass

            # Set temp file path
            file_path = os.path.join(
                    temp_dir,
                    request.FILES["file"].name)
            fout = open(file_path, "wb+")

            # Copy uploaded file into temp one
            file_content = ContentFile(request.FILES['file'].read())
            for chunk in file_content.chunks():
                fout.write(chunk)
            fout.close()

            # Execute loader
            loader_execute(file_path)

            # Delete temp file after loading
            os.remove(file_path)

    return render(request, "loader/read.html", {
            "form": form})

def loader_execute(file_path):
    pythoncom.CoInitialize()

    try:
        excel = client.DispatchEx("Excel.Application")
        excel.ScreenUpdating = False
        wb = excel.Workbooks.Open(file_path)
        for ws in wb.Worksheets:
            print ws.Name

    except Exception, e:
        print "An error occurs during loading initial data"
        print e
    finally:
        if wb is not None:
            wb.Close(False)

    pythoncom.CoUninitialize()
