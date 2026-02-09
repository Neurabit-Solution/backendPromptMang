#!/bin/bash
# ============================================================
# MagicPic Database Setup Script
# ============================================================
# This script sets up the complete database schema and sample data
# for the MagicPic application
# ============================================================

set -e  # Exit on error

echo "=========================================="
echo "MagicPic Database Setup"
echo "=========================================="
echo ""

# Configuration from docker-compose.yml
DB_USER="myuser"
DB_NAME="mydatabase"
DB_PASSWORD="example"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📋 Configuration:"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Script Directory: $SCRIPT_DIR"
echo ""

# Check if Docker is running
echo "🐳 Checking Docker..."
if ! docker ps &> /dev/null; then
    echo "❌ Error: Docker is not running or you don't have permission"
    echo "   Please start Docker and try again"
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Check if database container is running
echo "🔍 Checking PostgreSQL container..."
if ! docker-compose ps | grep -q "db.*Up"; then
    echo "⚠️  PostgreSQL container is not running"
    echo "   Starting containers..."
    docker-compose up -d
    echo "   Waiting for PostgreSQL to be ready..."
    sleep 5
fi
echo "✅ PostgreSQL container is running"
echo ""

# Test database connection
echo "🔌 Testing database connection..."
if docker-compose exec -T db psql -U $DB_USER -d $DB_NAME -c "SELECT 1;" &> /dev/null; then
    echo "✅ Database connection successful"
else
    echo "❌ Error: Cannot connect to database"
    echo "   Please check your docker-compose configuration"
    exit 1
fi
echo ""

# Create database tables
echo "📊 Creating database tables..."
if docker-compose exec -T db psql -U $DB_USER -d $DB_NAME < "$SCRIPT_DIR/database_schema.sql"; then
    echo "✅ Database schema created successfully"
else
    echo "❌ Error creating database schema"
    exit 1
fi
echo ""

# Insert sample data
echo "📝 Inserting sample data..."
if docker-compose exec -T db psql -U $DB_USER -d $DB_NAME < "$SCRIPT_DIR/sample_data.sql"; then
    echo "✅ Sample data inserted successfully"
else
    echo "❌ Error inserting sample data"
    exit 1
fi
echo ""

# Verify setup
echo "🔍 Verifying database setup..."
docker-compose exec -T db psql -U $DB_USER -d $DB_NAME << 'EOF'
SELECT 
    '✅ ' || table_name || ': ' || count || ' records' as status
FROM (
    SELECT 'users' as table_name, COUNT(*)::text as count FROM users
    UNION ALL
    SELECT 'categories', COUNT(*)::text FROM categories
    UNION ALL
    SELECT 'styles', COUNT(*)::text FROM styles
    UNION ALL
    SELECT 'creations', COUNT(*)::text FROM creations
    UNION ALL
    SELECT 'battles', COUNT(*)::text FROM battles
    UNION ALL
    SELECT 'votes', COUNT(*)::text FROM votes
    UNION ALL
    SELECT 'likes', COUNT(*)::text FROM likes
    UNION ALL
    SELECT 'credit_transactions', COUNT(*)::text FROM credit_transactions
    UNION ALL
    SELECT 'ad_watches', COUNT(*)::text FROM ad_watches
) t;
EOF
echo ""

echo "=========================================="
echo "✅ Database Setup Complete!"
echo "=========================================="
echo ""
echo "📌 Demo User Credentials:"
echo "   Email: demo@magicpic.com"
echo "   Password: Test123456"
echo ""
echo "🌐 Access Adminer (Web Interface):"
echo "   URL: http://localhost:8080"
echo "   Server: db"
echo "   Username: $DB_USER"
echo "   Password: $DB_PASSWORD"
echo "   Database: $DB_NAME"
echo ""
echo "🚀 Next Steps:"
echo "   1. Update config.properties with database credentials"
echo "   2. Run: uvicorn app.main:app --reload"
echo "   3. Visit: http://localhost:8000/docs"
echo ""
