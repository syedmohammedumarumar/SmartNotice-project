# SmartNotice API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Base Configuration](#base-configuration)
3. [Authentication System](#authentication-system)
4. [Student Management APIs](#student-management-apis)
5. [File Upload & Email Operations](#file-upload--email-operations)
6. [Enhanced Statistics & Email Management](#enhanced-statistics--email-management)
7. [Testing Guide](#testing-guide)
8. [Error Handling](#error-handling)
9. [Use Cases & Workflows](#use-cases--workflows)
10. [Best Practices](#best-practices)

---

## Overview

SmartNotice is a comprehensive student management system that provides:
- JWT-based authentication with OTP password reset
- Complete student CRUD operations
- Hierarchical data organization (Branch → Year → Students)
- File upload for exam room assignments
- Email notification system with enhanced tracking
- Advanced statistics and analytics
- Targeted email resending capabilities

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

### 4. User Logout

**Endpoint:** `POST /api/auth/logout/`

**Description:** Logs out the current user by blacklisting their refresh token, preventing further token refresh operations.

**Authentication:** Required - Bearer Token

**Request Body:**
```json
{
    "refresh_token": "your_refresh_token_here"
}
```

**Success Response (200 OK):**
```json
{
    "message": "Logout successful"
}
```

**Error Responses:**
- **401 Unauthorized**: Missing or invalid token
- **400 Bad Request**: Invalid refresh token

### 5. Get User Profile
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

### 2. Email Operations

#### 2.1 Test Email Configuration
**Endpoint:** `POST /api/students/test-email/`

**Headers:** `Authorization: Bearer <access_token>`

**Note:** Frontend team need not integrate this API

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

## Enhanced Statistics & Email Management

### 1. Enhanced Statistics API

#### Get Enhanced Statistics
**Endpoint:** `GET /api/students/statistics/`

**Headers:** `Authorization: Bearer <access_token>`

**Enhanced Response (200 OK):**
```json
{
    "total_students": 500,
    "students_with_gmail": 450,
    "students_with_room": 400,
    "emails_sent": 300,
    "emails_pending": 200,
    "students_ready_for_email": 150,
    "students_missing_gmail": 50,
    "students_missing_room": 100,
    "branches_statistics": {
        "CSE": {
            "name": "Computer Science & Engineering (CSE)",
            "count": 160,
            "emails_sent": 120,
            "with_room": 140,
            "with_gmail": 150,
            "ready_for_email": 30,
            "missing_gmail": 10,
            "missing_room": 20,
            "pending_email_students": [
                {
                    "id": 1,
                    "roll_number": "21CSE001",
                    "name": "John Doe",
                    "gmail_address": "john.doe@gmail.com",
                    "exam_hall_number": "101",
                    "year": "2"
                },
                {
                    "id": 2,
                    "roll_number": "21CSE002",
                    "name": "Jane Smith",
                    "gmail_address": "jane.smith@gmail.com",
                    "exam_hall_number": "102",
                    "year": "2"
                }
            ],
            "years": {
                "1": {
                    "name": "1st Year",
                    "count": 40,
                    "emails_sent": 35,
                    "emails_pending": 5,
                    "with_room": 38,
                    "with_gmail": 39,
                    "ready_for_email": 3,
                    "missing_gmail": 1,
                    "missing_room": 2,
                    "pending_email_students": [
                        {
                            "id": 3,
                            "roll_number": "23CSE001",
                            "name": "Alice Johnson",
                            "gmail_address": "alice.johnson@gmail.com",
                            "exam_hall_number": "103"
                        },
                        {
                            "id": 4,
                            "roll_number": "23CSE002",
                            "name": "Bob Wilson",
                            "gmail_address": "bob.wilson@gmail.com",
                            "exam_hall_number": "104"
                        }
                    ],
                    "missing_gmail_students": [
                        {
                            "id": 5,
                            "roll_number": "23CSE003",
                            "name": "Charlie Brown",
                            "exam_hall_number": "105"
                        }
                    ],
                    "missing_room_students": [
                        {
                            "id": 6,
                            "roll_number": "23CSE004",
                            "name": "Diana Prince",
                            "gmail_address": "diana.prince@gmail.com"
                        }
                    ]
                },
                "2": {
                    "name": "2nd Year",
                    "count": 45,
                    "emails_sent": 30,
                    "emails_pending": 15,
                    "with_room": 40,
                    "with_gmail": 42,
                    "ready_for_email": 12,
                    "missing_gmail": 3,
                    "missing_room": 5,
                    "pending_email_students": [
                        {
                            "id": 7,
                            "roll_number": "22CSE001",
                            "name": "Eve Adams",
                            "gmail_address": "eve.adams@gmail.com",
                            "exam_hall_number": "201"
                        }
                    ],
                    "missing_gmail_students": [],
                    "missing_room_students": []
                }
            }
        },
        "ECE": {
            "name": "Electronics & Communication Engineering (ECE)",
            "count": 120,
            "emails_sent": 80,
            "with_room": 100,
            "with_gmail": 110,
            "ready_for_email": 20,
            "missing_gmail": 10,
            "missing_room": 20,
            "pending_email_students": [
                {
                    "id": 8,
                    "roll_number": "21ECE001",
                    "name": "Frank Miller",
                    "gmail_address": "frank.miller@gmail.com",
                    "exam_hall_number": "301",
                    "year": "3"
                }
            ],
            "years": {
                "1": {
                    "name": "1st Year",
                    "count": 30,
                    "emails_sent": 25,
                    "emails_pending": 5,
                    "with_room": 28,
                    "with_gmail": 29,
                    "ready_for_email": 3,
                    "missing_gmail": 1,
                    "missing_room": 2,
                    "pending_email_students": [
                        {
                            "id": 9,
                            "roll_number": "23ECE001",
                            "name": "Grace Lee",
                            "gmail_address": "grace.lee@gmail.com",
                            "exam_hall_number": "302"
                        }
                    ],
                    "missing_gmail_students": [],
                    "missing_room_students": []
                }
            }
        }
    },
    "global_pending_email_students": [
        {
            "id": 1,
            "roll_number": "21CSE001",
            "name": "John Doe",
            "branch": "CSE",
            "year": "2",
            "gmail_address": "john.doe@gmail.com",
            "exam_hall_number": "101"
        },
        {
            "id": 2,
            "roll_number": "21CSE002",
            "name": "Jane Smith",
            "branch": "CSE",
            "year": "2",
            "gmail_address": "jane.smith@gmail.com",
            "exam_hall_number": "102"
        }
    ]
}
```

#### Enhanced Fields Explanation

**Global Level:**
- `students_ready_for_email`: Students who have both Gmail and room number but haven't received emails
- `students_missing_gmail`: Students without Gmail addresses
- `students_missing_room`: Students without room assignments
- `global_pending_email_students`: Complete list of all students ready for email resending

**Branch Level:**
- `ready_for_email`: Count of students ready for email but not sent
- `pending_email_students`: Detailed list of students ready for email resending
- `missing_gmail`: Count of students without Gmail addresses
- `missing_room`: Count of students without room assignments

**Year Level:**
- `emails_pending`: Count of students with pending email status
- `ready_for_email`: Count of students ready for email resending
- `pending_email_students`: Detailed student list ready for emails
- `missing_gmail_students`: Students without Gmail addresses
- `missing_room_students`: Students without room assignments

### 2. Students by Email Status API

#### Get Students by Email Status
**Endpoint:** `GET /api/students/students-by-email-status/`

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `status`: `pending` | `missing_gmail` | `missing_room` | `sent` (required)
- `branch`: Branch code (optional)
- `year`: Year code (optional)

#### Examples

##### Get Students Ready for Email (Pending)
```
GET /api/students/students-by-email-status/?status=pending&branch=CSE&year=2
```

**Response (200 OK):**
```json
{
    "status_filter": "pending",
    "branch": "CSE",
    "year": "2",
    "students": [
        {
            "id": 1,
            "roll_number": "21CSE001",
            "name": "John Doe",
            "gmail_address": "john.doe@gmail.com",
            "exam_hall_number": "101",
            "branch": "CSE",
            "year": "2",
            "email_sent": false
        },
        {
            "id": 2,
            "roll_number": "21CSE002",
            "name": "Jane Smith",
            "gmail_address": "jane.smith@gmail.com",
            "exam_hall_number": "102",
            "branch": "CSE",
            "year": "2",
            "email_sent": false
        }
    ],
    "total_students": 2
}
```

##### Get Students Missing Gmail
```
GET /api/students/students-by-email-status/?status=missing_gmail&branch=CSE
```

**Response (200 OK):**
```json
{
    "status_filter": "missing_gmail",
    "branch": "CSE",
    "students": [
        {
            "id": 5,
            "roll_number": "23CSE003",
            "name": "Charlie Brown",
            "gmail_address": null,
            "exam_hall_number": "105",
            "branch": "CSE",
            "year": "1",
            "email_sent": false
        }
    ],
    "total_students": 1
}
```

##### Get Students Missing Room
```
GET /api/students/students-by-email-status/?status=missing_room&branch=ECE&year=1
```

**Response (200 OK):**
```json
{
    "status_filter": "missing_room",
    "branch": "ECE",
    "year": "1",
    "students": [
        {
            "id": 10,
            "roll_number": "23ECE002",
            "name": "Helen Carter",
            "gmail_address": "helen.carter@gmail.com",
            "exam_hall_number": null,
            "branch": "ECE",
            "year": "1",
            "email_sent": false
        }
    ],
    "total_students": 1
}
```

##### Get Students with Sent Emails
```
GET /api/students/students-by-email-status/?status=sent&branch=CSE
```

**Response (200 OK):**
```json
{
    "status_filter": "sent",
    "branch": "CSE",
    "students": [
        {
            "id": 11,
            "roll_number": "21CSE010",
            "name": "Mike Johnson",
            "gmail_address": "mike.johnson@gmail.com",
            "exam_hall_number": "110",
            "branch": "CSE",
            "year": "2",
            "email_sent": true
        }
    ],
    "total_students": 1
}
```

### 3. Resend Pending Emails API

#### Resend Emails to Pending Students
**Endpoint:** `POST /api/students/resend-pending-emails/`

**Headers:** `Authorization: Bearer <access_token>`

**Request Body Options:**

##### Option 1: Resend to All Pending Students
```json
{
    "send_to_all": true
}
```

##### Option 2: Resend by Branch and Year
```json
{
    "branch": "CSE",
    "year": "2"
}
```

##### Option 3: Resend to Specific Students
```json
{
    "student_ids": [1, 2, 3, 4, 5]
}
```

##### Option 4: Combined Filters
```json
{
    "branch": "CSE",
    "year": "2",
    "student_ids": [1, 2, 3]
}
```

**Success Response (200 OK):**
```json
{
    "message": "Resend email operation completed",
    "total_students": 3,
    "emails_sent": 2,
    "email_failures": 1,
    "results": [
        {
            "success": true,
            "student_id": 1,
            "roll_number": "21CSE001",
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "message": "Email sent successfully to Gmail"
        },
        {
            "success": true,
            "student_id": 2,
            "roll_number": "21CSE002",
            "name": "Jane Smith",
            "email": "jane.smith@gmail.com",
            "message": "Email sent successfully to Gmail"
        },
        {
            "success": false,
            "student_id": 3,
            "roll_number": "21CSE003",
            "name": "Bob Wilson",
            "email": "invalid.email@gmail.com",
            "error": "SMTP Error: Invalid recipient"
        }
    ]
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "No students found matching the criteria",
    "details": "No students with pending email status found for the specified filters"
}
```

---

## Testing Guide

### 1. Authentication Testing Workflow

#### Step 1: User Registration
```bash
POST /api/auth/register/
Content-Type: application/json

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
Content-Type: application/json

{
    "email": "testuser@example.com",
    "password": "testpass123"
}
```

#### Step 3: Password Reset Flow
```bash
# Request OTP
POST /api/auth/forgot-password/
Content-Type: application/json

{
    "email": "testuser@example.com"
}

# Verify OTP (Optional)
POST /api/auth/verify-otp/
Content-Type: application/json

{
    "email": "testuser@example.com",
    "otp_code": "123456"
}

# Reset Password
POST /api/auth/reset-password/
Content-Type: application/json

{
    "email": "testuser@example.com",
    "otp_code": "123456",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
}
```

#### Step 4: Test Profile Access
```bash
GET /api/auth/profile/
Authorization: Bearer <access_token>
```

#### Step 5: Test Logout
```bash
POST /api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "refresh_token": "your_refresh_token_here"
}
```

### 2. Student Management Testing Workflow

#### Step 1: Create Test Students
```bash
POST /api/students/
Authorization: Bearer <access_token>
Content-Type: application/json

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
GET /api/students/?hall_number=A101
Authorization: Bearer <access_token>
```

#### Step 3: Test Hierarchical Data
```bash
GET /api/students/branches/
GET /api/students/branches/CSE/years/
GET /api/students/branches/CSE/years/2/students/
GET /api/students/hierarchy/
Authorization: Bearer <access_token>
```

#### Step 4: Test Student Updates
```bash
PUT /api/students/1/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "Alice Johnson Updated",
    "roll_number": "21CSE001",
    "phone_number": "9876543210",
    "gmail_address": "alice.updated@gmail.com",
    "branch": "CSE",
    "year": "2",
    "exam_hall_number": "A102"
}
```

### 3. File Upload Testing

#### Step 1: Create Test CSV File
```csv
S.No,Roll No,Room No
1,21CSE001,A101
2,21CSE002,A102
3,21CSE003,A103
4,21ECE001,B201
5,21ECE002,B202
```

#### Step 2: Upload File Without Emails
```bash
POST /api/students/upload-rooms/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Form-data:
- file: test_rooms.csv
- send_emails: false
```

#### Step 3: Upload with Email Sending
```bash
POST /api/students/upload-rooms/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Form-data:
- file: test_rooms.csv
- send_emails: true
```

### 4. Enhanced Email Testing Workflow

#### Step 1: Test Enhanced Statistics
```bash
GET /api/students/statistics/
Authorization: Bearer <access_token>
```

#### Step 2: Test Email Status Filtering
```bash
# Get students ready for email
GET /api/students/students-by-email-status/?status=pending&branch=CSE&year=2
Authorization: Bearer <access_token>

# Get students missing Gmail
GET /api/students/students-by-email-status/?status=missing_gmail
Authorization: Bearer <access_token>

# Get students missing room
GET /api/students/students-by-email-status/?status=missing_room&branch=ECE
Authorization: Bearer <access_token>

# Get students with sent emails
GET /api/students/students-by-email-status/?status=sent&branch=CSE&year=1
Authorization: Bearer <access_token>
```

#### Step 3: Test Individual Email Sending
```bash
POST /api/students/1/send-email/
Authorization: Bearer <access_token>
```

#### Step 4: Test Bulk Email Operations
```bash
POST /api/students/send-bulk-emails/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "student_ids": [1, 2, 3, 4, 5]
}
```

#### Step 5: Test Resend Operations
```bash
# Resend to all pending students
POST /api/students/resend-pending-emails/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "send_to_all": true
}

# Resend by branch and year
POST /api/students/resend-pending-emails/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "branch": "CSE",
    "year": "2"
}

# Resend to specific students
POST /api/students/resend-pending-emails/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "student_ids": [1, 2, 3]
}
```

### 5. Complete Testing Sequence

#### Full System Test
```bash
# 1. Register and login
POST /api/auth/register/ → Get tokens
POST /api/auth/login/ → Verify login

# 2. Create test data
POST /api/students/ → Create multiple students
GET /api/students/ → Verify creation

# 3. Upload room assignments
POST /api/students/upload-rooms/ → Upload CSV with send_emails=false

# 4. Check statistics
GET /api/students/statistics/ → Verify data integrity

# 5. Test email operations
GET /api/students/students-by-email-status/?status=pending
POST /api/students/resend-pending-emails/ → Send emails

# 6. Verify email status
GET /api/students/statistics/ → Check updated counts
GET /api/students/students-by-email-status/?status=sent
```

---

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
    "error": "Validation failed",
    "details": {
        "email": ["This field is required."],
        "password": ["Password must be at least 8 characters long."]
    }
}
```

#### 401 Unauthorized
```json
{
    "error": "Authentication failed",
    "message": "Invalid credentials or token expired"
}
```

#### 403 Forbidden
```json
{
    "error": "Permission denied",
    "message": "You don't have permission to access this resource"
}
```

#### 404 Not Found
```json
{
    "error": "Resource not found",
    "message": "Student with id 999 does not exist"
}
```

#### 409 Conflict
```json
{
    "error": "Duplicate entry",
    "message": "Student with roll number 21CSE001 already exists"
}
```

#### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "message": "An unexpected error occurred. Please try again later."
}
```

### Authentication-Specific Errors

#### Invalid OTP
```json
{
    "error": "Invalid OTP",
    "message": "The OTP code is invalid or has expired. Please request a new one."
}
```

#### Password Mismatch
```json
{
    "error": "Password confirmation failed",
    "message": "Password and confirmation password do not match"
}
```

#### Token Expired
```json
{
    "error": "Token expired",
    "message": "Your session has expired. Please login again."
}
```

### File Upload Errors

#### Invalid File Format
```json
{
    "error": "Invalid file format",
    "message": "Only CSV and Excel files are supported"
}
```

#### File Processing Error
```json
{
    "error": "File processing failed",
    "message": "Unable to process the uploaded file. Please check the format and try again.",
    "details": {
        "line_errors": [
            {
                "line": 5,
                "error": "Invalid roll number format"
            }
        ]
    }
}
```

### Email Operation Errors

#### SMTP Configuration Error
```json
{
    "error": "Email configuration error",
    "message": "Email service is not properly configured. Please contact administrator."
}
```

#### Bulk Email Failure
```json
{
    "error": "Bulk email operation failed",
    "message": "Some emails could not be sent",
    "details": {
        "total_requested": 10,
        "successful": 7,
        "failed": 3,
        "failed_students": [
            {
                "id": 5,
                "roll_number": "21CSE005",
                "error": "Invalid email address"
            }
        ]
    }
}
```

---
## Use Cases & Workflows

### 1. New Semester Setup Workflow

#### Step 1: Initial Data Setup
```bash
# Create students for new semester
POST /api/students/ (for each student)

# Verify data
GET /api/students/hierarchy/
GET /api/students/statistics/
```

#### Step 2: Room Assignment Process
```bash
# Upload room assignments
POST /api/students/upload-rooms/ (send_emails=false)

# Verify assignments
GET /api/students/statistics/
GET /api/students/students-by-email-status/?status=pending
```

#### Step 3: Email Notification Campaign
```bash
# Send emails to all students with rooms
POST /api/students/resend-pending-emails/ (send_to_all=true)

# Monitor results
GET /api/students/statistics/
GET /api/students/students-by-email-status/?status=sent
```

### 2. Exam Day Management Workflow

#### Step 1: Last-Minute Updates
```bash
# Check for students needing updates
GET /api/students/students-by-email-status/?status=missing_gmail
GET /api/students/students-by-email-status/?status=missing_room

# Update student information
PUT /api/students/{id}/ (for each student needing updates)
```

#### Step 2: Resend Notifications
```bash
# Resend to updated students
POST /api/students/resend-pending-emails/ (specific student_ids)

# Verify all students notified
GET /api/students/statistics/
```

### 3. Branch-Specific Communication

#### Step 1: Target Specific Branch
```bash
# Get students by branch
GET /api/students/branches/CSE/years/2/students/

# Check email status for branch
GET /api/students/students-by-email-status/?status=pending&branch=CSE&year=2
```

#### Step 2: Send Branch-Specific Emails
```bash
# Send to specific branch/year
POST /api/students/resend-pending-emails/
{
    "branch": "CSE",
    "year": "2"
}
```

### 4. Data Quality Management

#### Step 1: Identify Data Issues
```bash
# Find students with missing data
GET /api/students/students-by-email-status/?status=missing_gmail
GET /api/students/students-by-email-status/?status=missing_room

# Get comprehensive statistics
GET /api/students/statistics/
```

#### Step 2: Bulk Data Correction
```bash
# Update students with missing information
PUT /api/students/{id}/ (for each student)

# Re-upload corrected room assignments
POST /api/students/upload-rooms/
```

### 5. Email Campaign Monitoring

#### Step 1: Pre-Campaign Analysis
```bash
# Check readiness
GET /api/students/statistics/
GET /api/students/students-by-email-status/?status=pending
```

#### Step 2: Execute Campaign
```bash
# Send emails
POST /api/students/resend-pending-emails/
```

#### Step 3: Post-Campaign Analysis
```bash
# Analyze results
GET /api/students/statistics/
GET /api/students/students-by-email-status/?status=sent
```

---

## Best Practices

### 1. Authentication Best Practices

#### Token Management
- Store access tokens securely (not in localStorage for production)
- Implement automatic token refresh logic
- Handle token expiration gracefully
- Always include proper error handling for authentication failures

#### Password Security
- Enforce strong password requirements
- Use secure password reset flow with OTP
- Implement rate limiting for authentication attempts
- Log authentication events for security monitoring

### 2. API Usage Best Practices

#### Request Optimization
- Use pagination for large datasets
- Implement proper filtering to reduce payload size
- Cache frequently accessed data (like hierarchy)
- Use batch operations for bulk updates

#### Error Handling
- Always check response status codes
- Implement retry logic for transient failures
- Provide meaningful error messages to users
- Log errors for debugging and monitoring

### 3. Email Operations Best Practices

#### Email Delivery
- Validate email addresses before sending
- Implement email delivery tracking
- Handle SMTP failures gracefully
- Use email templates for consistent formatting

#### Bulk Operations
- Process bulk emails in batches
- Implement progress tracking for large operations
- Provide detailed success/failure reporting
- Allow resuming failed operations

### 4. Data Management Best Practices

#### File Uploads
- Validate file format and size before processing
- Provide clear error messages for file issues
- Support both CSV and Excel formats
- Implement data validation during import

#### Data Integrity
- Validate roll numbers for uniqueness
- Check email format validity
- Ensure branch/year combinations are valid
- Implement data backup before bulk operations

### 5. Performance Best Practices

#### Database Operations
- Use database indexes for frequently queried fields
- Implement proper pagination for large datasets
- Optimize queries for hierarchical data
- Use caching for static data

#### API Response Times
- Implement response caching where appropriate
- Use efficient serialization
- Minimize database queries per request
- Implement proper connection pooling

### 6. Security Best Practices

#### Data Protection
- Encrypt sensitive data in transit and at rest
- Implement proper input validation
- Use parameterized queries to prevent SQL injection
- Sanitize user inputs

#### Access Control
- Implement role-based access control
- Use JWT tokens with appropriate expiration
- Validate user permissions for each operation
- Implement rate limiting to prevent abuse

### 7. Testing Best Practices

#### Automated Testing
- Write unit tests for all API endpoints
- Implement integration tests for workflows
- Use test databases for development
- Maintain test data fixtures

#### Manual Testing
- Test with realistic data volumes
- Verify error scenarios
- Test edge cases and boundary conditions
- Validate email functionality in staging environment

### 8. Monitoring and Logging

#### Application Monitoring
- Log all API requests and responses
- Monitor email delivery rates
- Track system performance metrics
- Implement health checks for dependencies

#### Business Metrics
- Track student enrollment trends
- Monitor email campaign success rates
- Analyze system usage patterns
- Generate reports for administrators

---

## Conclusion

The SmartNotice API provides a comprehensive solution for student management and email notification systems. This documentation covers all aspects of the API, from basic authentication to advanced email management features.

Key features include:
- Secure JWT-based authentication with OTP password reset
- Complete student lifecycle management
- Hierarchical data organization
- Advanced email tracking and resending capabilities
- Comprehensive statistics and analytics
- Robust error handling and validation

For additional support or feature requests, please contact the development team or refer to the API source code repository.

---

## Version History

- **v1.0.0**: Initial release with basic student management
- **v1.1.0**: Added email notification system
- **v1.2.0**: Enhanced statistics and email tracking
- **v1.3.0**: Added bulk email operations and resending capabilities
- **v1.4.0**: Current version with comprehensive email management and enhanced analytics

---

## Contact Information

- **Development Team**: [team@smartnotice.com](mailto:team@smartnotice.com)
- **Support**: [Syed Mohammed Umar – umar.md.4474@gmail.com](mailto:umar.md.4474@gmail.com)
- **GitHub Repository**: [github.com/syedmohammedumarumar/SmartNotice-project](https://github.com/syedmohammedumarumar/SmartNotice-project)
- **Backend Developer**: [Syed Mohammed Umar](mailto:umar.md.4474@gmail.com)

