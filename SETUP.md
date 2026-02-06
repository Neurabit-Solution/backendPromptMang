# Setup Instructions

## Database Setup

Since you already have PostgreSQL deployed on Docker, follow these steps to prepare the database for the MagicPic backend.

### 1. Create the Database

Access your running PostgreSQL container (assuming container name is `postgres_container`, change it if different):

```bash
docker exec -it <your_postgres_container_name_or_id> psql -U postgres
```

Inside the psql shell, run:

```sql
CREATE DATABASE magicpic;
\c magicpic
```

The application will automatically create the tables when it starts (via `Base.metadata.create_all(bind=engine)` in `main.py`).

### 2. Configuration

Ensure your `config.properties` file in the root directory matches your PostgreSQL connection details:

```ini
[database]
db_host = localhost 
db_port = 5432
db_name = magicpic
db_user = postgres
db_password = postgres  # Change this to your actual password
```

Note: If your app is running outside Docker (e.g., on your host machine) and connecting to Docker, `localhost` usually works if the port is mapped. If running the app *inside* Docker, you might need to use `host.docker.internal` or the container name.

## Schema

The authentication system uses the `users` table with the following schema (automatically created):

- **id**: Integer (Primary Key)
- **email**: String (Unique, Indexed)
- **hashed_password**: String
- **name**: String
- **phone**: String (Optional)
- **avatar_url**: String (Optional)
- **credits**: Integer (Default: 2500)
- **is_verified**: Boolean (Default: False)
- **referral_code**: String (Unique)
- **created_at**: DateTime
- **updated_at**: DateTime

## Running the Application

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Test Authentication**:
   - **Signup**: POST `http://localhost:8000/api/auth/signup`
   - **Login**: POST `http://localhost:8000/api/auth/login`

   Check `http://localhost:8000/docs` for the interactive Swagger UI.
