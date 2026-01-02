import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from students.models import Student
from school_classes.models import SchoolClass

# Find Abhishek
abhishek = Student.objects.get(admission_number='13338')
print(f'Found: {abhishek.user.full_name}')
print(f'Current: class_name={abhishek.class_name}, school_class_id={abhishek.school_class_id}, section={abhishek.section}')

# Find the Grade 9 class
grade_9 = SchoolClass.objects.filter(class_name__icontains='9').first()
if grade_9:
    print(f'\nFound class: {grade_9.class_name} (ID: {grade_9.id})')
    abhishek.school_class = grade_9
    abhishek.save()
    print(f'✓ Updated Abhishek\'s school_class to {grade_9.class_name}')
else:
    print('\n✗ Could not find Grade 9 class')

# Verify
abhishek.refresh_from_db()
print(f'\nAfter update: school_class_id={abhishek.school_class_id}')
