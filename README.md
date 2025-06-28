# SmartNotice-project
# Authentication API Documentation

## Base URL
```
http://127.0.0.1:8000/api/auth/
```

## Authentication
The API uses JWT tokens for authentication. After successful login or registration, you'll receive:
- **Access Token**: Used for authenticated requests (expires in 5 minutes by default)
- **Refresh Token**: Used to obtain new access tokens (expires in 24 hours by default)

### Using Access Tokens
Include the access token in the Authorization header for protected endpoints:
```
Authorization: Bearer <your_access_token>
```

---

## API Endpoints

### 1. User Registration
**Endpoint:** `POST /register/`  
**Permission:** Public (no authentication required)  
**Description:** Register a new user account

#### Request Body
```json
{
    "username": "umar",
    "email": "umar@example.com",
    "first_name": "umar",
    "last_name": "syed",
    "password": "umarsyed1234",
    "password_confirm": "umarsyed1234"
}
```

#### Request Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | Unique username (must not already exist) |
| email | string | Yes | Valid email address (must not already exist) |
| first_name | string | Yes | User's first name |
| last_name | string | Yes | User's last name |
| password | string | Yes | Password (minimum 8 characters) |
| password_confirm | string | Yes | Password confirmation (must match password) |

#### Success Response (201 Created)
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "umar",
        "email": "umar@example.com",
        "first_name": "umar",
        "last_name": "syed",
        "date_joined": "2025-06-27T10:30:00Z"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### Error Response (400 Bad Request)
```json
{
    "username": ["A user with this username already exists."],
    "email": ["A user with this email already exists."],
    "password": ["Password fields didn't match."]
}
```

---

### 2. User Login
**Endpoint:** `POST /login/`  
**Permission:** Public (no authentication required)  
**Description:** Authenticate user and receive JWT tokens

#### Request Body
```json
{
    "username": "umar",
    "password": "umarsyed1234"
}
```

#### Request Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | User's username |
| password | string | Yes | User's password |

#### Success Response (200 OK)
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
       "username": "umar",
        "email": "umar@example.com",
        "first_name": "umar",
        "last_name": "syed",
        "date_joined": "2025-06-27T10:30:00Z"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### Error Response (400 Bad Request)
```json
{
    "non_field_errors": ["Invalid credentials"]
}
```

or

```json
{
    "non_field_errors": ["User account is disabled"]
}
```

---

### 3. User Logout
**Endpoint:** `POST /logout/`  
**Permission:** Requires authentication (Bearer token)  
**Description:** Logout user and blacklist refresh token

#### Headers
```
Authorization: Bearer <your_access_token>
```

#### Request Body
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Request Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| refresh_token | string | Yes | The refresh token to blacklist |

#### Success Response (200 OK)
```json
{
    "message": "Logout successful"
}
```

#### Error Response (400 Bad Request)
```json
{
    "message": "Error during logout",
    "error": "Token is blacklisted"
}
```

#### Error Response (401 Unauthorized)
```json
{
    "detail": "Given token not valid for any token type"
}
```

---

### 4. Refresh Token
**Endpoint:** `POST /token/refresh/`  
**Permission:** Public (no authentication required)  
**Description:** Get a new access token using refresh token

#### Request Body
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Success Response (200 OK)
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Error Response (401 Unauthorized)
```json
{
    "detail": "Token is invalid or expired",
    "code": "token_not_valid"
}
```

---

## Error Handling

### Common HTTP Status Codes
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or token invalid
- **403 Forbidden**: Permission denied
- **404 Not Found**: Endpoint not found
- **500 Internal Server Error**: Server error

### Error Response Format
All error responses follow this format:
```json
{
    "field_name": ["Error message"],
    "another_field": ["Another error message"]
}
```

For non-field errors:
```json
{
    "non_field_errors": ["Error message"]
}
```

---


# Students API - Frontend Integration Guide

### Base URL
```
http://127.0.0.1:8000/api/students/
```

### Authentication
All API calls require JWT authentication. Include this header in every request:
```javascript
headers: {
  'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
  'Content-Type': 'application/json'
}
```

---

