from rest_framework import serializers
from .models import TimeSlot, Timetable
from teachers.models import Teacher


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time', 'period_number', 'is_active']
        read_only_fields = ['id']


class TeacherBasicSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'employee_id']
    
    def get_name(self, obj):
        return obj.user.full_name if hasattr(obj.user, 'full_name') else f"{obj.user.first_name} {obj.user.last_name}"


class TimetableSerializer(serializers.ModelSerializer):
    teacher_details = TeacherBasicSerializer(source='teacher', read_only=True)
    time_slot_details = TimeSlotSerializer(source='time_slot', read_only=True)
    teacher_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    time_slot_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Timetable
        fields = [
            'id', 'class_name', 'section', 'day', 'subject', 
            'room_number', 'is_active', 'academic_year',
            'teacher_id', 'teacher_details',
            'time_slot_id', 'time_slot_details'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        teacher_id = validated_data.pop('teacher_id', None)
        time_slot_id = validated_data.pop('time_slot_id')
        
        teacher = None
        if teacher_id:
            teacher = Teacher.objects.get(id=teacher_id)
        
        time_slot = TimeSlot.objects.get(id=time_slot_id)
        
        timetable = Timetable.objects.create(
            teacher=teacher,
            time_slot=time_slot,
            **validated_data
        )
        return timetable
    
    def update(self, instance, validated_data):
        teacher_id = validated_data.pop('teacher_id', None)
        time_slot_id = validated_data.pop('time_slot_id', None)
        
        if teacher_id:
            instance.teacher = Teacher.objects.get(id=teacher_id)
        
        if time_slot_id:
            instance.time_slot = TimeSlot.objects.get(id=time_slot_id)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ClassTimetableSerializer(serializers.Serializer):
    """Serializer for class-wise timetable view"""
    day = serializers.CharField()
    periods = TimetableSerializer(many=True)


class TeacherTimetableSerializer(serializers.Serializer):
    """Serializer for teacher-wise timetable view"""
    day = serializers.CharField()
    periods = serializers.ListField()
