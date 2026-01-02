from rest_framework import serializers
from .models import Exam, ExamSubject, Result, AdmitCard


class ExamSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSubject
        fields = '__all__'
        read_only_fields = ('id', 'tenant')


class ExamSerializer(serializers.ModelSerializer):
    subjects = ExamSubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ('id', 'tenant', 'created_at', 'updated_at')


class CreateExamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    exam_type = serializers.ChoiceField(choices=['midterm', 'final', 'unit_test', 'quarterly', 'annual'])
    class_name = serializers.CharField(max_length=50)
    section = serializers.CharField(max_length=10)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_marks = serializers.IntegerField(required=False)
    passing_marks = serializers.IntegerField(required=False)
    subjects = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
    
    def validate_subjects(self, value):
        for subject in value:
            required_fields = ['subject_name', 'subject_code', 'exam_date', 'max_marks', 'passing_marks', 'duration_minutes']
            for field in required_fields:
                if field not in subject:
                    raise serializers.ValidationError(f"Subject missing required field: {field}")
        return value
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before end date")
        return data


class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    exam_name = serializers.SerializerMethodField()
    max_marks = serializers.SerializerMethodField()
    passing_marks = serializers.SerializerMethodField()
    
    class Meta:
        model = Result
        fields = '__all__'
        read_only_fields = ('id', 'tenant', 'created_at', 'updated_at')
    
    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"
    
    def get_subject_name(self, obj):
        return obj.exam_subject.subject_name
    
    def get_exam_name(self, obj):
        return obj.exam_subject.exam.name
    
    def get_max_marks(self, obj):
        return obj.exam_subject.max_marks
    
    def get_passing_marks(self, obj):
        return obj.exam_subject.passing_marks


class AdmitCardSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    exam_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AdmitCard
        fields = '__all__'
        read_only_fields = ('id', 'tenant', 'issued_date')
    
    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"
    
    def get_exam_name(self, obj):
        return obj.exam.name
