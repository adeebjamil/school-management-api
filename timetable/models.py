import uuid
from django.db import models


class TimeSlot(models.Model):
    """Time slots for classes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    period_number = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'timetable_slots'
        ordering = ['period_number']
        unique_together = ('tenant', 'period_number')
    
    def __str__(self):
        return f"Period {self.period_number}: {self.start_time} - {self.end_time}"


class Timetable(models.Model):
    """Timetable entries"""
    DAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    class_name = models.CharField(max_length=50)
    section = models.CharField(max_length=10, blank=True, null=True)
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, related_name='timetable_entries')
    room_number = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    academic_year = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'timetables'
        ordering = ['day', 'time_slot__period_number']
        indexes = [
            models.Index(fields=['tenant', 'class_name', 'section']),
        ]
    
    def __str__(self):
        return f"{self.class_name} - {self.day} - {self.subject}"
