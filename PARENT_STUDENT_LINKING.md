# Student-Parent Relationship & Parent Dashboard

## Overview
This system allows linking students to their parents/guardians and enables parents to view their children's data (attendance, results, etc.) while maintaining proper access control.

---

## Architecture

### Database Structure
```
Student (OneToOne with User)
    ↓
StudentParent (Link Table)
    ↓
Parent (OneToOne with User)
```

### Key Models
- **Student**: Contains student profile data
- **Parent**: Contains parent/guardian profile data  
- **StudentParent**: Links students to parents with additional metadata
  - `is_primary`: Marks primary guardian
  - Unique constraint on (student, parent) pair
  - Tracks relation type (father, mother, guardian)

---

## How It Works

### Step 1: Create Student
```http
POST /api/students/
{
  "first_name": "Rahul",
  "last_name": "Kumar",
  "email": "rahul.kumar@school.com",
  "password": "Student@123",
  "admission_number": "STU2024001",
  "class_name": "10",
  "section": "A",
  "roll_number": "15"
}
```

### Step 2: Create Parent
```http
POST /api/parents/
{
  "first_name": "Rajesh",
  "last_name": "Kumar",
  "email": "rajesh.kumar@gmail.com",
  "password": "Parent@123",
  "phone": "+919876543210",
  "relation": "father",
  "occupation": "Business Man"
}
```

### Step 3: Link Student to Parent
```http
POST /api/parents/link-student/
Authorization: Bearer {TENANT_ADMIN_TOKEN}
{
  "student_id": "uuid-of-student-rahul",
  "parent_id": "uuid-of-parent-rajesh",
  "is_primary": true
}
```

**What happens:**
- Creates StudentParent record
- Links Rahul (student) to Rajesh (father)
- Marks as primary guardian
- Validates both belong to same tenant

---

## API Endpoints

### For Tenant Admin

#### 1. Link Student to Parent
```http
POST /api/parents/link-student/
Body: {
  "student_id": "uuid",
  "parent_id": "uuid",
  "is_primary": true/false
}
```
**Use Case:** When enrolling a student, link them to their parent(s)

#### 2. Get Student's Parents
```http
GET /api/parents/student/{student_id}/parents/
```
**Returns:** All parents linked to this student
**Use Case:** View who can access this student's data

#### 3. Get Parent's Children
```http
GET /api/parents/parent/{parent_id}/children/
```
**Returns:** All students linked to this parent
**Use Case:** Admin viewing a parent's children list

#### 4. Unlink Student from Parent
```http
DELETE /api/parents/unlink/{link_id}/
```
**Use Case:** Remove parent access (e.g., custody changes)

---

### For Parent User (Logged In)

#### 1. Get My Children
```http
GET /api/parents/my-children/
Authorization: Bearer {PARENT_LOGIN_TOKEN}
```
**Returns:**
```json
[
  {
    "id": "student-uuid",
    "admission_number": "STU2024001",
    "first_name": "Rahul",
    "last_name": "Kumar",
    "class_name": "10",
    "section": "A",
    "roll_number": "15",
    "is_primary": true
  }
]
```
**Use Case:** Parent dashboard showing all their children

#### 2. Get Child's Attendance
```http
GET /api/parents/child/{student_id}/attendance/
Authorization: Bearer {PARENT_LOGIN_TOKEN}
Query Params: ?start_date=2024-01-01&end_date=2024-12-31&status=absent
```
**Returns:**
```json
{
  "student": {
    "id": "uuid",
    "name": "Rahul Kumar",
    "admission_number": "STU2024001",
    "class": "10",
    "section": "A"
  },
  "statistics": {
    "total_days": 180,
    "present": 165,
    "absent": 10,
    "late": 5,
    "attendance_percentage": 91.67
  },
  "records": [
    {
      "id": "uuid",
      "date": "2024-12-24",
      "status": "present",
      "status_display": "Present",
      "remarks": null,
      "marked_by": "Teacher Name",
      "marked_at": "2024-12-24T09:00:00Z"
    }
  ]
}
```
**Access Control:** 
- Parent can ONLY access their own children's data
- System verifies StudentParent link exists
- 403 error if trying to access other students

#### 3. Get All Children's Attendance Summary
```http
GET /api/parents/dashboard/attendance/
Authorization: Bearer {PARENT_LOGIN_TOKEN}
```
**Returns:** Quick overview of all children (last 30 days)
```json
{
  "parent": {
    "id": "uuid",
    "name": "Rajesh Kumar",
    "relation": "Father"
  },
  "children": [
    {
      "student": {
        "id": "uuid",
        "name": "Rahul Kumar",
        "class": "10",
        "section": "A"
      },
      "statistics": {
        "total_days": 20,
        "present": 18,
        "absent": 2,
        "attendance_percentage": 90.0
      },
      "is_primary": true
    }
  ]
}
```

---

## Access Control Logic

### Security Checks in `get_child_attendance`:
```python
1. Verify student exists in tenant
2. Check user role:
   - If parent:
     * Verify Parent profile exists
     * Verify StudentParent link exists
     * Reject if no link (403 Forbidden)
   - If tenant_admin/teacher:
     * Allow access
   - Else:
     * Reject (403 Forbidden)
3. Return filtered data
```

