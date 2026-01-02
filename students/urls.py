from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list_create, name='student_list_create'),
    path('profile/', views.student_profile, name='student_profile'),
    path('<uuid:student_id>/', views.student_detail, name='student_detail'),
]
