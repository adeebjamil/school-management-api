import uuid
from django.db import models
from django.conf import settings


class Parent(models.Model):
    RELATION_CHOICES = (
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='parents')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_profile')
    
    # Parent Information
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES)
    occupation = models.CharField(max_length=200, blank=True, null=True)
    
    # Contact Information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parents'
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.get_relation_display()})"


class StudentParent(models.Model):
    """Link students to their parents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='parent_links')
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='student_links')
    is_primary = models.BooleanField(default=False)  # Primary parent/guardian
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_parents'
        unique_together = ('student', 'parent')
        ordering = ['-is_primary']
    
    def __str__(self):
        return f"{self.student} -> {self.parent}"