## 📋 Table of Contents
- [Student Management](#-student-management)
- [Hierarchical Data](#-hierarchical-data-structure)
- [Email Operations](#-email-operations)
- [Statistics](#-statistics)
- [Error Handling](#-error-handling)

---

## 👥 Student Management

### Get All Students
```javascript
// GET /api/students/
// Optional query parameters for filtering
const response = await fetch('/api/students/?branch=CSE&year=3&section=A');
```

**Available Filters:**
- `roll_number` - Search by roll number
- `branch` - Filter by branch (CSE, ECE, etc.)
- `year` - Filter by year (1, 2, 3, 4)
- `section` - Filter by section (A, B, C, etc.)
- `hall_number` - Filter by exam hall
- `gmail` - Search by Gmail address

**Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "roll_number": "21CSE123",
    "phone_number": "9876543210",
    "gmail_address": "john.doe@gmail.com",
    "branch": "CSE",
    "branch_display": "Computer Science Engineering",
    "year": "3",
    "year_display": "3rd Year",
    "section": "A",
    "section_display": "Section A",
    "exam_hall_number": "H101",
    "email_sent": false,
    "institutional_email": "21cse123@mits.ac.in",
    "full_class_info": "Computer Science Engineering - 3rd Year - Section A"
  }
]
```

### Create New Student
```javascript
// POST /api/students/
const newStudent = {
  name: "Jane Smith",
  roll_number: "21CSE124",
  phone_number: "9876543211",
  gmail_address: "jane.smith@gmail.com",
  branch: "CSE",
  year: "3",
  section: "A",
  exam_hall_number: "H101"
};

const response = await fetch('/api/students/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(newStudent)
});
```

### Get Single Student
```javascript
// GET /api/students/{student_id}/
const response = await fetch('/api/students/1/');
```

### Update Student
```javascript
// PATCH /api/students/{student_id}/ (partial update)
// PUT /api/students/{student_id}/ (complete update)
const updates = {
  exam_hall_number: "H102",
  gmail_address: "updated.email@gmail.com"
};

const response = await fetch('/api/students/1/', {
  method: 'PATCH',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(updates)
});
```

### Delete Student
```javascript
// DELETE /api/students/{student_id}/
const response = await fetch('/api/students/1/', {
  method: 'DELETE'
});
```

---

## 🏗️ Hierarchical Data Structure

### Get All Branches
```javascript
// GET /api/students/branches/
const response = await fetch('/api/students/branches/');
```
**Response:**
```json
{
  "branches": [
    {
      "code": "CSE",
      "name": "Computer Science Engineering",
      "student_count": 150
    }
  ],
  "total_branches": 1
}
```

### Get Years in a Branch
```javascript
// GET /api/students/branches/{branch_code}/years/
const response = await fetch('/api/students/branches/CSE/years/');
```
**Response:**
```json
{
  "branch": {
    "code": "CSE",
    "name": "Computer Science Engineering"
  },
  "years": [
    {
      "code": "1",
      "name": "1st Year",
      "student_count": 40
    }
  ]
}
```

### Get Sections in Branch + Year
```javascript
// GET /api/students/branches/{branch}/years/{year}/sections/
const response = await fetch('/api/students/branches/CSE/years/3/sections/');
```

### Get Students in Branch + Year + Section
```javascript
// GET /api/students/branches/{branch}/years/{year}/sections/{section}/students/
const response = await fetch('/api/students/branches/CSE/years/3/sections/A/students/');
```

### Get Complete Hierarchy Overview
```javascript
// GET /api/students/hierarchy/
const response = await fetch('/api/students/hierarchy/');
```
**Perfect for building navigation trees!**

---

## 📧 Email Operations

### Send Email to Single Student
```javascript
// POST /api/students/{student_id}/send-email/
const response = await fetch('/api/students/1/send-email/', {
  method: 'POST'
});
```

### Send Bulk Emails
```javascript
// POST /api/students/send-bulk-emails/
const emailData = {
  student_ids: [1, 2, 3, 4, 5]
};

const response = await fetch('/api/students/send-bulk-emails/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(emailData)
});
```

**Response:**
```json
{
  "message": "Bulk email sending completed",
  "total_students": 5,
  "emails_sent": 4,
  "email_failures": 1,
  "results": [
    {
      "success": true,
      "student_id": 1,
      "roll_number": "21CSE123",
      "email": "john.doe@gmail.com",
      "message": "Email sent successfully"
    }
  ]
}
```

### Test Email Configuration
```javascript
// POST /api/students/test-email/
const response = await fetch('/api/students/test-email/', {
  method: 'POST'
});
```

---

# 📊 Statistics API Backend Documentation

## Endpoint Overview

### Get System Statistics
```http
GET /api/students/statistics/
```

**Base URL:** `http://127.0.0.1:8000`

**Full URL:** `http://127.0.0.1:8000/api/students/statistics/`

**Method:** `GET`

**Content-Type:** `application/json`

## Response Structure

### Root Level Schema
```json
{
    "total_students": Integer,
    "students_with_gmail": Integer,
    "emails_sent": Integer,
    "emails_pending": Integer,
    "branches_statistics": Object
}
```

### Branch Statistics Schema
```json
"branches_statistics": {
    "BRANCH_CODE": {
        "name": String,
        "count": Integer,
        "emails_sent": Integer,
        "years": Object
    }
}
```

### Year Statistics Schema
```json
"years": {
    "YEAR_NUMBER": {
        "name": String,
        "count": Integer,
        "emails_sent": Integer,
        "sections": Object
    }
}
```

### Section Statistics Schema
```json
"sections": {
    "SECTION_CODE": {
        "name": String,
        "count": Integer,
        "emails_sent": Integer
    }
}
```

## Complete Response Example

```json
{
    "total_students": 53,
    "students_with_gmail": 53,
    "emails_sent": 18,
    "emails_pending": 35,
    "branches_statistics": {
        "CSE": {
            "name": "Computer Science & Engineering (CSE)",
            "count": 47,
            "emails_sent": 13,
            "years": {
                "1": {
                    "name": "1st Year",
                    "count": 47,
                    "emails_sent": 13,
                    "sections": {
                        "A": {
                            "name": "Section A",
                            "count": 47,
                            "emails_sent": 13
                        }
                    }
                }
            }
        },
        "ECE": {
            "name": "Electronics and Communication Engineering (ECE)",
            "count": 3,
            "emails_sent": 3,
            "years": {
                "1": {
                    "name": "1st Year",
                    "count": 3,
                    "emails_sent": 3,
                    "sections": {
                        "A": {
                            "name": "Section A",
                            "count": 3,
                            "emails_sent": 3
                        }
                    }
                }
            }
        },
        "EEE": {
            "name": "Electrical and Electronics Engineering (EEE)",
            "count": 2,
            "emails_sent": 2,
            "years": {
                "1": {
                    "name": "1st Year",
                    "count": 2,
                    "emails_sent": 2,
                    "sections": {
                        "A": {
                            "name": "Section A",
                            "count": 2,
                            "emails_sent": 2
                        }
                    }
                }
            }
        }
    }
}
```

## Field Descriptions

### Root Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_students` | Integer | Total count of all students in the system |
| `students_with_gmail` | Integer | Number of students who have Gmail email addresses |
| `emails_sent` | Integer | Total number of emails that have been successfully sent |
| `emails_pending` | Integer | Number of emails queued/waiting to be sent |
| `branches_statistics` | Object | Hierarchical breakdown by academic branches |

### Branch Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Full descriptive name of the academic branch/department |
| `count` | Integer | Total number of students enrolled in this branch |
| `emails_sent` | Integer | Number of emails sent to students in this branch |
| `years` | Object | Year-wise breakdown within this branch |

### Year Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Display name for the academic year (e.g., "1st Year", "2nd Year") |
| `count` | Integer | Number of students in this year within the branch |
| `emails_sent` | Integer | Emails sent to students in this specific year |
| `sections` | Object | Section-wise breakdown within this year |

### Section Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Section identifier with descriptive text (e.g., "Section A") |
| `count` | Integer | Number of students in this specific section |
| `emails_sent` | Integer | Emails sent to students in this section |

## Data Hierarchy

```
Root
├── total_students (Integer)
├── students_with_gmail (Integer)  
├── emails_sent (Integer)
├── emails_pending (Integer)
└── branches_statistics (Object)
    └── [BRANCH_CODE] (Object)
        ├── name (String)
        ├── count (Integer)
        ├── emails_sent (Integer)
        └── years (Object)
            └── [YEAR_NUMBER] (Object)
                ├── name (String)
                ├── count (Integer)
                ├── emails_sent (Integer)
                └── sections (Object)
                    └── [SECTION_CODE] (Object)
                        ├── name (String)
                        ├── count (Integer)
                        └── emails_sent (Integer)
```

## HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| `200 OK` | Request successful, statistics data returned |
| `401 Unauthorized` | Authentication credentials missing or invalid |
| `403 Forbidden` | Insufficient permissions to access statistics |
| `500 Internal Server Error` | Server-side error occurred |

## Authentication Requirements

This endpoint requires authentication. Ensure proper authentication headers are included in the request.

## 🚨 Error Handling

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad request (validation errors) |
| 401 | Unauthorized |
| 404 | Not found |
| 500 | Server error |

### Example Error Response
```json
{
  "roll_number": ["Student with this roll number already exists."],
  "gmail_address": ["Please provide a valid Gmail address ending with @gmail.com"]
}
```

---

## 📝 Data Models Reference

### Available Branch Codes
- `CSE` - Computer Science & Engineering
- `CSM` - CS & Engineering - AI & ML
- `CAI` - CS & Engineering - Artificial Intelligence
- `CSD` - CS & Engineering - Data Science
- `CSC` - CS & Engineering - Cyber Security
- `ECE` - Electronics and Communication Engineering
- `EEE` - Electrical and Electronics Engineering
- `MEC` - Mechanical Engineering
- `CIV` - Civil Engineering

### Year Codes
- `1` - 1st Year
- `2` - 2nd Year
- `3` - 3rd Year
- `4` - 4th Year

### Section Codes
- `A` to `J` - Section A through Section J

---


### API Testing
Use tools like Postman or Thunder Client with these base settings:
- Base URL: `http://127.0.0.1:8000/api/students/`
- Authorization: Bearer Token
- Content-Type: application/json

---

**Happy Coding! 🚀**
