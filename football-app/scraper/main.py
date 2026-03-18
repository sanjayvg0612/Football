import requests
import psycopg2
import schedule
import time
from datetime import datetime

# Database Configuration
DB_HOST = "database-1.cluster-cz26q8osk56h.ap-south-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "Sanjayvg0612"

# Set up database connection and ensure the live_scores table exists
def init_db():
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS live_scores (
                match_id BIGINT PRIMARY KEY,
                home_team VARCHAR(100),
                away_team VARCHAR(100),
                home_score INT,
                away_score INT,
                minute VARCHAR(20),
                status VARCHAR(50),
                updated_at TIMESTAMP
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Scrape logic targeting FotMob's hidden JSON API (Example for today's matches)
def scrape_football_data():
    print(f"[{datetime.now()}] Scraping football data...")
    # Date format YYYYMMDD
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://www.fotmob.com/api/matches?date={today}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            matches_to_insert = []
            
            # The JSON structure features leagues -> matches
            leagues = data.get("leagues", [])
            for league in leagues:
                # We specifically look for prominent leagues or active matches
                for match in league.get("matches", []):
                    status_obj = match.get("status", {})
                    
                    # FotMob status: finished, ongoing, cancelled, not started
                    match_status = "LIVE" if status_obj.get("started") and not status_obj.get("finished") else ("FINISHED" if status_obj.get("finished") else "SCHEDULED")
                    
                    matches_to_insert.append((
                        match.get("id"),
                        match.get("home", {}).get("name", "Unknown"),
                        match.get("away", {}).get("name", "Unknown"),
                        match.get("home", {}).get("score", 0) if match.get("home", {}).get("score") is not None else 0,
                        match.get("away", {}).get("score", 0) if match.get("away", {}).get("score") is not None else 0,
                        status_obj.get("liveTime", {}).get("short", "0'"),
                        match_status,
                        datetime.now()
                    ))
            
            update_database(matches_to_insert)
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
    except Exception as e:
        print(f"Error during scraping: {e}")

def update_database(matches):
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        for match in matches:
            # Upsert logic (Insert or Update if exists)
            cur.execute('''
                INSERT INTO live_scores (match_id, home_team, away_team, home_score, away_score, minute, status, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (match_id) DO UPDATE 
                SET home_score = EXCLUDED.home_score,
                    away_score = EXCLUDED.away_score,
                    minute = EXCLUDED.minute,
                    status = EXCLUDED.status,
                    updated_at = EXCLUDED.updated_at;
            ''', match)
            
        conn.commit()
        cur.close()
        conn.close()
        print(f"Successfully updated/inserted {len(matches)} matches in PostgreSQL.")
    except Exception as e:
        print(f"Database update error: {e}")

if __name__ == "__main__":
    init_db()
    # Run immediately once
    scrape_football_data()
    
    # Then schedule every 5 minutes
    schedule.every(5).minutes.do(scrape_football_data)
    
    print("Scraper is running. Waiting for scheduled tasks...")
    while True:
        schedule.run_pending()
        time.sleep(1)
