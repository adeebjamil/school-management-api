from django.urls import path
from . import views

urlpatterns = [
    # Course management
    path('', views.course_list_create, name='course_list_create'),
    path('<uuid:course_id>/', views.course_detail, name='course_detail'),
    path('<uuid:course_id>/auto-enroll/', views.auto_enroll_by_class, name='auto_enroll_by_class'),
    
    # Module management
    path('<uuid:course_id>/modules/', views.module_list_create, name='module_list_create'),
    path('<uuid:course_id>/modules/<uuid:module_id>/', views.module_detail, name='module_detail'),
    
    # Content management
    path('<uuid:course_id>/modules/<uuid:module_id>/contents/', views.content_list_create, name='content_list_create'),
    path('<uuid:course_id>/modules/<uuid:module_id>/contents/<uuid:content_id>/', views.content_detail, name='content_detail'),
    
    # Enrollment management
    path('<uuid:course_id>/enrollments/', views.enrollment_list_create, name='enrollment_list_create'),
    path('bulk-enroll/', views.bulk_enroll, name='bulk_enroll'),
    
    # User-specific views
    path('my/courses/', views.my_courses, name='my_courses'),
]
