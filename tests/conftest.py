# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import tempfile
import pytest
from datetime import datetime, timedelta, timezone

from questboard import create_app
from questboard.extensions import db as _db
from questboard.services.nlp_service import NLPService
from questboard.models import BaseModel, User, SQLAlchemyQuest, Quest as DataclassQuest

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for testing."""
    # Set the testing environment variable
    os.environ['FLASK_ENV'] = 'testing'
    
    # Create the app with test config
    app = create_app('testing')
    
    # Configure the test database to use SQLite in-memory
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Initialize the database
    with app.app_context():
        _db.create_all()
    
    yield app
    
    # Clean up after tests
    with app.app_context():
        _db.session.remove()
        _db.drop_all()
        _db.get_engine(app).dispose()

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
    with app.app_context():
        _db.create_all()
        
    yield _db
    
    # Clean up after each test
    with app.app_context():
        # Clear all data but keep tables
        meta = _db.metadata
        for table in reversed(meta.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()
    
    return _db

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
    from questboard.models.quest import Quest as DataclassQuest
    return DataclassQuest(
        id="test-quest-1",
        title="Test Quest",
        description="A test quest for testing purposes.",
        source="test",
        url="http://example.com/quest/1",
        posted_date=datetime.now(timezone.utc),
        difficulty=5.0,
        reward="Test Reward",
        is_approved=True
    )

@pytest.fixture
def sqlalchemy_quest(db):
    """Create a sample SQLAlchemy quest in the database."""
    quest = SQLAlchemyQuest(
        id="test-sqlalchemy-quest-1",
        title="SQLAlchemy Test Quest",
        description="A test quest using SQLAlchemy.",
        source="test",
        url="http://example.com/sqlalchemy-quest/1",
        posted_date=datetime.now(timezone.utc),
        difficulty=5.0,
        reward="SQLAlchemy Test Reward",
        is_approved=True
    )
    
    db.session.add(quest)
    db.session.commit()
    
    return quest

@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return {
        "id": "test-user-1",
        "username": "testuser",
        "email": "test@example.com",
        "is_admin": False
    }

@pytest.fixture
def sqlalchemy_user(db):
    """Create a sample SQLAlchemy user in the database."""
    user = User(
        id="test-sqlalchemy-user-1",
        username="sqlalchemy_testuser",
        email="sqlalchemy_test@example.com",
        password="testpassword",
        is_admin=False
    )
    
    db.session.add(user)
    db.session.commit()
    
    return user
