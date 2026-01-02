from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Tenant, TenantFeature
from .serializers import TenantSerializer, TenantFeatureSerializer, CreateTenantSerializer
from accounts.models import User
from accounts.serializers import UserSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tenant_list_create(request):
    """List all tenants or create a new one (Super Admin only)"""
    if request.user.role != 'super_admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        tenants = Tenant.objects.all()
        serializer = TenantSerializer(tenants, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CreateTenantSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        features = data.pop('features', [])
        
        # Create tenant
        tenant = Tenant.objects.create(**data)
        
        # Create features
        for feature in features:
            TenantFeature.objects.create(
                tenant=tenant,
                feature=feature,
                is_enabled=True
            )
        
        return Response({
            'message': 'Tenant created successfully',
            'tenant': TenantSerializer(tenant).data
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def tenant_detail(request, tenant_id):
    """Get, update, or delete a tenant (Super Admin only)"""
    if request.user.role != 'super_admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(TenantSerializer(tenant).data)
    
    elif request.method == 'PUT':
        serializer = TenantSerializer(tenant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        tenant.is_active = False
        tenant.save()
        return Response({'message': 'Tenant deactivated'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tenant_features(request, tenant_id):
    """Get features for a tenant"""
    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Allow Super Admin and Tenant Admin of this tenant
    if request.user.role not in ['super_admin', 'tenant_admin'] or \
       (request.user.role == 'tenant_admin' and str(request.user.tenant_id) != str(tenant_id)):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    features = TenantFeature.objects.filter(tenant=tenant)
    serializer = TenantFeatureSerializer(features, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_feature(request, tenant_id, feature):
    """Toggle a feature for a tenant (Super Admin only)"""
    if request.user.role != 'super_admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get or create feature
    tenant_feature, created = TenantFeature.objects.get_or_create(
        tenant=tenant,
        feature=feature,
        defaults={'is_enabled': True}
    )
    
    if not created:
        tenant_feature.is_enabled = not tenant_feature.is_enabled
        tenant_feature.save()
    
    return Response({
        'message': f'Feature {feature} {"enabled" if tenant_feature.is_enabled else "disabled"}',
        'feature': TenantFeatureSerializer(tenant_feature).data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_tenant_by_school_code(request):
    """Public endpoint to get tenant ID by school code (for login)"""
    school_code = request.query_params.get('school_code')
    
    if not school_code:
        return Response({'error': 'school_code parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        tenant = Tenant.objects.get(school_code=school_code, is_active=True)
        return Response({
            'tenant_id': str(tenant.id),
            'name': tenant.name,
            'school_code': tenant.school_code
        })
    except Tenant.DoesNotExist:
        return Response({'error': 'Invalid school code'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tenant_users(request, tenant_id):
    """Get all users for a specific tenant (Super Admin only)"""
    if request.user.role != 'super_admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get all users for this tenant
    users = User.objects.filter(tenant=tenant).order_by('-date_joined')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