### What Parents Can See:
✅ Their own children's attendance  
✅ Their own children's results (when implemented)  
✅ Their own children's assignments  
❌ Other students' data  
❌ Teacher information  
❌ Other parents' data  

---

## Example Scenario

### Scenario: Father wants to check son's attendance

**1. Father logs in:**
```http
POST /api/auth/login/
{
  "email": "rajesh.kumar@gmail.com",
  "password": "Parent@123"
}
```
Gets JWT token with role="parent"

**2. View all children:**
```http
GET /api/parents/my-children/
Authorization: Bearer {token}
```
Returns: Rahul Kumar (son)

**3. Check Rahul's attendance:**
```http
GET /api/parents/child/rahul-uuid/attendance/?start_date=2024-12-01
Authorization: Bearer {token}
```
Returns: December attendance with statistics

**4. System validates:**
- ✅ Token valid
- ✅ User is parent (Rajesh)
- ✅ StudentParent link exists (Rahul → Rajesh)
- ✅ Both in same tenant
- ✅ Returns data

**5. If father tries to access another student:**
```http
GET /api/parents/child/other-student-uuid/attendance/
```
Returns: **403 Forbidden** "You do not have permission..."

---

## Frontend Implementation

### Parent Dashboard Component Structure:
```
Parent Dashboard
├── My Children Cards
│   ├── Student 1 Card
│   │   ├── Name, Class, Section
│   │   ├── Attendance %
│   │   └── View Details Button
│   └── Student 2 Card
│
└── Child Detail View
    ├── Attendance Tab
    │   ├── Calendar View
    │   ├── Statistics
    │   └── Date Range Filter
    ├── Results Tab (future)
    └── Assignments Tab (future)
```

### Frontend Service (TypeScript):
```typescript
// services/parentService.ts
export const parentService = {
  // Get my children
  async getMyChildren() {
    return await apiClient.get('/parents/my-children/');
  },
  
  // Get child attendance
  async getChildAttendance(studentId: string, filters?: {
    start_date?: string;
    end_date?: string;
    status?: string;
  }) {
    return await apiClient.get(`/parents/child/${studentId}/attendance/`, {
      params: filters
    });
  },
  
  // Get all children attendance summary
  async getChildrenAttendance() {
    return await apiClient.get('/parents/dashboard/attendance/');
  }
};
```

---

## Multiple Children Support

A parent can have multiple children:
```
Father (Rajesh Kumar)
├── Son 1: Rahul Kumar (Class 10-A)
├── Son 2: Rohan Kumar (Class 8-B)
└── Daughter: Priya Kumar (Class 6-A)
```

Each link is separate:
- StudentParent(Rahul → Rajesh, is_primary=true)
- StudentParent(Rohan → Rajesh, is_primary=true)
- StudentParent(Priya → Rajesh, is_primary=true)

Parent can view all three children's data.

---

## Multiple Parents Support

A student can have multiple parents/guardians:
```
Student: Rahul Kumar
├── Father: Rajesh Kumar (primary=true)
└── Mother: Sunita Kumar (primary=false)
```

Both parents can login and view Rahul's data.

---

## Future Enhancements

### 1. Results/Exams API
```http
GET /api/parents/child/{student_id}/results/
GET /api/parents/child/{student_id}/exam/{exam_id}/
```

### 2. Assignments API
```http
GET /api/parents/child/{student_id}/assignments/
GET /api/parents/child/{student_id}/assignment/{assignment_id}/
```

### 3. Fee Payments API
```http
GET /api/parents/child/{student_id}/fees/
POST /api/parents/child/{student_id}/pay-fee/
```

### 4. Communication
```http
POST /api/parents/message-teacher/
GET /api/parents/notifications/
```

### 5. Leave Requests
```http
POST /api/parents/child/{student_id}/leave-request/
GET /api/parents/child/{student_id}/leave-requests/
```

---

## Testing the Flow

### 1. As Tenant Admin:
```bash
# Create student and parent
POST /api/students/ → Student ID: ABC123
POST /api/parents/ → Parent ID: XYZ789

# Link them
POST /api/parents/link-student/
{
  "student_id": "ABC123",
  "parent_id": "XYZ789",
  "is_primary": true
}
```

### 2. As Parent (login with parent credentials):
```bash
# View my children
GET /api/parents/my-children/
→ Returns: [Student ABC123]

# View child attendance
GET /api/parents/child/ABC123/attendance/
→ Returns: Attendance records + statistics
```

### 3. Try unauthorized access:
```bash
# Parent tries to view another student
GET /api/parents/child/DIFFERENT-STUDENT/attendance/
→ Returns: 403 Forbidden
```

---

## Summary

✅ **Created:** StudentParent linking system  
✅ **Created:** Parent dashboard APIs  
✅ **Implemented:** Access control (parents can only see their children)  
✅ **Supports:** Multiple children per parent  
✅ **Supports:** Multiple parents per student  
✅ **Ready for:** Results, assignments, fees (same pattern)  

The system is now ready for parents to view their children's attendance. You can extend this pattern for results, assignments, and other student data by following the same access control logic!
