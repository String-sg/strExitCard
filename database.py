
import os
import psycopg2
from datetime import datetime

def init_db():
    """Initialize the database and create tables if needed"""
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # Create feedback table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                session_id TEXT,
                search_term TEXT,
                nps_score INTEGER,
                email TEXT,
                comments TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        conn.commit()
    except Exception as e:
        print(f"Database initialization error: {e}")
    finally:
        cur.close()
        conn.close()

def save_feedback(session_id, search_term, nps_score=None, email=None, comments=None):
    """Save feedback to PostgreSQL database"""
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute(
            '''
            INSERT INTO feedback (session_id, search_term, nps_score, email, comments, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (session_id, search_term, nps_score, email, comments, datetime.now())
        )
        
        conn.commit()
    finally:
        cur.close()
        conn.close()
