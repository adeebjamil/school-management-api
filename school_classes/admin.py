from django.contrib import admin
from .models import SchoolClass


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'grade', 'section', 'academic_year', 'class_teacher', 'tenant', 'get_student_count']
    list_filter = ['academic_year', 'grade', 'section', 'tenant']
    search_fields = ['class_name', 'grade', 'section', 'class_teacher__user__first_name', 'class_teacher__user__last_name']
    raw_id_fields = ['tenant', 'class_teacher']
    ordering = ['grade', 'section']
    
    def get_student_count(self, obj):
        return obj.student_count
    get_student_count.short_description = 'Students'
