"""
Test script to manually initialize the database and verify table creation.
"""
import os
import sys
import logging
from datetime import datetime
from flask import Flask
# Import the SQLAlchemy instance from the models
from questboard.models.base import db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_db_init.log')
    ]
)
logger = logging.getLogger(__name__)

def log_section(title):
    """Log a section header."""
    logger.info('\n' + '=' * 80)
    logger.info(f' {title} '.center(80, '='))
    logger.info('=' * 80 + '\n')

def log_subsection(title):
    """Log a subsection header."""
    logger.info(f'--- {title} ---')

try:
    # Log script start
    log_section('Starting Database Initialization Test')
    logger.info(f'Script started at {datetime.now().isoformat()}')
    
    # Create a test app with development configuration
    logger.info('Initializing Flask application...')
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # Log all SQL queries

    # Set up SQLite database in the instance folder
    instance_path = os.path.join(os.getcwd(), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, 'questboard_test.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    logger.info(f'Database path: {db_path}')

    # Initialize the database with the app
    logger.info('Initializing database...')
    db.init_app(app)
    
    # Import models after db is initialized
    logger.info('Importing models...')
    from questboard.models import User, Quest, Tag
    logger.info(f'Imported models: {[m.__name__ for m in [User, Quest, Tag]]}')
    
    # Ensure all models are imported and registered with SQLAlchemy
    from questboard.models import associations  # Import associations to register them
    logger.info('All models and associations imported')

    # Create an application context
    with app.app_context():
        log_section('Database Operations')
        
        # Drop all tables
        log_subsection('Dropping Tables')
        logger.info('Dropping all existing tables...')
        db.drop_all()
        logger.info('All tables dropped successfully')
        
        # Create all tables
        log_subsection('Creating Tables')
        logger.info('Creating database tables...')
        db.create_all()
        logger.info('Database tables created successfully')
        
        # Verify tables were created
        log_subsection('Verifying Database Schema')
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        logger.info('\n=== Database Tables ===')
        for table in tables:
            logger.info(f'- {table}')
        
        # Log table details
        for table_name in tables:
            logger.info(f'\nTable: {table_name}')
            columns = inspector.get_columns(table_name)
            for column in columns:
                logger.info(f'  - {column["name"]}: {column["type"]}')
        
        # Verify models are registered
        log_subsection('Registered Models')
        for model in [User, Quest, Tag]:
            logger.info(f'- {model.__name__} (table: {model.__tablename__ if hasattr(model, "__tablename__") else "N/A"})')
        
        logger.info('\nDatabase initialization completed successfully!')

except Exception as e:
    logger.error('An error occurred during database initialization:', exc_info=True)
    raise

finally:
    log_section('Test Completed')
    logger.info(f'Script finished at {datetime.now().isoformat()}')
    logger.info('Check test_db_init.log for detailed logs')
