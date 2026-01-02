from rest_framework import serializers
from .models import Teacher
from accounts.models import User
from accounts.serializers import UserSerializer


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Teacher
        fields = '__all__'
        read_only_fields = ('id', 'tenant', 'user', 'created_at', 'updated_at')
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class CreateTeacherSerializer(serializers.Serializer):
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    # Teacher fields
    employee_id = serializers.CharField(max_length=50)
    date_of_birth = serializers.DateField()
    gender = serializers.ChoiceField(choices=['male', 'female', 'other'])
    nationality = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    # Professional fields
    qualification = serializers.ChoiceField(choices=['bachelor', 'master', 'phd', 'diploma'])
    specialization = serializers.CharField(max_length=200, required=False, allow_blank=True)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    experience_years = serializers.IntegerField(default=0)
    joining_date = serializers.DateField()
    salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    subjects = serializers.CharField(required=False, allow_blank=True)
    
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


class UpdateTeacherSerializer(serializers.Serializer):
    # User fields
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    # Teacher fields
    date_of_birth = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=['male', 'female', 'other'], required=False)
    nationality = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    # Professional fields
    qualification = serializers.ChoiceField(choices=['bachelor', 'master', 'phd', 'diploma'], required=False)
    specialization = serializers.CharField(max_length=200, required=False, allow_blank=True)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    experience_years = serializers.IntegerField(required=False)
    salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    subjects = serializers.CharField(required=False, allow_blank=True)
    
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
