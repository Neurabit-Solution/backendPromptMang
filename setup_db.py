import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def setup_database():
    # Database credentials
    host = "35.154.148.0"
    port = "5432"
    user = "admin"
    password = "admin@123"
    dbname = "magicpin"
    
    # 1. Connect to default 'postgres' database to create the new DB
    try:
        print(f"Connecting to default 'postgres' database at {host}...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres" # Connect to default DB first
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        exists = cur.fetchone()
        
        if not exists:
            print(f"Creating database '{dbname}'...")
            cur.execute(f"CREATE DATABASE {dbname}")
            print(f"Database '{dbname}' created successfully.")
        else:
            print(f"Database '{dbname}' already exists.")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return

    # 2. Connect to the new 'magicpin' database and run the schema
    try:
        print(f"Connecting to '{dbname}' database...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        cur = conn.cursor()
        
        # Read the SQL file
        sql_file_path = "/home/mritunjay/Desktop/backendPromptMang/database_schema.sql"
        print(f"Reading schema from {sql_file_path}...")
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
            
        # Execute the script
        print("Executing schema script...")
        cur.execute(sql_script)
        conn.commit()
        print("Schema applied successfully!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error applying schema: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    setup_database()
