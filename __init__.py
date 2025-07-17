# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""QuestBoard application factory."""
from flask import Flask
from config import Config
from database import get_database

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database
    db = get_database()
    
    # Register blueprints
    from routes.main import main_bp
    from routes.admin import admin_bp
    from routes.user import user_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    
    # Initialize services
    from services.quest_fetcher import init_quest_fetcher
    init_quest_fetcher(app)
    
    return app
