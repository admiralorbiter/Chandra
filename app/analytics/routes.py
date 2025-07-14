"""
Analytics routes
"""

from flask import jsonify, request, current_app, Response, render_template
from . import analytics_bp
from .collector import collector, log_script_event, update_lesson_progress
from .charts import (
    generate_lesson_completion_timeline,
    generate_user_progress_chart,
    generate_dashboard_overview
)

@analytics_bp.route('/progress/<int:user_id>', methods=['GET'])
def get_user_progress(user_id):
    """Get user progress across all lessons."""
    try:
        progress_data = collector.get_user_progress(user_id)
        return jsonify({
            'success': True,
            'data': progress_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/events', methods=['POST'])
def log_event():
    """Log an analytics event."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Event data is required'
            }), 400
        
        required_fields = ['event_type', 'session_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        success = collector.log_event(
            event_type=data['event_type'],
            session_id=data['session_id'],
            user_id=data.get('user_id'),
            lesson_id=data.get('lesson_id'),
            data=data.get('data')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Event logged successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to log event'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/progress', methods=['POST'])
def update_progress():
    """Update user progress for a lesson."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Progress data is required'
            }), 400
        
        required_fields = ['user_id', 'lesson_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract progress fields
        progress_fields = {}
        for field in ['completed', 'score', 'attempts', 'time_spent']:
            if field in data:
                progress_fields[field] = data[field]
        
        success = collector.update_progress(
            user_id=data['user_id'],
            lesson_id=data['lesson_id'],
            **progress_fields
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Progress updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update progress'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/dashboard/data', methods=['GET'])
def analytics_dashboard():
    """Get analytics dashboard data."""
    try:
        dashboard_data = collector.get_dashboard_data()
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/lessons/<lesson_id>/analytics', methods=['GET'])
def get_lesson_analytics(lesson_id):
    """Get analytics for a specific lesson."""
    try:
        days = request.args.get('days', 30, type=int)
        analytics_data = collector.get_lesson_analytics(lesson_id, days)
        return jsonify({
            'success': True,
            'data': analytics_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/events/flush', methods=['POST'])
def flush_events():
    """Manually flush buffered events to database."""
    try:
        collector.flush_events()
        return jsonify({
            'success': True,
            'message': 'Events flushed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/charts/lesson/<lesson_id>/timeline', methods=['GET'])
def get_lesson_timeline_chart(lesson_id):
    """Generate lesson completion timeline chart."""
    try:
        days = request.args.get('days', 30, type=int)
        chart_data = generate_lesson_completion_timeline(lesson_id, days)
        
        # Return as base64 encoded PNG
        return Response(
            chart_data,
            mimetype='image/png',
            headers={'Content-Disposition': f'attachment; filename=lesson_{lesson_id}_timeline.png'}
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/charts/user/<int:user_id>/progress', methods=['GET'])
def get_user_progress_chart(user_id):
    """Generate user progress chart."""
    try:
        chart_data = generate_user_progress_chart(user_id)
        
        # Return as base64 encoded PNG
        return Response(
            chart_data,
            mimetype='image/png',
            headers={'Content-Disposition': f'attachment; filename=user_{user_id}_progress.png'}
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/charts/dashboard/overview', methods=['GET'])
def get_dashboard_overview_chart():
    """Generate dashboard overview chart."""
    try:
        chart_data = generate_dashboard_overview()
        
        # Return as base64 encoded PNG
        return Response(
            chart_data,
            mimetype='image/png',
            headers={'Content-Disposition': 'attachment; filename=dashboard_overview.png'}
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/dashboard', methods=['GET'])
def analytics_dashboard_page():
    """Serve the analytics dashboard page."""
    return render_template('analytics_dashboard.html') 