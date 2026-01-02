# Test Credentials for Demo School

This document contains all test account credentials created for demonstration purposes.

## School Information
- **School Name**: Demo High School
- **School Code**: `DEMO2025`
- **Academic Year**: 2024-2025

---

## Super Admin Account
**Purpose**: System-wide administrator access

- **Email**: `superadmin@sms.com`
- **Password**: `SuperAdmin@2025`
- **Role**: Super Admin
- **Access**: Full system access across all tenants

---

## 1. Tenant Admin
**Purpose**: School administrator with full access to Demo High School

- **Name**: John Anderson
- **Email**: `admin@demohigh.edu`
- **Password**: `Admin@2025`
- **Role**: Tenant Admin
- **School**: Demo High School (DEMO2025)
- **Access**: Full administrative access to school management

---

## 2. Teacher Account
**Purpose**: Teacher account for classroom and student management

- **Name**: Sarah Williams
- **Email**: `teacher@demohigh.edu`
- **Password**: `Teacher@2025`
- **Role**: Teacher
- **Employee ID**: TCH2025001
- **Department**: Mathematics
- **Qualification**: Master's Degree
- **Date of Birth**: March 20, 1990
- **Joining Date**: July 1, 2020
- **Class Teacher**: Grade 10 - A
- **School**: Demo High School (DEMO2025)
- **Access**: 
  - View and manage assigned classes
  - Mark attendance
  - Enter grades and assessments
  - View student information
  - Manage timetable

---

## 3. Student Account
**Purpose**: Student portal access for viewing schedules, grades, etc.

- **Name**: Michael Johnson
- **Email**: `student@demohigh.edu`
- **Password**: `Student@2025`
- **Role**: Student
- **Admission Number**: STU2025001
- **Class**: Grade 10 - A
- **Section**: A
- **Date of Birth**: May 15, 2010
- **Blood Group**: O+
- **Admission Date**: June 1, 2024
- **Academic Year**: 2024-2025
- **School**: Demo High School (DEMO2025)
- **Access**:
  - View personal timetable
  - View attendance records
  - View grades and report cards
  - View assignments
  - Access learning materials

---

## 4. Parent Account
**Purpose**: Parent portal access to monitor student progress

- **Name**: Emily Johnson
- **Email**: `parent@demohigh.edu`
- **Password**: `Parent@2025`
- **Role**: Parent
- **Relation**: Mother
- **Occupation**: Software Engineer
- **Linked Student**: Michael Johnson (STU2025001)
- **School**: Demo High School (DEMO2025)
- **Access**:
  - View child's attendance
  - View child's grades and report cards
  - View child's timetable
  - Receive notifications about child's activities
  - View teacher remarks
  - Communication with teachers

---

## Quick Login Guide

### For Local Development (http://localhost:3000)
1. Navigate to http://localhost:3000
2. Select your role or use the appropriate login
3. Enter email and password from above
4. Use school code `DEMO2025` if prompted

### For Production (https://school-management-theta-five.vercel.app)
1. Navigate to the production URL
2. Follow the same login process as local

---

## School Features Enabled

The following features are enabled for Demo High School:

1. ✅ **Student Management** - Manage student records and enrollment
2. ✅ **Teacher Management** - Manage teacher profiles and assignments
3. ✅ **Class Management** - Manage classes, sections, and schedules
4. ✅ **Attendance** - Track and manage student attendance
5. ✅ **Exams & Grades** - Create exams and manage grading
6. ✅ **Timetable** - Create and manage class timetables
7. ✅ **Library Management** - Manage library books and borrowing
8. ✅ **Parent Portal** - Parents can monitor student progress
9. ✅ **Transport Management** - Manage school transport and routes
10. ✅ **Fee Management** - Manage fee collection and tracking

---

## Sample Data Structure

### Class Information
- **Class**: Grade 10
- **Section**: A
- **Academic Year**: 2024-2025
- **Class Teacher**: Sarah Williams
- **Students**: 1 (Michael Johnson)

### Parent-Student Relationship
- **Parent**: Emily Johnson (Mother)
- **Student**: Michael Johnson
- **Relationship**: Primary Contact

---

## Notes for Testing

1. **Password Policy**: All test passwords follow the format `[Role]@2025`
2. **Email Format**: All test emails use `[role]@demohigh.edu` format
3. **School Code**: Always use `DEMO2025` for this demo school
4. **Data Persistence**: Local database stores all changes; production uses PostgreSQL on Render
5. **Reset Data**: Run `python create_sample_data.py` to recreate sample data if needed

---

## Security Notes

⚠️ **IMPORTANT**: These are TEST CREDENTIALS only!

- These credentials are for demonstration purposes only
- Never use these credentials in a real production environment
- Always create strong, unique passwords for production use
- Regularly update passwords and review access permissions
- Enable two-factor authentication for production systems

---

## Support

For issues or questions about these test accounts:
1. Check the console logs for error messages
2. Verify database connection in Django admin
3. Ensure migrations are up to date: `python manage.py migrate`
4. Contact system administrator

---

**Last Updated**: January 2, 2026
**Created By**: create_sample_data.py script
**Database**: PostgreSQL (Local: school_management | Production: Render)
