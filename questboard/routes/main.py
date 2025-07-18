# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from datetime import datetime
from flask import Blueprint, jsonify, current_app, render_template, redirect, url_for
from flask_login import login_required, current_user

# Create main blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main entry point."""
    if current_app.config.get('API_ONLY', False):
        return jsonify({
            'name': 'QuestBoard API',
            'version': '1.0.0',
            'status': 'running',
            'environment': current_app.config.get('ENV', 'production'),
            'documentation': '/api/docs/'
        })
    return render_template('home/index.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint.
    
    Returns:
        JSON: Health status and timestamp
    """
    # Check database connection
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import text
    
    db = SQLAlchemy()
    db_status = 'disconnected'
    try:
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        current_app.logger.error(f'Database connection error: {str(e)}')
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'QuestBoard API',
        'database': db_status,
        'environment': current_app.config.get('ENV', 'production')
    })

@main_bp.route('/status')
def status():
    """Detailed status endpoint.
    
    Returns:
        JSON: Detailed system status information
    """
    from flask import current_app
    import sys
    import platform
    
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'environment': current_app.config.get('ENV', 'production'),
        'python_version': platform.python_version(),
        'flask_version': current_app.config.get('FLASK_VERSION'),
        'debug': current_app.debug
    })

# Template routes
@main_bp.route('/about')
def about():
    """About page."""
    return render_template('main/about.html')

@main_bp.route('/terms')
def terms():
    """Terms of Service page."""
    return render_template('main/terms.html')

@main_bp.route('/privacy')
def privacy():
    """Privacy Policy page."""
    return render_template('main/privacy.html')

@main_bp.route('/quests')
@login_required
def quests():
    """List all quests."""
    return render_template('quests/list.html')

@main_bp.route('/quests/create', methods=['GET', 'POST'])
@login_required
def create_quest():
    """Create a new quest."""
    if request.method == 'POST':
        # Handle quest creation
        pass
    return render_template('quests/create.html')

@main_bp.route('/quests/<int:quest_id>')
@login_required
def view_quest(quest_id):
    """View a specific quest."""
    return render_template('quests/view.html', quest_id=quest_id)

# Error handlers
@main_bp.app_errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/api/') or 'application/json' in request.headers.get('Accept', ''):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found.',
            'status_code': 404
        }), 404
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(403)
def forbidden_error(error):
    if request.path.startswith('/api/') or 'application/json' in request.headers.get('Accept', ''):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.',
            'status_code': 403
        }), 403
    return render_template('errors/403.html'), 403

@main_bp.app_errorhandler(500)
def internal_error(error):
    current_app.logger.error(f'Server Error: {error}', exc_info=True)
    if request.path.startswith('/api/') or 'application/json' in request.headers.get('Accept', ''):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred on the server.',
            'status_code': 500
        }), 500
    return render_template('errors/500.html'), 500

@main_bp.app_errorhandler(401)
def unauthorized_error(error):
    if request.path.startswith('/api/') or 'application/json' in request.headers.get('Accept', ''):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource.',
            'status_code': 401
        }), 401
    return redirect(url_for('auth.login', next=request.path))
