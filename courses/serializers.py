from rest_framework import serializers
from .models import Course, CourseModule, CourseContent, CourseEnrollment, ContentProgress
from school_classes.serializers import SchoolClassSerializer
from teachers.serializers import TeacherSerializer
from students.serializers import StudentSerializer


class CourseContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseContent
        fields = [
            'id', 'content_type', 'title', 'description', 'content',
            'file_url', 'video_url', 'external_link',
            'due_date', 'max_points', 'order', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseModuleSerializer(serializers.ModelSerializer):
    contents = CourseContentSerializer(many=True, read_only=True)
    total_contents = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseModule
        fields = [
            'id', 'module_number', 'title', 'description', 'learning_objectives',
            'start_date', 'end_date', 'duration_hours', 'order',
            'is_active', 'contents', 'total_contents',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_contents(self, obj):
        return obj.contents.count() if hasattr(obj, 'contents') else 0


class CourseSerializer(serializers.ModelSerializer):
    school_class_details = SchoolClassSerializer(source='school_class', read_only=True)
    primary_teacher_details = TeacherSerializer(source='primary_teacher', read_only=True)
    additional_teachers_details = TeacherSerializer(source='additional_teachers', many=True, read_only=True)
    modules = CourseModuleSerializer(many=True, read_only=True)
    total_modules = serializers.SerializerMethodField()
    enrolled_students_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'course_name', 'description',
            'school_class', 'school_class_details', 'section',
            'credits', 'duration_weeks', 'academic_year', 'semester',
            'primary_teacher', 'primary_teacher_details',
            'additional_teachers', 'additional_teachers_details',
            'syllabus', 'course_objectives', 'prerequisites',
            'is_active', 'is_published', 'modules', 'total_modules',
            'enrolled_students_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_modules(self, obj):
        # Use annotated value if available, otherwise count
        if hasattr(obj, 'modules_count'):
            return obj.modules_count
        return obj.modules.count() if hasattr(obj, 'modules') else 0
    
    def get_enrolled_students_count(self, obj):
        # Use annotated value if available, otherwise count
        if hasattr(obj, 'enrollments_count'):
            return obj.enrollments_count
        return obj.enrollments.filter(is_active=True).count() if hasattr(obj, 'enrollments') else 0


class CreateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'course_code', 'course_name', 'description',
            'school_class', 'section', 'credits', 'duration_weeks',
            'academic_year', 'semester', 'primary_teacher', 'additional_teachers',
            'syllabus', 'course_objectives', 'prerequisites',
            'is_active', 'is_published'
        ]


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    course_details = CourseSerializer(source='course', read_only=True)
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'student', 'student_details', 'course', 'course_details',
            'enrollment_date', 'completion_percentage', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'enrollment_date', 'created_at', 'updated_at']


class ContentProgressSerializer(serializers.ModelSerializer):
    content_details = CourseContentSerializer(source='content', read_only=True)
    
    class Meta:
        model = ContentProgress
        fields = [
            'id', 'content', 'content_details', 'is_completed', 'completed_at',
            'time_spent_minutes', 'score', 'submission_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BulkEnrollSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False
    )
