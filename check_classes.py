import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from students.models import Student
from courses.models import Course

print('\n=== STUDENTS ===')
students = Student.objects.all()
for s in students:
    print(f'{s.user.full_name}:')
    print(f'  class_name: {s.class_name}')
    print(f'  school_class_id: {s.school_class_id}')
    print(f'  section: {s.section}')
    print()

print('\n=== COURSES ===')
courses = Course.objects.all()
for c in courses:
    print(f'{c.course_name}:')
    print(f'  school_class_id: {c.school_class_id}')
    print(f'  section: {c.section}')
    print()
