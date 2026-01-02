from rest_framework import serializers
from .models import StudentParent, Parent
from students.models import Student


class StudentParentSerializer(serializers.ModelSerializer):
    """Serializer for student-parent relationships"""
    student_name = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    student_details = serializers.SerializerMethodField()
    parent_details = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentParent
        fields = [
            'id', 'tenant', 'student', 'parent', 'is_primary',
            'student_name', 'parent_name', 'student_details', 'parent_details',
            'created_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_at']
    
    def get_student_name(self, obj):
        return obj.student.user.full_name
    
    def get_parent_name(self, obj):
        return obj.parent.user.full_name
    
    def get_student_details(self, obj):
        return {
            'id': str(obj.student.id),
            'admission_number': obj.student.admission_number,
            'class_name': obj.student.class_name,
            'section': obj.student.section,
            'roll_number': obj.student.roll_number,
        }
    
    def get_parent_details(self, obj):
        return {
            'id': str(obj.parent.id),
            'relation': obj.parent.relation,
            'email': obj.parent.user.email,
            'phone': obj.parent.user.phone,
        }


class LinkStudentParentSerializer(serializers.Serializer):
    """Serializer for linking a student to a parent"""
    student_id = serializers.UUIDField()
    parent_id = serializers.UUIDField()
    is_primary = serializers.BooleanField(default=False)


class ParentChildrenSerializer(serializers.Serializer):
    """Serializer for parent's children list"""
    id = serializers.UUIDField()
    admission_number = serializers.CharField()
    roll_number = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    class_name = serializers.CharField()
    section = serializers.CharField()
    is_primary = serializers.BooleanField()
