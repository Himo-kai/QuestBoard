# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

# Create user blueprint
user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@login_required
def user_profile():
    """Get the current user's profile.
    
    Returns:
        JSON: User profile data
    """
    return jsonify({
        'status': 'ok',
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'is_admin': getattr(current_user, 'is_admin', False),
            'created_at': current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else None,
            'updated_at': current_user.updated_at.isoformat() if hasattr(current_user, 'updated_at') else None
        }
    })

@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update the current user's profile.
    
    Returns:
        JSON: Updated user profile
    """
    data = request.get_json()
    
    # Update user fields
    if 'username' in data:
        current_user.username = data['username']
    if 'email' in data:
        current_user.email = data['email']
    if 'password' in data:
        current_user.set_password(data['password'])
    
    current_user.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Profile updated successfully'
    })

@user_bp.route('/bookmarks', methods=['GET'])
@login_required
def get_user_bookmarks():
    """Get the current user's bookmarked quests.
    
    Returns:
        JSON: List of bookmarked quests
    """
    # In a real application, this would get the user's bookmarks from the database
    bookmarks = current_user.bookmarks.all() if hasattr(current_user, 'bookmarks') else []
    
    return jsonify({
        'status': 'ok',
        'bookmarks': [{
            'id': b.id,
            'title': b.title,
            'description': b.description,
            'bookmarked_at': b.bookmarked_at.isoformat()
        } for b in bookmarks]
    })
