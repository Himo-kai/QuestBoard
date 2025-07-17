# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Admin routes for quest management and moderation.

This module provides endpoints for administrative tasks such as approving/rejecting
quests, managing users, and viewing system metrics.
"""
from datetime import datetime
from flask import (
    Blueprint, 
    jsonify, 
    request, 
    render_template, 
    redirect, 
    url_for, 
    flash,
    current_app
)
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from werkzeug.exceptions import BadRequest

from ..services.logging_service import LoggingService
from ..models.quest import Quest

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Default pagination settings
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20

@admin_bp.before_request
@login_required
def require_admin():
    """Ensure the user is an admin before processing any admin requests."""
    if not current_user.is_authenticated or not current_user.is_admin:
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Admin access required',
                'login_url': url_for('auth.login', next=request.url)
            }), 403
        flash('Admin access required', 'error')
        return redirect(url_for('main.index'))

@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard with system overview and metrics."""
    return render_template('admin/dashboard.html')

@admin_bp.route('/quests')
def list_quests():
    """List all quests with pagination and filtering."""
    try:
        page = request.args.get('page', DEFAULT_PAGE, type=int)
        per_page = request.args.get('per_page', DEFAULT_PER_PAGE, type=int)
        status = request.args.get('status', 'pending')  # pending, approved, rejected, all
        
        # Get quests with pagination and filtering
        query = Quest.query
        
        if status != 'all':
            if status == 'pending':
                query = query.filter_by(is_approved=None)
            elif status == 'approved':
                query = query.filter_by(is_approved=True)
            elif status == 'rejected':
                query = query.filter_by(is_approved=False)
        
        quests = query.order_by(Quest.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'data': {
                    'items': [q.to_dict() for q in quests.items],
                    'pagination': {
                        'page': quests.page,
                        'per_page': quests.per_page,
                        'total': quests.total,
                        'pages': quests.pages
                    }
                }
            })
            
        return render_template(
            'admin/quests/list.html',
            quests=quests,
            status=status,
            current_page='quests'
        )
        
    except Exception as e:
        LoggingService.get_logger(__name__).error(
            f"Error listing quests: {str(e)}", exc_info=True)
        
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Failed to retrieve quests',
                'error': str(e)
            }), 500
            
        flash('Failed to retrieve quests', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/quests/<int:quest_id>/approve', methods=['POST'])
def approve_quest(quest_id):
    """Approve a quest submission."""
    try:
        # Validate CSRF token for form submissions
        if request.content_type == 'application/x-www-form-urlencoded':
            validate_csrf(request.form.get('csrf_token'))
        
        quest = Quest.query.get_or_404(quest_id)
        
        # Log the approval action
        LoggingService.get_logger('admin.quests').info(
            f"Quest {quest_id} approved by admin {current_user.id}",
            extra={
                'quest_id': quest_id,
                'admin_id': current_user.id,
                'action': 'approve'
            }
        )
        
        # Update quest status
        quest.is_approved = True
        quest.approved_by = current_user.id
        quest.approved_at = datetime.utcnow()
        quest.save()
        
        # TODO: Notify the quest submitter
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'message': 'Quest approved successfully',
                'quest': quest.to_dict()
            })
            
        flash('Quest approved successfully', 'success')
        return redirect(request.referrer or url_for('admin.list_quests'))
        
    except BadRequest as e:
        # CSRF validation failed
        LoggingService.get_logger('security.csrf').warning(
            f"CSRF validation failed for admin action: {str(e)}")
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Invalid request',
                'error': 'CSRF token missing or invalid'
            }), 400
        flash('Invalid request', 'error')
        return redirect(url_for('admin.list_quests'))
        
    except Exception as e:
        LoggingService.get_logger(__name__).error(
            f"Error approving quest {quest_id}: {str(e)}", exc_info=True)
            
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Failed to approve quest',
                'error': str(e)
            }), 500
            
        flash('Failed to approve quest', 'error')
        return redirect(url_for('admin.list_quests'))

@admin_bp.route('/quests/<int:quest_id>/reject', methods=['POST'])
def reject_quest(quest_id):
    """Reject a quest submission."""
    try:
        # Validate CSRF token for form submissions
        if request.content_type == 'application/x-www-form-urlencoded':
            validate_csrf(request.form.get('csrf_token'))
            reason = request.form.get('reason', 'No reason provided')
        else:
            reason = request.json.get('reason', 'No reason provided')
        
        quest = Quest.query.get_or_404(quest_id)
        
        # Log the rejection action
        LoggingService.get_logger('admin.quests').info(
            f"Quest {quest_id} rejected by admin {current_user.id}",
            extra={
                'quest_id': quest_id,
                'admin_id': current_user.id,
                'action': 'reject',
                'reason': reason
            }
        )
        
        # Update quest status
        quest.is_approved = False
        quest.rejection_reason = reason
        quest.reviewed_by = current_user.id
        quest.reviewed_at = datetime.utcnow()
        quest.save()
        
        # TODO: Notify the quest submitter with the reason
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'message': 'Quest rejected successfully',
                'quest': quest.to_dict()
            })
            
        flash('Quest rejected successfully', 'success')
        return redirect(request.referrer or url_for('admin.list_quests'))
        
    except BadRequest as e:
        # CSRF validation failed
        LoggingService.get_logger('security.csrf').warning(
            f"CSRF validation failed for admin action: {str(e)}")
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Invalid request',
                'error': 'CSRF token missing or invalid'
            }), 400
        flash('Invalid request', 'error')
        return redirect(url_for('admin.list_quests'))
        
    except Exception as e:
        LoggingService.get_logger(__name__).error(
            f"Error rejecting quest {quest_id}: {str(e)}", exc_info=True)
            
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Failed to reject quest',
                'error': str(e)
            }), 500
            
        flash('Failed to reject quest', 'error')
        return redirect(url_for('admin.list_quests'))

@admin_bp.route('/quests/<int:quest_id>')
def view_quest(quest_id):
    """View details of a specific quest."""
    try:
        quest = Quest.query.get_or_404(quest_id)
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'data': quest.to_dict()
            })
            
        return render_template(
            'admin/quests/view.html',
            quest=quest,
            current_page='quests'
        )
        
    except Exception as e:
        LoggingService.get_logger(__name__).error(
            f"Error viewing quest {quest_id}: {str(e)}", exc_info=True)
            
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Failed to retrieve quest',
                'error': str(e)
            }), 500
            
        flash('Failed to retrieve quest', 'error')
        return redirect(url_for('admin.list_quests'))
