# SmartNotice API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Base Configuration](#base-configuration)
3. [Authentication System](#authentication-system)
4. [Student Management APIs](#student-management-apis)
5. [File Upload & Email Operations](#file-upload--email-operations)
6. [Statistics & Analytics](#statistics--analytics)
7. [Testing Guide](#testing-guide)
8. [Error Handling](#error-handling)
9. [Postman Collection Setup](#postman-collection-setup)

---

## Overview

SmartNotice is a comprehensive student management system that provides:
- JWT-based authentication with OTP password reset
- Complete student CRUD operations
- Hierarchical data organization (Branch → Year → Students)
- File upload for exam room assignments
- Email notification system
- Statistics and analytics

---

## Base Configuration

### Base URLs
```
Authentication API: http://127.0.0.1:8000/api/auth/
Student Management API: http://127.0.0.1:8000/api/students/
```

### Global Headers
```
Content-Type: application/json
Authorization: Bearer <access_token>  # For protected endpoints
```

### Authentication Token Types
- **Access Token**: Used for API requests (expires in 5 minutes)
- **Refresh Token**: Used to obtain new access tokens (expires in 24 hours)

---

## Authentication System

### 1. User Registration
Create a new user account with email verification capability.

**Endpoint:** `POST /api/auth/register/`

**Request Body:**
```json
{
    "username": "testuser",
    "email": "testuser@example.com",
    "phone_number": "+1234567890",
    "password": "testpass123",
    "password_confirm": "testpass123"
}
```

**Success Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "phone_number": "+1234567890",
        "date_joined": "2025-07-02T10:30:00Z"
    },
    "tokens": {
        "refresh": "refresh_token_here",
        "access": "access_token_here"
    }
}
```

### 2. User Login
Authenticate user with email and password.

**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
    "email": "testuser@example.com",
    "password": "testpass123"
}
```

**Success Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "phone_number": "+1234567890",
        "date_joined": "2025-07-02T10:30:00Z"
    },
    "tokens": {
        "refresh": "refresh_token_here",
        "access": "access_token_here"
    }
}
```

### 3. Password Reset Flow (OTP-based)

#### 3.1 Request Password Reset OTP
**Endpoint:** `POST /api/auth/forgot-password/`

**Request Body:**
```json
{
    "email": "testuser@example.com"
}
```

**Success Response (200 OK):**
```json
{
    "message": "OTP sent successfully to your email. Please check your email and enter the 6-digit code."
}
```

#### 3.2 Verify OTP (Optional)
**Endpoint:** `POST /api/auth/verify-otp/`

**Request Body:**
```json
{
    "email": "testuser@example.com",
    "otp_code": "123456"
}
```

**Success Response (200 OK):**
```json
{
    "message": "OTP verified successfully. You can now reset your password.",
    "email": "testuser@example.com",
    "otp_verified": true
}
```

#### 3.3 Reset Password with OTP
**Endpoint:** `POST /api/auth/reset-password/`

**Request Body:**
```json
{
    "email": "testuser@example.com",
    "otp_code": "123456",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
}
```

**Success Response (200 OK):**
```json
{
    "message": "Password reset successfully",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "phone_number": "+1234567890",
        "date_joined": "2025-07-02T10:30:00Z"
    },
    "tokens": {
        "refresh": "new_refresh_token_here",
        "access": "new_access_token_here"
    }
}
```

## User Logout

### Endpoint
**POST** `/api/auth/logout/`

### Description
Logs out the current user by blacklisting their refresh token, preventing further token refresh operations.

### Authentication
- **Required**: Yes
- **Type**: Bearer Token
- **Header**: `Authorization: Bearer <access_token>`

### Request Body
```json
{
    "refresh_token": "your_refresh_token_here"
}
```

### Success Response
**Status Code**: `200 OK`

```json
{
    "message": "Logout successful"
}
```

### Error Responses

#### Missing or Invalid Token
**Status Code**: `401 Unauthorized`
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### Invalid Refresh Token
**Status Code**: `400 Bad Request`
```json
{
    "message": "Error during logout",
    "error": "Token is invalid or expired"
}
```

### 4. Get User Profile
**Endpoint:** `GET /api/auth/profile/`

**Headers:** `Authorization: Bearer <access_token>`

**Success Response (200 OK):**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "testuser@example.com",
    "phone_number": "+1234567890",
    "date_joined": "2025-07-02T10:30:00Z"
}
```

---

## Student Management APIs

### 1. Student CRUD Operations

#### 1.1 Create Student
**Endpoint:** `POST /api/students/`

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "name": "John Doe",
    "roll_number": "21CSE001",
    "phone_number": "9876543210",
    "gmail_address": "john.doe@gmail.com",
    "branch": "CSE",
    "year": "2",
    "exam_hall_number": "A101"
}
```

**Success Response (201 Created):**
```json
{
    "id": 1,
    "name": "John Doe",
    "roll_number": "21CSE001",
    "phone_number": "9876543210",
    "gmail_address": "john.doe@gmail.com",
    "branch": "CSE",
    "year": "2",
    "exam_hall_number": "A101",
    "created_at": "2025-07-02T10:30:00Z",
    "updated_at": "2025-07-02T10:30:00Z"
}
```

#### 1.2 Get All Students (with filtering)
**Endpoint:** `GET /api/students/`

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `roll_number`: Filter by roll number
- `branch`: Filter by branch code
- `year`: Filter by year
- `hall_number`: Filter by exam hall number
- `gmail`: Filter by Gmail address (partial match)

**Example:** `GET /api/students/?branch=CSE&year=2`

**Success Response (200 OK):**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/students/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "John Doe",
            "roll_number": "21CSE001",
            "phone_number": "9876543210",
            "gmail_address": "john.doe@gmail.com",
            "branch": "CSE",
            "year": "2",
            "exam_hall_number": "A101",
            "created_at": "2025-07-02T10:30:00Z",
            "updated_at": "2025-07-02T10:30:00Z"
        }
    ]
}
```

#### 1.3 Get Single Student
**Endpoint:** `GET /api/students/{student_id}/`

**Headers:** `Authorization: Bearer <access_token>`

**Success Response (200 OK):**
```json
{
    "id": 1,
    "name": "John Doe",
    "roll_number": "21CSE001",
    "phone_number": "9876543210",
    "gmail_address": "john.doe@gmail.com",
    "branch": "CSE",
    "year": "2",
    "exam_hall_number": "A101",
    "created_at": "2025-07-02T10:30:00Z",
    "updated_at": "2025-07-02T10:30:00Z"
}
```

#### 1.4 Update Student
**Endpoint:** `PUT /api/students/{student_id}/`

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "name": "John Doe Updated",
    "roll_number": "21CSE001",
    "phone_number": "9876543210",
    "gmail_address": "john.updated@gmail.com",
    "branch": "CSE",
    "year": "2",
    "exam_hall_number": "A102"
}
```

#### 1.5 Delete Student
**Endpoint:** `DELETE /api/students/{student_id}/`

**Headers:** `Authorization: Bearer <access_token>`

**Success Response (204 No Content)**

### 2. Hierarchical Data Operations

#### 2.1 Get All Branches
**Endpoint:** `GET /api/students/branches/`

**Headers:** `Authorization: Bearer <access_token>`

**Success Response (200 OK):**
```json
{
    "branches": [
        {
            "code": "CSE",
            "name": "Computer Science & Engineering (CSE)",
            "student_count": 150
        },
        {
            "code": "ECE",
            "name": "Electronics & Communication Engineering (ECE)",
            "student_count": 120
        }
    ],
    "total_branches": 5
}
```

#### 2.2 Get Years by Branch
**Endpoint:** `GET /api/students/branches/{branch_code}/years/`

**Headers:** `Authorization: Bearer <access_token>`

**Example:** `GET /api/students/branches/CSE/years/`

**Success Response (200 OK):**
```json
{
    "branch": {
        "code": "CSE",
        "name": "Computer Science & Engineering (CSE)"
    },
    "years": [
        {
            "year": "1",
            "name": "1st Year",
            "student_count": 40
        },
        {
            "year": "2",
            "name": "2nd Year",
            "student_count": 45
        }
    ]
}
```

#### 2.3 Get Students by Branch and Year
**Endpoint:** `GET /api/students/branches/{branch_code}/years/{year}/students/`

**Headers:** `Authorization: Bearer <access_token>`

**Example:** `GET /api/students/branches/CSE/years/2/students/`

#### 2.4 Get Hierarchy Overview
**Endpoint:** `GET /api/students/hierarchy/`

**Headers:** `Authorization: Bearer <access_token>`

**Success Response (200 OK):**
```json
{
    "total_students": 500,
    "total_branches": 5,
    "branches": {
        "CSE": {
            "name": "Computer Science & Engineering (CSE)",
            "total_students": 150,
            "years": {
                "1": {
                    "name": "1st Year",
                    "student_count": 40
                },
                "2": {
                    "name": "2nd Year",
                    "student_count": 45
                }
            }
        }
    }
}
```

---

## File Upload & Email Operations

### 1. Upload Exam Room Assignments
**Endpoint:** `POST /api/students/upload-rooms/`

**Headers:** `Authorization: Bearer <access_token>`

**Request Body (form-data):**
- `file`: Excel/CSV file
- `send_emails`: boolean (true/false)

**Excel/CSV File Format:**
```csv
S.No,Roll No,Room No
1,21CSE001,A101
2,21CSE002,A102
3,21CSE003,A103
```

**Success Response (200 OK):**
```json
{
    "message": "File uploaded and processed successfully",
    "processed_records": 150,
    "updated_students": 145,
    "failed_records": 5,
    "emails_sent": 145,
    "email_failures": 0
}
```

### 2. Email Operations -- Frontend team Need not to integrate this api 

#### 2.1 Test Email Configuration
**Endpoint:** `POST /api/students/test-email/`

**Headers:** `Authorization: Bearer <access_token>`

**Success Response (200 OK):**
```json
{
    "message": "Test email sent successfully",
    "email_sent_to": "admin@example.com"
}
```

#### 2.2 Send Individual Email
**Endpoint:** `POST /api/students/{student_id}/send-email/`

**Headers:** `Authorization: Bearer <access_token>`

**Success Response (200 OK):**
```json
{
    "message": "Email sent successfully",
    "student": {
        "id": 1,
        "name": "John Doe",
        "gmail_address": "john.doe@gmail.com",
        "exam_hall_number": "A101"
    },
    "email_sent_at": "2025-07-02T10:30:00Z"
}
```

#### 2.3 Send Bulk Emails
**Endpoint:** `POST /api/students/send-bulk-emails/`

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "student_ids": [1, 2, 3, 4, 5]
}
```

