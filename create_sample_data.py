"""
Create sample data for testing
- 1 Tenant (School)
- 1 Tenant Admin
- 1 Teacher
- 1 Student
- 1 Parent
"""
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from accounts.models import User
from tenants.models import Tenant, TenantFeature
from teachers.models import Teacher
from students.models import Student
from parents.models import Parent, StudentParent
from school_classes.models import SchoolClass
from django.utils import timezone
import uuid

def create_sample_data():
    print("🏫 Creating Sample School Data...")
    print("=" * 60)
    
    # 1. Create Tenant (School)
    print("\n1️⃣ Creating Tenant (School)...")
    tenant, created = Tenant.objects.get_or_create(
        school_code='DEMO2025',
        defaults={
            'name': 'Demo High School',
            'email': 'contact@demohigh.edu',
            'phone': '+1-555-0100',
            'address': '123 Education Street, Learning City, LC 12345',
            'is_active': True,
        }
    )
    if created:
        print(f"   ✅ Tenant created: {tenant.name}")
        print(f"   📝 School Code: {tenant.school_code}")
        print(f"   🆔 Tenant ID: {tenant.id}")
        
        # Add features
        features = ['attendance', 'exams', 'library', 'transport', 'timetable', 'courses']
        for feature in features:
            TenantFeature.objects.create(tenant=tenant, feature=feature, is_enabled=True)
        print(f"   ✅ Features enabled: {', '.join(features)}")
    else:
        print(f"   ℹ️  Tenant already exists: {tenant.name}")
    
    # 2. Create Tenant Admin
    print("\n2️⃣ Creating Tenant Admin...")
    admin_user, created = User.objects.get_or_create(
        email='admin@demohigh.edu',
        defaults={
            'first_name': 'John',
            'last_name': 'Anderson',
            'phone': '+1-555-0101',
            'role': 'tenant_admin',
            'tenant': tenant,
            'is_active': True,
        }
    )
    if created:
        admin_user.set_password('Admin@2025')
        admin_user.save()
        print(f"   ✅ Tenant Admin created: {admin_user.full_name}")
        print(f"   📧 Email: {admin_user.email}")
        print(f"   🔑 Password: Admin@2025")
    else:
        print(f"   ℹ️  Tenant Admin already exists: {admin_user.email}")
    
    # 3. Create School Class
    print("\n3️⃣ Creating School Class...")
    school_class, created = SchoolClass.objects.get_or_create(
        tenant=tenant,
        class_name='Grade 10',
        section='A',
        defaults={
            'academic_year': '2024-2025',
            'class_teacher': None,
        }
    )
    if created:
        print(f"   ✅ Class created: {school_class.class_name} - Section {school_class.section}")
    else:
        print(f"   ℹ️  Class already exists: {school_class.class_name} - {school_class.section}")
    
    # 4. Create Teacher
    print("\n4️⃣ Creating Teacher...")
    teacher_user, created = User.objects.get_or_create(
        email='teacher@demohigh.edu',
        defaults={
            'first_name': 'Sarah',
            'last_name': 'Williams',
            'phone': '+1-555-0102',
            'role': 'teacher',
            'tenant': tenant,
            'is_active': True,
        }
    )
    if created:
        teacher_user.set_password('Teacher@2025')
        teacher_user.save()
        print(f"   ✅ Teacher User created: {teacher_user.full_name}")
        print(f"   📧 Email: {teacher_user.email}")
        print(f"   🔑 Password: Teacher@2025")
        
        # Create Teacher Profile
        teacher = Teacher.objects.create(
            tenant=tenant,
            user=teacher_user,
            employee_id='TCH2025001',
            date_of_birth='1990-03-20',
            gender='male',
            department='Mathematics',
            qualification='master',
            joining_date='2020-07-01',
        )
        print(f"   ✅ Teacher Profile created: {teacher.employee_id}")
        
        # Assign as class teacher
        school_class.class_teacher = teacher
        school_class.save()
        print(f"   ✅ Assigned as Class Teacher for {school_class.class_name}-{school_class.section}")
    else:
        print(f"   ℹ️  Teacher already exists: {teacher_user.email}")
        try:
            teacher = Teacher.objects.get(user=teacher_user)
        except Teacher.DoesNotExist:
            teacher = Teacher.objects.create(
                tenant=tenant,
                user=teacher_user,
                employee_id='TCH2025001',
                date_of_birth='1990-03-20',
                gender='male',
                department='Mathematics',
                qualification='master',
                joining_date='2020-07-01',
            )
            print(f"   ✅ Teacher Profile created: {teacher.employee_id}")
    
    # 5. Create Student
    print("\n5️⃣ Creating Student...")
    student_user, created = User.objects.get_or_create(
        email='student@demohigh.edu',
        defaults={
            'first_name': 'Michael',
            'last_name': 'Johnson',
            'phone': '+1-555-0103',
            'role': 'student',
            'tenant': tenant,
            'is_active': True,
        }
    )
    if created:
        student_user.set_password('Student@2025')
        student_user.save()
        print(f"   ✅ Student User created: {student_user.full_name}")
        print(f"   📧 Email: {student_user.email}")
        print(f"   🔑 Password: Student@2025")
        
        # Create Student Profile
        student = Student.objects.create(
            tenant=tenant,
            user=student_user,
            admission_number='STU2025001',
            date_of_birth='2010-05-15',
            gender='male',
            blood_group='O+',
            address='456 Student Lane, Learning City, LC 12345',
            emergency_contact_name='Mrs. Emily Johnson',
            emergency_contact_phone='+1-555-0104',
            school_class=school_class,
            class_name='Grade 10',
            section='A',
            admission_date='2024-06-01',
            academic_year='2024-2025',
        )
        print(f"   ✅ Student Profile created: {student.admission_number}")
        print(f"   📚 Class: {school_class.class_name}-{school_class.section}")
    else:
        print(f"   ℹ️  Student already exists: {student_user.email}")
        try:
            student = Student.objects.get(user=student_user)
        except Student.DoesNotExist:
            student = Student.objects.create(
                tenant=tenant,
                user=student_user,
                admission_number='STU2025001',
                date_of_birth='2010-05-15',
                gender='male',
                blood_group='O+',
                address='456 Student Lane, Learning City, LC 12345',
                emergency_contact_name='Mrs. Emily Johnson',
                emergency_contact_phone='+1-555-0104',
                school_class=school_class,
                class_name='Grade 10',
                section='A',
                admission_date='2024-06-01',
                academic_year='2024-2025',
            )
            print(f"   ✅ Student Profile created: {student.admission_number}")
    
    # 6. Create Parent
    print("\n6️⃣ Creating Parent...")
    parent_user, created = User.objects.get_or_create(
        email='parent@demohigh.edu',
        defaults={
            'first_name': 'Emily',
            'last_name': 'Johnson',
            'phone': '+1-555-0105',
            'role': 'parent',
            'tenant': tenant,
            'is_active': True,
        }
    )
    if created:
        parent_user.set_password('Parent@2025')
        parent_user.save()
        print(f"   ✅ Parent User created: {parent_user.full_name}")
        print(f"   📧 Email: {parent_user.email}")
        print(f"   🔑 Password: Parent@2025")
        
        # Create Parent Profile
        parent = Parent.objects.create(
            tenant=tenant,
            user=parent_user,
            relation='mother',
            occupation='Software Engineer',
            address='456 Student Lane, Learning City, LC 12345',
        )
        print(f"   ✅ Parent Profile created")
    else:
        print(f"   ℹ️  Parent already exists: {parent_user.email}")
        try:
            parent = Parent.objects.get(user=parent_user)
        except Parent.DoesNotExist:
            parent = Parent.objects.create(
                tenant=tenant,
                user=parent_user,
                relation='mother',
                occupation='Software Engineer',
                address='456 Student Lane, Learning City, LC 12345',
            )
            print(f"   ✅ Parent Profile created")
    
    # Link Parent to Student (if not already linked)
    if not StudentParent.objects.filter(student=student, parent=parent).exists():
        StudentParent.objects.create(
            tenant=tenant,
            student=student,
            parent=parent,
            is_primary=True,
        )
        print(f"   ✅ Linked to Student: {student.user.full_name}")
    else:
        print(f"   ℹ️  Already linked to Student: {student.user.full_name}")
    
    print("\n" + "=" * 60)
    print("✅ Sample data creation completed!")
    print("=" * 60)
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"   🏫 School: {tenant.name}")
    print(f"   👤 Tenant Admin: {admin_user.full_name}")
    print(f"   👨‍🏫 Teacher: {teacher_user.full_name}")
    print(f"   👨‍🎓 Student: {student_user.full_name}")
    print(f"   👨‍👩‍👧 Parent: {parent_user.full_name}")
    print("\n🔑 All passwords: Check TEST_CREDENTIALS.md")

if __name__ == '__main__':
    create_sample_data()
