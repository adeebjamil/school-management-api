from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from parents.models import Parent, StudentParent
from students.models import Student
from attendance.models import Attendance
from datetime import datetime, timedelta


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_child_attendance(request, student_id):
    """
    Get attendance records for a specific child
    Only accessible by the child's parent or tenant admin
    """
    user = request.user
    tenant = request.tenant
    
    # Verify student exists in tenant
    try:
        student = Student.objects.get(id=student_id, tenant=tenant)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is parent of this student or is admin
    if user.role == 'parent':
        try:
            parent = Parent.objects.get(user=user, tenant=tenant)
            # Verify this parent is linked to this student
            if not StudentParent.objects.filter(
                parent=parent, 
                student=student, 
                tenant=tenant
            ).exists():
                return Response(
                    {'error': 'You do not have permission to view this student\'s attendance'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Parent.DoesNotExist:
            return Response(
                {'error': 'Parent profile not found'},
                status=status.HTTP_403_FORBIDDEN
            )
    elif user.role not in ['tenant_admin', 'teacher']:
        return Response(
            {'error': 'You do not have permission to view attendance'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get query parameters for filtering
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    status_filter = request.query_params.get('status')
    
    # Build query
    attendance_records = Attendance.objects.filter(
        student=student,
        tenant=tenant
    ).select_related('marked_by')
    
    # Apply date filters
    if start_date:
        attendance_records = attendance_records.filter(date__gte=start_date)
    if end_date:
        attendance_records = attendance_records.filter(date__lte=end_date)
    if status_filter:
        attendance_records = attendance_records.filter(status=status_filter)
    
    # If no date range specified, default to last 30 days
    if not start_date and not end_date:
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        attendance_records = attendance_records.filter(date__gte=thirty_days_ago)
    
    # Serialize data
    data = []
    for record in attendance_records:
        data.append({
            'id': str(record.id),
            'date': record.date,
            'status': record.status,
            'status_display': record.get_status_display(),
            'remarks': record.remarks,
            'marked_by': record.marked_by.full_name if record.marked_by else 'System',
            'marked_at': record.marked_at,
        })
    
    # Calculate statistics
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    absent_days = attendance_records.filter(status='absent').count()
    late_days = attendance_records.filter(status='late').count()
    
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    return Response({
        'student': {
            'id': str(student.id),
            'name': student.user.full_name,
            'admission_number': student.admission_number,
            'class': student.class_name,
            'section': student.section,
        },
        'statistics': {
            'total_days': total_days,
            'present': present_days,
            'absent': absent_days,
            'late': late_days,
            'attendance_percentage': round(attendance_percentage, 2),
        },
        'records': data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_children_attendance(request):
    """
    Get attendance summary for all children of logged-in parent
    """
    user = request.user
    tenant = request.tenant
    
    # Verify user is a parent
    try:
        parent = Parent.objects.get(user=user, tenant=tenant)
    except Parent.DoesNotExist:
        return Response(
            {'error': 'You are not registered as a parent'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get all children
    student_links = StudentParent.objects.filter(
        parent=parent,
        tenant=tenant
    ).select_related('student__user')
    
    if not student_links.exists():
        return Response({
            'message': 'No children found',
            'children': []
        })
    
    # Get attendance for each child (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    children_attendance = []
    
    for link in student_links:
        student = link.student
        attendance_records = Attendance.objects.filter(
            student=student,
            tenant=tenant,
            date__gte=thirty_days_ago
        )
        
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='present').count()
        absent_days = attendance_records.filter(status='absent').count()
        
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        children_attendance.append({
            'student': {
                'id': str(student.id),
                'name': student.user.full_name,
                'admission_number': student.admission_number,
                'class': student.class_name,
                'section': student.section,
            },
            'statistics': {
                'total_days': total_days,
                'present': present_days,
                'absent': absent_days,
                'attendance_percentage': round(attendance_percentage, 2),
            },
            'is_primary': link.is_primary,
        })
    
    return Response({
        'parent': {
            'id': str(parent.id),
            'name': parent.user.full_name,
            'relation': parent.get_relation_display() if parent.relation else 'Guardian',
        },
        'children': children_attendance
    })
