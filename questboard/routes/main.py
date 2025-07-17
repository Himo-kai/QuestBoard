# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from flask import Blueprint, jsonify, request
from datetime import datetime

# Create main blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'QuestBoard API'
    })

@main_bp.route('/')
def index():
    """Main entry point."""
    return jsonify({
        'name': 'QuestBoard API',
        'version': '1.0.0',
        'status': 'running'
    })
