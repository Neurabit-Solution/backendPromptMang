
import sys
import os

# Add the current directory to sys.path to import app correctly
sys.path.append(os.getcwd())

from app.db.session import engine, Base
from app.models.admin import Admin, User, Category, Style, SystemSetting, AdminActivityLog
# Note: Importing these models ensures they are registered with Base.metadata

def create_all_tables():
    print("Connecting to database...")
    try:
        # This will create all tables defined in models if they don't exist
        Base.metadata.create_all(bind=engine)
        print("Successfully created all tables (if they didn't exist).")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Current tables in database: {', '.join(tables)}")
        
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_all_tables()
