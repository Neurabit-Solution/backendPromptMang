
import psycopg2
import sys

db_url = "postgresql://admin:admin%40123@35.154.148.0:5432/magicpin"

def migrate():
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("Creating challenges table...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS challenges (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            target_image_url VARCHAR(500) NOT NULL,
            prompt_template TEXT NOT NULL,
            starts_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            ends_at TIMESTAMP WITH TIME ZONE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        print("Updating creations table...")
        cur.execute("""
        ALTER TABLE creations ADD COLUMN IF NOT EXISTS challenge_id INTEGER REFERENCES challenges(id) ON DELETE SET NULL;
        ALTER TABLE creations ADD COLUMN IF NOT EXISTS similarity_score FLOAT DEFAULT 0;
        """)
        
        conn.commit()
        print("Migration successful!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