**Success Response (200 OK):**
```json
{
    "message": "Bulk emails processed",
    "total_requested": 5,
    "emails_sent": 4,
    "emails_failed": 1,
    "failed_students": [
        {
            "id": 5,
            "name": "Student Name",
            "reason": "No Gmail address"
        }
    ]
}
```

---

## Statistics & Analytics

### Get System Statistics
**Endpoint:** `GET /api/students/statistics/`

**Headers:** `Authorization: Bearer <access_token>`

**Success Response (200 OK):**
```json
{
    "total_students": 500,
    "students_with_gmail": 450,
    "students_with_room": 400,
    "emails_sent": 350,
    "emails_pending": 150,
    "branches_statistics": {
        "CSE": {
            "name": "Computer Science & Engineering (CSE)",
            "count": 150,
            "emails_sent": 120,
            "with_room": 140,
            "years": {
                "1": {
                    "name": "1st Year",
                    "count": 40,
                    "emails_sent": 35,
                    "with_room": 38
                },
                "2": {
                    "name": "2nd Year",
                    "count": 45,
                    "emails_sent": 40,
                    "with_room": 42
                }
            }
        },
        "ECE": {
            "name": "Electronics & Communication Engineering (ECE)",
            "count": 120,
            "emails_sent": 100,
            "with_room": 110,
            "years": {
                "1": {
                    "name": "1st Year",
                    "count": 35,
                    "emails_sent": 30,
                    "with_room": 32
                }
            }
        }
    }
}
```

