"""Test configuration for the application."""
import os
import tempfile

# Use in-memory SQLite for testing
TESTING = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_TRACK_MODIFICATIONS = False
WTF_CSRF_ENABLED = False

# Test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'test_data')

# Test upload folder
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'questboard_test_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Test secret key
SECRET_KEY = 'test-secret-key'

# Disable rate limiting during testing
RATELIMIT_ENABLED = False
