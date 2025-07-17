"""
API Documentation for QuestBoard using Flask-RESTX.
"""
from flask_restx import Api, fields, Namespace, Resource
from functools import wraps
from flask import jsonify

# Create API documentation
api = Api(
    title='QuestBoard API',
    version='1.0',
    description='A REST API for managing quests and bookmarks',
    doc='/api/docs/',  # Enable Swagger UI at /api/docs/
    default='Quests',
    default_label='Quest related operations'
)

# Namespaces
ns_quests = Namespace('quests', description='Quest operations')
ns_bookmarks = Namespace('bookmarks', description='Bookmark operations')

# Models
quest_model = api.model('Quest', {
    'id': fields.String(required=True, description='The quest identifier'),
    'title': fields.String(required=True, description='The quest title'),
    'description': fields.String(description='The quest description'),
    'source': fields.String(description='Source of the quest'),
    'region': fields.String(description='Region for the quest'),
    'is_approved': fields.Boolean(description='Whether the quest is approved'),
    'posted_date': fields.DateTime(description='When the quest was posted'),
    'user_id': fields.String(description='ID of the user who posted the quest')
})

bookmark_model = api.model('Bookmark', {
    'user_id': fields.String(required=True, description='The user ID'),
    'quest_id': fields.String(required=True, description='The quest ID to bookmark')
})

# Helper decorator for error handling
def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return {'message': str(e)}, 500
    return wrapper

# Add namespaces to API
api.add_namespace(ns_quests)
api.add_namespace(ns_bookmarks)
