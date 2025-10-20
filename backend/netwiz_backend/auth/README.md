# NetWiz Authentication System

A comprehensive JWT-based authentication system for NetWiz backend with role-based access control, automatic admin account creation, and decorator-based endpoint protection.

## 🚀 Features

- **JWT Authentication** - Access and refresh tokens with configurable expiration
- **Password Security** - bcrypt hashing with application-specific pepper
- **Role-Based Access** - User and Admin roles with automatic assignment
- **Auto Admin Creation** - Admin account created on startup with configurable password
- **Decorator-Based Protection** - Simple decorators for endpoint access control
- **Password Management** - Change password functionality
- **Token Refresh** - Automatic token refresh mechanism

## 📁 Structure

```
auth/
├── __init__.py              # Module initialization
├── models.py                # Pydantic models for auth
├── repository.py            # Database operations
├── jwt_utils.py             # JWT and password utilities
├── middleware.py            # Authentication middleware
├── middleware_auth.py       # Decorator-based auth middleware
├── decorators.py            # Access control decorators
├── controller.py            # Auth endpoints controller
├── admin_init.py            # Admin account initialization
└── decorator_examples.py    # Usage examples
```

## 🔧 Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Configuration
PASSWORD_PEPPER=NetWizAOSDFAMSDF
ADMIN_TEMP_PASSWORD=admin
```

### Default Behavior

- **Access tokens**: 30 minutes expiration
- **Refresh tokens**: 7 days expiration
- **Password pepper**: "NetWizAOSDFAMSDF"
- **Admin temp password**: "admin"
- **Default access**: Requires authentication (secure by default)

## 🔐 Authentication Decorators

### Available Decorators

```python
from netwiz_backend.auth.decorators import PUBLIC, AUTH, ADMIN, OPTIONAL_AUTH

@PUBLIC
async def public_endpoint():
    """Anyone can access this endpoint"""
    return {"message": "Public access"}

@AUTH
async def protected_endpoint(current_user: User = Depends(get_current_active_user)):
    """Only authenticated users can access this"""
    return {"user": current_user.username}

@ADMIN
async def admin_endpoint(current_user: User = Depends(get_current_active_user)):
    """Only admins can access this"""
    return {"admin": current_user.username}

@OPTIONAL_AUTH
async def flexible_endpoint(current_user: User | None = Depends(get_optional_current_user)):
    """Works with or without authentication"""
    if current_user:
        return {"message": f"Hello {current_user.username}"}
    return {"message": "Hello anonymous user"}

# No decorator = requires authentication by default
async def default_endpoint(current_user: User = Depends(get_current_active_user)):
    """This endpoint requires auth by default"""
    return {"user": current_user.username}
```

### Decorator Behavior

| Decorator | Auth Required | User Type | Description |
|-----------|---------------|-----------|-------------|
| `@PUBLIC` | ❌ No | Any | Public access |
| `@AUTH` | ✅ Yes | User/Admin | Authenticated users |
| `@ADMIN` | ✅ Yes | Admin only | Admin privileges required |
| `@OPTIONAL_AUTH` | ⚠️ Optional | Any | Works with/without auth |
| No decorator | ✅ Yes | User/Admin | Default behavior |

### ⚠️ Important: Decorator Conflicts

**Conflicting decorators will raise a `ValueError`** to prevent ambiguous behavior:

```python
# ❌ This will raise ValueError
@PUBLIC
@AUTH
def conflicting_endpoint():
    return {"error": "This will never work"}

# ✅ This is fine - non-conflicting decorators
@staticmethod
@PUBLIC
def static_public_endpoint():
    return {"message": "This works"}
```

**Allowed combinations:**
- `@staticmethod` + auth decorators
- `@classmethod` + auth decorators
- `@property` + auth decorators
- Other non-auth decorators + auth decorators

**Forbidden combinations:**
- Multiple auth decorators on the same function
- Any combination of `@PUBLIC`, `@AUTH`, `@ADMIN`, `@OPTIONAL_AUTH`

## 🌐 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `POST` | `/auth/signup` | Public | Create new user account |
| `POST` | `/auth/signin` | Public | Authenticate user |
| `POST` | `/auth/signout` | Auth | Sign out user |
| `POST` | `/auth/refresh` | Public | Refresh access token |
| `POST` | `/auth/change-password` | Auth | Change user password |
| `GET` | `/auth/me` | Auth | Get current user info |

### Request/Response Examples

#### Sign Up
```bash
POST /auth/signup
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}
```

Response:
```json
{
  "id": "uuid-here",
  "username": "john_doe",
  "user_type": "user",
  "created_at": "2024-01-01T00:00:00Z",
  "is_active": true
}
```

#### Sign In
```bash
POST /auth/signin
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}
```

Response:
```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_expires_in": 604800
}
```

#### Change Password
```bash
POST /auth/change-password
Authorization: Bearer jwt-access-token
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

