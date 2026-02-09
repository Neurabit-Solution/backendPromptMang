# Quick Database Setup Commands

## 🚀 One-Line Setup (Recommended)

```bash
cd /home/mritunjay/Desktop/backendPromptMang && ./setup_database.sh
```

This automated script will:
- ✅ Check Docker is running
- ✅ Start PostgreSQL if needed
- ✅ Create all 9 database tables
- ✅ Insert sample data (5 categories, 12 styles, 1 demo user)
- ✅ Verify everything is set up correctly

---

## 📝 Manual Setup (Step-by-Step)

### 1. Navigate to Project Directory
```bash
cd /home/mritunjay/Desktop/backendPromptMang
```

### 2. Create Database Tables
```bash
docker-compose exec -T db psql -U myuser -d mydatabase < database_schema.sql
```

### 3. Insert Sample Data
```bash
docker-compose exec -T db psql -U myuser -d mydatabase < sample_data.sql
```

### 4. Verify Setup
```bash
docker-compose exec db psql -U myuser -d mydatabase -c "\dt"
```

---

## 🔍 Quick Verification

### Connect to Database
```bash
docker-compose exec db psql -U myuser -d mydatabase
```

### Inside psql, run:
```sql
-- List all tables
\dt

-- Count records
SELECT 'users' as table, COUNT(*) FROM users
UNION ALL SELECT 'categories', COUNT(*) FROM categories
UNION ALL SELECT 'styles', COUNT(*) FROM styles;

-- Exit
\q
```

---

## 🌐 Adminer (Web Interface)

**URL**: http://localhost:8080

**Login:**
- System: PostgreSQL
- Server: db
- Username: myuser
- Password: example
- Database: mydatabase

---

## 👤 Demo Credentials

After setup, you can test with:
- **Email**: demo@magicpic.com
- **Password**: Test123456
- **Credits**: 2500

---

## 🔄 Reset Database

If you need to start over:

```bash
docker-compose exec db psql -U myuser -d mydatabase << EOF
DROP TABLE IF EXISTS ad_watches CASCADE;
DROP TABLE IF EXISTS credit_transactions CASCADE;
DROP TABLE IF EXISTS likes CASCADE;
DROP TABLE IF EXISTS votes CASCADE;
DROP TABLE IF EXISTS battles CASCADE;
DROP TABLE IF EXISTS creations CASCADE;
DROP TABLE IF EXISTS styles CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;
EOF
```

Then run setup again:
```bash
./setup_database.sh
```

---

## 📊 What Gets Created

### 9 Tables:
1. **users** (1 demo user)
2. **categories** (5 categories)
3. **styles** (12 sample styles)
4. **creations** (empty)
5. **battles** (empty)
6. **votes** (empty)
7. **likes** (empty)
8. **credit_transactions** (1 signup transaction)
9. **ad_watches** (empty)

### Sample Categories:
- 🎨 Artistic
- 💒 Wedding
- 📚 Education
- 💼 Professional
- 🎭 Fun & Creative

### Sample Styles:
- Studio Ghibli Art
- Watercolor Portrait
- Oil Painting - Renaissance
- Modern Anime Character
- Cyberpunk Neon
- Elegant Wedding Card
- Romantic Portrait
- Textbook Illustration
- Professional Headshot
- Vintage Polaroid
- Pop Art Style
- And more...

---

## 🐛 Troubleshooting

### Docker not running?
```bash
# Check Docker status
docker ps

# Start Docker if needed
sudo systemctl start docker
```

### Container not running?
```bash
# Start containers
docker-compose up -d

# Check status
docker-compose ps
```

### Connection refused?
```bash
# Wait a few seconds and try again
sleep 5

# Or restart containers
docker-compose restart
```

---

## ✅ Success Indicators

You should see:
```
✅ Database schema created successfully
✅ Sample data inserted successfully
✅ users: 1 records
✅ categories: 5 records
✅ styles: 12 records
✅ Database Setup Complete!
```

---

## 🚀 Next Steps After Setup

1. **Update config.properties**:
   ```ini
   [database]
   db_host = localhost
   db_port = 5432
   db_name = mydatabase
   db_user = myuser
   db_password = example
   ```

2. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Test the API**:
   - Docs: http://localhost:8000/docs
   - Test signup/login endpoints

That's it! 🎉
