import uuid
from django.db import models


class Course(models.Model):
    """Complete courses with modules and content"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='courses')
    
    # Basic Information
    course_code = models.CharField(max_length=50)
    course_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Class and Section Assignment
    school_class = models.ForeignKey('school_classes.SchoolClass', on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    section = models.CharField(max_length=10, blank=True, null=True, help_text="e.g., A, B, C")
    
    # Course Details
    credits = models.IntegerField(default=0)
    duration_weeks = models.IntegerField(default=16, help_text="Course duration in weeks")
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=20, choices=[
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('summer', 'Summer'),
        ('annual', 'Annual'),
    ], default='1')
    
    # Teacher Assignment
    primary_teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_courses')
    additional_teachers = models.ManyToManyField('teachers.Teacher', blank=True, related_name='additional_courses')
    
    # Course Materials
    syllabus = models.TextField(blank=True, null=True)
    course_objectives = models.TextField(blank=True, null=True)
    prerequisites = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='courses_created')
    
    class Meta:
        db_table = 'courses'
        ordering = ['course_code']
        unique_together = ('tenant', 'course_code', 'academic_year', 'semester')
        indexes = [
            models.Index(fields=['tenant', 'school_class', 'section']),
            models.Index(fields=['tenant', 'academic_year', 'semester']),
        ]
    
    def __str__(self):
        return f"{self.course_code} - {self.course_name}"
    
    @property
    def total_modules(self):
        return self.modules.count()
    
    @property
    def enrolled_students_count(self):
        return self.enrollments.filter(is_active=True).count()


class CourseModule(models.Model):
    """Modules/Units within a course"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    
    module_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    learning_objectives = models.TextField(blank=True, null=True)
    
    # Scheduling
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration_hours = models.IntegerField(default=0, help_text="Estimated hours to complete")
    
    # Order
    order = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_modules'
        ordering = ['course', 'order', 'module_number']
        unique_together = ('course', 'module_number')
    
    def __str__(self):
        return f"Module {self.module_number}: {self.title}"
    
    @property
    def total_contents(self):
        return self.contents.count()


class CourseContent(models.Model):
    """Content items within a module (lessons, assignments, resources)"""
    CONTENT_TYPES = [
        ('lesson', 'Lesson'),
        ('assignment', 'Assignment'),
        ('quiz', 'Quiz'),
        ('resource', 'Resource'),
        ('video', 'Video'),
        ('reading', 'Reading Material'),
        ('lab', 'Lab/Practical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='contents')
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True, help_text="Main content or instructions")
    
    # Resources
    file_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    
    # Assignment/Quiz specific
    due_date = models.DateTimeField(null=True, blank=True)
    max_points = models.IntegerField(default=0)
    
    # Order and visibility
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_contents'
        ordering = ['module', 'order']
    
    def __str__(self):
        return f"{self.get_content_type_display()}: {self.title}"


class CourseEnrollment(models.Model):
    """Track student enrollments in courses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    enrollment_date = models.DateField(auto_now_add=True)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_enrollments'
        unique_together = ('student', 'course')
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


class ContentProgress(models.Model):
    """Track student progress on individual content items"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='content_progress')
    content = models.ForeignKey(CourseContent, on_delete=models.CASCADE, related_name='student_progress')
    
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.IntegerField(default=0)
    
    # For assignments/quizzes
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    submission_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_progress'
        unique_together = ('student', 'content')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.student} - {self.content.title}"
