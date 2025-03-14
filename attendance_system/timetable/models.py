from django.db import models

# `from django.db import models` is a Python import statement that imports the `models` module from
# the `django.db` package. This statement is commonly used in Django projects to define database
# models using Django's Object-Relational Mapping (ORM) system. The `models` module provides classes
# and functions that allow developers to define database tables and their fields as Python classes.
# Create your models here.

class TimeTable(models.Model):
    name = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to='timetables/')
    
    def __str__(self):
        return self.name

class AttendanceSession(models.Model):
    day = models.CharField(max_length=10)
    time_slot = models.CharField(max_length=20)
    class_name = models.CharField(max_length=100)
    display_number = models.IntegerField(null=True, blank=True)
    session_date = models.DateField(auto_now_add=True)
    duration = models.IntegerField(choices=[(1, '1 minute'), (3, '3 minutes')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.day} - {self.time_slot} - {self.class_name}"