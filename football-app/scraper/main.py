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
    
    # Debug logs for URL and headers
    print(f"Constructed URL: {url}")
    print(f"Headers: {headers}")
    
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
                
                # Add debug log for each match being processed
                print(f"Processing match: {match}")

                # Add match data to the list for insertion
                matches_to_insert.append({
                    "match_id": match["id"],
                    "home_team": match["homeTeam"]["name"],
                    "away_team": match["awayTeam"]["name"],
                    "home_score": match["score"]["fullTime"]["home"],
                    "away_score": match["score"]["fullTime"]["away"],
                    "minute": match.get("minute", "N/A"),
                    "status": match_status,
                    "updated_at": datetime.now()
                })
                
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
            print(f"Processing match: {match}")
            insert_match_to_db(match)
            print(f"[DEBUG] Match with ID {match['id']} processed.")
            
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

# Updated database insertion logic with debug logs
def insert_match_to_db(match):
    try:
        # Construct the SQL query for insertion
        query = """
        INSERT INTO live_scores (match_id, away_score, away_team, home_score, home_team, minute, status, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (match_id) DO UPDATE SET
            away_score = EXCLUDED.away_score,
            home_score = EXCLUDED.home_score,
            minute = EXCLUDED.minute,
            status = EXCLUDED.status,
            updated_at = NOW();
        """

        # Extract match details
        match_id = match['id']
        away_score = match['score']['fullTime']['away']
        away_team = match['awayTeam']['name']
        home_score = match['score']['fullTime']['home']
        home_team = match['homeTeam']['name']
        minute = match.get('minute', 'FT')  # Default to 'FT' if minute is not available
        status = match['status']

        # Log the query and values
        print(f"[DEBUG] Executing query: {query}")
        print(f"[DEBUG] Values: {match_id}, {away_score}, {away_team}, {home_score}, {home_team}, {minute}, {status}")

        # Execute the query
        cursor.execute(query, (match_id, away_score, away_team, home_score, home_team, minute, status))
        connection.commit()

        print(f"[INFO] Successfully inserted/updated match with ID {match_id} into the database.")
    except Exception as e:
        print(f"[ERROR] Failed to insert match with ID {match['id']}: {e}")

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
