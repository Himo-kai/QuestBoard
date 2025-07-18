"""
Quest API endpoints.

This module handles all quest-related API operations.
"""
from flask_restx import Resource, fields, abort
from flask import request
from ...models.quest import Quest
from .namespaces import quest_ns

# Request/Response models
quest_model = quest_ns.model('Quest', {
    'id': fields.Integer(readonly=True, description='The quest unique identifier'),
    'title': fields.String(required=True, description='The quest title'),
    'description': fields.String(required=True, description='The quest description'),
    'reward': fields.Float(required=True, description='The quest reward amount'),
    'status': fields.String(required=True, description='The quest status'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readonly=True, description='Last update timestamp')
})

@quest_ns.route('/')
class QuestList(Resource):
    """Shows a list of all quests, and lets you POST to add new quests"""
    
    @quest_ns.doc('list_quests')
    @quest_ns.marshal_list_with(quest_model)
    def get(self):
        """List all quests"""
        return Quest.query.all()
    
    @quest_ns.doc('create_quest')
    @quest_ns.expect(quest_model)
    @quest_ns.marshal_with(quest_model, code=201)
    def post(self):
        """Create a new quest"""
        data = request.get_json()
        quest = Quest(
            title=data['title'],
            description=data['description'],
            reward=data['reward'],
            status=data.get('status', 'open')
        )
        quest.save()
        return quest, 201

@quest_ns.route('/<int:id>')
@quest_ns.response(404, 'Quest not found')
@quest_ns.param('id', 'The quest identifier')
class QuestResource(Resource):
    """Show a single quest and lets you update/delete it"""
    
    @quest_ns.doc('get_quest')
    @quest_ns.marshal_with(quest_model)
    def get(self, id):
        """Fetch a quest given its identifier"""
        quest = Quest.query.get_or_404(id)
        return quest
    
    @quest_ns.doc('update_quest')
    @quest_ns.expect(quest_model)
    @quest_ns.marshal_with(quest_model)
    def put(self, id):
        """Update a quest given its identifier"""
        quest = Quest.query.get_or_404(id)
        data = request.get_json()
        
        quest.title = data.get('title', quest.title)
        quest.description = data.get('description', quest.description)
        quest.reward = data.get('reward', quest.reward)
        quest.status = data.get('status', quest.status)
        
        quest.save()
        return quest
    
    @quest_ns.doc('delete_quest')
    @quest_ns.response(204, 'Quest deleted')
    def delete(self, id):
        """Delete a quest given its identifier"""
        quest = Quest.query.get_or_404(id)
        quest.delete()
        return '', 204
