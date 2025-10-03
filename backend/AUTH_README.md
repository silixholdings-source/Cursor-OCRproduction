# Authentication & Multi-Tenant System

This document describes the authentication and multi-tenant system implemented in Phase B of the AI ERP SaaS application.

## Overview

The system provides:
- **JWT-based authentication** with access and refresh tokens
- **Multi-tenant architecture** with company isolation
- **Role-based access control** (RBAC)
- **Secure password handling** with bcrypt hashing
- **Company registration** with automatic user creation
- **Token refresh** mechanism for long-term sessions

## Architecture

### Core Components

1. **Models** (`src/models/`)
   - `User`: User accounts with roles and company association
   - `Company`: Company information with subscription tiers
   - `Invoice`: Basic invoice structure (placeholder)
   - `AuditLog`: Audit trail for compliance

2. **Authentication** (`src/core/auth.py`)
   - JWT token creation and validation
   - Password hashing and verification
   - User authentication and authorization

3. **Middleware** (`src/core/middleware.py`)
   - Multi-tenant request processing
   - Company context extraction
   - Request isolation

4. **Schemas** (`src/schemas/`)
   - Pydantic models for request/response validation
   - Input sanitization and type checking

5. **API Endpoints** (`src/api/v1/endpoints/auth.py`)
   - User registration and login
   - Token management
   - Profile operations

## Database Schema

### Users Table
- UUID primary key
- Email and username (unique)
- Hashed password
- Company association
- Role and status
- Security fields (2FA, login attempts, etc.)

### Companies Table
- UUID primary key
- Company information
- Subscription status and tier
- Feature flags and limits
- JSON settings and configuration

### Relationships
- Users belong to one Company
- Companies can have multiple Users
- Invoices and AuditLogs are company-scoped

## Authentication Flow

### 1. Registration
```
POST /api/v1/auth/register
{
  "company_name": "Company Name",
  "company_email": "admin@company.com",
  "owner_email": "owner@company.com",
  "owner_password": "secure_password",
  "owner_first_name": "John",
  "owner_last_name": "Doe"
}
```

**Response:**
- Company created with trial status
- Owner user created with OWNER role
- JWT tokens returned for immediate login

### 2. Login
```
POST /api/v1/auth/login
{
  "email": "user@company.com",
  "password": "password",
  "remember_me": false
}
```

**Response:**
- Access token (30 minutes)
- Refresh token (7 days)
- User and company information

### 3. Token Refresh
```
POST /api/v1/auth/refresh
{
  "refresh_token": "refresh_token_here"
}
```

**Response:**
- New access token
- New refresh token

### 4. Protected Endpoints
```
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

## Multi-Tenant Features

### Company Isolation
- All requests include company context
- Database queries automatically scoped to company
- Users can only access their company's data

### Context Extraction
The middleware extracts company context from:
1. JWT token (preferred)
2. Custom headers (`X-Company-ID`)

### Public Endpoints
The following endpoints don't require company context:
- `/health`
- `/docs`
- `/api/v1/auth/login`
- `/api/v1/auth/register`
- `/api/v1/auth/refresh`

## Security Features

### Password Security
- bcrypt hashing with configurable rounds
- Minimum 8 character requirement
- Password confirmation validation

### JWT Security
- HS256 algorithm
- Configurable expiration times
- Token type validation (access vs refresh)

### Account Protection
- Failed login attempt tracking
- Account locking after multiple failures
- Email verification support

## Role-Based Access Control

### User Roles
1. **OWNER**: Full company access, billing management
2. **ADMIN**: User management, company settings
3. **MANAGER**: Team management, advanced features
4. **USER**: Standard user access
5. **VIEWER**: Read-only access

### Role Hierarchy
```
OWNER > ADMIN > MANAGER > USER > VIEWER
```

## Configuration

### Environment Variables
```bash
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=postgresql://user:pass@host:port/db
```

### Company Tiers
- **FREE**: Basic features, limited users
- **BASIC**: OCR, 3-way matching
- **PROFESSIONAL**: Advanced analytics
- **ENTERPRISE**: API access, custom features

## Database Migrations

### Setup
```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

### Migration Files
- `0001_initial_migration.py`: Creates all tables and enums

## Testing

### Test Script
Run the test script to verify the system:
```bash
python test_auth.py
```

### Test Coverage
- Company and user registration
- User login and authentication
- Token refresh
- Protected endpoint access
- User logout

## API Documentation

### Swagger UI
Access the interactive API documentation at:
```
http://localhost:8000/docs
```

### Available Endpoints
- `POST /api/v1/auth/register` - Company registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Current user info
- `POST /api/v1/auth/change-password` - Change password
- `PUT /api/v1/auth/profile` - Update profile
- `POST /api/v1/auth/forgot-password` - Password reset request
- `POST /api/v1/auth/reset-password` - Password reset
- `POST /api/v1/auth/verify-email` - Email verification

## Future Enhancements

### Planned Features
- Email service integration
- Two-factor authentication (2FA)
- Single sign-on (SSO) support
- API rate limiting
- Advanced audit logging
- User invitation system

### Security Improvements
- Token blacklisting
- IP-based access control
- Session management
- Advanced threat detection

## Troubleshooting

### Common Issues

1. **Database Connection**
   - Verify PostgreSQL is running
   - Check connection string in `.env`
   - Ensure database exists

2. **Migration Errors**
   - Check Alembic configuration
   - Verify model imports
   - Run `alembic current` to check status

3. **Authentication Failures**
   - Verify JWT secret is set
   - Check token expiration
   - Validate company context

### Logs
Check application logs for detailed error information:
```bash
docker logs <container_name>
```

## Support

For issues or questions:
1. Check the logs for error details
2. Verify configuration settings
3. Test with the provided test script
4. Review API documentation at `/docs`