Response:
```json
{
  "message": "Password changed successfully"
}
```

## 👤 User Management

### User Types

- **USER** - Regular user account (default)
- **ADMIN** - Administrator account with elevated privileges

### Admin Account

- **Auto-creation**: Admin account created on startup if it doesn't exist
- **Username**: "admin" (case-insensitive)
- **Password**: Configurable via `ADMIN_TEMP_PASSWORD` (default: "admin")
- **Security**: Change password immediately after first login

### User Model

```python
class User(BaseModel):
    id: str                    # Auto-generated UUID
    username: str              # 3-50 characters
    hashed_password: str       # bcrypt + pepper
    user_type: UserType        # USER or ADMIN
    created_at: datetime       # Creation timestamp
    is_active: bool            # Account status
```

## 🔒 Security Features

### Password Security

- **bcrypt hashing** with configurable rounds
- **Application pepper** for defense-in-depth
- **Salt per password** (handled by bcrypt)
- **Minimum 6 characters** password requirement

### JWT Security

- **Separate secrets** for access and refresh tokens
- **Token type validation** to prevent misuse
- **Configurable expiration** times
- **HS256 algorithm** by default

### Access Control

- **Secure by default** - endpoints require auth unless marked `@PUBLIC`
- **Role-based permissions** - admin-only endpoints with `@ADMIN`
- **Token validation** - automatic token verification
- **User state management** - active/inactive user support

## 🚀 Getting Started

### 1. Configure Environment

```bash
# Copy and modify environment variables
cp .env.example .env

# Set your secrets
JWT_SECRET_KEY=your-super-secret-key-here
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-here
PASSWORD_PEPPER=your-application-pepper-here
ADMIN_TEMP_PASSWORD=your-admin-password-here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Application

```bash
python -m netwiz_backend.main
```

### 4. First Login

```bash
# Login as admin with temporary password
curl -X POST http://localhost:5000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Change admin password immediately
curl -X POST http://localhost:5000/auth/change-password \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"current_password": "admin", "new_password": "newsecurepassword123"}'
```

## 🛠️ Development

### Adding New Endpoints

```python
from netwiz_backend.auth.decorators import AUTH, ADMIN
from netwiz_backend.auth.middleware import get_current_active_user

class MyController:
    @AUTH
    async def my_endpoint(self, current_user: User = Depends(get_current_active_user)):
        return {"message": f"Hello {current_user.username}"}

    @ADMIN
    async def admin_only_endpoint(self, current_user: User = Depends(get_current_active_user)):
        return {"admin_action": "performed"}
```

### Testing Authentication

```python
# Test decorator inspection
from netwiz_backend.auth.decorators import requires_auth, get_auth_level, is_admin_required

def test_endpoint():
    pass

@AUTH
def protected_endpoint():
    pass

@ADMIN
def admin_endpoint():
    pass

# Check decorator attributes
print(requires_auth(test_endpoint))      # True (default)
print(get_auth_level(protected_endpoint))  # "user"
print(is_admin_required(admin_endpoint))  # True
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc
- **OpenAPI JSON**: http://localhost:5000/openapi.json

## 🔧 Troubleshooting

### Common Issues

1. **Admin account not created**
   - Check `ADMIN_TEMP_PASSWORD` environment variable
   - Verify database connection
   - Check startup logs for admin creation messages

2. **Token validation fails**
   - Verify `JWT_SECRET_KEY` is set correctly
   - Check token expiration times
   - Ensure token is sent in Authorization header

3. **Password verification fails**
   - Check `PASSWORD_PEPPER` configuration
   - Verify bcrypt installation
   - Ensure password meets minimum requirements

### Debug Mode

Set `ENVIRONMENT=development` to enable debug logging and detailed error messages.

## 📄 License

This authentication system is part of the NetWiz project. See the main project LICENSE file for details.