---

## Testing Guide

### 1. Authentication Testing Workflow

#### Step 1: User Registration
```bash
POST /api/auth/register/
{
    "username": "testuser",
    "email": "testuser@example.com",
    "phone_number": "+1234567890",
    "password": "testpass123",
    "password_confirm": "testpass123"
}
```

#### Step 2: User Login
```bash
POST /api/auth/login/
{
    "email": "testuser@example.com",
    "password": "testpass123"
}
```

#### Step 3: Password Reset Flow
```bash
# Request OTP
POST /api/auth/forgot-password/
{
    "email": "testuser@example.com"
}

# Verify OTP (Optional)
POST /api/auth/verify-otp/
{
    "email": "testuser@example.com",
    "otp_code": "123456"
}

# Reset Password
POST /api/auth/reset-password/
{
    "email": "testuser@example.com",
    "otp_code": "123456",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
}
```

### 2. Student Management Testing Workflow

#### Step 1: Create Test Students
```bash
POST /api/students/
{
    "name": "Alice Johnson",
    "roll_number": "21CSE001",
    "phone_number": "9876543210",
    "gmail_address": "alice.j@gmail.com",
    "branch": "CSE",
    "year": "2"
}
```

#### Step 2: Test Filtering
```bash
GET /api/students/?branch=CSE&year=2
GET /api/students/?roll_number=21CSE001
GET /api/students/?gmail=alice
```

