
from replit import db
from datetime import datetime

def init_db():
    """Initialize the database if needed"""
    if 'feedback' not in db:
        db['feedback'] = []

def save_feedback(session_id, search_term, nps_score=None, email=None):
    """Save feedback to Replit database"""
    if 'feedback' not in db:
        db['feedback'] = []
    
    feedback_entry = {
        'session_id': session_id,
        'search_term': search_term,
        'nps_score': nps_score,
        'email': email,
        'created_at': str(datetime.now())
    }
    
    current_feedback = db['feedback']
    current_feedback.append(feedback_entry)
    db['feedback'] = current_feedback
