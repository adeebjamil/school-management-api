import uuid
from django.db import models


class SchoolClass(models.Model):
    """Model for school classes/grades"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='school_classes')
    
    # Class Information
    grade = models.CharField(max_length=10, help_text="e.g., 8, 9, 10")
    section = models.CharField(max_length=10, help_text="e.g., A, B, C")
    class_name = models.CharField(max_length=100, help_text="e.g., Grade 8-A")
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    
    # Class Teacher Assignment
    class_teacher = models.ForeignKey(
        'teachers.Teacher', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_classes',
        help_text="Class teacher will automatically become counselor for all students in this class"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'school_classes'
        verbose_name = 'School Class'
        verbose_name_plural = 'School Classes'
        unique_together = ['tenant', 'grade', 'section', 'academic_year']
        ordering = ['grade', 'section']
    
    def __str__(self):
        return f"{self.class_name} ({self.academic_year})"
    
    @property
    def student_count(self):
        """Get the count of students in this class"""
        return self.students.count()
    
    def save(self, *args, **kwargs):
        # Auto-generate class_name if not provided
        if not self.class_name:
            self.class_name = f"Grade {self.grade}-{self.section}"
        super().save(*args, **kwargs)
