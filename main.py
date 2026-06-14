import os
import logging
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s'
)

# ─── CONNECT ─────────────────────────────────────────────────────────────────

def connect_spotify():
    """OAuth 2.0 connection to Spotify Web API."""
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-read-recently-played"
    ))

# ─── EXTRACT ─────────────────────────────────────────────────────────────────

def extract_data(sp):
    """Pull the last 50 plays from Spotify."""
    logging.info("EXTRACT: Requesting recently played tracks...")
    results = sp.current_user_recently_played(limit=50)
    return results['items']

# ─── TRANSFORM ───────────────────────────────────────────────────────────────

def transform_data(raw_items):
    """Flatten nested JSON into a clean DataFrame."""
    logging.info("TRANSFORM: Parsing track metadata...")
    cleaned = []
    for item in raw_items:
        track = item['track']
        cleaned.append({
            "played_at": pd.to_datetime(item['played_at']),
            "song_name": track['name'],
            "artist_name": ", ".join(a['name'] for a in track['artists']),
            "album_name": track['album']['name'],
            "duration_min": round(track['duration_ms'] / 60000, 2),
        })
    df = pd.DataFrame(cleaned)

    if df.empty:
        logging.warning("TRANSFORM: No tracks returned. Nothing to load.")
        return None

    logging.info(f"TRANSFORM: Built DataFrame with {len(df)} rows.")
    return df

# ─── LOAD ─────────────────────────────────────────────────────────────────────
# FIX: Original df.to_sql(if_exists='append') raises IntegrityError on
# duplicate played_at values. This version uses ON CONFLICT DO NOTHING.

def load_data(df):
    """Upsert rows — duplicates are silently skipped."""
    if df is None:
        return
    
    logging.info("LOAD: Connecting to Supabase PostgreSQL...")
    engine = create_engine(os.getenv("DATABASE_URL"))
    inserted = 0
    skipped = 0
    
    with engine.connect() as conn:
        for _, row in df.iterrows():
            result = conn.execute(text("""
                INSERT INTO listening_history
                (played_at, song_name, artist_name, album_name, duration_min)
                VALUES
                (:played_at, :song_name, :artist_name, :album_name, :duration_min)
                ON CONFLICT (played_at) DO NOTHING
            """), row.to_dict())
            
            if result.rowcount == 1:
                inserted += 1
            else:
                skipped += 1
        conn.commit()

    logging.info(f"LOAD: {inserted} rows inserted, {skipped} duplicates skipped.")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        sp = connect_spotify()
        raw = extract_data(sp)
        clean_df = transform_data(raw)
        load_data(clean_df)
        logging.info("Pipeline run complete.")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise