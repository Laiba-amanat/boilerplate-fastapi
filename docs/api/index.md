# API Documentation

## Overview

This is the complete API documentation for the FastAPI backend template. All APIs follow RESTful design principles and use JSON format for data exchange.

## Authentication

Most APIs require JWT authentication. Please obtain an access token via the login interface and then include it in the request header:

```
Authorization: Bearer <your-access-token>
```

## Response Format

All API responses follow a unified format:

### Successful Response
```json
{
  "code": 200,
  "msg": "success",
  "data": {...}
}
```

### Error Response
```json
{
  "code": 400,
  "msg": "error message",
  "data": null
}
```

### Error Code Explanation

| Error Code | Description |
|--------|------|
| 200 | Success |
| 400 | Bad Request Parameters |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Resource Not Found |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

## API Modules

- [Authentication & Authorization](base.md) - User login, token refresh, etc.
- [User Management](users.md) - User CRUD operations
- [Role Management](role.md) - Role and permission management
- [Menu Management](menu.md) - System menu configuration
- [File Management](files.md) - File upload and download
- [Department Management](dept.md) - Organizational structure management
- [API Permissions](api.md) - API access control
- [Audit Log](auditlog.md) - Operation log recording

## Online Testing

After starting the service, you can access the interactive API documentation at the following addresses:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Request Limits

- File upload size limit: 10MB
- Login attempt limit: 5 times/minute
- Token refresh limit: 10 times/minute
- API request frequency: Varies by specific interface

## Health Check

- **Health Status**: `GET /api/v1/base/health`
- **Version Information**: `GET /api/v1/base/version`
