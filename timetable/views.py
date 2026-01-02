from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from collections import defaultdict

from .models import TimeSlot, Timetable
from .serializers import (
    TimeSlotSerializer, TimetableSerializer, 
    ClassTimetableSerializer, TeacherTimetableSerializer
)
from students.models import Student
from teachers.models import Teacher


class TimeSlotViewSet(viewsets.ModelViewSet):
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        return TimeSlot.objects.filter(tenant=tenant, is_active=True).order_by('period_number')
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)


class TimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        queryset = Timetable.objects.filter(tenant=tenant, is_active=True)
        
        # Filter by class and section
        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')
        
        if class_name:
            queryset = queryset.filter(class_name=class_name)
        if section:
            queryset = queryset.filter(section=section)
        
        # Filter by teacher
        teacher_id = self.request.query_params.get('teacher_id')
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        
        # Filter by day
        day = self.request.query_params.get('day')
        if day:
            queryset = queryset.filter(day=day)
        
        return queryset.select_related('teacher', 'teacher__user', 'time_slot').order_by('day', 'time_slot__period_number')
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)
    
    @action(detail=False, methods=['get'])
    def class_timetable(self, request):
        """Get timetable for a specific class and section"""
        tenant = request.tenant
        class_name = request.query_params.get('class_name')
        section = request.query_params.get('section')
        
        if not class_name:
            return Response(
                {'error': 'class_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get timetable entries
        queryset = Timetable.objects.filter(
            tenant=tenant,
            class_name=class_name,
            is_active=True
        )
        
        if section:
            queryset = queryset.filter(section=section)
        
        queryset = queryset.select_related('teacher', 'teacher__user', 'time_slot').order_by('time_slot__period_number')
        
        # Group by day
        days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        timetable_by_day = defaultdict(list)
        
        for entry in queryset:
            timetable_by_day[entry.day].append(entry)
        
        # Format response
        result = []
        for day in days_order:
            if day in timetable_by_day:
                serializer = TimetableSerializer(timetable_by_day[day], many=True)
                result.append({
                    'day': day.capitalize(),
                    'periods': serializer.data
                })
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def teacher_timetable(self, request):
        """Get timetable for a specific teacher"""
        tenant = request.tenant
        teacher_id = request.query_params.get('teacher_id')
        
        # If no teacher_id provided, try to get current user's teacher profile
        if not teacher_id:
            try:
                teacher = Teacher.objects.get(user=request.user, tenant=tenant)
                teacher_id = teacher.id
            except Teacher.DoesNotExist:
                return Response(
                    {'error': 'Teacher profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get timetable entries
        queryset = Timetable.objects.filter(
            tenant=tenant,
            teacher_id=teacher_id,
            is_active=True
        ).select_related('teacher', 'time_slot').order_by('time_slot__period_number')
        
        # Group by day
        days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        timetable_by_day = defaultdict(list)
        
        for entry in queryset:
            timetable_by_day[entry.day].append({
                'id': str(entry.id),
                'period_number': entry.time_slot.period_number,
                'start_time': entry.time_slot.start_time.strftime('%H:%M'),
                'end_time': entry.time_slot.end_time.strftime('%H:%M'),
                'subject': entry.subject,
                'class_name': entry.class_name,
                'section': entry.section or '',
                'room_number': entry.room_number or '',
            })
        
        # Format response
        result = []
        for day in days_order:
            if day in timetable_by_day:
                result.append({
                    'day': day.capitalize(),
                    'periods': timetable_by_day[day]
                })
        
        return Response(result)
    
    @action(detail=False, methods=['GET'])
    def my_timetable(self, request):
        """Get timetable for current logged-in user (student or teacher)"""
        print(f"DEBUG: my_timetable called for user: {request.user}")
        user = request.user
        tenant = request.tenant
        
        # Check if user is a student
        try:
            student = Student.objects.get(user=user, tenant=tenant)
            print(f"DEBUG: Found student: {student}")
            # Get student's class information
            try:
                from students.models import AcademicRegistration
                registration = AcademicRegistration.objects.filter(
                    student=student,
                    is_current=True
                ).first()
                print(f"DEBUG: Registration: {registration}")
                
                if not registration:
                    print(f"DEBUG: No registration found")
                    return Response(
                        {'error': 'No active class assignment found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Get class_name and section from AcademicRegistration
                class_name = registration.class_name
                section = registration.section or ''
                print(f"DEBUG: class_name={class_name}, section={section}")
                
                # Get timetable entries directly
                queryset = Timetable.objects.filter(
                    tenant=tenant,
                    class_name=class_name,
                    section=section,
                    is_active=True
                ).select_related('teacher', 'teacher__user', 'time_slot').order_by('time_slot__period_number')
                print(f"DEBUG: Found {queryset.count()} timetable entries")
                
                # Group by day
                days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
                timetable_by_day = defaultdict(list)
                
                for entry in queryset:
                    serialized_entry = TimetableSerializer(entry).data
                    timetable_by_day[entry.day].append(serialized_entry)
                
                # Format response
                result = [
                    {
                        'day': day,
                        'periods': timetable_by_day[day]
                    }
                    for day in days_order if day in timetable_by_day
                ]
                print(f"DEBUG: Returning {len(result)} days")
                
                return Response(result)
                
            except Exception as e:
                import traceback
                print(f"DEBUG: Exception in student branch: {e}")
                traceback.print_exc()
                return Response(
                    {'error': f'Failed to get class information: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Student.DoesNotExist:
            print(f"DEBUG: Student does not exist")
            pass
        
        # Check if user is a teacher
        try:
            teacher = Teacher.objects.get(user=user, tenant=tenant)
            print(f"DEBUG: Found teacher: {teacher}")
            
            # Get teacher's timetable directly
            queryset = Timetable.objects.filter(
                tenant=tenant,
                teacher=teacher,
                is_active=True
            ).select_related('time_slot').order_by('day', 'time_slot__period_number')
            
            # Group by day
            days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
            timetable_by_day = defaultdict(list)
            
            for entry in queryset:
                serialized_entry = TimetableSerializer(entry).data
                timetable_by_day[entry.day].append(serialized_entry)
            
            # Format response
            result = [
                {
                    'day': day,
                    'periods': timetable_by_day[day]
                }
                for day in days_order if day in timetable_by_day
            ]
            
            return Response(result)
            
        except Teacher.DoesNotExist:
            print(f"DEBUG: Teacher does not exist")
            pass
        
        print(f"DEBUG: Neither student nor teacher found - returning 404")
        
        return Response(
            {'error': 'No student or teacher profile found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple timetable entries at once"""
        entries = request.data.get('entries', [])
        
        if not entries:
            return Response(
                {'error': 'No entries provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_entries = []
        errors = []
        
        for entry_data in entries:
            serializer = self.get_serializer(data=entry_data)
            if serializer.is_valid():
                serializer.save(tenant=request.tenant)
                created_entries.append(serializer.data)
            else:
                errors.append({
                    'entry': entry_data,
                    'errors': serializer.errors
                })
        
        return Response({
            'created': len(created_entries),
            'failed': len(errors),
            'entries': created_entries,
            'errors': errors
        }, status=status.HTTP_201_CREATED if created_entries else status.HTTP_400_BAD_REQUEST)

