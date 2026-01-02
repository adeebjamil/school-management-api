from rest_framework import serializers
from .models import Student
from accounts.models import User
from accounts.serializers import UserSerializer


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ('id', 'tenant', 'user', 'created_at', 'updated_at')
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class CreateStudentSerializer(serializers.Serializer):
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    # Student fields - matching exactly with Student model
    admission_number = serializers.CharField(max_length=50)
    roll_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    date_of_birth = serializers.DateField()
    gender = serializers.ChoiceField(choices=['male', 'female', 'other'])
    blood_group = serializers.CharField(max_length=5, required=False, allow_blank=True)
    nationality = serializers.CharField(max_length=100, required=False, allow_blank=True)
    religion = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    # Academic fields
    class_name = serializers.CharField(max_length=50)
    section = serializers.CharField(max_length=10, required=False, allow_blank=True)
    admission_date = serializers.DateField()
    academic_year = serializers.CharField(max_length=20)
    
    # Contact fields
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    pincode = serializers.CharField(max_length=10, required=False, allow_blank=True)
    
    # Emergency contact
    emergency_contact_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    emergency_contact_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    emergency_contact_relation = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    # Status
    is_active = serializers.BooleanField(default=True)


class UpdateStudentSerializer(serializers.Serializer):
    # User fields
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    # Student fields
    roll_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=['male', 'female', 'other'], required=False)
    blood_group = serializers.CharField(max_length=5, required=False, allow_blank=True)
    nationality = serializers.CharField(max_length=100, required=False, allow_blank=True)
    religion = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    # Academic fields
    class_name = serializers.CharField(max_length=50, required=False)
    section = serializers.CharField(max_length=10, required=False, allow_blank=True)
    academic_year = serializers.CharField(max_length=20, required=False)
    school_class = serializers.UUIDField(required=False, allow_null=True)
    
    # Contact fields
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    pincode = serializers.CharField(max_length=10, required=False, allow_blank=True)
    
    # Emergency contact
    emergency_contact_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    emergency_contact_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    emergency_contact_relation = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    # Status
    is_active = serializers.BooleanField(required=False)
