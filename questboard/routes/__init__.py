# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
QuestBoard routes package.

This module handles the registration of all route blueprints for the application.
"""

def register_blueprints(app):
    """Register all blueprints with the Flask application.
    
    Args:
        app: The Flask application instance
    """
    # Import blueprints here to avoid circular imports
    from .main import main_bp
    from .admin import admin_bp
    from .user import user_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    
    # Import and register API namespaces
    from .api.namespaces import api
    from .api.quests import quest_ns
    from .api.users import user_ns
    
    # Add namespaces to the API
    api.add_namespace(quest_ns, path='/quests')
    api.add_namespace(user_ns, path='/users')
