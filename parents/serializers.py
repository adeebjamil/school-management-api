from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Parent

User = get_user_model()


class ParentSerializer(serializers.ModelSerializer):
    """Serializer for reading parent data with nested user"""
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Parent
        fields = [
            'id', 'tenant', 'user', 'relation', 'occupation',
            'address', 'city', 'state', 'pincode',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        return {
            'id': str(obj.user.id),
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'phone': obj.user.phone,
            'is_active': obj.user.is_active,
        }


class CreateParentSerializer(serializers.Serializer):
    """Serializer for creating a new parent"""
    # User fields
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    # Parent fields
    relation = serializers.ChoiceField(choices=['father', 'mother', 'guardian'])
    occupation = serializers.CharField(max_length=200, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    pincode = serializers.CharField(max_length=10, required=False, allow_blank=True)


class UpdateParentSerializer(serializers.Serializer):
    """Serializer for updating parent data"""
    # User fields
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
    
    # Parent fields
    relation = serializers.ChoiceField(choices=['father', 'mother', 'guardian'], required=False)
    occupation = serializers.CharField(max_length=200, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    pincode = serializers.CharField(max_length=10, required=False, allow_blank=True)
