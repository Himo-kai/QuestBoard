# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Admin routes for quest management."""
from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from database import get_database

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def require_admin():
    """Ensure the user is an admin."""
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403

@admin_bp.route('/guildhall')
def guildhall():
    """Admin dashboard for reviewing quests."""
    try:
        db = get_database()
        pending_quests = db.get_pending_quests()
        return render_template('admin/guildhall.html', quests=pending_quests)
    except Exception as e:
        current_app.logger.error(f"Error in guildhall: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/approve/<quest_id>', methods=['POST'])
def approve_quest(quest_id):
    """Approve a quest submission."""
    try:
        db = get_database()
        success = db.approve_quest(quest_id)
        if success:
            return jsonify({"status": "success", "message": "Quest approved"})
        return jsonify({"error": "Failed to approve quest"}), 400
    except Exception as e:
        current_app.logger.error(f"Error approving quest: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/reject/<quest_id>', methods=['POST'])
def reject_quest(quest_id):
    """Reject a quest submission."""
    try:
        db = get_database()
        success = db.reject_quest(quest_id)
        if success:
            return jsonify({"status": "success", "message": "Quest rejected"})
        return jsonify({"error": "Failed to reject quest"}), 400
    except Exception as e:
        current_app.logger.error(f"Error rejecting quest: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/stats')
def stats():
    """Admin statistics dashboard."""
    try:
        db = get_database()
        stats = {
            'total_quests': db.get_quest_count(),
            'pending_approval': len(db.get_pending_quests()),
            'by_source': db.get_quests_by_source(),
            'recent_activity': db.get_recent_activity(days=7),
            'popular_gear': db.get_popular_gear(limit=10)
        }
        return render_template('admin/stats.html', stats=stats)
    except Exception as e:
        current_app.logger.error(f"Error generating stats: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
