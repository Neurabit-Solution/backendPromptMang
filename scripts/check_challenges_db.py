
import psycopg2

DB_URL = "postgresql://admin:admin%40123@35.154.148.0:5432/magicpin"

def check_challenges():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT id, name, challenge_type, is_active, starts_at, ends_at FROM challenges;")
        rows = cur.fetchall()
        
        print(f"Total challenges: {len(rows)}")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Type: {row[2]}, Active: {row[3]}, Starts: {row[4]}, Ends: {row[5]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_challenges()
