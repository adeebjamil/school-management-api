from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Parent
from .serializers import ParentSerializer, CreateParentSerializer, UpdateParentSerializer

User = get_user_model()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def parent_list_create(request):
    """
    GET: List all parents for the tenant
    POST: Create a new parent
    """
    tenant = request.tenant
    
    if request.method == 'GET':
        # Get query parameters for filtering
        search = request.query_params.get('search', '')
        relation = request.query_params.get('relation', '')
        is_active = request.query_params.get('is_active', '')
        
        # Get all parents for this tenant
        parents = Parent.objects.filter(tenant=tenant).select_related('user')
        
        # Apply filters
        if search:
            parents = parents.filter(
                user__first_name__icontains=search
            ) | parents.filter(
                user__last_name__icontains=search
            ) | parents.filter(
                user__email__icontains=search
            )
        
        if relation:
            parents = parents.filter(relation=relation)
        
        if is_active:
            parents = parents.filter(is_active=is_active.lower() == 'true')
        
        serializer = ParentSerializer(parents, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CreateParentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Check if user with email already exists
        if User.objects.filter(email=data['email']).exists():
            return Response(
                {'error': 'A user with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    email=data['email'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone=data.get('phone', ''),
                    role='parent',
                    tenant=tenant
                )
                
                # Create parent profile
                parent = Parent.objects.create(
                    tenant=tenant,
                    user=user,
                    relation=data['relation'],
                    occupation=data.get('occupation', ''),
                    address=data.get('address', ''),
                    city=data.get('city', ''),
                    state=data.get('state', ''),
                    pincode=data.get('pincode', ''),
                )
                
                serializer = ParentSerializer(parent)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def parent_detail(request, pk):
    """
    GET: Retrieve a parent
    PUT: Update a parent
    DELETE: Delete a parent
    """
    tenant = request.tenant
    
    try:
        parent = Parent.objects.select_related('user').get(pk=pk, tenant=tenant)
    except Parent.DoesNotExist:
        return Response(
            {'error': 'Parent not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = ParentSerializer(parent)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UpdateParentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with transaction.atomic():
                # Update user fields
                user = parent.user
                if 'first_name' in data:
                    user.first_name = data['first_name']
                if 'last_name' in data:
                    user.last_name = data['last_name']
                if 'phone' in data:
                    user.phone = data['phone']
                if 'is_active' in data:
                    user.is_active = data['is_active']
                user.save()
                
                # Update parent fields
                if 'relation' in data:
                    parent.relation = data['relation']
                if 'occupation' in data:
                    parent.occupation = data['occupation']
                if 'address' in data:
                    parent.address = data['address']
                if 'city' in data:
                    parent.city = data['city']
                if 'state' in data:
                    parent.state = data['state']
                if 'pincode' in data:
                    parent.pincode = data['pincode']
                parent.save()
                
                serializer = ParentSerializer(parent)
                return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'DELETE':
        try:
            with transaction.atomic():
                user = parent.user
                parent.delete()
                user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
