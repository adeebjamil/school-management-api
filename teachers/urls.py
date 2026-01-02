from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_list_create, name='teacher-list-create'),
    path('profile/', views.teacher_profile, name='teacher-profile'),
    path('<uuid:teacher_id>/', views.teacher_detail, name='teacher-detail'),
]
