# SETUP GUIDE - Multi-Tenant School Management System

## Current Status
✅ Backend structure created
✅ All Django models implemented
✅ Authentication system ready
✅ Tenant management APIs ready
✅ Multi-tenant middleware configured

## What's Been Built

### Backend (Django)
1. **Custom User Model** with 5 roles:
   - Super Admin
   - Tenant Admin
   - Student
   - Teacher
   - Parent

2. **Complete Database Models**:
   - Users & Authentication (User, SuperAdminSession, AuditLog)
   - Tenants (Tenant, TenantFeature)
   - Students (Student, AcademicRegistration)
   - Teachers (Teacher)
   - Parents (Parent, StudentParent)
   - Attendance (Attendance, TeacherAttendance)
   - Exams (Exam, ExamSubject, Result, AdmitCard)
   - Library (Book, BookIssue)
   - Transport (Bus, Route, BusAssignment)
   - Timetable (TimeSlot, Timetable)
   - Courses (Course, CourseEnrollment)

3. **Authentication APIs**:
   - Super Admin login (hardcoded credentials)
   - Tenant user login
   - Logout with IP tracking
   - JWT token management
   - Tenant Admin creation

4. **Tenant Management APIs**:
   - Create/List/Update/Delete tenants
   - Manage tenant features
   - Toggle features per tenant

5. **Security Features**:
   - IP address logging for all logins
   - Super Admin session tracking
   - Tenant Admin creation logs
   - Complete audit trail

## Next Steps

### 1. Database Setup (REQUIRED BEFORE RUNNING)

#### Option A: Use PostgreSQL (Recommended)
1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE school_management;
```
3. Update `.env` file with your PostgreSQL credentials

#### Option B: Use SQLite for Development
Update `settings.py` temporarily:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 2. Run Migrations
```bash
cd backend
.\venv\Scripts\Activate.ps1
python manage.py makemigrations
python manage.py migrate
```

### 3. Initialize Super Admin
```bash
python manage.py init_superadmin
```

### 4. Start Backend Server
```bash
python manage.py runserver
```

### 5. Test Authentication
Use the API_TESTING.md file to test:
1. Super Admin login at `/api/auth/super-admin/login/`
2. Create tenant at `/api/tenants/`
3. Create Tenant Admin
4. Test tenant user login

## What Still Needs to Be Built

### Backend APIs (Next Priority)
1. **Student Management APIs**
   - Create/List/Update students (Tenant Admin)
   - View own profile (Student)
   - Academic registration

2. **Teacher Management APIs**
   - Create/List/Update teachers (Tenant Admin)
   - View own profile (Teacher)

3. **Parent Management APIs**
   - Create/List/Update parents (Tenant Admin)
   - Link parents to students
   - View children's data (Parent)

4. **Attendance APIs**
   - Mark attendance (Teacher)
   - View attendance (Student, Parent, Teacher)

5. **Exam & Results APIs**
   - Create exams (Tenant Admin)
   - Enter results (Teacher)
   - View results (Student, Parent)
   - Generate admit cards

6. **Library APIs**
   - Manage books (Tenant Admin, Librarian)
   - Issue/Return books

7. **Transport APIs**
   - Manage buses & routes
   - Student bus assignments

8. **Timetable APIs**
   - Create/Update timetables
   - View timetables

### Frontend (Next.js)
1. **Authentication UI**
   - Login pages for each role
   - JWT token management
   - Protected routes

2. **Super Admin Dashboard**
   - Tenant management interface
   - Create Tenant Admins
   - View audit logs

3. **Tenant Admin Dashboard**
   - Student/Teacher/Parent management
   - School data management
   - Reports

4. **Student Dashboard**
   - View attendance
   - View results
   - Access courses
   - Library, Transport, Timetable views

5. **Teacher Dashboard**
   - Mark attendance
   - Enter results
   - View timetable

6. **Parent Dashboard**
   - View children's attendance
   - View children's results
   - Access counseling

## File Structure Created

```
backend/
├── manage.py
├── requirements.txt
├── .env (you need to create from .env.example)
├── README.md
├── API_TESTING.md
├── school_management/
│   ├── settings.py (configured)
│   ├── urls.py (configured)
│   └── wsgi.py
├── accounts/ (User management)
│   ├── models.py (User, Session, AuditLog)
│   ├── views.py (Auth endpoints)
│   ├── serializers.py
│   ├── urls.py
│   └── management/commands/init_superadmin.py
├── tenants/ (Multi-tenant)
│   ├── models.py (Tenant, TenantFeature)
│   ├── middleware.py (Tenant context)
│   ├── views.py (Tenant APIs)
│   ├── serializers.py
│   └── urls.py
├── students/ (Student management)
│   ├── models.py (Student, AcademicRegistration)
│   └── course_models.py (Course, Enrollment)
├── teachers/ (Teacher management)
│   └── models.py (Teacher)
├── parents/ (Parent management)
│   └── models.py (Parent, StudentParent)
├── attendance/ (Attendance tracking)
│   └── models.py (Attendance, TeacherAttendance)
├── exams/ (Exams & Results)
│   └── models.py (Exam, Result, AdmitCard)
├── library/ (Library management)
│   └── models.py (Book, BookIssue)
├── transport/ (Transport management)
│   └── models.py (Bus, Route, BusAssignment)
└── timetable/ (Timetable)
    └── models.py (TimeSlot, Timetable)
```

## Environment Variables (.env)

```
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_NAME=school_management
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

SUPER_ADMIN_EMAIL=superadmin@sms.com
SUPER_ADMIN_PASSWORD=SuperAdmin@2025

JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Testing Flow

1. **Start backend**: `python manage.py runserver`
2. **Login as Super Admin**:
   ```
   POST http://localhost:8000/api/auth/super-admin/login/
   Body: { "email": "superadmin@sms.com", "password": "SuperAdmin@2025" }
   ```
3. **Create a Tenant**:
   ```
   POST http://localhost:8000/api/tenants/
   Headers: Authorization: Bearer <token>
   Body: {
     "name": "Demo School",
     "email": "demo@school.com",
     "school_code": "SCH001",
     "features": ["attendance", "exams", "library"]
   }
   ```
4. **Create Tenant Admin**:
   ```
   POST http://localhost:8000/api/auth/tenant-admin/create/
   Headers: Authorization: Bearer <super_admin_token>
   Body: {
     "email": "admin@school.com",
     "password": "Admin@12345",
     "first_name": "John",
     "last_name": "Doe",
     "tenant_id": "<tenant_uuid>"
   }
   ```

## Questions?

Review:
- `README.md` - Setup instructions
- `API_TESTING.md` - API endpoints and testing
- Models in each app directory

The system is ready for:
1. Database setup
2. Migration execution
3. API testing
4. Frontend development
