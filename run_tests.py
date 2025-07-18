#!/usr/bin/env python3
"""
Test runner for QuestBoard application.
This script sets up the test environment and runs the test suite.
"""
import os
import sys
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_tests():
    """Run the test suite."""
    # Set up test environment variables
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = '1'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['WTF_CSRF_ENABLED'] = 'False'
    
    # Run pytest with coverage and verbose output
    return pytest.main([
        '--cov=questboard',
        '--cov-report=term-missing',
        '-v',
        'tests/'
    ])

if __name__ == '__main__':
    sys.exit(run_tests())
