import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Vehicle(models.Model):
    """School vehicles (buses, vans, etc.)"""
    VEHICLE_TYPES = [
        ('bus', 'Bus'),
        ('van', 'Van'),
        ('mini_bus', 'Mini Bus'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
        ('inactive', 'Inactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='bus')
    capacity = models.IntegerField()
    route = models.ForeignKey('Route', on_delete=models.SET_NULL, related_name='vehicles', null=True, blank=True)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20)
    driver_license = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transport_vehicles'
        ordering = ['vehicle_number']
        indexes = [
            models.Index(fields=['tenant', 'status']),
        ]
    
    def __str__(self):
        return f"{self.vehicle_type.title()} {self.vehicle_number}"
    
    @property
    def students_assigned(self):
        return self.transport_assignments.filter(is_active=True).count()


class Route(models.Model):
    """Bus routes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    route_number = models.CharField(max_length=50, blank=True, null=True)
    route_name = models.CharField(max_length=200)
    stops = models.JSONField(help_text="List of stops with timings", default=list)
    pickup_time = models.TimeField(blank=True, null=True)
    drop_time = models.TimeField(blank=True, null=True)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transport_routes'
        ordering = ['route_name']
    
    def __str__(self):
        return f"{self.route_number} - {self.route_name}" if self.route_number else self.route_name


class TransportAssignment(models.Model):
    """Assign students/teachers to transport"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('inactive', 'Inactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='transport_assignments')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='transport_assignments')
    
    # Generic foreign key for student or teacher
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    user = GenericForeignKey('content_type', 'object_id')
    
    pickup_point = models.CharField(max_length=200)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    effective_from = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transport_assignments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user} -> {self.vehicle}"


# Keep old models for backward compatibility
class Bus(models.Model):
    """School buses (Legacy - use Vehicle model instead)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    bus_number = models.CharField(max_length=50)
    registration_number = models.CharField(max_length=50, unique=True)
    capacity = models.IntegerField()
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20)
    driver_license = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transport_buses'
        ordering = ['bus_number']
    
    def __str__(self):
        return f"Bus {self.bus_number} ({self.registration_number})"


class BusAssignment(models.Model):
    """Assign students to buses (Legacy - use TransportAssignment instead)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='bus_assignments')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='student_assignments')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='student_assignments', null=True)
    pickup_point = models.CharField(max_length=200)
    drop_point = models.CharField(max_length=200)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    assigned_date = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'transport_bus_assignments'
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.student} -> Bus {self.bus.bus_number}"
