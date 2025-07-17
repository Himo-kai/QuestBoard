# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import tempfile
import pytest
from datetime import datetime, timedelta

from questboard import create_app
from questboard.database import QuestDatabase
from questboard.services.nlp_service import NLPService

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for testing."""
    # Set the testing environment variable
    os.environ['FLASK_ENV'] = 'testing'
    
    # Create the app with test config
    app = create_app('testing')
    
    # Configure the test database
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Initialize the database
    with app.app_context():
        # The database is already initialized by create_app
        pass
    
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def db(app):
    """Get the test database instance."""
    from questboard.database import get_database
    
    # Get the database instance
    db = get_database()
    
    # Create all tables
    with app.app_context():
        db.create_tables()
    
    yield db
    
    # Clean up after each test
    with app.app_context():
        # Close any open connections
        pass

@pytest.fixture
def nlp_service():
    """Get an instance of the NLP service."""
    service = NLPService()
    # Initialize with some sample data
    sample_docs = [
        "Python developer needed for web application",
        "Frontend React developer with TypeScript experience",
        "DevOps engineer for cloud infrastructure",
        "Cybersecurity expert for penetration testing",
        "Data scientist with machine learning experience"
    ]
    service.fit(sample_docs)
    return service

@pytest.fixture
def sample_quest():
    """Create a sample quest for testing."""
    return {
        'id': 'test-quest-1',
        'title': 'Test Quest',
        'description': 'This is a test quest description with Python and Flask keywords.',
        'source': 'test',
        'url': 'http://example.com/test-quest',
        'posted_date': datetime.utcnow().isoformat(),
        'difficulty': 5.0,
        'reward': '$100',
        'region': 'test-region',
        'tags': ['python', 'flask', 'test'],
        'is_approved': True
    }

@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return {
        'id': 'test-user-1',
        'username': 'testuser',
        'email': 'test@example.com',
        'is_admin': False
    }
