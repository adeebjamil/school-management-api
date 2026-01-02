from django.contrib import admin
from .models import Tenant, TenantFeature


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'email', 'school_code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'school_code']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TenantFeature)
class TenantFeatureAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'feature', 'is_enabled', 'enabled_at']
    list_filter = ['feature', 'is_enabled', 'tenant']
