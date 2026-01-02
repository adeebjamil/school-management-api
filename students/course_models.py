import uuid
from django.db import models


class Course(models.Model):
    """Courses/Subjects offered"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    course_code = models.CharField(max_length=50)
    course_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    class_name = models.CharField(max_length=50)
    credits = models.IntegerField(default=0)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, related_name='courses')
    academic_year = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['course_code']
        unique_together = ('tenant', 'course_code', 'academic_year')
        indexes = [
            models.Index(fields=['tenant', 'class_name']),
        ]
    
    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class CourseEnrollment(models.Model):
    """Track student enrollments in courses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'course_enrollments'
        unique_together = ('student', 'course')
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student} enrolled in {self.course}"
