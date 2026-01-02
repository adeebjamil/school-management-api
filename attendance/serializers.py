from rest_framework import serializers
from .models import Attendance, TeacherAttendance
from students.serializers import StudentSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    marked_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ('id', 'tenant', 'marked_by', 'marked_at')
    
    def get_marked_by_name(self, obj):
        if obj.marked_by:
            return f"{obj.marked_by.first_name} {obj.marked_by.last_name}"
        return None


class BulkAttendanceSerializer(serializers.Serializer):
    date = serializers.DateField()
    attendance_records = serializers.ListField(
        child=serializers.DictField()
    )
    
    def validate_attendance_records(self, value):
        for record in value:
            if 'student_id' not in record or 'status' not in record:
                raise serializers.ValidationError(
                    "Each attendance record must have 'student_id' and 'status'"
                )
            if record['status'] not in ['present', 'absent', 'late', 'half_day']:
                raise serializers.ValidationError(
                    f"Invalid status: {record['status']}. Must be one of: present, absent, late, half_day"
                )
        return value


class AttendanceStatsSerializer(serializers.Serializer):
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    half_days = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()


class TeacherAttendanceSerializer(serializers.ModelSerializer):
    marked_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherAttendance
        fields = '__all__'
        read_only_fields = ('id', 'tenant', 'marked_by', 'marked_at')
    
    def get_marked_by_name(self, obj):
        if obj.marked_by:
            return f"{obj.marked_by.first_name} {obj.marked_by.last_name}"
        return None
