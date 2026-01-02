from rest_framework import serializers
from .models import SchoolClass
from teachers.models import Teacher


class TeacherBasicSerializer(serializers.ModelSerializer):
    """Basic teacher information for class assignments"""
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'email', 'employee_id', 'department']


class SchoolClassSerializer(serializers.ModelSerializer):
    """Serializer for SchoolClass model"""
    class_teacher_details = TeacherBasicSerializer(source='class_teacher', read_only=True)
    class_teacher_id = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)
    
    class Meta:
        model = SchoolClass
        fields = [
            'id',
            'tenant_id',
            'grade',
            'section',
            'class_name',
            'academic_year',
            'class_teacher',
            'class_teacher_id',
            'class_teacher_details',
            'student_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'tenant_id', 'student_count', 'created_at', 'updated_at']
        extra_kwargs = {
            'class_teacher': {'write_only': True}
        }
    
    def get_student_count(self, obj):
        """Get the count of students in this class"""
        return obj.student_count
    
    def get_class_teacher_id(self, obj):
        """Get the class teacher ID if exists"""
        if hasattr(obj, 'class_teacher') and obj.class_teacher:
            return str(obj.class_teacher.id)
        return None
    
    def validate(self, data):
        """Validate class data"""
        # Check if grade and section are provided
        if 'grade' not in data or 'section' not in data:
            raise serializers.ValidationError("Grade and Section are required")
        
        return data
    
    def create(self, validated_data):
        """Create a new school class"""
        # Get tenant from request context
        request = self.context.get('request')
        
        if request and request.user.tenant:
            validated_data['tenant'] = request.user.tenant
        else:
            raise serializers.ValidationError({"error": "User is not associated with any tenant"})
        
        # Handle class_teacher if provided (can be UUID string or Teacher object)
        class_teacher_data = validated_data.pop('class_teacher', None)
        if class_teacher_data:
            if isinstance(class_teacher_data, str):
                # It's a UUID string
                try:
                    teacher = Teacher.objects.get(id=class_teacher_data)
                    validated_data['class_teacher'] = teacher
                except Teacher.DoesNotExist:
                    raise serializers.ValidationError({"class_teacher": "Teacher not found"})
            elif isinstance(class_teacher_data, Teacher):
                # It's already a Teacher object
                validated_data['class_teacher'] = class_teacher_data
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update school class"""
        # Handle class_teacher if provided (can be UUID string or Teacher object)
        class_teacher_data = validated_data.pop('class_teacher', None)
        if class_teacher_data:
            if isinstance(class_teacher_data, str):
                # It's a UUID string
                try:
                    teacher = Teacher.objects.get(id=class_teacher_data)
                    validated_data['class_teacher'] = teacher
                except Teacher.DoesNotExist:
                    raise serializers.ValidationError({"class_teacher": "Teacher not found"})
            elif isinstance(class_teacher_data, Teacher):
                # It's already a Teacher object
                validated_data['class_teacher'] = class_teacher_data
        elif 'class_teacher' in validated_data and validated_data['class_teacher'] is None:
            # Allow removing class teacher
            validated_data['class_teacher'] = None
        
        return super().update(instance, validated_data)


class SchoolClassListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing classes"""
    class_teacher_name = serializers.SerializerMethodField()
    student_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = SchoolClass
        fields = [
            'id',
            'grade',
            'section',
            'class_name',
            'academic_year',
            'class_teacher',
            'class_teacher_name',
            'student_count',
        ]
    
    def get_class_teacher_name(self, obj):
        """Get full name of class teacher"""
        if obj.class_teacher and obj.class_teacher.user:
            return f"{obj.class_teacher.user.first_name} {obj.class_teacher.user.last_name}"
        return None
