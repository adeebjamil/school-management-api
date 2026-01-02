from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Exam, ExamSubject, Result, AdmitCard
from .serializers import (
    ExamSerializer, 
    CreateExamSerializer, 
    ExamSubjectSerializer,
    ResultSerializer,
    AdmitCardSerializer
)


@api_view(['GET', 'POST'])
def exam_list_create(request):
    """List all exams or create a new exam"""
    if request.user.role not in ['super_admin', 'tenant_admin']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        # Get query parameters for filtering
        class_name = request.GET.get('class_name')
        section = request.GET.get('section')
        exam_type = request.GET.get('exam_type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        exams = Exam.objects.filter(tenant=request.user.tenant)
        
        if class_name:
            exams = exams.filter(subjects__class_name=class_name).distinct()
        if section:
            exams = exams.filter(subjects__class_name__contains=section).distinct()
        if exam_type:
            exams = exams.filter(exam_type=exam_type)
        if start_date:
            exams = exams.filter(start_date__gte=start_date)
        if end_date:
            exams = exams.filter(end_date__lte=end_date)
        
        serializer = ExamSerializer(exams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        print("DEBUG: Received exam data:", request.data)  # Debug log
        
        serializer = CreateExamSerializer(data=request.data)
        if not serializer.is_valid():
            print("DEBUG: Validation errors:", serializer.errors)  # Debug log
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            # Get current academic year
            current_year = datetime.now().year
            academic_year = f"{current_year}-{current_year + 1}"
            
            # Create exam
            exam = Exam.objects.create(
                tenant=request.user.tenant,
                name=data['name'],
                exam_type=data['exam_type'],
                academic_year=academic_year,
                start_date=data['start_date'],
                end_date=data['end_date'],
            )
            
            # Create exam subjects
            for subject_data in data['subjects']:
                ExamSubject.objects.create(
                    tenant=request.user.tenant,
                    exam=exam,
                    subject_name=subject_data['subject_name'],
                    class_name=f"{data['class_name']}-{data['section']}",
                    max_marks=subject_data['max_marks'],
                    passing_marks=subject_data['passing_marks'],
                    exam_date=subject_data['exam_date'],
                    duration_minutes=subject_data['duration_minutes'],
                )
            
            exam_serializer = ExamSerializer(exam)
            return Response(exam_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print("DEBUG: Error creating exam:", str(e))  # Debug log
            return Response(
                {'error': f'Failed to create exam: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET', 'PUT', 'DELETE'])
def exam_detail(request, exam_id):
    """Get, update or delete an exam"""
    if request.user.role not in ['super_admin', 'tenant_admin']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        exam = Exam.objects.get(id=exam_id, tenant=request.user.tenant)
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ExamSerializer(exam)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = ExamSerializer(exam, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        exam.delete()
        return Response({'message': 'Exam deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def exam_subjects(request, exam_id):
    """Get subjects for an exam"""
    if request.user.role not in ['super_admin', 'tenant_admin', 'teacher']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        exam = Exam.objects.get(id=exam_id, tenant=request.user.tenant)
        subjects = exam.subjects.all()
        serializer = ExamSubjectSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def mark_entry(request):
    """Enter marks for students in bulk"""
    if request.user.role not in ['super_admin', 'tenant_admin', 'teacher']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    exam_subject_id = request.data.get('exam_subject_id')
    marks_data = request.data.get('marks', [])
    
    if not exam_subject_id or not marks_data:
        return Response(
            {'error': 'exam_subject_id and marks are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        exam_subject = ExamSubject.objects.get(id=exam_subject_id, tenant=request.user.tenant)
        
        created_count = 0
        updated_count = 0
        
        for mark in marks_data:
            student_id = mark.get('student_id')
            marks_obtained = mark.get('marks_obtained')
            
            if student_id and marks_obtained is not None:
                result, created = Result.objects.update_or_create(
                    tenant=request.user.tenant,
                    student_id=student_id,
                    exam_subject=exam_subject,
                    defaults={'marks_obtained': marks_obtained}
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
        
        return Response({
            'message': 'Marks entered successfully',
            'created': created_count,
            'updated': updated_count,
        }, status=status.HTTP_201_CREATED)
        
    except ExamSubject.DoesNotExist:
        return Response({'error': 'Exam subject not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {'error': f'Failed to enter marks: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def student_results(request, student_id):
    """Get all results for a student"""
    if request.user.role not in ['super_admin', 'tenant_admin', 'teacher', 'student', 'parent']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    results = Result.objects.filter(
        tenant=request.user.tenant,
        student_id=student_id
    ).select_related('exam_subject', 'exam_subject__exam')
    
    serializer = ResultSerializer(results, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def exam_results(request, exam_id):
    """Get all results for an exam"""
    if request.user.role not in ['super_admin', 'tenant_admin', 'teacher']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    results = Result.objects.filter(
        tenant=request.user.tenant,
        exam_subject__exam_id=exam_id
    ).select_related('student', 'exam_subject')
    
    serializer = ResultSerializer(results, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

