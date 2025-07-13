"""
Progress and analytics models for tracking user engagement
"""

from datetime import datetime
from app import db

class Progress(db.Model):
    """User progress tracking for lessons."""
    
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float, default=0.0)
    attempts = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Integer, default=0)  # seconds
    last_played = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('progress', lazy=True))
    
    def to_dict(self):
        """Convert progress to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'completed': self.completed,
            'score': self.score,
            'attempts': self.attempts,
            'time_spent': self.time_spent,
            'last_played': self.last_played.isoformat() if self.last_played else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Progress {self.user_id}:{self.lesson_id}>'

class EventLog(db.Model):
    """Event logging for analytics and debugging."""
    
    __tablename__ = 'event_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # gesture, lesson_start, lesson_complete, etc.
    lesson_id = db.Column(db.String(100), nullable=True)
    data = db.Column(db.JSON)  # Flexible JSON data for event details
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('events', lazy=True))
    
    def to_dict(self):
        """Convert event log to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'event_type': self.event_type,
            'lesson_id': self.lesson_id,
            'data': self.data,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<EventLog {self.event_type}:{self.session_id}>' 