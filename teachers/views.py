from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from .models import Teacher
from .serializers import TeacherSerializer, CreateTeacherSerializer, UpdateTeacherSerializer
from accounts.models import User


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def teacher_list_create(request):
    """List all teachers or create a new one (Tenant Admin only)"""
    tenant_id = getattr(request, 'tenant_id', None)
    
    if not tenant_id:
        return Response({'error': 'Tenant context required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.user.role not in ['super_admin', 'tenant_admin']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        teachers = Teacher.objects.filter(tenant_id=tenant_id).select_related('user')
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CreateTeacherSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if employee ID already exists
        if Teacher.objects.filter(employee_id=data['employee_id']).exists():
            return Response({'error': 'Employee ID already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Create user account
                user = User.objects.create_user(
                    email=data['email'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone=data.get('phone', ''),
                    role='teacher',
                    tenant_id=tenant_id,
                    is_active=data.get('is_active', True)
                )
                
                # Create teacher profile
                teacher = Teacher.objects.create(
                    tenant_id=tenant_id,
                    user=user,
                    employee_id=data['employee_id'],
                    date_of_birth=data['date_of_birth'],
                    gender=data['gender'],
                    nationality=data.get('nationality', ''),
                    qualification=data['qualification'],
                    specialization=data.get('specialization', ''),
                    department=data.get('department', ''),
                    experience_years=data.get('experience_years', 0),
                    joining_date=data['joining_date'],
                    salary=data.get('salary'),
                    subjects=data.get('subjects', ''),
                    address=data.get('address', ''),
                    city=data.get('city', ''),
                    state=data.get('state', ''),
                    pincode=data.get('pincode', ''),
                    emergency_contact_name=data.get('emergency_contact_name', ''),
                    emergency_contact_phone=data.get('emergency_contact_phone', ''),
                    emergency_contact_relation=data.get('emergency_contact_relation', '')
                )
                
                return Response({
                    'message': 'Teacher created successfully',
                    'teacher': TeacherSerializer(teacher).data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def teacher_detail(request, teacher_id):
    """Get, update, or delete a teacher"""
    tenant_id = getattr(request, 'tenant_id', None)
    
    if not tenant_id:
        return Response({'error': 'Tenant context required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        teacher = Teacher.objects.select_related('user').get(id=teacher_id, tenant_id=tenant_id)
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = TeacherSerializer(teacher)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if request.user.role not in ['super_admin', 'tenant_admin']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UpdateTeacherSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with transaction.atomic():
                # Update user fields
                user = teacher.user
                if 'first_name' in data:
                    user.first_name = data['first_name']
                if 'last_name' in data:
                    user.last_name = data['last_name']
                if 'phone' in data:
                    user.phone = data['phone']
                if 'is_active' in data:
                    user.is_active = data['is_active']
                user.save()
                
                # Update teacher fields
                for field, value in data.items():
                    if field not in ['first_name', 'last_name', 'phone', 'is_active']:
                        setattr(teacher, field, value)
                teacher.save()
                
                return Response({
                    'message': 'Teacher updated successfully',
                    'teacher': TeacherSerializer(teacher).data
                })
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if request.user.role not in ['super_admin', 'tenant_admin']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            with transaction.atomic():
                teacher.user.delete()  # Cascade will delete teacher profile
                return Response({'message': 'Teacher deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_profile(request):
    """Get current teacher's profile"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        teacher = Teacher.objects.select_related('user').get(user=request.user)
        return Response(TeacherSerializer(teacher).data)
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher profile not found'}, status=status.HTTP_404_NOT_FOUND)
