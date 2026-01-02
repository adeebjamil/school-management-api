from django.contrib import admin
from .models import Vehicle, Route, TransportAssignment, Bus, BusAssignment


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'vehicle_type', 'capacity', 'driver_name', 'status', 'monthly_fee', 'tenant']
    list_filter = ['vehicle_type', 'status', 'tenant']
    search_fields = ['vehicle_number', 'driver_name', 'driver_phone']
    readonly_fields = ['id', 'created_at', 'updated_at', 'students_assigned']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['route_number', 'route_name', 'pickup_time', 'drop_time', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['route_number', 'route_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(TransportAssignment)
class TransportAssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'vehicle', 'route', 'pickup_point', 'monthly_fee', 'status', 'is_active', 'tenant']
    list_filter = ['status', 'is_active', 'content_type', 'tenant']
    search_fields = ['pickup_point']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def user(self, obj):
        return str(obj.user)
    user.short_description = 'User'


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ['bus_number', 'registration_number', 'capacity', 'driver_name', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['bus_number', 'registration_number', 'driver_name']


@admin.register(BusAssignment)
class BusAssignmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'bus', 'route', 'pickup_point', 'fee_amount', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['student__user__first_name', 'student__user__last_name']
