from django.contrib import admin
from .models import Course, CourseModule, CourseContent, CourseEnrollment, ContentProgress


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'course_name', 'school_class', 'section', 'primary_teacher', 'academic_year', 'semester', 'is_published', 'is_active']
    list_filter = ['is_active', 'is_published', 'academic_year', 'semester', 'school_class']
    search_fields = ['course_code', 'course_name', 'description']
    filter_horizontal = ['additional_teachers']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ['module_number', 'title', 'course', 'order', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'course']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'module', 'order', 'is_published', 'due_date']
    list_filter = ['content_type', 'is_published', 'module__course']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrollment_date', 'completion_percentage', 'is_active']
    list_filter = ['is_active', 'enrollment_date', 'course']
    search_fields = ['student__user__email', 'course__course_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ContentProgress)
class ContentProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'content', 'is_completed', 'completed_at', 'score']
    list_filter = ['is_completed', 'content__content_type']
    search_fields = ['student__user__email', 'content__title']
    readonly_fields = ['created_at', 'updated_at']
