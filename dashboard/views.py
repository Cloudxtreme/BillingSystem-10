from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dashboard.models import Notes
from django.http.response import HttpResponseBadRequest
from .forms import *

@login_required
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


def api_create_note(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        print form.errors
        if form.is_valid():
            print "123"
            cleaned_data = form.cleaned_data
            Notes.objects.create(
                    author=request.user,
                    **cleaned_data)
            return JsonResponse('', safe=False)

    return HttpResponseBadRequest('[]', content_type='application/json')