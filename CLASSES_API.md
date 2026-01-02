# School Classes API Documentation

## Base URL
`http://localhost:8000/api/classes/`

## Authentication
All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Endpoints

### 1. List All Classes
**GET** `/api/classes/`

Get all classes for the current tenant.

**Response:**
```json
[
  {
    "id": "uuid",
    "grade": "8",
    "section": "A",
    "className": "Grade 8-A",
    "academicYear": "2024-2025",
    "classTeacher": "uuid",
    "classTeacherName": "John Doe",
    "studentCount": 45
  }
]
```

**Query Parameters:**
- `search` - Search by class name, grade, or section
- `grade` - Filter by grade
- `section` - Filter by section
- `academic_year` - Filter by academic year
- `class_teacher` - Filter by teacher ID

---

### 2. Get Class Details
**GET** `/api/classes/{id}/`

Get detailed information about a specific class.

**Response:**
```json
{
  "id": "uuid",
  "tenantId": "uuid",
  "grade": "8",
  "section": "A",
  "className": "Grade 8-A",
  "academicYear": "2024-2025",
  "classTeacher": "uuid",
  "classTeacherId": "uuid",
  "classTeacherDetails": {
    "id": "uuid",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@school.com",
    "employeeId": "T001",
    "department": "Mathematics"
  },
  "studentCount": 45,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

---

### 3. Create New Class
**POST** `/api/classes/`

Create a new class.

**Request Body:**
```json
{
  "grade": "8",
  "section": "A",
  "class_name": "Grade 8-A",  // Optional, auto-generated if not provided
  "academic_year": "2024-2025",
  "class_teacher": "uuid"  // Optional, teacher ID
}
```

**Response:**
```json
{
  "id": "uuid",
  "grade": "8",
  "section": "A",
  "className": "Grade 8-A",
  "academicYear": "2024-2025",
  "classTeacher": "uuid",
  "classTeacherDetails": {...},
  "studentCount": 0,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

---

### 4. Update Class
**PATCH** `/api/classes/{id}/`

Update an existing class (partial update).

**Request Body:**
```json
{
  "grade": "9",
  "section": "B",
  "class_name": "Grade 9-B",
  "class_teacher": "uuid"
}
```

**PUT** `/api/classes/{id}/`

Full update (all fields required).

---

### 5. Delete Class
**DELETE** `/api/classes/{id}/`

Delete a class. 

**Note:** Cannot delete a class that has students assigned. Students must be reassigned first.

**Response:**
```json
{
  "message": "Class deleted successfully"
}
```

**Error Response (if class has students):**
```json
{
  "error": "Cannot delete class with 45 students. Please reassign students first."
}
```

---

### 6. Get All Teachers
**GET** `/api/classes/teachers/`

Get all teachers available for class teacher assignment.

**Response:**
```json
[
  {
    "id": "uuid",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@school.com",
    "employeeId": "T001",
    "department": "Mathematics"
  }
]
```

---

### 7. Get Class Statistics
**GET** `/api/classes/statistics/`

Get statistics about classes in the current tenant.

**Response:**
```json
{
  "totalClasses": 10,
  "withTeachers": 8,
  "withoutTeachers": 2,
  "totalStudents": 450
}
```

---

## Error Responses

All endpoints return standard error responses:

**400 Bad Request**
```json
{
  "error": "Grade and Section are required"
}
```

**401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**404 Not Found**
```json
{
  "detail": "Not found."
}
```

**500 Internal Server Error**
```json
{
  "error": "An unexpected error occurred"
}
```

---

## Frontend Integration

The frontend uses `classService.ts` which provides the following methods:

```typescript
// Get all classes
await classService.getAllClasses()

// Get class by ID
await classService.getClassById(id)

// Create class
await classService.createClass({
  grade: '8',
  section: 'A',
  className: 'Grade 8-A',
  academicYear: '2024-2025',
  classTeacherId: 'teacher-uuid'
})

// Update class
await classService.updateClass(id, {
  grade: '9',
  classTeacherId: 'teacher-uuid'
})

// Delete class
await classService.deleteClass(id)

// Get all teachers
await classService.getAllTeachers()

// Get statistics
await classService.getStatistics()

// Search classes
await classService.searchClasses('Grade 8')

// Filter by academic year
await classService.filterByAcademicYear('2024-2025')
```

---

## Database Schema

### SchoolClass Table
```sql
CREATE TABLE school_classes (
    id UUID PRIMARY KEY,
    tenant_id UUID FOREIGN KEY REFERENCES tenants,
    grade VARCHAR(10),
    section VARCHAR(10),
    class_name VARCHAR(100),
    academic_year VARCHAR(20),
    class_teacher_id UUID FOREIGN KEY REFERENCES teachers,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(tenant_id, grade, section, academic_year)
);
```

### Student Table (Updated)
```sql
ALTER TABLE students 
ADD COLUMN school_class_id UUID 
FOREIGN KEY REFERENCES school_classes(id);
```

---

## Notes

1. **Auto-generated Class Name**: If `class_name` is not provided, it will be auto-generated as "Grade {grade}-{section}"

2. **Class Teacher as Counselor**: When a teacher is assigned as a class teacher, they automatically become the counselor for all students in that class

3. **Unique Constraint**: A class with the same grade, section, and academic year cannot exist twice in the same tenant

4. **Cascade Behavior**: 
   - If a teacher is deleted, their class teacher assignment is set to NULL
   - If a tenant is deleted, all their classes are deleted
   - Classes cannot be deleted if they have students assigned

5. **Student Count**: The `studentCount` field is computed dynamically from the number of students assigned to the class
