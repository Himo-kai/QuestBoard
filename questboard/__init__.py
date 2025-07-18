# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
QuestBoard - A platform for finding and managing gigs and freelance opportunities.

This package contains the main application factory and configuration.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config, DevelopmentConfig, TestingConfig, ProductionConfig

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Import models to ensure they are registered with SQLAlchemy
# Models are now imported through models/__init__.py

# Initialize extensions
from .models import db, init_app as init_models
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Initialize API
def create_api():
    """Create and configure the Flask-RESTX API."""
    api = Api(
        version='1.0',
        title='QuestBoard API',
        description='A REST API for managing gigs and freelance opportunities',
        doc='/api/docs/',
        default='QuestBoard',
        default_label='QuestBoard API Endpoints',
        validate=True
    )
    
    # Add namespaces
    from .routes.api.quests import quest_ns
    from .routes.api.users import user_ns
    
    api.add_namespace(quest_ns, path='/api/quests')
    api.add_namespace(user_ns, path='/api/users')
    
    return api

# Create the application factory
def create_app(config_name=None):
    """
    Create and configure an instance of the Flask application.
    
    Args:
        config_name: The name of the configuration to use (development, testing, production).
                    If not specified, uses FLASK_CONFIG environment variable or defaults to 'development'.
    
    Returns:
        Flask: The configured Flask application instance.
    """
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure the database URI is set
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = config[config_name].SQLALCHEMY_DATABASE_URI
    
    # Initialize extensions
    # Set the database URI from the config
    app.config['SQLALCHEMY_DATABASE_URI'] = config[config_name].SQLALCHEMY_DATABASE_URI
    
    # Initialize models and database
    init_models(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure login manager
    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Register main blueprint
    from .routes.main import main_bp
    app.register_blueprint(main_bp)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/questboard.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('QuestBoard startup')
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)
    
    # Initialize API
    api = create_api()
    api.init_app(app)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'message': 'The requested resource was not found.'
            }), 404
        return 'Not Found', 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}', exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'message': 'An internal server error occurred.'
            }), 500
        return 'Internal Server Error', 500
    
    # Shell context for Flask shell
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Quest': Quest,
            'Tag': Tag
        }
    
    return app

def register_error_handlers(app):
    """Register error handlers for the application."""
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error),
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}", exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": "Internal server error"}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": "Forbidden"}), 403
        return render_template('errors/403.html'), 403

def register_commands(app):
    """Register Click commands."""
    import click
    from flask.cli import with_appcontext
    from .services.quest_fetcher import fetch_gigs
    from database import get_database
    
    @app.cli.group()
    def db():
        """Database management commands."""
        pass
    
    @db.command("init")
    @with_appcontext
    def init_db():
        """Initialize the database."""
        db = get_database()
        db.create_all()
        click.echo("✅ Database initialized successfully.")
    
    @app.cli.command("fetch-quests")
    @with_appcontext
    def fetch_quests():
        """Fetch quests from all sources."""
        click.echo("🔍 Fetching quests from all sources...")
        
        try:
            quests = fetch_gigs()
            db = get_database()
            
            for quest in quests:
                # Process quest with NLP service
                quest['difficulty'] = nlp_service.calculate_difficulty(
                    f"{quest.get('title', '')} {quest.get('description', '')}"
                )
                quest['tags'] = nlp_service.extract_keywords(
                    f"{quest.get('title', '')} {quest.get('description', '')}",
                    top_n=5
                )
                
                # Cache the quest
                db.cache_quest(quest)
            
            click.echo(f"✅ Fetched and cached {len(quests)} quests")
            return len(quests)
            
        except Exception as e:
            logger.error(f"Error fetching quests: {str(e)}", exc_info=True)
            click.echo(f"❌ Error: {str(e)}", err=True)
            return 0
    
    @app.cli.command("train-nlp")
    @click.argument('training_data', type=click.Path(exists=True), required=False)
    @with_appcontext
    def train_nlp(training_data):
        """Train the NLP model with custom data."""
        if training_data:
            click.echo(f"Training NLP model with data from {training_data}...")
            # Add custom training logic here
            click.echo("NLP model training completed.")
        else:
            click.echo("Using default training data...")
            # Train with default data
            click.echo("NLP model initialized with default data.")
