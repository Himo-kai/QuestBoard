# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
QuestBoard - A platform for finding and managing gigs and freelance opportunities.

This package contains the main application factory and configuration.
"""
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from config import config
from .services.logging_service import LoggingService
from .services.nlp_service import NLPService
from .monitoring import init_monitoring, monitor_request
from .api_spec import api
from .api_docs import api as api_blueprint

# Initialize services
logger = LoggingService.get_logger(__name__)
nlp_service = NLPService()

def create_app(config_name=None):
    """
    Create and configure the Flask application.
    
    Args:
        config_name: The configuration to use (development, testing, production)
        
    Returns:
        Flask: The configured Flask application
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create and configure the app
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Configure logging
    LoggingService.configure(
        log_level=logging.DEBUG if config_name == 'development' else logging.INFO,
        log_file='questboard.log'
    )
    
    # Initialize database
    from .database import init_app as init_db
    db = init_db(app)
    
    # Make db available on the app
    app.db = db
    
    # Initialize NLP service with sample data
    with app.app_context():
        # Sample documents for TF-IDF initialization
        sample_docs = [
            "Python developer needed for web application",
            "Frontend React developer with TypeScript experience",
            "DevOps engineer for cloud infrastructure",
            "Cybersecurity expert for penetration testing",
            "Data scientist with machine learning experience"
        ]
        nlp_service.fit(sample_docs)
        
        # Ensure database tables exist
        db.create_tables()
    
    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .routes import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # Initialize monitoring
    init_monitoring(app)
    
    # Initialize API documentation
    api.init_app(app)
    
    # Import and register API routes
    from .routes import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_commands(app)
    
    # Add URL converters, context processors, etc.
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'QuestBoard',
            'current_year': datetime.now().year
        }
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': config_name
        })
    
    logger.info(f"Application initialized in {config_name} mode")
    return app

def register_error_handlers(app):
    """Register error handlers for the application."""
    from flask import jsonify, render_template, request
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": "Not found"}), 404
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
