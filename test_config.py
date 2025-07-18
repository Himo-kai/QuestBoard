"""
Test script to verify database configuration and initialization.
"""
import os
import sys
import logging
from sqlalchemy import inspect, text
from questboard import create_app, db
from questboard.config import DevelopmentConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_database.log')
    ]
)
logger = logging.getLogger(__name__)

def test_database_config():
    logger.info("=== Starting Database Configuration Test ===")
    
    # Test DevelopmentConfig
    logger.info("\nTesting Development Configuration:")
    dev_config = DevelopmentConfig()
    logger.info(f"Database URI: {dev_config.SQLALCHEMY_DATABASE_URI}")
    
    # Check if database file is created
    db_path = dev_config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
    logger.info(f"Database file path: {db_path}")
    logger.info(f"Database file exists: {os.path.exists(db_path)}")
    
    # Initialize the app with development config
    logger.info("\nInitializing Flask app...")
    app = create_app('development')
    
    with app.app_context():
        logger.info("\n=== Database Connection Test ===")
        
        # Test database connection
        try:
            with db.engine.connect() as conn:
                logger.info("Successfully connected to the database")
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")
            return
        
        # Create all tables
        logger.info("\n=== Creating Database Tables ===")
        try:
            db.create_all()
            logger.info("Successfully created all tables")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
        
        # List all tables using SQLAlchemy inspector
        logger.info("\n=== Database Schema Inspection ===")
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.warning("No tables found in the database!")
            
            # Try to get more detailed error information
            try:
                with db.engine.connect() as conn:
                    # Try to get tables using raw SQL
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    tables = [row[0] for row in result]
                    logger.info(f"Tables found via raw SQL: {tables}")
                    
                    # If still no tables, try to create them again with more verbosity
                    if not tables:
                        logger.info("No tables found, attempting to create them...")
                        db.create_all()
                        
                        # Check again after creation attempt
                        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                        tables = [row[0] for row in result]
                        logger.info(f"Tables after creation attempt: {tables}")
                        
            except Exception as e:
                logger.error(f"Error querying database: {e}")
                logger.exception("Full traceback:")
        else:
            logger.info("Tables in database:")
            for table in tables:
                logger.info(f"- {table}")
                
                # Log columns for each table
                columns = inspector.get_columns(table)
                for column in columns:
                    logger.info(f"  - {column['name']}: {column['type']}")
        
        logger.info("\nDatabase initialization test completed!")

if __name__ == "__main__":
    test_database_config()
