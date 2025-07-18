"""
Test script to verify model registration with SQLAlchemy.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from questboard import create_app
from questboard.models import db

# Create a test app
app = create_app('development')

# Push an application context
with app.app_context():
    # Get the metadata
    metadata = db.metadata
    
    # Print all tables
    print("\n=== Database Tables ===")
    for table in metadata.sorted_tables:
        print(f"- {table.name}")
    
    # Print all models
    print("\n=== Registered Models ===")
    for mapper in db.Model.registry.mappers:
        print(f"- {mapper.class_.__name__} (table: {mapper.class_.__table__.name if hasattr(mapper.class_, '__table__') else 'N/A'})")
    
    # Print the SQL for table creation
    print("\n=== SQL for Table Creation ===")
    from sqlalchemy.schema import CreateTable
    for table in metadata.sorted_tables:
        print(f"-- {table.name}")
        print(CreateTable(table).compile(db.engine))
        print()
