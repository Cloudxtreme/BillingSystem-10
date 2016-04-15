from django import forms
from dashboard.models import Notes
from base.models import BASE_DECIMAL


class NotesForm(forms.ModelForm):

    class Meta:
        model = Notes
        exclude = [ 'created', 'modified', 'author' ]