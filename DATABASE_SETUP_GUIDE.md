# Database Setup Guide

This guide will help you set up the PostgreSQL database for MagicPic.

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL running in Docker (as per your docker-compose.yml)

## Your Database Configuration

Based on your docker-compose.yml:
- **Host**: localhost
- **Port**: 5432
- **Database**: mydatabase
- **User**: myuser
- **Password**: example

---

## Setup Steps

### Step 1: Start PostgreSQL Container

Make sure your Docker containers are running:

```bash
# Navigate to directory with docker-compose.yml
cd /path/to/your/docker-compose-directory

# Start containers
docker-compose up -d

# Verify PostgreSQL is running
docker-compose ps
```

### Step 2: Connect to PostgreSQL

**Option A: Using Docker Exec (Recommended)**

```bash
# Connect to PostgreSQL inside the container
docker-compose exec db psql -U myuser -d mydatabase
```

**Option B: Using psql from your local machine**

```bash
# If you have psql installed locally
psql -h localhost -p 5432 -U myuser -d mydatabase
```

When prompted, enter password: `example`

### Step 3: Create Database Tables

**From inside the container or psql:**

```bash
# Navigate to your project directory
cd /home/mritunjay/Desktop/backendPromptMang

# Execute the schema file
docker-compose exec -T db psql -U myuser -d mydatabase < database_schema.sql
```

**Alternative: Copy-paste the SQL**

```bash
# Connect to database
docker-compose exec db psql -U myuser -d mydatabase

# Then inside psql, run:
\i /path/to/database_schema.sql
```

### Step 4: Insert Sample Data (Optional)

```bash
# Execute sample data file
docker-compose exec -T db psql -U myuser -d mydatabase < sample_data.sql
```

### Step 5: Verify Setup

Connect to the database and verify tables were created:

```bash
# Connect to database
docker-compose exec db psql -U myuser -d mydatabase
```

Inside psql, run these commands:

```sql
-- List all tables
\dt

-- Check table counts
SELECT 
    'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'categories', COUNT(*) FROM categories
UNION ALL
SELECT 'styles', COUNT(*) FROM styles;

-- View sample category data
SELECT * FROM categories;

-- View sample styles
SELECT id, name, category_id FROM styles;

-- Exit psql
\q
```

---

## Quick Command Reference

### Connect to Database

```bash
docker-compose exec db psql -U myuser -d mydatabase
```

### Execute SQL File

```bash
docker-compose exec -T db psql -U myuser -d mydatabase < filename.sql
```

### View All Tables

```sql
\dt
```

### Describe a Table

```sql
\d users
\d styles
\d creations
```

### View Table Data

```sql
SELECT * FROM categories;
SELECT * FROM styles LIMIT 5;
SELECT * FROM users;
```

### Drop All Tables (Reset Database)

```sql
DROP TABLE IF EXISTS ad_watches CASCADE;
DROP TABLE IF EXISTS credit_transactions CASCADE;
DROP TABLE IF EXISTS likes CASCADE;
DROP TABLE IF EXISTS votes CASCADE;
DROP TABLE IF EXISTS battles CASCADE;
DROP TABLE IF EXISTS creations CASCADE;
DROP TABLE IF EXISTS styles CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;
```

---

## Complete Setup Script (All-in-One)

Create a shell script for easy setup:

```bash
#!/bin/bash
# setup_database.sh

echo "Starting PostgreSQL setup for MagicPic..."

# Check if containers are running
echo "Checking Docker containers..."
docker-compose ps

# Create tables
echo "Creating database tables..."
docker-compose exec -T db psql -U myuser -d mydatabase < database_schema.sql

# Insert sample data
echo "Inserting sample data..."
docker-compose exec -T db psql -U myuser -d mydatabase < sample_data.sql

# Verify setup
echo "Verifying setup..."
docker-compose exec db psql -U myuser -d mydatabase -c "\dt"

echo "Database setup complete!"
echo ""
echo "Demo credentials:"
echo "  Email: demo@magicpic.com"
echo "  Password: Test123456"
```

Make it executable and run:

```bash
chmod +x setup_database.sh
./setup_database.sh
```

---

## Adminer (Web Interface)

You can also use Adminer to view and manage your database:

1. Open browser: http://localhost:8080
2. Login with:
   - **System**: PostgreSQL
   - **Server**: db
   - **Username**: myuser
   - **Password**: example
   - **Database**: mydatabase

---

## Update config.properties

Update your application configuration:

```ini
[database]
db_host = localhost
db_port = 5432
db_name = mydatabase
db_user = myuser
db_password = example

[security]
secret_key = your-super-secret-key-change-this-in-production
algorithm = HS256
access_token_expire_minutes = 30
refresh_token_expire_days = 7
```

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Testing the Setup

Start your FastAPI application:

```bash
# Navigate to project directory
cd /home/mritunjay/Desktop/backendPromptMang

# Activate virtual environment (if using)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload

# Open API docs
# http://localhost:8000/docs
```

Test signup:

```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "name": "Test User"
  }'
```

---

## Troubleshooting

### Cannot connect to database

```bash
# Check if container is running
docker-compose ps

# Check container logs
docker-compose logs db

# Restart containers
docker-compose restart
```

### Permission denied

```bash
# Make sure you're in the right directory
cd /home/mritunjay/Desktop/backendPromptMang

# Check file permissions
ls -la database_schema.sql
```

### Tables already exist

```bash
# Connect to database
docker-compose exec db psql -U myuser -d mydatabase

# Drop all tables
DROP TABLE IF EXISTS ad_watches CASCADE;
DROP TABLE IF EXISTS credit_transactions CASCADE;
DROP TABLE IF EXISTS likes CASCADE;
DROP TABLE IF EXISTS votes CASCADE;
DROP TABLE IF EXISTS battles CASCADE;
DROP TABLE IF EXISTS creations CASCADE;
DROP TABLE IF EXISTS styles CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

# Exit
\q

# Re-run setup
docker-compose exec -T db psql -U myuser -d mydatabase < database_schema.sql
```

---

## Expected Database Schema

After successful setup, you should have **9 tables**:

1. ✅ **users** - User accounts (1 demo user)
2. ✅ **categories** - Style categories (5 categories)
3. ✅ **styles** - AI styles (12 sample styles)
4. ✅ **creations** - Generated images (empty initially)
5. ✅ **battles** - Style battles (empty initially)
6. ✅ **votes** - Battle votes (empty initially)
7. ✅ **likes** - Creation likes (empty initially)
8. ✅ **credit_transactions** - Credit log (1 signup transaction)
9. ✅ **ad_watches** - Ad tracking (empty initially)

---

## Next Steps

1. ✅ Database tables created
2. ✅ Sample data inserted
3. 🔲 Update `config.properties` with database credentials
4. 🔲 Run FastAPI application
5. 🔲 Test signup/login endpoints
6. 🔲 Implement image generation feature
7. 🔲 Set up S3/Cloudinary for image storage
8. 🔲 Configure Gemini AI API

Good luck! 🚀