#### Step 3: Test Hierarchical Data
```bash
GET /api/students/branches/
GET /api/students/branches/CSE/years/
GET /api/students/branches/CSE/years/2/students/
GET /api/students/hierarchy/
```

### 3. File Upload Testing

#### Step 1: Create Test CSV File
```csv
S.No,Roll No,Room No
1,21CSE001,A101
2,21CSE002,A102
3,21CSE003,A103
```

#### Step 2: Upload File
```bash
POST /api/students/upload-rooms/
Form-data:
- file: test_rooms.csv
- send_emails: false
```

#### Step 3: Upload with Email Sending
```bash
POST /api/students/upload-rooms/
Form-data:
- file: test_rooms.csv
- send_emails: true
```

### 4. Email Testing Workflow

#### Step 1: Test Email Configuration
```bash
POST /api/students/test-email/
```

#### Step 2: Send Individual Email
```bash
POST /api/students/1/send-email/
```

#### Step 3: Send Bulk Emails
```bash
POST /api/students/send-bulk-emails/
{
    "student_ids": [1, 2, 3, 4, 5]
}
```

#### Step 4: Check Statistics
```bash
GET /api/students/statistics/
```

---

## Error Handling

### HTTP Status Codes
- **200 OK**: Successful GET, PUT, POST operations
- **201 Created**: Successful resource creation
- **204 No Content**: Successful DELETE operation
- **400 Bad Request**: Invalid data or validation errors
- **401 Unauthorized**: Missing or invalid authentication
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Common Error Responses

#### Authentication Errors
```json
{
    "detail": "Invalid email or password."
}
```

#### Validation Errors
```json
{
    "name": ["This field is required."],
    "roll_number": ["Student with this roll number already exists."],
    "gmail_address": ["Enter a valid email address."]
}
```

#### OTP Errors
```json
{
    "otp_code": ["Invalid OTP code."]
}
```

#### File Upload Errors
```json
{
    "error": "Invalid file format. Please upload Excel or CSV file.",
    "details": "Supported formats: .xlsx, .xls, .csv"
}
```

---

## Postman Collection Setup

### 1. Collection Variables
```
base_url: http://localhost:8000
auth_token: {{your_jwt_token}}
student_id: 1
```

### 2. Pre-request Script for Authentication
```javascript
// Add this to collection pre-request script
if (pm.info.requestName !== 'Login' && pm.info.requestName !== 'Register') {
    pm.request.headers.add({
        key: 'Authorization',
        value: 'Bearer ' + pm.collectionVariables.get('auth_token')
    });
}
```

### 3. Test Script for Login
```javascript
// Add this to Login request test script
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.collectionVariables.set('auth_token', jsonData.tokens.access);
}
```

### 4. Sample Request Structure
```
Method: POST
URL: {{base_url}}/api/students/
Headers:
- Content-Type: application/json
- Authorization: Bearer {{auth_token}}

Body:
{
    "name": "Test Student",
    "roll_number": "21CSE001",
    "gmail_address": "test@gmail.com",
    "branch": "CSE",
    "year": "2"
}
```

### 5. Complete Test Scenarios

#### Scenario 1: Complete Authentication Flow
1. Register new user
2. Login with credentials
3. Get user profile
4. Request password reset
5. Reset password with OTP
6. Login with new password

#### Scenario 2: Student Management Flow
1. Create multiple students
2. Filter by branch and year
3. Update student details
4. Get hierarchical data
5. Delete student

#### Scenario 3: File Upload and Email Flow
1. Upload CSV file without emails
2. Verify room assignments
3. Upload CSV with email sending
4. Check statistics
5. Send individual emails
6. Send bulk emails

#### Scenario 4: Error Testing
1. Test invalid authentication
2. Test invalid data validation
3. Test file upload errors
4. Test email sending errors

### 6. Performance Testing
- Test with 100+ students
- Upload files with 500+ records
- Send bulk emails to 200+ students
- Test concurrent operations

---

## Best Practices

### 1. Security
- Always use HTTPS in production
- Store JWT tokens securely
- Implement rate limiting
- Validate all input data

### 2. Error Handling
- Implement proper error logging
- Return meaningful error messages
- Handle edge cases gracefully

### 3. Performance
- Use pagination for large datasets
- Implement caching where appropriate
- Optimize database queries
- Use background tasks for email sending

### 4. Testing
- Test all endpoints with valid and invalid data
- Test authentication flows thoroughly
- Test file upload edge cases
- Monitor email delivery rates

This comprehensive documentation provides a complete guide for implementing and testing the SmartNotice API system.
