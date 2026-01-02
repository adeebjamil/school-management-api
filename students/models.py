import uuid
from django.db import models
from django.conf import settings


class Student(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='students')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    
    # Student Information
    admission_number = models.CharField(max_length=50, unique=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Personal Information
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    
    # Academic Information
    school_class = models.ForeignKey(
        'school_classes.SchoolClass',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text="Student's assigned class"
    )
    class_name = models.CharField(max_length=50)
    section = models.CharField(max_length=10, blank=True, null=True)
    admission_date = models.DateField()
    academic_year = models.CharField(max_length=20)
    
    # Contact Information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students'
        ordering = ['admission_number']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['class_name', 'section']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.admission_number})"


class AcademicRegistration(models.Model):
    """Track student's academic registration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='registrations')
    academic_year = models.CharField(max_length=20)
    class_name = models.CharField(max_length=50)
    section = models.CharField(max_length=10, blank=True, null=True)
    registration_date = models.DateField(auto_now_add=True)
    is_current = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'academic_registrations'
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.student} - {self.academic_year}"
