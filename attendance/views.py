from django.shortcuts import render
from django.db.models import Count, Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from .models import Attendance, TeacherAttendance
from .serializers import (
    AttendanceSerializer, 
    BulkAttendanceSerializer,
    AttendanceStatsSerializer,
    TeacherAttendanceSerializer
)
from students.models import Student


@api_view(['POST'])
def mark_bulk_attendance(request):
    """Mark attendance for multiple students at once"""
    if request.user.role not in ['super_admin', 'tenant_admin', 'teacher']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    print("DEBUG: Received data:", request.data)  # Debug log
    
    serializer = BulkAttendanceSerializer(data=request.data)
    if not serializer.is_valid():
        print("DEBUG: Validation errors:", serializer.errors)  # Debug log
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    date = serializer.validated_data['date']
    records = serializer.validated_data['attendance_records']
    
    created_records = []
    updated_records = []
    
    for record in records:
        try:
            student = Student.objects.get(id=record['student_id'], tenant=request.user.tenant)
            
            attendance, created = Attendance.objects.update_or_create(
                tenant=request.user.tenant,
                student=student,
                date=date,
                defaults={
                    'status': record['status'],
                    'remarks': record.get('remarks', ''),
                    'marked_by': request.user,
                }
            )
            
            if created:
                created_records.append(attendance)
            else:
                updated_records.append(attendance)
                
        except Student.DoesNotExist:
            return Response(
                {'error': f'Student with ID {record["student_id"]} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    return Response({
        'message': 'Attendance marked successfully',
        'created': len(created_records),
        'updated': len(updated_records),
        'total': len(created_records) + len(updated_records),
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_attendance_by_date(request):
    """Get attendance records for a specific date and optional class filter"""
    if request.user.role not in ['super_admin', 'tenant_admin', 'teacher']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    date = request.GET.get('date')
    class_id = request.GET.get('class_id')
    
    if not date:
        return Response({'error': 'Date parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        attendance_records = Attendance.objects.filter(
            tenant=request.user.tenant,
            date=date
        ).select_related('student', 'student__user', 'marked_by')
        
        if class_id:
            attendance_records = attendance_records.filter(student__school_class_id=class_id)
        
        serializer = AttendanceSerializer(attendance_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_student_attendance_history(request, student_id):
    """Get attendance history for a specific student"""
    if request.user.role not in ['super_admin', 'tenant_admin', 'teacher', 'student', 'parent']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Students and parents can only view their own records
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user, tenant=request.user.tenant)
            if str(student.id) != student_id:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        attendance_records = Attendance.objects.filter(
            tenant=request.user.tenant,
            student_id=student_id
        ).select_related('marked_by').order_by('-date')
        
        if start_date:
            attendance_records = attendance_records.filter(date__gte=start_date)
        if end_date:
            attendance_records = attendance_records.filter(date__lte=end_date)
        
        serializer = AttendanceSerializer(attendance_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_student_attendance_stats(request, student_id):
    """Get attendance statistics for a specific student"""
    if request.user.role not in ['super_admin', 'tenant_admin', 'teacher', 'student', 'parent']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Students and parents can only view their own records
    if request.user.role == 'student':
        try:
            student = Student.objects.get(user=request.user, tenant=request.user.tenant)
            if str(student.id) != student_id:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        attendance_records = Attendance.objects.filter(
            tenant=request.user.tenant,
            student_id=student_id
        )
        
        if start_date:
            attendance_records = attendance_records.filter(date__gte=start_date)
        if end_date:
            attendance_records = attendance_records.filter(date__lte=end_date)
        
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='present').count()
        absent_days = attendance_records.filter(status='absent').count()
        late_days = attendance_records.filter(status='late').count()
        half_days = attendance_records.filter(status='half_day').count()
        
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        stats = {
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'half_days': half_days,
            'attendance_percentage': round(attendance_percentage, 2),
        }
        
        serializer = AttendanceStatsSerializer(data=stats)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_class_attendance_stats(request):
    """Get attendance statistics for a class"""
    if request.user.role not in ['super_admin', 'tenant_admin', 'teacher']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    class_id = request.GET.get('class_id')
    date = request.GET.get('date', datetime.now().date())
    
    if not class_id:
        return Response({'error': 'class_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get total students in the class
        total_students = Student.objects.filter(
            tenant=request.user.tenant,
            school_class_id=class_id
        ).count()
        
        # Get attendance for the date
        attendance_today = Attendance.objects.filter(
            tenant=request.user.tenant,
            student__school_class_id=class_id,
            date=date
        )
        
        present_count = attendance_today.filter(status='present').count()
        absent_count = attendance_today.filter(status='absent').count()
        late_count = attendance_today.filter(status='late').count()
        
        return Response({
            'total_students': total_students,
            'present': present_count,
            'absent': absent_count,
            'late': late_count,
            'unmarked': total_students - attendance_today.count(),
            'date': date,
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
