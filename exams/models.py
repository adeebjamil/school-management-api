import uuid
from django.db import models


class Exam(models.Model):
    EXAM_TYPE_CHOICES = (
        ('midterm', 'Mid-Term'),
        ('final', 'Final'),
        ('quarterly', 'Quarterly'),
        ('unit_test', 'Unit Test'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    class_name = models.CharField(max_length=50, blank=True, null=True)
    section = models.CharField(max_length=10, blank=True, null=True)
    academic_year = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exams'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['tenant', 'academic_year']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.academic_year})"


class ExamSubject(models.Model):
    """Subjects for each exam"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='subjects')
    subject_name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)
    max_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    exam_date = models.DateField()
    duration_minutes = models.IntegerField()
    
    class Meta:
        db_table = 'exam_subjects'
        ordering = ['exam_date']
    
    def __str__(self):
        return f"{self.exam.name} - {self.subject_name}"


class Result(models.Model):
    GRADE_CHOICES = (
        ('A+', 'A+'), ('A', 'A'), ('B+', 'B+'), ('B', 'B'),
        ('C+', 'C+'), ('C', 'C'), ('D', 'D'), ('F', 'Fail'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='results')
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'results'
        unique_together = ('student', 'exam_subject')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'student']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.exam_subject.subject_name} - {self.marks_obtained}"
    
    @property
    def percentage(self):
        return (self.marks_obtained / self.exam_subject.max_marks) * 100


class AdmitCard(models.Model):
    """Admit cards for students"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='admit_cards')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='admit_cards')
    admit_card_number = models.CharField(max_length=50, unique=True)
    issued_date = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'admit_cards'
        unique_together = ('student', 'exam')
        ordering = ['-issued_date']
    
    def __str__(self):
        return f"{self.student} - {self.exam.name} - {self.admit_card_number}"
