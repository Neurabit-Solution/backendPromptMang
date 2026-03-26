#!/usr/bin/env python3
"""
Adds missing columns for the Collaborative Canvas feature to the 'challenges' table.
Missing columns: challenge_type, day_number, group_id, previous_winner_id.
"""

import psycopg2
import sys

# Using the database URL from your environment configuration
DB_URL = "postgresql://admin:admin%40123@35.154.148.0:5432/magicpin"

def migrate_collaborative_columns():
    """
    Applies the ALTER TABLE commands to add the necessary columns 
    for the Collaborative Canvas challenge type.
    """
    try:
        print(f"Connecting to database at 35.154.148.0...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        print("Migrating 'challenges' table for collaborative canvas features...")
        
        # 1. Add challenge_type
        cur.execute("ALTER TABLE challenges ADD COLUMN IF NOT EXISTS challenge_type VARCHAR(50) DEFAULT 'mystery';")
        
        # 2. Add day_number
        cur.execute("ALTER TABLE challenges ADD COLUMN IF NOT EXISTS day_number INTEGER DEFAULT 1;")
        
        # 3. Add group_id
        cur.execute("ALTER TABLE challenges ADD COLUMN IF NOT EXISTS group_id INTEGER;")
        
        # 4. Add previous_winner_id (pointing to creations)
        cur.execute("ALTER TABLE challenges ADD COLUMN IF NOT EXISTS previous_winner_id INTEGER REFERENCES creations(id) ON DELETE SET NULL;")
        
        conn.commit()
        print("SUCCESS: Collaborative canvas columns added to 'challenges' table.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"CRITICAL: Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_collaborative_columns()
