
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
# Using the same URL found in your environment
db_url = "postgresql://admin:admin%40123@35.154.148.0:5432/magicpin"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def reset_user_credits():
    """
    Resets ALL users to 2 base credits and 0 daily credits.
    Also updates daily_credits_date to today to prevent immediate top-ups.
    """
    db = SessionLocal()
    try:
        print("Starting credit reset for all users...")
        
        # 1. Update the 'users' table
        update_query = text("""
            UPDATE users 
            SET credits = 2, 
                daily_credits = 0,
                daily_credits_date = CURRENT_TIMESTAMP
        """)
        
        result = db.execute(update_query)
        db.commit()
        
        print(f"Successfully reset credits for {result.rowcount} users.")
        
        # 2. Add an audit log entry for each user (optional, but good for tracking)
        # Assuming you want to track this change in credit_transactions
        audit_query = text("""
            INSERT INTO credit_transactions (user_id, amount, type, description, balance_after)
            SELECT id, 2, 'admin_adjustment', 'Mass credit reset to 2 units', 2
            FROM users
        """)
        # db.execute(audit_query)
        # db.commit()
        # print("Audit transactions recorded.")

    except Exception as e:
        db.rollback()
        print(f"FAILED to reset credits: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    confirm = input("Are you SURE you want to reset ALL users back to 2 credits? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_user_credits()
    else:
        print("Reset aborted.")
