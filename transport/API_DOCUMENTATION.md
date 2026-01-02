# Transport System API Documentation

## Overview
The transport system allows tenant admins to manage vehicles, routes, and assign transport to students and teachers. Students and teachers can view their assigned transport and monthly fees.

## Models

### Vehicle
- **vehicle_number**: Vehicle registration number (e.g., AP-09-XY-1234)
- **vehicle_type**: bus, van, mini_bus
- **capacity**: Total seats
- **driver_name**: Driver's full name
- **driver_phone**: Contact number
- **status**: active, maintenance, inactive
- **monthly_fee**: Base monthly fee for this vehicle

### Route
- **route_number**: Route identifier (e.g., R1, R2)
- **route_name**: Descriptive name
- **stops**: JSON array of stops
- **pickup_time**: Morning pickup time
- **drop_time**: Afternoon drop time

### TransportAssignment
- **vehicle**: FK to Vehicle
- **route**: FK to Route
- **user**: Generic FK to Student or Teacher
- **pickup_point**: User's specific pickup location
- **monthly_fee**: Fee for this user
- **status**: active, pending, inactive
- **effective_from**: Start date

## API Endpoints

### Tenant Admin Endpoints

#### 1. Vehicles Management

**GET /api/transport/vehicles/**
- Get all vehicles for tenant
- Query params:
  - `status`: active/maintenance/inactive
  - `vehicle_type`: bus/van/mini_bus
  - `route`: Filter by route ID
  - `search`: Search by vehicle number or driver name
- Response: Array of vehicle objects

**POST /api/transport/vehicles/**
- Create new vehicle
- Body:
```json
{
  "vehicle_number": "AP-09-XY-1234",
  "vehicle_type": "bus",
  "capacity": 50,
  "driver_name": "Rajesh Kumar",
  "driver_phone": "9876543210",
  "driver_license": "DL123456",
  "status": "active",
  "monthly_fee": 2500
}
```

**GET /api/transport/vehicles/{id}/**
- Get single vehicle details

**PUT /api/transport/vehicles/{id}/**
- Update vehicle

**DELETE /api/transport/vehicles/{id}/**
- Delete vehicle

**GET /api/transport/vehicles/stats/**
- Get transport statistics
- Response:
```json
{
  "total_vehicles": 12,
  "active_vehicles": 10,
  "maintenance": 2,
  "total_students": 485,
  "total_routes": 8
}
```

**GET /api/transport/vehicles/{id}/assignments/**
- Get all assignments for a specific vehicle
- Response: Array of assignment objects with user details

#### 2. Routes Management

**GET /api/transport/routes/**
- Get all routes

**POST /api/transport/routes/**
- Create new route
- Body:
```json
{
  "route_number": "R1",
  "route_name": "Downtown Route",
  "stops": ["Green Park Plaza", "City Center", "Railway Station", "School"],
  "pickup_time": "07:30:00",
  "drop_time": "15:45:00",
  "distance_km": 15.5,
  "is_active": true
}
```

**GET /api/transport/routes/{id}/**
- Get single route

**PUT /api/transport/routes/{id}/**
- Update route

**DELETE /api/transport/routes/{id}/**
- Delete route

#### 3. Transport Assignments

**GET /api/transport/assignments/**
- Get all assignments
- Query params:
  - `vehicle_id`: Filter by vehicle
  - `status`: active/pending/inactive
  - `user_type`: student/teacher

**POST /api/transport/assignments/**
- Assign transport to student/teacher
- Body:
```json
{
  "vehicle_id": "uuid-here",
  "route_id": "uuid-here",
  "user_type": "student",
  "user_id": "student-uuid",
  "pickup_point": "Green Park Plaza",
  "monthly_fee": 2500,
  "effective_from": "2024-01-01",
  "status": "active"
}
```

**GET /api/transport/assignments/{id}/**
- Get assignment details

**POST /api/transport/assignments/{id}/deactivate/**
- Remove/deactivate assignment

**GET /api/transport/assignments/available_users/**
- Get list of students/teachers for assignment
- Query params:
  - `user_type`: student/teacher (required)
  - `search`: Search by name or ID
- Response:
```json
[
  {
    "id": "uuid",
    "name": "Rahul Sharma",
    "user_id": "S001",
    "class_section": "10-A",
    "type": "student"
  }
]
```

### Student/Teacher Endpoints

**GET /api/transport/assignments/my_transport/**
- Get current user's transport assignment
- Authentication required
- Automatically detects if user is student or teacher
- Response:
```json
{
  "id": "uuid",
  "user_name": "Rahul Sharma",
  "user_type": "student",
  "class_section": "10-A",
  "pickup_point": "Green Park Plaza",
  "monthly_fee": 2500,
  "status": "active",
  "vehicle_details": {
    "vehicle_number": "AP-09-XY-1234",
    "vehicle_type": "bus",
    "driver_name": "Rajesh Kumar",
    "driver_phone": "9876543210"
  },
  "route_details": {
    "route_number": "R1",
    "route_name": "Downtown Route",
    "pickup_time": "07:30",
    "drop_time": "15:45",
    "stops": ["Green Park", "City Center", "Railway Station", "School"]
  }
}
```

## Frontend Integration

### Tenant Admin Pages

1. **Vehicle List Page** (`/tenant-admin/transport`)
   - Displays all vehicles with stats
   - Filter by status, type, route
   - Search functionality
   - Actions: View assignments, Assign users, Edit vehicle

2. **Assign Transport Modal**
   - Select user type (student/teacher)
   - Search and select user
   - Choose pickup point
   - Set monthly fee
   - Set effective date

3. **View Assignments Modal**
   - Shows all users assigned to a vehicle
   - Summary cards (total, active, pending)
   - List with remove option

### Student/Teacher Pages

1. **My Transport Page** (`/student/transport` or `/teacher/transport`)
   - Shows assigned route details
   - Vehicle and driver information
   - Pickup point and timings
   - Route stops with visual map
   - Monthly fee
   - Bus capacity indicator

## Database Migration

Run these commands to create the database tables:

```bash
cd backend
python manage.py makemigrations transport
python manage.py migrate transport
```

## Testing the API

### Create a Vehicle
```bash
curl -X POST http://localhost:8000/api/transport/vehicles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "vehicle_number": "AP-09-XY-1234",
    "vehicle_type": "bus",
    "capacity": 50,
    "driver_name": "Rajesh Kumar",
    "driver_phone": "9876543210",
    "status": "active",
    "monthly_fee": 2500
  }'
```

### Create a Route
```bash
curl -X POST http://localhost:8000/api/transport/routes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "route_number": "R1",
    "route_name": "Downtown Route",
    "stops": ["Green Park", "City Center", "School"],
    "pickup_time": "07:30:00",
    "drop_time": "15:45:00"
  }'
```

### Assign Transport
```bash
curl -X POST http://localhost:8000/api/transport/assignments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "vehicle_id": "vehicle-uuid",
    "route_id": "route-uuid",
    "user_type": "student",
    "user_id": "student-uuid",
    "pickup_point": "Green Park Plaza",
    "monthly_fee": 2500,
    "effective_from": "2024-01-01"
  }'
```

### Get My Transport (Student/Teacher)
```bash
curl http://localhost:8000/api/transport/assignments/my_transport/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Payment Integration

For billing and payment:

1. Transport assignments with `status='active'` should be included in monthly bills
2. The `monthly_fee` field contains the amount to charge
3. Create a billing entry when assignment is created
4. Update billing when assignment is deactivated
5. Students/Teachers can view transport fee in their bill/payment page

## Notes

- All endpoints require authentication
- Tenant middleware automatically filters data by tenant
- Use generic foreign keys for flexible user assignment (students/teachers)
- Monthly fees can vary per user (different pickup points, etc.)
- Vehicle capacity tracking is automatic based on active assignments
