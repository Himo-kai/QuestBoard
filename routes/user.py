# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""User-related routes."""
from flask import Blueprint, render_template, jsonify, current_app, request
from flask_login import login_required, current_user
from database import get_database

user_bp = Blueprint('user', __name__)

@user_bp.route('/guildcard/<user_id>')
@login_required
def guild_card(user_id):
    """Display a user's guild card with stats."""
    try:
        if user_id != current_user.id and not current_user.is_admin:
            return jsonify({"error": "Unauthorized"}), 403
            
        db = get_database()
        stats = db.get_user_stats(user_id)
        
        return render_template('user/guild_card.html', 
                             user_stats=stats,
                             current_user=current_user)
    except Exception as e:
        current_app.logger.error(f"Error fetching guild card: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@user_bp.route('/quests/region/<region>')
def quests_by_region(region):
    """Get quests filtered by region."""
    try:
        db = get_database()
        quests = db.get_quests_by_region(region)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'success',
                'region': region,
                'count': len(quests),
                'quests': quests
            })
            
        return render_template('quests/region.html', 
                            quests=quests,
                            region=region)
    except Exception as e:
        current_app.logger.error(f"Error getting quests for region {region}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@user_bp.route('/bookmarks')
@login_required
def bookmarks():
    """View user's bookmarked quests."""
    try:
        db = get_database()
        bookmarked_quests = db.get_user_bookmarks(current_user.id)
        return render_template('user/bookmarks.html', quests=bookmarked_quests)
    except Exception as e:
        current_app.logger.error(f"Error fetching bookmarks: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@user_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Update user preferences."""
    if request.method == 'POST':
        try:
            data = request.get_json() or {}
            theme = data.get('theme', 'light')
            
            # Update user preferences in database
            db = get_database()
            db.update_user_preferences(current_user.id, {'theme': theme})
            
            return jsonify({
                'status': 'success',
                'message': 'Preferences updated',
                'theme': theme
            })
        except Exception as e:
            current_app.logger.error(f"Error updating preferences: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    # GET request - return current preferences
    return jsonify({
        'theme': getattr(current_user, 'theme_preference', 'light')
    })
