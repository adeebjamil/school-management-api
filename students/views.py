from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from datetime import datetime

from .models import Student, AcademicRegistration
from .serializers import StudentSerializer, CreateStudentSerializer, UpdateStudentSerializer
from accounts.models import User
from parents.models import Parent


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def student_list_create(request):
    """List all students or create a new one"""
    tenant_id = getattr(request, 'tenant_id', None)
    
    if not tenant_id:
        return Response({'error': 'Tenant context required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        # Teachers and admins can view students
        if request.user.role not in ['super_admin', 'tenant_admin', 'teacher']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        students = Student.objects.filter(tenant_id=tenant_id).select_related('user')
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Only admins can create students
        if request.user.role not in ['super_admin', 'tenant_admin']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CreateStudentSerializer(data=request.data)
        
        if not serializer.is_valid():
            print('Validation errors:', serializer.errors)  # Debug log
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if admission number already exists
        if Student.objects.filter(admission_number=data['admission_number']).exists():
            return Response({'error': 'Admission number already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Create user account
                user = User.objects.create_user(
                    email=data['email'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone=data.get('phone', ''),
                    role='student',
                    tenant_id=tenant_id,
                    is_active=data.get('is_active', True)
                )
                
                # Create student profile
                student = Student.objects.create(
                    tenant_id=tenant_id,
                    user=user,
                    admission_number=data['admission_number'],
                    roll_number=data.get('roll_number', ''),
                    date_of_birth=data['date_of_birth'],
                    gender=data['gender'],
                    blood_group=data.get('blood_group', ''),
                    nationality=data.get('nationality', ''),
                    religion=data.get('religion', ''),
                    class_name=data['class_name'],
                    section=data.get('section', ''),
                    admission_date=data['admission_date'],
                    academic_year=data['academic_year'],
                    address=data.get('address', ''),
                    city=data.get('city', ''),
                    state=data.get('state', ''),
                    pincode=data.get('pincode', ''),
                    emergency_contact_name=data.get('emergency_contact_name', ''),
                    emergency_contact_phone=data.get('emergency_contact_phone', ''),
                    emergency_contact_relation=data.get('emergency_contact_relation', '')
                )
                
                # Create AcademicRegistration if class is assigned
                class_name = data.get('class_name')
                section = data.get('section', '')
                
                if class_name:
                    # Create AcademicRegistration
                    AcademicRegistration.objects.create(
                        tenant_id=tenant_id,
                        student=student,
                        academic_year=data['academic_year'],
                        class_name=class_name,
                        section=section,
                        is_current=True
                    )
                    print(f"DEBUG: Created AcademicRegistration for {student} in {class_name}-{section}")
                
                return Response({
                    'message': 'Student created successfully',
                    'student': StudentSerializer(student).data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def student_detail(request, student_id):
    """Get, update, or delete a student"""
    tenant_id = getattr(request, 'tenant_id', None)
    
    if not tenant_id:
        return Response({'error': 'Tenant context required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.user.role not in ['super_admin', 'tenant_admin']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = Student.objects.select_related('user').get(id=student_id, tenant_id=tenant_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(StudentSerializer(student).data)
    
    elif request.method == 'PUT':
        serializer = UpdateStudentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with transaction.atomic():
                # Update user fields
                user = student.user
                if 'first_name' in data:
                    user.first_name = data['first_name']
                if 'last_name' in data:
                    user.last_name = data['last_name']
                if 'phone' in data:
                    user.phone = data['phone']
                if 'is_active' in data:
                    user.is_active = data['is_active']
                user.save()
                
                # Update student fields
                for field, value in data.items():
                    if field not in ['first_name', 'last_name', 'phone', 'is_active']:
                        if field == 'school_class' and value:
                            # Handle ForeignKey to SchoolClass
                            from school_classes.models import SchoolClass
                            try:
                                school_class = SchoolClass.objects.get(id=value, tenant=student.tenant)
                                student.school_class = school_class
                            except SchoolClass.DoesNotExist:
                                pass  # Skip if class doesn't exist
                        elif hasattr(student, field):
                            setattr(student, field, value)
                student.save()
                
                return Response({
                    'message': 'Student updated successfully',
                    'student': StudentSerializer(student).data
                })
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            with transaction.atomic():
                user = student.user
                student.delete()
                user.delete()
                
            return Response({'message': 'Student deleted successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_profile(request):
    """Get current student's profile"""
    if request.user.role != 'student':
        return Response({'error': 'Only students can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = Student.objects.select_related('user', 'school_class').get(user=request.user)
        return Response(StudentSerializer(student).data)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
