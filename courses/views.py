from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Prefetch
from datetime import datetime

from .models import Course, CourseModule, CourseContent, CourseEnrollment, ContentProgress
from .serializers import (
    CourseSerializer, CreateCourseSerializer, CourseModuleSerializer,
    CourseContentSerializer, CourseEnrollmentSerializer, ContentProgressSerializer,
    BulkEnrollSerializer
)
from students.models import Student
from school_classes.models import SchoolClass


# ==================== COURSE MANAGEMENT ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def course_list_create(request):
    """List all courses or create a new course (Tenant Admin only)"""
    tenant_id = request.tenant_id
    
    if not tenant_id:
        return Response({'error': 'Tenant ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        # Get query parameters
        class_id = request.query_params.get('class_id')
        section_id = request.query_params.get('section_id')
        academic_year = request.query_params.get('academic_year')
        semester = request.query_params.get('semester')
        teacher_id = request.query_params.get('teacher_id')
        is_published = request.query_params.get('is_published')
        
        # Build query - only show active courses by default
        courses = Course.objects.filter(tenant_id=tenant_id, is_active=True).select_related(
            'school_class', 'primary_teacher', 'created_by'
        ).prefetch_related('additional_teachers', 'modules')
        
        # Apply filters
        if class_id:
            courses = courses.filter(school_class_id=class_id)
        if section_id:
            courses = courses.filter(section_id=section_id)
        if academic_year:
            courses = courses.filter(academic_year=academic_year)
        if semester:
            courses = courses.filter(semester=semester)
        if teacher_id:
            courses = courses.filter(
                Q(primary_teacher_id=teacher_id) | Q(additional_teachers__id=teacher_id)
            ).distinct()
        if is_published is not None:
            courses = courses.filter(is_published=is_published.lower() == 'true')
        
        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(courses, request)
        serializer = CourseSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        # Only Tenant Admin can create courses
        if request.user.role != 'tenant_admin':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CreateCourseSerializer(data=request.data)
        if serializer.is_valid():
            try:
                course = serializer.save(
                    tenant_id=tenant_id,
                    created_by=request.user
                )
            except Exception as e:
                error_message = str(e)
                if 'UNIQUE constraint failed' in error_message or 'unique constraint' in error_message.lower():
                    return Response({
                        'error': 'A course with this course code already exists for the selected academic year and semester.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
            
            # Auto-enroll all students from the assigned class
            if course.school_class:
                from students.models import Student
                students_query = Student.objects.filter(
                    tenant_id=tenant_id,
                    school_class=course.school_class,
                    is_active=True
                )
                
                if course.section:
                    students_query = students_query.filter(section=course.section)
                
                students = students_query.all()
                enrolled_count = 0
                
                for student in students:
                    CourseEnrollment.objects.get_or_create(
                        tenant_id=tenant_id,
                        student=student,
                        course=course,
                        defaults={'is_active': True}
                    )
                    enrolled_count += 1
            
            return Response(
                CourseSerializer(course).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def course_detail(request, course_id):
    """Get, update, or delete a course"""
    tenant_id = request.tenant_id
    
    if not tenant_id:
        return Response({'error': 'Tenant ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    course = get_object_or_404(
        Course.objects.select_related(
            'school_class', 'primary_teacher', 'created_by'
        ).prefetch_related(
            'additional_teachers',
            'modules__contents'
        ),
        id=course_id,
        tenant_id=tenant_id
    )
    
    if request.method == 'GET':
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Only Tenant Admin or assigned teacher can update
        if request.user.role not in ['tenant_admin', 'teacher']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.role == 'teacher':
            teacher = request.user.teacher
            if course.primary_teacher != teacher and teacher not in course.additional_teachers.all():
                return Response({'error': 'You are not assigned to this course'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CreateCourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(CourseSerializer(course).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Only Tenant Admin can delete
        if request.user.role != 'tenant_admin':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Permanently delete the course
        course.delete()
        return Response({'message': 'Course deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# ==================== MODULE MANAGEMENT ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def module_list_create(request, course_id):
    """List modules for a course or create a new module"""
    tenant_id = request.tenant_id
    
    if not tenant_id:
        return Response({'error': 'Tenant ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    course = get_object_or_404(Course, id=course_id, tenant_id=tenant_id)
    
    if request.method == 'GET':
        modules = CourseModule.objects.filter(
            course=course,
            tenant_id=tenant_id
        ).prefetch_related('contents')
        serializer = CourseModuleSerializer(modules, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Check permissions
        if request.user.role not in ['tenant_admin', 'teacher']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.role == 'teacher':
            teacher = request.user.teacher
            if course.primary_teacher != teacher and teacher not in course.additional_teachers.all():
                return Response({'error': 'You are not assigned to this course'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CourseModuleSerializer(data=request.data)
        if serializer.is_valid():
            module = serializer.save(
                tenant_id=tenant_id,
                course=course
            )
            return Response(
                CourseModuleSerializer(module).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def module_detail(request, course_id, module_id):
    """Get, update, or delete a module"""
    tenant_id = request.tenant_id
    
    if not tenant_id:
        return Response({'error': 'Tenant ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    course = get_object_or_404(Course, id=course_id, tenant_id=tenant_id)
    module = get_object_or_404(
        CourseModule.objects.prefetch_related('contents'),
        id=module_id,
        course=course,
        tenant_id=tenant_id
    )
    
    if request.method == 'GET':
        serializer = CourseModuleSerializer(module)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'DELETE']:
        # Check permissions
        if request.user.role not in ['tenant_admin', 'teacher']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.role == 'teacher':
            teacher = request.user.teacher
            if course.primary_teacher != teacher and teacher not in course.additional_teachers.all():
                return Response({'error': 'You are not assigned to this course'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            serializer = CourseModuleSerializer(module, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:  # DELETE
            module.delete()
            return Response({'message': 'Module deleted successfully'})


# ==================== CONTENT MANAGEMENT ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def content_list_create(request, course_id, module_id):
    """List contents for a module or create new content"""
    tenant_id = request.tenant_id
    
    if not tenant_id:
        return Response({'error': 'Tenant ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    course = get_object_or_404(Course, id=course_id, tenant_id=tenant_id)
    module = get_object_or_404(CourseModule, id=module_id, course=course, tenant_id=tenant_id)
    
    if request.method == 'GET':
        contents = CourseContent.objects.filter(module=module, tenant_id=tenant_id)
        serializer = CourseContentSerializer(contents, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Check permissions
        if request.user.role not in ['tenant_admin', 'teacher']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.role == 'teacher':
            teacher = request.user.teacher
            if course.primary_teacher != teacher and teacher not in course.additional_teachers.all():
                return Response({'error': 'You are not assigned to this course'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CourseContentSerializer(data=request.data)
        if serializer.is_valid():
            content = serializer.save(
                tenant_id=tenant_id,
                module=module
            )
            return Response(
                CourseContentSerializer(content).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def content_detail(request, course_id, module_id, content_id):
    """Get, update, or delete content"""
    tenant_id = request.tenant_id
    
    if not tenant_id:
        return Response({'error': 'Tenant ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    course = get_object_or_404(Course, id=course_id, tenant_id=tenant_id)
    module = get_object_or_404(CourseModule, id=module_id, course=course, tenant_id=tenant_id)
    content = get_object_or_404(CourseContent, id=content_id, module=module, tenant_id=tenant_id)
    
    if request.method == 'GET':
        serializer = CourseContentSerializer(content)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'DELETE']:
        # Check permissions
        if request.user.role not in ['tenant_admin', 'teacher']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.role == 'teacher':
            teacher = request.user.teacher
            if course.primary_teacher != teacher and teacher not in course.additional_teachers.all():
                return Response({'error': 'You are not assigned to this course'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            serializer = CourseContentSerializer(content, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:  # DELETE
            content.delete()
            return Response({'message': 'Content deleted successfully'})


# ==================== ENROLLMENT MANAGEMENT ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def enrollment_list_create(request, course_id):
    """List enrollments for a course or enroll students"""
    tenant_id = request.tenant_id
    
    if not tenant_id:
        return Response({'error': 'Tenant ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    course = get_object_or_404(Course, id=course_id, tenant_id=tenant_id)
    
    if request.method == 'GET':
        enrollments = CourseEnrollment.objects.filter(
            course=course,
            tenant_id=tenant_id
        ).select_related('student', 'student__user')
        
        serializer = CourseEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Only Tenant Admin can enroll students
        if request.user.role != 'tenant_admin':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CourseEnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            enrollment = serializer.save(
                tenant_id=tenant_id,
                course=course
            )
            return Response(
                CourseEnrollmentSerializer(enrollment).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_enroll(request):
    """Enroll multiple students in a course"""
    tenant_id = request.tenant_id
    
    if not tenant_id:
        return Response({'error': 'Tenant ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.user.role != 'tenant_admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = BulkEnrollSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    course_id = serializer.validated_data['course_id']
    student_ids = serializer.validated_data['student_ids']
    
    course = get_object_or_404(Course, id=course_id, tenant_id=tenant_id)
    
    enrolled_count = 0
    errors = []
    
    for student_id in student_ids:
        try:
            student = Student.objects.get(id=student_id, tenant_id=tenant_id)
            enrollment, created = CourseEnrollment.objects.get_or_create(
                tenant_id=tenant_id,
                student=student,
                course=course,
                defaults={'is_active': True}
            )
            if created:
                enrolled_count += 1
        except Student.DoesNotExist:
            errors.append(f'Student {student_id} not found')
    
    return Response({
        'message': f'Successfully enrolled {enrolled_count} students',
        'enrolled_count': enrolled_count,
        'errors': errors
    })


# ==================== STUDENT/TEACHER VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_courses(request):
    """Get courses for current user (student or teacher)"""
    tenant_id = request.tenant_id
    
    if not tenant_id:
        return Response({'error': 'Tenant ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.user.role == 'student':
        try:
            student = request.user.student_profile
        except AttributeError:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        enrollments = CourseEnrollment.objects.filter(
            student=student,
            tenant_id=tenant_id,
            is_active=True
        ).select_related('course', 'course__primary_teacher')
        
        courses = [enrollment.course for enrollment in enrollments]
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    
    elif request.user.role == 'teacher':
        try:
            teacher = request.user.teacher_profile
        except AttributeError:
            return Response({'error': 'Teacher profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        courses = Course.objects.filter(
            Q(primary_teacher=teacher) | Q(additional_teachers=teacher),
            tenant_id=tenant_id,
            is_active=True
        ).distinct().select_related('school_class').prefetch_related('modules')
        
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    
    else:
        return Response({'error': 'Only students and teachers can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_enroll_by_class(request, course_id):
    """Auto-enroll all students from the course's class and section"""
    tenant_id = request.tenant_id
    
    if not tenant_id:
        return Response({'error': 'Tenant ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.user.role != 'tenant_admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    course = get_object_or_404(Course, id=course_id, tenant_id=tenant_id)
    
    if not course.school_class:
        return Response({
            'error': 'Course must have a class assigned',
            'course_details': {
                'course_name': course.course_name,
                'course_code': course.course_code,
                'has_class': bool(course.school_class),
                'section': course.section
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get students from the class and section
    students_query = Student.objects.filter(
        tenant_id=tenant_id,
        school_class=course.school_class,
        is_active=True
    )
    
    if course.section:
        students_query = students_query.filter(section=course.section)
    
    students = students_query.all()
    total_students = students.count()
    
    enrolled_count = 0
    already_enrolled = 0
    for student in students:
        enrollment, created = CourseEnrollment.objects.get_or_create(
            tenant_id=tenant_id,
            student=student,
            course=course,
            defaults={'is_active': True}
        )
        if created:
            enrolled_count += 1
        else:
            already_enrolled += 1
    
    return Response({
        'message': f'Successfully enrolled {enrolled_count} students!',
        'enrolled_count': enrolled_count,
        'already_enrolled': already_enrolled,
        'total_students': total_students,
        'class_info': {
            'class_name': course.school_class.class_name if course.school_class else None,
            'section': course.section
        }
    })
