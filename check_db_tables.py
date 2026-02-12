
import sys
import os

sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from sqlalchemy import text, inspect

def check_tables():
    try:
        db = SessionLocal()
        engine = db.get_bind()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("Tables in database:", tables)
        
        if 'admins' in tables:
            print("Admins table exists.")
            columns = [c['name'] for c in inspector.get_columns('admins')]
            print("Admins columns:", columns)
        else:
            print("Admins table MISSING!")

        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_tables()
