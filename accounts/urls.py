from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints
    path('super-admin/login/', views.super_admin_login, name='super_admin_login'),
    path('login/', views.tenant_login, name='tenant_login'),
    path('logout/', views.logout, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password management
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # User profile
    path('profile/', views.get_profile, name='get_profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Super Admin operations
    path('tenant-admin/create/', views.create_tenant_admin, name='create_tenant_admin'),
    path('admin-sessions/', views.admin_sessions, name='admin_sessions'),
    path('tenant-admin-logs/', views.tenant_admin_logs, name='tenant_admin_logs'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
]

