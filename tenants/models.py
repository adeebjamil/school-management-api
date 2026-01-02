import uuid
from django.db import models
from django.utils.text import slugify


class Tenant(models.Model):
    """School/Organization tenant"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    
    # Contact Information
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # School Details
    school_code = models.CharField(max_length=50, unique=True)
    established_date = models.DateField(blank=True, null=True)
    logo = models.ImageField(upload_to='tenant_logos/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Subscription/Features
    subscription_start = models.DateField(blank=True, null=True)
    subscription_end = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'tenants'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class TenantFeature(models.Model):
    """Features/modules available to each tenant"""
    FEATURE_CHOICES = (
        ('attendance', 'Attendance Management'),
        ('exams', 'Exams & Results'),
        ('library', 'Library Management'),
        ('transport', 'Transport Management'),
        ('timetable', 'Timetable'),
        ('counseling', 'Counseling'),
        ('ai_assistant', 'AI Fine-Tuned Assistant'),
        ('courses', 'Course Management'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='features')
    feature = models.CharField(max_length=50, choices=FEATURE_CHOICES)
    is_enabled = models.BooleanField(default=True)
    enabled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tenant_features'
        unique_together = ('tenant', 'feature')
        ordering = ['tenant', 'feature']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.get_feature_display()}"
