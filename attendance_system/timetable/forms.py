# timetable/forms.py
from django import forms
from .models import TimeTable


class TimeTableUploadForm(forms.ModelForm):
    class Meta:
        model = TimeTable
        fields = ['name', 'csv_file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'csv_file': forms.FileInput(attrs={'class': 'form-control'})
        }


