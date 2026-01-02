from rest_framework import serializers
from .models import Tenant, TenantFeature


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'email', 'phone', 'address', 'school_code',
                  'established_date', 'logo', 'is_active', 'created_at', 'subscription_start', 'subscription_end']
        read_only_fields = ['id', 'created_at', 'slug']


class TenantFeatureSerializer(serializers.ModelSerializer):
    feature_display = serializers.CharField(source='get_feature_display', read_only=True)
    
    class Meta:
        model = TenantFeature
        fields = ['id', 'tenant', 'feature', 'feature_display', 'is_enabled', 'enabled_at']
        read_only_fields = ['id', 'enabled_at']


class CreateTenantSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False)
    address = serializers.CharField(required=False)
    school_code = serializers.CharField(max_length=50)
    established_date = serializers.DateField(required=False)
    subscription_start = serializers.DateField(required=False)
    subscription_end = serializers.DateField(required=False)
    features = serializers.ListField(
        child=serializers.ChoiceField(choices=TenantFeature.FEATURE_CHOICES),
        required=False
    )
