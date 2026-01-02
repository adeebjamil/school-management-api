from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import StudentParent, Parent
from students.models import Student
from .student_parent_serializers import (
    StudentParentSerializer, 
    LinkStudentParentSerializer,
    ParentChildrenSerializer
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def link_student_to_parent(request):
    """
    Link a student to a parent
    POST: Create a student-parent relationship
    """
    tenant = request.tenant
    serializer = LinkStudentParentSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Verify student and parent belong to this tenant
        student = Student.objects.get(id=data['student_id'], tenant=tenant)
        parent = Parent.objects.get(id=data['parent_id'], tenant=tenant)
        
        # Check if link already exists
        if StudentParent.objects.filter(student=student, parent=parent).exists():
            return Response(
                {'error': 'This student is already linked to this parent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the link
        student_parent = StudentParent.objects.create(
            tenant=tenant,
            student=student,
            parent=parent,
            is_primary=data.get('is_primary', False)
        )
        
        serializer = StudentParentSerializer(student_parent)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    except Parent.DoesNotExist:
        return Response({'error': 'Parent not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_parents(request, student_id):
    """
    Get all parents linked to a student
    """
    tenant = request.tenant
    
    try:
        student = Student.objects.get(id=student_id, tenant=tenant)
        links = StudentParent.objects.filter(student=student, tenant=tenant)
        serializer = StudentParentSerializer(links, many=True)
        return Response(serializer.data)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_parent_children(request, parent_id):
    """
    Get all children (students) of a parent
    """
    tenant = request.tenant
    
    try:
        parent = Parent.objects.get(id=parent_id, tenant=tenant)
        links = StudentParent.objects.filter(
            parent=parent, 
            tenant=tenant
        ).select_related('student__user')
        
        children = []
        for link in links:
            children.append({
                'id': str(link.student.id),
                'admission_number': link.student.admission_number,
                'roll_number': link.student.roll_number,
                'first_name': link.student.user.first_name,
                'last_name': link.student.user.last_name,
                'class_name': link.student.class_name,
                'section': link.student.section,
                'is_primary': link.is_primary,
            })
        
        return Response(children)
    except Parent.DoesNotExist:
        return Response({'error': 'Parent not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_children(request):
    """
    Get children of the logged-in parent user
    """
    user = request.user
    tenant = request.tenant
    
    # Check if user is a parent
    try:
        parent = Parent.objects.get(user=user, tenant=tenant)
    except Parent.DoesNotExist:
        return Response(
            {'error': 'You are not registered as a parent'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    links = StudentParent.objects.filter(
        parent=parent,
        tenant=tenant
    ).select_related('student__user')
    
    children = []
    for link in links:
        children.append({
            'id': str(link.student.id),
            'link_id': str(link.id),  # Added link ID for unlinking
            'admission_number': link.student.admission_number,
            'roll_number': link.student.roll_number,
            'first_name': link.student.user.first_name,
            'last_name': link.student.user.last_name,
            'class_name': link.student.class_name,
            'section': link.student.section,
            'is_primary': link.is_primary,
        })
    
    return Response(children)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unlink_student_from_parent(request, link_id):
    """
    Remove a student-parent link
    """
    tenant = request.tenant
    
    try:
        link = StudentParent.objects.get(id=link_id, tenant=tenant)
        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except StudentParent.DoesNotExist:
        return Response({'error': 'Link not found'}, status=status.HTTP_404_NOT_FOUND)
