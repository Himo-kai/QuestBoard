"""
API specification for QuestBoard using Flask-RESTX.
"""
from flask_restx import Api, fields, Namespace

# Create API instance
api = Api(
    title='QuestBoard API',
    version='1.0',
    description='A REST API for managing quests and bookmarks',
    doc='/api/docs/',
    default='Quests',
    default_label='Quest related operations',
    security='Bearer Auth',
    authorizations={
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Type in the *Value* input box: **Bearer &lt;JWT&gt;**, where JWT is the token'  # noqa: E501
        }
    }
)

# Create namespaces
ns_quests = Namespace('quests', description='Quest operations')
ns_bookmarks = Namespace('bookmarks', description='Bookmark operations')
ns_auth = Namespace('auth', description='Authentication operations')

# Request models
quest_parser = api.parser()
quest_parser.add_argument('page', type=int, default=1, help='Page number')
quest_parser.add_argument('per_page', type=int, default=10, help='Items per page')
quest_parser.add_argument('search', type=str, help='Search term')

# Response models
error_model = api.model('Error', {
    'message': fields.String(description='Error message')
})

pagination_model = api.model('Pagination', {
    'page': fields.Integer,
    'per_page': fields.Integer,
    'total': fields.Integer,
    'total_pages': fields.Integer
})

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

quest_list_model = api.model('QuestList', {
    'quests': fields.List(fields.Nested(quest_model)),
    'pagination': fields.Nested(pagination_model)
})

bookmark_model = api.model('Bookmark', {
    'user_id': fields.String(required=True, description='The user ID'),
    'quest_id': fields.String(required=True, description='The quest ID'),
    'created_at': fields.DateTime(description='When the bookmark was created')
})

# Add namespaces to API
api.add_namespace(ns_quests, path='/quests')
api.add_namespace(ns_bookmarks, path='/bookmarks')
api.add_namespace(ns_auth, path='/auth')
