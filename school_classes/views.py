from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from .models import SchoolClass
from .serializers import SchoolClassSerializer, SchoolClassListSerializer
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer


class SchoolClassViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing school classes
    
    Provides CRUD operations for school classes including:
    - List all classes
    - Create new class
    - Retrieve class details
    - Update class
    - Delete class
    - Get all teachers (for assignment)
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grade', 'section', 'academic_year', 'class_teacher']
    search_fields = ['class_name', 'grade', 'section']
    ordering_fields = ['grade', 'section', 'created_at']
    ordering = ['grade', 'section']
    
    def get_queryset(self):
        """Get classes for the current tenant"""
        user = self.request.user
        
        # Get tenant from user directly
        tenant = user.tenant
        
        if not tenant:
            return SchoolClass.objects.none()
        
        # Annotate with student count (using a different name to avoid conflict with the property)
        queryset = SchoolClass.objects.filter(tenant=tenant).select_related(
            'class_teacher',
            'class_teacher__user'
        ).annotate(
            _student_count=Count('students')
        )
        
        return queryset
        
        return queryset
    
    def get_serializer_class(self):
        """Use full serializer for all actions to include teacher details"""
        return SchoolClassSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new school class"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Reload the instance with teacher details
        instance = SchoolClass.objects.select_related(
            'class_teacher',
            'class_teacher__user'
        ).get(pk=serializer.instance.pk)
        response_serializer = self.get_serializer(instance)
        
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """Update a school class"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Reload the instance with teacher details
        instance = SchoolClass.objects.select_related(
            'class_teacher',
            'class_teacher__user'
        ).get(pk=instance.pk)
        response_serializer = self.get_serializer(instance)
        
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a school class"""
        instance = self.get_object()
        
        # Unassign students from this class before deletion
        if instance.student_count > 0:
            # Set school_class to None for all students in this class
            instance.students.update(school_class=None)
        
        self.perform_destroy(instance)
        return Response(
            {"message": "Class deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['get'])
    def teachers(self, request):
        """
        Get all teachers for class teacher assignment
        Endpoint: /api/classes/teachers/
        """
        user = request.user
        
        # Get tenant from user directly
        tenant = user.tenant
        
        if not tenant:
            return Response(
                {"error": "User is not associated with any tenant"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all teachers for this tenant
        teachers = Teacher.objects.filter(tenant=tenant).select_related('user').order_by(
            'user__first_name',
            'user__last_name'
        )
        
        # Return simplified teacher data
        teacher_data = [
            {
                'id': str(teacher.id),
                'firstName': teacher.user.first_name,
                'lastName': teacher.user.last_name,
                'email': teacher.user.email,
                'employeeId': teacher.employee_id,
                'department': teacher.department or '',
            }
            for teacher in teachers
        ]
        
        return Response(teacher_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get statistics about classes
        Endpoint: /api/classes/statistics/
        """
        queryset = self.get_queryset()
        
        total_classes = queryset.count()
        with_teachers = queryset.filter(class_teacher__isnull=False).count()
        without_teachers = total_classes - with_teachers
        total_students = sum(c.student_count for c in queryset)
        
        return Response({
            'totalClasses': total_classes,
            'withTeachers': with_teachers,
            'withoutTeachers': without_teachers,
            'totalStudents': total_students,
        }, status=status.HTTP_200_OK)
