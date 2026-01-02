from rest_framework import serializers
from .models import Book, BookIssue
from accounts.models import User


class BookSerializer(serializers.ModelSerializer):
    available_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'publisher', 'publication_year',
            'category', 'total_copies', 'available_copies', 'shelf_location',
            'available_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set available_copies equal to total_copies on creation if not provided
        if 'available_copies' not in validated_data:
            validated_data['available_copies'] = validated_data.get('total_copies', 1)
        return super().create(validated_data)
    
    def get_available_status(self, obj):
        if obj.available_copies > 0:
            return 'available'
        return 'unavailable'


class BookIssueSerializer(serializers.ModelSerializer):
    book_details = BookSerializer(source='book', read_only=True)
    user_details = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()
    calculated_fine = serializers.SerializerMethodField()
    
    class Meta:
        model = BookIssue
        fields = [
            'id', 'book', 'book_details', 'user', 'user_details',
            'issue_date', 'due_date', 'return_date', 'status',
            'fine_amount', 'remarks', 'days_overdue', 'calculated_fine'
        ]
        read_only_fields = ['id', 'issue_date', 'fine_amount']
    
    def get_user_details(self, obj):
        return {
            'id': str(obj.user.id),
            'name': obj.user.full_name,
            'email': obj.user.email,
            'role': obj.user.role
        }
    
    def get_days_overdue(self, obj):
        if obj.status == 'returned' or not obj.due_date:
            return 0
        
        from django.utils import timezone
        today = timezone.now().date()
        if today > obj.due_date:
            return (today - obj.due_date).days
        return 0
    
    def get_calculated_fine(self, obj):
        days_overdue = self.get_days_overdue(obj)
        if days_overdue > 0:
            # 1 rupee per day after due date
            return float(days_overdue)
        return 0.0


class IssueBookSerializer(serializers.Serializer):
    book_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    duration_weeks = serializers.IntegerField(min_value=1, max_value=12)
    remarks = serializers.CharField(required=False, allow_blank=True)
    
    def validate_duration_weeks(self, value):
        # Duration must be in multiples of 7 days (1 week)
        if value < 1:
            raise serializers.ValidationError("Duration must be at least 1 week")
        return value


class ReturnBookSerializer(serializers.Serializer):
    issue_id = serializers.UUIDField()
    condition = serializers.ChoiceField(
        choices=['good', 'damaged', 'lost'],
        default='good'
    )
    remarks = serializers.CharField(required=False, allow_blank=True)
