#!/usr/bin/env python3
"""
Add credits to a specific user identified by their email address.
The script increments the existing credit balance of the user and recorded as an admin_adjustment transaction.

Usage:
    python scripts/add_user_credits.py <email> <amount>
"""

import sys
import argparse
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection details (matching existing script configurations)
DB_URL = "postgresql://admin:admin%40123@35.154.148.0:5432/magicpin"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_credits_to_user(email: str, amount_to_add: int):
    """
    Increments credit balance for the user with the specified email.
    Records transaction in credit_transactions for audit purposes.
    """
    db = SessionLocal()
    try:
        # Check if user exists and get current credits
        print(f"Searching for user with email: {email}...")
        check_query = text("SELECT id, name, credits FROM users WHERE email = :email")
        user = db.execute(check_query, {"email": email}).fetchone()
        
        if not user:
            print(f"ERROR: User with email '{email}' NOT found in database.")
            return

        user_id, user_name, current_credits = user
        new_balance = (current_credits or 0) + amount_to_add
        print(f"Found User ID: {user_id}, Name: {user_name}, Current Balance: {current_credits}")
        
        # Confirm action
        confirm = input(f"Are you sure you want to add {amount_to_add} credits to {user_name}? (New balance: {new_balance}) (yes/no): ")
        if confirm.lower() != 'yes':
            print("Operation aborted.")
            return

        # 1. Update the 'users' table
        update_query = text("""
            UPDATE users 
            SET credits = :new_balance,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :user_id
        """)
        db.execute(update_query, {"new_balance": new_balance, "user_id": user_id})
        
        # 2. Record the transaction for audit log
        audit_query = text("""
            INSERT INTO credit_transactions (user_id, amount, type, description, balance_after)
            VALUES (:user_id, :amount, 'admin_adjustment', :description, :balance_after)
        """)
        db.execute(audit_query, {
            "user_id": user_id,
            "amount": amount_to_add,
            "description": f"Admin manual top-up of {amount_to_add} units",
            "balance_after": new_balance
        })

        db.commit()
        print(f"SUCCESS: Credits updated for {user_name}.")
        print(f"  Old balance: {current_credits}")
        print(f"  Added: {amount_to_add}")
        print(f"  New balance: {new_balance}")

    except Exception as e:
        db.rollback()
        print(f"FAILED to update credits: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Program to increment credits for a user by their email.")
    parser.add_argument("email", type=str, help="Email address of the user to increment.")
    parser.add_argument("amount", type=int, help="Number of credits to increment (add).")

    args = parser.parse_args()
    
    add_credits_to_user(args.email, args.amount)
