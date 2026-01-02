import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from students.models import Student, AcademicRegistration
from school_classes.models import SchoolClass

# Find the student
student = Student.objects.filter(admission_number='1254').first()
print(f"Student: {student}")

if student:
    # Create AcademicRegistration with class_name and section
    reg, created = AcademicRegistration.objects.get_or_create(
        tenant_id=student.tenant_id,
        student=student,
        academic_year='2024-25',
        defaults={
            'class_name': '8',
            'section': 'C',
            'is_current': True
        }
    )
    
    if created:
        print(f"✓ Created AcademicRegistration: {reg}")
    else:
        # Update existing registration
        reg.class_name = '8'
        reg.section = 'C'
        reg.is_current = True
        reg.save()
        print(f"✓ Updated AcademicRegistration: {reg}")
else:
    print("✗ Student not found")
