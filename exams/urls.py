from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list_create, name='exam_list_create'),
    path('<str:exam_id>/', views.exam_detail, name='exam_detail'),
    path('<str:exam_id>/subjects/', views.exam_subjects, name='exam_subjects'),
    path('marks/entry/', views.mark_entry, name='mark_entry'),
    path('results/student/<str:student_id>/', views.student_results, name='student_results'),
    path('results/exam/<str:exam_id>/', views.exam_results, name='exam_results'),
]
