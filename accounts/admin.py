from django.contrib import admin
from .models import User, SuperAdminSession, TenantAdminCreationLog, AuditLog, PasswordResetOTP


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'role', 'tenant', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'tenant']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']


@admin.register(SuperAdminSession)
class SuperAdminSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'login_time', 'logout_time', 'is_active']
    list_filter = ['is_active', 'login_time']
    ordering = ['-login_time']


@admin.register(TenantAdminCreationLog)
class TenantAdminCreationLogAdmin(admin.ModelAdmin):
    list_display = ['super_admin', 'tenant_admin', 'tenant', 'ip_address', 'created_at']
    list_filter = ['tenant', 'created_at']
    ordering = ['-created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'tenant', 'ip_address', 'timestamp']
    list_filter = ['action', 'model_name', 'tenant', 'timestamp']
    search_fields = ['user__email', 'description']
    ordering = ['-timestamp']


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp', 'created_at', 'expires_at', 'is_used', 'ip_address']
    list_filter = ['is_used', 'created_at']
    search_fields = ['email', 'otp']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'expires_at']

