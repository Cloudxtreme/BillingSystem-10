from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dashboard.models import Notes
from django.http.response import HttpResponseBadRequest
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import *
from django.core import serializers

@login_required
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def api_create_note(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        print form.errors
        if form.is_valid():
            cleaned_data = form.cleaned_data
            print cleaned_data
            Notes.objects.create(
                    author=request.user,
                    **cleaned_data)
            return JsonResponse('', safe=False)

    if request.method == 'GET' and 'get' in request.GET :
        notes = Notes.objects.all();
        n = serializers.serialize('python', notes, use_natural_foreign_keys=True)
        s = dict(notes=n)
        return JsonResponse(data=s, safe=False)

    return HttpResponseBadRequest('[]', content_type='application/json')

def api_delete_note(request):
    if request.method == 'POST':
        Notes.objects.all().delete();
        return JsonResponse('', safe=False)
    return HttpResponseBadRequest('[]', content_type='application/json')