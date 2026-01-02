# API Testing Guide

## 1. Super Admin Login

**Endpoint:** `POST http://localhost:8000/api/auth/super-admin/login/`

**Request Body:**
```json
{
    "email": "superadmin@sms.com",
    "password": "SuperAdmin@2025"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": "uuid",
        "email": "superadmin@sms.com",
        "full_name": "Super Admin",
        "role": "super_admin"
    },
    "session_id": "uuid"
}
```

## 2. Create Tenant (Need to implement tenant APIs)

## 3. Create Tenant Admin

**Endpoint:** `POST http://localhost:8000/api/auth/tenant-admin/create/`

**Headers:**
```
Authorization: Bearer <super_admin_access_token>
```

**Request Body:**
```json
{
    "email": "admin@school1.com",
    "password": "Admin@12345",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "tenant_id": "<tenant_uuid>"
}
```

**Response:**
```json
{
    "message": "Tenant Admin created successfully",
    "user": {
        "id": "uuid",
        "email": "admin@school1.com",
        "full_name": "John Doe",
        "role": "tenant_admin",
        "tenant": "<tenant_uuid>"
    }
}
```

## 4. Tenant User Login

**Endpoint:** `POST http://localhost:8000/api/auth/login/`

**Headers:**
```
X-Tenant-ID: <tenant_uuid>
```

**Request Body:**
```json
{
    "email": "admin@school1.com",
    "password": "Admin@12345"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": "uuid",
        "email": "admin@school1.com",
        "full_name": "John Doe",
        "role": "tenant_admin"
    }
}
```

## 5. Get Profile

**Endpoint:** `GET http://localhost:8000/api/auth/profile/`

**Headers:**
```
Authorization: Bearer <access_token>
```

## 6. Logout

**Endpoint:** `POST http://localhost:8000/api/auth/logout/`

**Headers:**
```
Authorization: Bearer <access_token>
```

## 7. Get Audit Logs

**Endpoint:** `GET http://localhost:8000/api/auth/audit-logs/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Note:** Returns logs based on user role:
- Super Admin: All logs
- Tenant Admin: Tenant-specific logs
- Others: Own logs only

## 8. Token Refresh

**Endpoint:** `POST http://localhost:8000/api/auth/token/refresh/`

**Request Body:**
```json
{
    "refresh": "<refresh_token>"
}
```

## Development Testing with Postman/Thunder Client

1. Import the API endpoints
2. Create environment variables:
   - `base_url`: http://localhost:8000
   - `access_token`: (set after login)
   - `tenant_id`: (set after creating tenant)

3. Test flow:
   - Login as Super Admin
   - Create Tenant
   - Create Tenant Admin
   - Login as Tenant Admin
   - Create students/teachers
