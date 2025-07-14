"""
Analytics Collector Service
Handles event logging and progress tracking from script orchestrator
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask import current_app
from app import db
from app.models import EventLog, Progress

logger = logging.getLogger(__name__)

class AnalyticsCollector:
    """Service for collecting and storing analytics events and progress data."""
    
    def __init__(self):
        self.batch_size = 10
        self.event_buffer = []
    
    def log_event(self, event_type: str, session_id: str, user_id: Optional[int] = None, 
                  lesson_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        """Log an analytics event."""
        try:
            event = EventLog(
                user_id=user_id,
                session_id=session_id,
                event_type=event_type,
                lesson_id=lesson_id,
                data=data or {},
                timestamp=datetime.utcnow()
            )
            
            # Add to buffer for batch processing
            self.event_buffer.append(event)
            
            # Flush buffer if it's full
            if len(self.event_buffer) >= self.batch_size:
                self.flush_events()
                
            logger.debug(f"Logged event: {event_type} for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging event {event_type}: {e}")
            return False
    
    def flush_events(self):
        """Flush buffered events to database."""
        if not self.event_buffer:
            return
            
        try:
            with current_app.app_context():
                db.session.add_all(self.event_buffer)
                db.session.commit()
                logger.info(f"Flushed {len(self.event_buffer)} events to database")
                self.event_buffer.clear()
        except Exception as e:
            logger.error(f"Error flushing events: {e}")
            db.session.rollback()
    
    def update_progress(self, user_id: int, lesson_id: str, **kwargs):
        """Update user progress for a lesson."""
        try:
            with current_app.app_context():
                progress = Progress.query.filter_by(
                    user_id=user_id, 
                    lesson_id=lesson_id
                ).first()
                
                if not progress:
                    progress = Progress(
                        user_id=user_id,
                        lesson_id=lesson_id,
                        last_played=datetime.utcnow()
                    )
                    db.session.add(progress)
                
                # Update fields
                for key, value in kwargs.items():
                    if hasattr(progress, key):
                        setattr(progress, key, value)
                
                progress.last_played = datetime.utcnow()
                db.session.commit()
                
                logger.debug(f"Updated progress for user {user_id}, lesson {lesson_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
            db.session.rollback()
            return False
    
    def get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive progress data for a user."""
        try:
            with current_app.app_context():
                progress_records = Progress.query.filter_by(user_id=user_id).all()
                
                total_lessons = len(progress_records)
                completed_lessons = sum(1 for p in progress_records if p.completed)
                total_score = sum(p.score for p in progress_records)
                total_time = sum(p.time_spent for p in progress_records)
                
                return {
                    'user_id': user_id,
                    'total_lessons': total_lessons,
                    'completed_lessons': completed_lessons,
                    'progress_percentage': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
                    'average_score': (total_score / total_lessons) if total_lessons > 0 else 0,
                    'total_time_spent': total_time,
                    'lessons': [p.to_dict() for p in progress_records]
                }
                
        except Exception as e:
            logger.error(f"Error getting user progress: {e}")
            return {}
    
    def get_lesson_analytics(self, lesson_id: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a specific lesson."""
        try:
            with current_app.app_context():
                from datetime import timedelta
                
                # Get recent events for this lesson
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                events = EventLog.query.filter(
                    EventLog.lesson_id == lesson_id,
                    EventLog.timestamp >= cutoff_date
                ).all()
                
                # Get progress data
                progress_records = Progress.query.filter_by(lesson_id=lesson_id).all()
                
                # Calculate metrics
                total_plays = len(progress_records)
                completed_plays = sum(1 for p in progress_records if p.completed)
                average_score = sum(p.score for p in progress_records) / total_plays if total_plays > 0 else 0
                average_time = sum(p.time_spent for p in progress_records) / total_plays if total_plays > 0 else 0
                
                # Event type breakdown
                event_counts = {}
                for event in events:
                    event_type = event.event_type
                    event_counts[event_type] = event_counts.get(event_type, 0) + 1
                
                return {
                    'lesson_id': lesson_id,
                    'total_plays': total_plays,
                    'completed_plays': completed_plays,
                    'completion_rate': (completed_plays / total_plays * 100) if total_plays > 0 else 0,
                    'average_score': average_score,
                    'average_time_spent': average_time,
                    'event_breakdown': event_counts,
                    'recent_events': len(events)
                }
                
        except Exception as e:
            logger.error(f"Error getting lesson analytics: {e}")
            return {}
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get overall dashboard analytics."""
        try:
            with current_app.app_context():
                # Get basic counts
                total_users = db.session.query(Progress.user_id).distinct().count()
                total_lessons = db.session.query(Progress.lesson_id).distinct().count()
                
                # Get recent activity (last 24 hours)
                from datetime import timedelta
                cutoff_date = datetime.utcnow() - timedelta(hours=24)
                recent_events = EventLog.query.filter(
                    EventLog.timestamp >= cutoff_date
                ).count()
                
                # Get popular lessons
                lesson_counts = db.session.query(
                    Progress.lesson_id,
                    db.func.count(Progress.id).label('play_count')
                ).group_by(Progress.lesson_id).order_by(
                    db.func.count(Progress.id).desc()
                ).limit(5).all()
                
                popular_lessons = [
                    {'id': lesson_id, 'plays': count} 
                    for lesson_id, count in lesson_counts
                ]
                
                return {
                    'total_users': total_users,
                    'total_lessons': total_lessons,
                    'recent_activity': recent_events,
                    'popular_lessons': popular_lessons
                }
                
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}

# Global collector instance
collector = AnalyticsCollector()

def log_script_event(event_type: str, session_id: str, script_id: str, 
                    user_id: Optional[int] = None, data: Optional[Dict[str, Any]] = None):
    """Convenience function for logging script-related events."""
    return collector.log_event(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        lesson_id=script_id,
        data=data
    )

def update_lesson_progress(user_id: int, lesson_id: str, **kwargs):
    """Convenience function for updating lesson progress."""
    return collector.update_progress(user_id, lesson_id, **kwargs) 