from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q

from .models import Vehicle, Route, TransportAssignment
from .serializers import (
    VehicleSerializer, RouteSerializer, TransportAssignmentSerializer,
    CreateTransportAssignmentSerializer, VehicleStatsSerializer
)
from students.models import Student
from teachers.models import Teacher


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        queryset = Vehicle.objects.filter(tenant=tenant)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by vehicle type
        vehicle_type = self.request.query_params.get('vehicle_type')
        if vehicle_type:
            queryset = queryset.filter(vehicle_type=vehicle_type)
        
        # Filter by route
        route_id = self.request.query_params.get('route')
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(vehicle_number__icontains=search) |
                Q(driver_name__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get transport statistics"""
        tenant = request.tenant
        
        total_vehicles = Vehicle.objects.filter(tenant=tenant).count()
        active_vehicles = Vehicle.objects.filter(tenant=tenant, status='active').count()
        maintenance = Vehicle.objects.filter(tenant=tenant, status='maintenance').count()
        total_students = TransportAssignment.objects.filter(
            tenant=tenant,
            is_active=True,
            content_type=ContentType.objects.get_for_model(Student)
        ).count()
        total_routes = Route.objects.filter(tenant=tenant, is_active=True).count()
        
        data = {
            'total_vehicles': total_vehicles,
            'active_vehicles': active_vehicles,
            'maintenance': maintenance,
            'total_students': total_students,
            'total_routes': total_routes,
        }
        
        serializer = VehicleStatsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def assignments(self, request, pk=None):
        """Get all assignments for a vehicle"""
        vehicle = self.get_object()
        assignments = TransportAssignment.objects.filter(
            vehicle=vehicle,
            is_active=True
        )
        serializer = TransportAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class RouteViewSet(viewsets.ModelViewSet):
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        return Route.objects.filter(tenant=tenant)
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)


class TransportAssignmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTransportAssignmentSerializer
        return TransportAssignmentSerializer
    
    def get_queryset(self):
        tenant = self.request.tenant
        queryset = TransportAssignment.objects.filter(tenant=tenant)
        
        # Filter by vehicle
        vehicle_id = self.request.query_params.get('vehicle_id')
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by user type
        user_type = self.request.query_params.get('user_type')
        if user_type == 'student':
            queryset = queryset.filter(content_type=ContentType.objects.get_for_model(Student))
        elif user_type == 'teacher':
            queryset = queryset.filter(content_type=ContentType.objects.get_for_model(Teacher))
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save()
        
        # Return with full details
        response_serializer = TransportAssignmentSerializer(assignment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate/remove an assignment"""
        assignment = self.get_object()
        assignment.is_active = False
        assignment.status = 'inactive'
        assignment.save()
        
        serializer = self.get_serializer(assignment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_transport(self, request):
        """Get transport assignment for current user (student/teacher)"""
        user = request.user
        tenant = request.tenant
        
        # Check if user is student
        try:
            student = Student.objects.get(user=user, tenant=tenant)
            content_type = ContentType.objects.get_for_model(Student)
            user_id = student.id
        except Student.DoesNotExist:
            # Check if user is teacher
            try:
                teacher = Teacher.objects.get(user=user, tenant=tenant)
                content_type = ContentType.objects.get_for_model(Teacher)
                user_id = teacher.id
            except Teacher.DoesNotExist:
                return Response(
                    {'detail': 'No student or teacher profile found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get active assignment
        try:
            assignment = TransportAssignment.objects.get(
                tenant=tenant,
                content_type=content_type,
                object_id=user_id,
                is_active=True,
                status='active'
            )
            serializer = TransportAssignmentSerializer(assignment)
            return Response(serializer.data)
        except TransportAssignment.DoesNotExist:
            return Response(
                {'detail': 'No active transport assignment found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except TransportAssignment.MultipleObjectsReturned:
            # Return the most recent one
            assignment = TransportAssignment.objects.filter(
                tenant=tenant,
                content_type=content_type,
                object_id=user_id,
                is_active=True,
                status='active'
            ).order_by('-created_at').first()
            serializer = TransportAssignmentSerializer(assignment)
            return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available_users(self, request):
        """Get list of students/teachers for assignment"""
        tenant = request.tenant
        user_type = request.query_params.get('user_type', 'student')
        search = request.query_params.get('search', '')
        
        if user_type == 'student':
            users = Student.objects.filter(tenant=tenant, is_active=True)
            if search:
                users = users.filter(
                    Q(user__first_name__icontains=search) |
                    Q(user__last_name__icontains=search) |
                    Q(admission_number__icontains=search)
                )
            
            data = []
            for student in users[:20]:  # Limit to 20 results
                # Try to get class information from academic registration
                class_info = None
                try:
                    from students.models import AcademicRegistration
                    registration = AcademicRegistration.objects.filter(
                        student=student,
                        is_active=True
                    ).first()
                    if registration and hasattr(registration, 'class_assigned'):
                        class_info = f"{registration.class_assigned.name}-{registration.class_assigned.section}"
                except Exception:
                    pass
                
                data.append({
                    'id': str(student.id),
                    'name': student.user.full_name if hasattr(student.user, 'full_name') else f"{student.user.first_name} {student.user.last_name}",
                    'user_id': student.admission_number,
                    'class_section': class_info or 'N/A',
                    'type': 'student'
                })
        
        elif user_type == 'teacher':
            users = Teacher.objects.filter(tenant=tenant, is_active=True)
            if search:
                users = users.filter(
                    Q(user__first_name__icontains=search) |
                    Q(user__last_name__icontains=search) |
                    Q(employee_id__icontains=search)
                )
            
            data = []
            for teacher in users[:20]:
                data.append({
                    'id': str(teacher.id),
                    'name': teacher.user.full_name if hasattr(teacher.user, 'full_name') else f"{teacher.user.first_name} {teacher.user.last_name}",
                    'user_id': teacher.employee_id,
                    'type': 'teacher'
                })
        else:
            return Response({'detail': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data)
