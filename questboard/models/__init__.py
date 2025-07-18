"""
QuestBoard Models Package

This package contains all the data models and database setup for the QuestBoard application.
"""
import os
import sys
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, event
from sqlalchemy.sql.expression import text

# Initialize SQLAlchemy
db = SQLAlchemy()

# This will be populated after models are imported
Model = db.Model

# Import models after db is initialized to avoid circular imports
# Import order is important to avoid circular imports
from .base import BaseModel
from .user import User
from .quest import Quest
from .tag import Tag
from .associations import user_quests, quest_tags

# List of all models for easy iteration
MODELS = [User, Quest, Tag]

def init_app(app):
    """Initialize the database with the Flask app."""
    # Configure SQLAlchemy with the app
    db.init_app(app)
    
    # Create all database tables
    with app.app_context():
        # Enable foreign key support for SQLite
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            def _fk_pragma_on_connect(dbapi_con, con_record):
                dbapi_con.execute('PRAGMA foreign_keys=ON')
            
            with db.engine.connect() as conn:
                conn.execute(text('PRAGMA foreign_keys=ON'))
            
            event.listen(db.engine, 'connect', _fk_pragma_on_connect)
        
        # Only create tables if we're in testing mode or explicitly requested
        if app.config.get('TESTING') or os.environ.get('CREATE_TABLES'):
            db.create_all()
            
        # Verify tables were created
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("\n=== Database Tables ===")
        for table in tables:
            print(f"- {table}")
            
        # Print registered models
        print("\n=== Registered Models ===")
        for model in MODELS:
            tablename = model.__tablename__ if hasattr(model, '__tablename__') else 'N/A'
            print(f"- {model.__name__} (table: {tablename})")
            
            # Print columns for each model
            if tablename != 'N/A' and tablename in tables:
                print(f"  Columns:")
                for column in inspector.get_columns(tablename):
                    print(f"  - {column['name']}: {column['type']}")
    
    return db
