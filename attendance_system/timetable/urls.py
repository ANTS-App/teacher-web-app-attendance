# timetable/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_timetable, name='upload_timetable'),
    path('display/', views.display_timetable, name='display_timetable'),
    path('select-class/<str:day>/<int:time_slot_index>/', views.select_class, name='select_class'),
    path('start-attendance/<str:day>/<str:time_slot>/<str:class_name>/<int:duration>/', 
         views.start_attendance, name='start_attendance'),
    path('end-attendance/<str:timestamp>/', views.end_attendance, name='end_attendance'),
    path('archives/', views.attendance_archives, name='attendance_archives'),
    path('test-firebase/', views.test_firebase, name='test_firebase'),
]
