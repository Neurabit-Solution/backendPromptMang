# MagicPic Admin Backend

This is the FastAPI-based backend for the MagicPic Admin Panel.

## 🛠️ Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic v2

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- PostgreSQL

### 2. Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup
1. Create a PostgreSQL database named `magicpic`.
2. Run the base schema: `psql -d magicpic -f database_schema.sql`
3. Run the admin extension: `psql -d magicpic -f admin_schema_extension.sql`

### 4. Configuration
The application uses `config.properties` for configuration. Ensure it exists in the root directory and contains the correct database credentials and security settings.

```ini
[database]
db_host = localhost
db_port = 5432
db_name = magicpic
db_user = myuser
db_password = example

[security]
secret_key = YOUR_SUPER_SECRET_KEY_CHANGE_THIS
algorithm = HS256
access_token_expire_minutes = 30
refresh_token_expire_days = 7
```

### 5. Running the API
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
Documentation: `http://localhost:8000/docs`

## 📁 Project Structure
- `app/api/`: API routes and logic
- `app/core/`: Configuration and security
- `app/db/`: Database session and base models
- `app/models/`: SQLAlchemy database models
- `app/schemas/`: Pydantic validation schemas

## 📘 Documentation
- [Admin API Specification](./ADMIN_API_SPECIFICATION.md)
- [Frontend Integration Guide](./FRONTEND_API_GUIDE.md)
