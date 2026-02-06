# MagicPic Backend - Authentication System

A FastAPI-based backend service for the MagicPic application with JWT authentication, user management, and PostgreSQL database integration.

## 🚀 Features

- ✅ **User Authentication**: JWT-based signup, login, and token refresh
- ✅ **Secure Password Handling**: Bcrypt password hashing
- ✅ **Database Integration**: PostgreSQL with SQLAlchemy ORM
- ✅ **Configuration Management**: Properties file-based configuration
- ✅ **RESTful API**: FastAPI with automatic OpenAPI documentation

## 📋 Table of Contents

- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)

## 📁 Project Structure

```
backendPromptMang/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── auth.py             # Authentication endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration loader
│   │   ├── database.py         # Database connection
│   │   └── security.py         # JWT & password utilities
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py             # User SQLAlchemy model
│   └── schemas/
│       ├── __init__.py
│       └── user.py             # Pydantic schemas
├── config.properties           # Configuration file (gitignored)
├── requirements.txt
├── SETUP.md                    # Detailed setup instructions
├── API_SPECIFICATION.md        # Complete API specification
├── .gitignore
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL (Docker or local installation)
- pip

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

Since you have PostgreSQL running in Docker, create the database:

```bash
# Access your PostgreSQL container
docker exec -it <postgres_container_name> psql -U postgres

# Create database
CREATE DATABASE magicpic;
\q
```

### 3. Configure Application

Edit `config.properties` and update with your PostgreSQL credentials:

```ini
[database]
db_host = localhost
db_port = 5432
db_name = magicpic
db_user = postgres
db_password = your_password_here

[security]
secret_key = your-super-secret-key-change-this-in-production
algorithm = HS256
access_token_expire_minutes = 30
refresh_token_expire_days = 7
```

**Important**: Generate a strong secret key for production:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Authentication

#### POST `/api/auth/signup`

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe",
  "phone": "+911234567890"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "credits": 2500,
      "is_verified": false,
      "referral_code": "XYZ12345"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "message": "Account created successfully. Please verify your email."
}
```

#### POST `/api/auth/login`

Login with existing credentials.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** Same as signup response

#### POST `/api/auth/refresh`

Refresh access token using refresh token.

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## 🗄️ Database Schema

### Users Table

The application automatically creates the `users` table with the following schema:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Auto-incrementing user ID |
| `email` | String | Unique, Indexed | User email address |
| `hashed_password` | String | NOT NULL | Bcrypt hashed password |
| `name` | String | NOT NULL | User's full name |
| `phone` | String | Nullable | Phone number |
| `avatar_url` | String | Nullable | Profile picture URL |
| `credits` | Integer | Default: 2500 | Virtual currency balance |
| `is_verified` | Boolean | Default: False | Email verification status |
| `referral_code` | String | Unique, Indexed | User's referral code |
| `created_at` | DateTime | Auto | Account creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |

## ⚙️ Configuration

### Environment Variables

The application uses `config.properties` for configuration. All sensitive values should be changed for production:

#### Database Configuration
- `db_host`: PostgreSQL host (default: localhost)
- `db_port`: PostgreSQL port (default: 5432)
- `db_name`: Database name
- `db_user`: Database user
- `db_password`: Database password

#### Security Configuration
- `secret_key`: JWT signing key (MUST be changed in production)
- `algorithm`: JWT algorithm (default: HS256)
- `access_token_expire_minutes`: Access token TTL (default: 30)
- `refresh_token_expire_days`: Refresh token TTL (default: 7)

## 🏃 Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn (Recommended for Production)

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing the API

### Using cURL

**Signup:**
```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "name": "Test User"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

**Refresh Token:**
```bash
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Authorization: Bearer <your_refresh_token>"
```

## 🔐 Security Features

- ✅ Password hashing using Bcrypt
- ✅ JWT-based stateless authentication
- ✅ Separate access and refresh tokens
- ✅ Token expiration handling
- ✅ Secure token storage requirements
- ✅ Input validation using Pydantic

## 🚧 Roadmap & Future Features

See [API_SPECIFICATION.md](API_SPECIFICATION.md) for the complete feature specification including:

- User profile management
- AI image generation with Gemini
- Credit system & transactions
- Style catalog & categories
- Battle system & voting
- Real-time updates
- Payment integration
- Push notifications

## 📝 Notes

- The database tables are created automatically when the application starts
- Make sure PostgreSQL is running before starting the application
- Always use HTTPS in production
- Change the `secret_key` in production
- Implement rate limiting for production use

## 📄 License

This project is part of the MagicPic application.

## 🤝 Contributing

For detailed setup and development guidelines, see [SETUP.md](SETUP.md).
