# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from flask import Blueprint, jsonify, request

# Create user blueprint
user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile')
def user_profile():
    """Get user profile."""
    # In a real application, this would get the user's profile from the database
    return jsonify({
        'status': 'ok',
        'user': {
            'id': 'user123',
            'username': 'testuser',
            'email': 'test@example.com',
            'is_admin': False
        }
    })

@user_bp.route('/bookmarks', methods=['GET'])
def get_user_bookmarks():
    """Get user's bookmarked quests."""
    # In a real application, this would get the user's bookmarks from the database
    return jsonify({
        'status': 'ok',
        'bookmarks': []
    })
