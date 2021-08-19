from django import forms
from .models import File

class FileUploadForm(forms.Form):
    # owner = forms.CharField(max_length=1000)
    path = forms.CharField(max_length=1000)
    docfile = forms.FileField(
         label='Select a file',
         help_text='max. 42 megabytes')
    sha256 = forms.CharField(max_length=1000)



class FileDownloadForm(forms.Form):
    # owner = forms.CharField(max_length=1000)
    path = forms.CharField(max_length=1000)
    # docfile = forms.FileField(
    #      label='Select a file',
    #      help_text='max. 42 megabytes')
    # sha256 = forms.CharField(max_length=1000)