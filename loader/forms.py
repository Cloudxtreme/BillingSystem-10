from django import forms


class LoaderForm(forms.Form):
    file = forms.FileField(label="Select a valid data file")
