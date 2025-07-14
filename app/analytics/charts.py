"""
Analytics Charts Module
Generates matplotlib charts for analytics data
"""

import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
from app import db
from app.models import EventLog, Progress

def generate_lesson_completion_timeline(lesson_id: str, days: int = 30) -> str:
    """Generate a PNG chart showing lesson completion timeline."""
    try:
        # Get completion events for the lesson
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        events = EventLog.query.filter(
            EventLog.lesson_id == lesson_id,
            EventLog.event_type == 'lesson_complete',
            EventLog.timestamp >= cutoff_date
        ).order_by(EventLog.timestamp).all()
        
        if not events:
            return _generate_empty_chart("No completion data available")
        
        # Group by date
        dates = [event.timestamp.date() for event in events]
        date_counts = {}
        for date in dates:
            date_counts[date] = date_counts.get(date, 0) + 1
        
        # Create the chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot completion timeline
        dates_list = list(date_counts.keys())
        counts_list = list(date_counts.values())
        
        ax.bar(dates_list, counts_list, alpha=0.7, color='#4CAF50')
        ax.set_title(f'Lesson Completion Timeline: {lesson_id}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Completions')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates_list) // 7)))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Add total completions text
        total_completions = sum(counts_list)
        ax.text(0.02, 0.98, f'Total Completions: {total_completions}', 
                transform=ax.transAxes, fontsize=12, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        return _figure_to_base64(fig)
        
    except Exception as e:
        return _generate_error_chart(str(e))

def generate_user_progress_chart(user_id: int) -> str:
    """Generate a PNG chart showing user progress across lessons."""
    try:
        # Get user progress data
        progress_records = Progress.query.filter_by(user_id=user_id).all()
        
        if not progress_records:
            return _generate_empty_chart("No progress data available")
        
        # Prepare data
        lesson_ids = [p.lesson_id for p in progress_records]
        scores = [p.score for p in progress_records]
        completed = [1 if p.completed else 0 for p in progress_records]
        
        # Create the chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Score chart
        bars1 = ax1.bar(range(len(lesson_ids)), scores, alpha=0.7, color='#2196F3')
        ax1.set_title('Lesson Scores', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Lessons')
        ax1.set_ylabel('Score')
        ax1.set_xticks(range(len(lesson_ids)))
        ax1.set_xticklabels(lesson_ids, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        
        # Add score values on bars
        for i, bar in enumerate(bars1):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}', ha='center', va='bottom')
        
        # Completion chart
        bars2 = ax2.bar(range(len(lesson_ids)), completed, alpha=0.7, 
                        color=['#4CAF50' if c else '#FF5722' for c in completed])
        ax2.set_title('Lesson Completion Status', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Lessons')
        ax2.set_ylabel('Completed')
        ax2.set_xticks(range(len(lesson_ids)))
        ax2.set_xticklabels(lesson_ids, rotation=45, ha='right')
        ax2.set_ylim(0, 1.2)
        ax2.grid(True, alpha=0.3)
        
        # Add completion labels
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            status = "Completed" if height > 0 else "Not Completed"
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    status, ha='center', va='bottom', fontsize=10)
        
        # Add summary text
        total_lessons = len(progress_records)
        completed_lessons = sum(completed)
        avg_score = sum(scores) / len(scores) if scores else 0
        
        fig.suptitle(f'User Progress Summary (User ID: {user_id})', fontsize=16, fontweight='bold')
        fig.text(0.02, 0.02, f'Total Lessons: {total_lessons} | Completed: {completed_lessons} | Avg Score: {avg_score:.1f}%', 
                fontsize=12, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        plt.tight_layout()
        
        return _figure_to_base64(fig)
        
    except Exception as e:
        return _generate_error_chart(str(e))

def generate_dashboard_overview() -> str:
    """Generate a PNG chart showing dashboard overview metrics."""
    try:
        # Get dashboard data
        total_users = db.session.query(Progress.user_id).distinct().count()
        total_lessons = db.session.query(Progress.lesson_id).distinct().count()
        
        # Get recent activity (last 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
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
        
        lesson_names = [lesson_id for lesson_id, _ in lesson_counts]
        play_counts = [count for _, count in lesson_counts]
        
        # Create the chart
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Metric 1: Total Users
        ax1.pie([total_users, 100-total_users], labels=['Active Users', 'Inactive'], 
                autopct='%1.1f%%', startangle=90, colors=['#4CAF50', '#E0E0E0'])
        ax1.set_title('User Activity', fontweight='bold')
        
        # Metric 2: Total Lessons
        ax2.pie([total_lessons, 20-total_lessons], labels=['Available Lessons', 'Remaining'], 
                autopct='%1.1f%%', startangle=90, colors=['#2196F3', '#E0E0E0'])
        ax2.set_title('Lesson Coverage', fontweight='bold')
        
        # Metric 3: Recent Activity
        ax3.bar(['Recent Events'], [recent_events], color='#FF9800', alpha=0.7)
        ax3.set_title('Recent Activity (7 days)', fontweight='bold')
        ax3.set_ylabel('Event Count')
        ax3.text(0, recent_events + 1, str(recent_events), ha='center', va='bottom', fontweight='bold')
        
        # Metric 4: Popular Lessons
        if lesson_names and play_counts:
            bars = ax4.bar(range(len(lesson_names)), play_counts, color='#9C27B0', alpha=0.7)
            ax4.set_title('Popular Lessons', fontweight='bold')
            ax4.set_xlabel('Lessons')
            ax4.set_ylabel('Play Count')
            ax4.set_xticks(range(len(lesson_names)))
            ax4.set_xticklabels(lesson_names, rotation=45, ha='right')
            ax4.grid(True, alpha=0.3)
            
            # Add count labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        str(int(height)), ha='center', va='bottom')
        else:
            ax4.text(0.5, 0.5, 'No lesson data available', ha='center', va='center', 
                    transform=ax4.transAxes, fontsize=12)
            ax4.set_title('Popular Lessons', fontweight='bold')
        
        fig.suptitle('Chandra Analytics Dashboard Overview', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return _figure_to_base64(fig)
        
    except Exception as e:
        return _generate_error_chart(str(e))

def _figure_to_base64(fig: Figure) -> str:
    """Convert matplotlib figure to base64 encoded PNG string."""
    canvas = FigureCanvas(fig)
    canvas.draw()
    
    # Save to bytes buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    
    # Convert to base64
    img_data = base64.b64encode(buf.getvalue()).decode()
    buf.close()
    plt.close(fig)
    
    return img_data

def _generate_empty_chart(message: str) -> str:
    """Generate an empty chart with a message."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.text(0.5, 0.5, message, ha='center', va='center', 
            transform=ax.transAxes, fontsize=14, style='italic')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    return _figure_to_base64(fig)

def _generate_error_chart(error_message: str) -> str:
    """Generate an error chart with error message."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.text(0.5, 0.5, f'Error generating chart:\n{error_message}', 
            ha='center', va='center', transform=ax.transAxes, 
            fontsize=12, color='red', style='italic')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    return _figure_to_base64(fig) 