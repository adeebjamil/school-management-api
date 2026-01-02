from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Book, BookIssue
from .serializers import (
    BookSerializer, BookIssueSerializer,
    IssueBookSerializer, ReturnBookSerializer
)
from students.models import Student


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        print(f"DEBUG Library: Tenant = {tenant}, Tenant ID = {tenant.id if tenant else 'None'}")
        queryset = Book.objects.filter(tenant=tenant)
        print(f"DEBUG Library: Found {queryset.count()} books")
        
        # Search
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(isbn__icontains=search) |
                Q(category__icontains=search)
            )
        
        # Filter by category
        category = self.request.query_params.get('category', '')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by availability
        availability = self.request.query_params.get('availability', '')
        if availability == 'available':
            queryset = queryset.filter(available_copies__gt=0)
        elif availability == 'unavailable':
            queryset = queryset.filter(available_copies=0)
        
        print(f"DEBUG Library: After filters {queryset.count()} books")
        return queryset.order_by('title')
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get list of unique categories"""
        tenant = request.tenant
        categories = Book.objects.filter(tenant=tenant).values_list('category', flat=True).distinct()
        return Response(list(categories))
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get library statistics"""
        tenant = request.tenant
        
        total_books = Book.objects.filter(tenant=tenant).count()
        total_copies = Book.objects.filter(tenant=tenant).aggregate(
            total=Sum('total_copies')
        )['total'] or 0
        available_copies = Book.objects.filter(tenant=tenant).aggregate(
            available=Sum('available_copies')
        )['available'] or 0
        issued_count = BookIssue.objects.filter(
            tenant=tenant,
            status='issued'
        ).count()
        overdue_count = BookIssue.objects.filter(
            tenant=tenant,
            status='issued',
            due_date__lt=timezone.now().date()
        ).count()
        
        return Response({
            'total_books': total_books,
            'total_copies': total_copies,
            'available_copies': available_copies,
            'issued_count': issued_count,
            'overdue_count': overdue_count
        })


class BookIssueViewSet(viewsets.ModelViewSet):
    serializer_class = BookIssueSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        queryset = BookIssue.objects.filter(tenant=tenant).select_related(
            'book', 'user'
        )
        
        # Filter by status
        issue_status = self.request.query_params.get('status', '')
        if issue_status:
            queryset = queryset.filter(status=issue_status)
        
        # Filter by user
        user_id = self.request.query_params.get('user_id', '')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-issue_date')
    
    @action(detail=False, methods=['post'])
    def issue_book(self, request):
        """Issue a book to a student/teacher"""
        serializer = IssueBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tenant = request.tenant
        book_id = serializer.validated_data['book_id']
        user_id = serializer.validated_data['user_id']
        duration_weeks = serializer.validated_data['duration_weeks']
        remarks = serializer.validated_data.get('remarks', '')
        
        # Check if book exists and is available
        try:
            book = Book.objects.get(id=book_id, tenant=tenant)
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if book.available_copies < 1:
            return Response(
                {'error': 'No copies available for this book'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate due date (duration in weeks, multiples of 7 days)
        issue_date = timezone.now().date()
        due_date = issue_date + timedelta(weeks=duration_weeks)
        
        # Create issue record
        issue = BookIssue.objects.create(
            tenant=tenant,
            book=book,
            user_id=user_id,
            issue_date=issue_date,
            due_date=due_date,
            status='issued',
            remarks=remarks
        )
        
        # Decrease available copies
        book.available_copies -= 1
        book.save()
        
        return Response(
            BookIssueSerializer(issue).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def return_book(self, request):
        """Return a book"""
        serializer = ReturnBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tenant = request.tenant
        issue_id = serializer.validated_data['issue_id']
        condition = serializer.validated_data['condition']
        remarks = serializer.validated_data.get('remarks', '')
        
        # Get issue record
        try:
            issue = BookIssue.objects.get(id=issue_id, tenant=tenant)
        except BookIssue.DoesNotExist:
            return Response(
                {'error': 'Issue record not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if issue.status != 'issued':
            return Response(
                {'error': 'Book is not currently issued'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate fine (1 rupee per day after due date)
        return_date = timezone.now().date()
        fine_amount = 0
        if return_date > issue.due_date:
            days_overdue = (return_date - issue.due_date).days
            fine_amount = days_overdue * 1.0  # 1 rupee per day
        
        # Update issue record
        issue.return_date = return_date
        issue.fine_amount = fine_amount
        
        if condition == 'lost':
            issue.status = 'lost'
        elif condition == 'damaged':
            issue.status = 'damaged'
        else:
            issue.status = 'returned'
            # Only increase available copies if book is returned in good condition
            issue.book.available_copies += 1
            issue.book.save()
        
        if remarks:
            issue.remarks = remarks
        
        issue.save()
        
        return Response(BookIssueSerializer(issue).data)
    
    @action(detail=False, methods=['get'])
    def my_books(self, request):
        """Get books issued to current user (student/teacher)"""
        user = request.user
        tenant = request.tenant
        
        issues = BookIssue.objects.filter(
            tenant=tenant,
            user=user,
            status='issued'
        ).select_related('book')
        
        serializer = BookIssueSerializer(issues, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue books"""
        tenant = request.tenant
        today = timezone.now().date()
        
        overdue_issues = BookIssue.objects.filter(
            tenant=tenant,
            status='issued',
            due_date__lt=today
        ).select_related('book', 'user')
        
        serializer = BookIssueSerializer(overdue_issues, many=True)
        return Response(serializer.data)

