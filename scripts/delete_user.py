import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
db_url = "postgresql://admin:admin%40123@35.154.148.0:5432/magicpin"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def delete_user_by_email(email):
    """
    Deletes the user with the specified email.
    """
    db = SessionLocal()
    try:
        # Check if user exists
        check_query = text("SELECT id, name FROM users WHERE email = :email")
        user = db.execute(check_query, {"email": email}).fetchone()
        
        if not user:
            print(f"User with email '{email}' NOT found.")
            return

        print(f"Found User ID: {user.id}, Name: {user.name}")
        
        # Admin confirmation
        confirm = input(f"Are you SURE you want to DELETE user {user.name} and all their data? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Deletion aborted.")
            return

        # Deleting the user (cascading deletes based on schema should handle relations)
        delete_query = text("DELETE FROM users WHERE id = :user_id")
        db.execute(delete_query, {"user_id": user.id})
        db.commit()
        
        print(f"User '{email}' successfully deleted.")

    except Exception as e:
        db.rollback()
        print(f"FAILED to delete user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    email_to_delete = "mritunjay.sharma@neurabitsolution.com"
    delete_user_by_email(email_to_delete)
