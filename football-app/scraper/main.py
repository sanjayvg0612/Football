import os
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

API_TOKEN = os.getenv("FOOTBALL_DATA_API_TOKEN", "d599c4dcb18c4f84b2000c37301f1916")

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
        cur.execute('''
            CREATE TABLE IF NOT EXISTS fixtures (
                id BIGINT PRIMARY KEY,
                home_team VARCHAR(100),
                away_team VARCHAR(100),
                match_date TIMESTAMP,
                league VARCHAR(100),
                status VARCHAR(50)
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

from datetime import datetime, timedelta

# Scrape logic targeting football-data.org API
def scrape_football_data():
    print(f"[{datetime.now()}] Scraping football data from football-data.org...")
    
    date_from = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    date_to = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    url = f"https://api.football-data.org/v4/matches?dateFrom={date_from}&dateTo={date_to}"
    headers = {
        "X-Auth-Token": API_TOKEN
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            matches_to_insert = []
            fixtures_to_insert = []
            
            for match in data.get("matches", []):
                api_status = match.get("status")
                
                # Map football-data.org status to our internal status
                if api_status in ["IN_PLAY", "PAUSED"]:
                    match_status = "LIVE"
                elif api_status == "FINISHED":
                    match_status = "FINISHED"
                else:
                    match_status = "SCHEDULED"
                
                score_obj = match.get("score", {}).get("fullTime", {})
                if score_obj is None:
                    score_obj = {}
                home_score = score_obj.get("home") if score_obj.get("home") is not None else 0
                away_score = score_obj.get("away") if score_obj.get("away") is not None else 0
                
                minute = "Live" if match_status == "LIVE" else ""
                
                matches_to_insert.append((
                    match.get("id"),
                    match.get("homeTeam", {}).get("name", "Unknown"),
                    match.get("awayTeam", {}).get("name", "Unknown"),
                    home_score,
                    away_score,
                    minute,
                    match_status,
                    datetime.now()
                ))
                
                # If Scheduled, also add to fixtures table
                if match_status == "SCHEDULED":
                    utc_date_str = match.get("utcDate", "")
                    try:
                        match_date = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ")
                    except:
                        match_date = datetime.now()
                        
                    fixtures_to_insert.append((
                        match.get("id"),
                        match.get("homeTeam", {}).get("name", "Unknown"),
                        match.get("awayTeam", {}).get("name", "Unknown"),
                        match_date,
                        match.get("competition", {}).get("name", "Unknown"),
                        match_status
                    ))
            
            if matches_to_insert or fixtures_to_insert:
                update_database(matches_to_insert, fixtures_to_insert)
            else:
                print("No matches retrieved from football-data.org for today.")
                
        else:
            print(f"Failed to fetch data, status code: {response.status_code}. Response: {response.text}")
    except Exception as e:
        print(f"Error during scraping: {e}")

def update_database(matches, fixtures):
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        for match in matches:
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
            
        for fixture in fixtures:
            cur.execute('''
                INSERT INTO fixtures (id, home_team, away_team, match_date, league, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE 
                SET home_team = EXCLUDED.home_team,
                    away_team = EXCLUDED.away_team,
                    match_date = EXCLUDED.match_date,
                    league = EXCLUDED.league,
                    status = EXCLUDED.status;
            ''', fixture)
            
        conn.commit()
        cur.close()
        conn.close()
        print(f"Successfully updated/inserted {len(matches)} live scores and {len(fixtures)} fixtures in PostgreSQL.")
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
