# Multi-Tenant School Management System - Backend

## Technology Stack
- Django 5.1.4
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Multi-tenant architecture

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database
1. Create a PostgreSQL database named `school_management`
2. Copy `.env.example` to `.env`
3. Update database credentials in `.env`:
```
DB_NAME=school_management
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Initialize Super Admin
```bash
python manage.py init_superadmin
```
This creates the Super Admin with credentials from `.env`:
- Email: superadmin@sms.com
- Password: SuperAdmin@2025

### 5. Run Development Server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/super-admin/login/` - Super Admin login (hardcoded credentials)
- `POST /api/auth/login/` - Tenant user login (Tenant Admin, Student, Teacher, Parent)
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/token/refresh/` - Refresh JWT token

### User Management
- `GET /api/auth/profile/` - Get current user profile
- `POST /api/auth/tenant-admin/create/` - Create Tenant Admin (Super Admin only)

### Audit & Logs
- `GET /api/auth/admin-sessions/` - Get Super Admin sessions
- `GET /api/auth/tenant-admin-logs/` - Get Tenant Admin creation logs
- `GET /api/auth/audit-logs/` - Get audit logs (role-based)

## Multi-Tenant Architecture

### Tenant Identification
1. **Subdomain-based**: `school1.domain.com` → identifies tenant by `school1` slug
2. **Header-based** (for development): Send `X-Tenant-ID` header with tenant UUID
3. **Query parameter** (for development): Add `?tenant_id=<uuid>` to requests

### Tenant Middleware
The `TenantMiddleware` automatically:
- Extracts tenant from subdomain/header/query
- Injects `request.tenant` and `request.tenant_id`
- Skips tenant resolution for Super Admin paths (`/super-admin/`)

### Data Isolation
All tenant-specific models include:
- `tenant = ForeignKey('tenants.Tenant')`
- Queries automatically filtered by tenant in views

## Models Structure

### Core Models
- **User** - Custom user model with roles (super_admin, tenant_admin, student, teacher, parent)
- **Tenant** - School/Organization
- **TenantFeature** - Features enabled for each tenant

### User Profiles
- **Student** - Student information with academic details
- **Teacher** - Teacher information with professional details
- **Parent** - Parent/Guardian information
- **StudentParent** - Link students to parents

### Academic Models
- **Course** - Courses/Subjects
- **CourseEnrollment** - Student course enrollments
- **Attendance** - Student attendance records
- **TeacherAttendance** - Teacher attendance records
- **Exam** - Exam definitions
- **ExamSubject** - Exam subjects with marks
- **Result** - Student exam results
- **AdmitCard** - Exam admit cards

### Infrastructure Models
- **Book** - Library books
- **BookIssue** - Book issue tracking
- **Bus** - School buses
- **Route** - Bus routes
- **BusAssignment** - Student bus assignments
- **TimeSlot** - Class time slots
- **Timetable** - Class timetables

### Audit Models
- **SuperAdminSession** - Track Super Admin logins
- **TenantAdminCreationLog** - Track Tenant Admin creation
- **AuditLog** - General audit trail

## Role-Based Access Control

### Super Admin
- Only ONE
- Hardcoded credentials
- Can create tenants
- Can create Tenant Admins
- View all audit logs
- No tenant affiliation

### Tenant Admin
- One per tenant (or multiple)
- Created by Super Admin
- Manage school users
- View tenant-specific data

### Student/Teacher/Parent
- Created by Tenant Admin
- Access role-specific features
- View own data only

## IP Logging & Security
- All logins tracked with IP address
- Super Admin sessions logged
- Tenant Admin creation logged with IP
- Complete audit trail for all actions

## Next Steps
1. Configure PostgreSQL
2. Update `.env` file
3. Run migrations
4. Initialize Super Admin
5. Start development server
6. Test authentication endpoints
