"""
API namespaces for the QuestBoard application.

This module defines the main API instance and namespaces for organizing routes.
"""
from flask_restx import Namespace

# Import the main API instance from __init__.py
from . import api

# Create namespaces
quest_ns = Namespace('quests', description='Quest related operations')
user_ns = Namespace('users', description='User related operations')

# Export namespaces for easy access
__all__ = ['api', 'quest_ns', 'user_ns']
