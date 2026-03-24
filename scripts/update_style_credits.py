#!/usr/bin/env python3
"""
Update all styles in the database to require only 1 credit.
"""

import sys
from pathlib import Path
from sqlalchemy import text

# Allow importing app when run as script from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal

def update_style_credits():
    """
    Updates all entries in the 'styles' table to have credits_required = 1.
    """
    db = SessionLocal()
    try:
        print("Starting update of credit requirements for all styles...")
        
        # Update the 'styles' table
        update_query = text("""
            UPDATE styles 
            SET credits_required = 1
        """)
        
        result = db.execute(update_query)
        db.commit()
        
        print(f"Successfully updated {result.rowcount} styles to 1 credit requirement.")

    except Exception as e:
        db.rollback()
        print(f"FAILED to update styles: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    confirm = input("Are you SURE you want to change credit requirements for EVERY style to 1? (yes/no): ")
    if confirm.lower() == 'yes':
        update_style_credits()
    else:
        print("Update aborted.")
