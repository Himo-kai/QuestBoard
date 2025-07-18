"""
This package contains all the test files for the QuestBoard application.
"""

# Import test modules to ensure they're registered with pytest
from . import test_admin
from . import test_api
from . import test_bookmark_race
from . import test_bookmarks
from . import test_database
from . import test_models
from . import test_nlp_service
from . import test_scoring_service
from . import test_services

__all__ = [
    'test_admin',
    'test_api',
    'test_bookmark_race',
    'test_bookmarks',
    'test_database',
    'test_models',
    'test_nlp_service',
    'test_scoring_service',
    'test_services',
]
