
import psycopg2
from datetime import datetime, timedelta, timezone

db_url = "postgresql://admin:admin%40123@35.154.148.0:5432/magicpin"

def insert_sample_challenge():
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        now = datetime.now(timezone.utc)
        ends = now + timedelta(days=7)
        
        print("Inserting sample Mystery Prompt challenge...")
        cur.execute("""
            INSERT INTO challenges (name, description, target_image_url, prompt_template, starts_at, ends_at, is_active)
            VALUES (
                'Studio Ghibli Mastery', 
                'Can you match the whimsical aesthetic of Hayao Miyaki? Upload your portrait and see how perfectly you can transform into a Ghibli character.', 
                'https://prompt-management-system.s3.ap-south-1.amazonaws.com/styles/ghibli_reference.jpg', 
                'Transform this person into a high-quality Studio Ghibli anime style portrait. Use soft pastel colors, dreamy lighting, and a peaceful hand-drawn forest background. Maintain facial identity.', 
                %s, %s, true
            )
        """, (now, ends))
        
        conn.commit()
        print("Sample challenge inserted successfully!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to insert sample: {e}")

if __name__ == "__main__":
    insert_sample_challenge()
