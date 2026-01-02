from django.urls import path
from . import views

urlpatterns = [
    path('mark/', views.mark_bulk_attendance, name='mark_bulk_attendance'),
    path('date/', views.get_attendance_by_date, name='get_attendance_by_date'),
    path('student/<str:student_id>/history/', views.get_student_attendance_history, name='get_student_attendance_history'),
    path('student/<str:student_id>/stats/', views.get_student_attendance_stats, name='get_student_attendance_stats'),
    path('class/stats/', views.get_class_attendance_stats, name='get_class_attendance_stats'),
]
