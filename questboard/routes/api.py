# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
from flask import request, current_app
from datetime import datetime
from flask_restx import Resource, Namespace, fields, reqparse
from flask import Blueprint, jsonify
from ..database import get_database
from ..api_docs import api, quest_model, bookmark_model, handle_errors

# Set up logging
logger = logging.getLogger(__name__)

# Create API namespace and blueprint
ns = Namespace('api', description='QuestBoard API operations')
api_bp = Blueprint('api', __name__)
api.init_app(api_bp)
api.add_namespace(ns, path='/')

# Request parsers
quest_parser = reqparse.RequestParser()
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

quest_list_model = api.model('QuestList', {
    'quests': fields.List(fields.Nested(quest_model)),
    'pagination': fields.Nested(pagination_model)
})

@ns.route('/health')
class HealthCheck(Resource):
    @ns.response(200, 'API is healthy')
    @ns.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Health check endpoint."""
        logger.info("Health check requested")
        try:
            response = {
                'status': 'ok',
                'timestamp': datetime.utcnow().timestamp()
            }
            logger.debug(f"Health check response: {response}")
            return response, 200
        except Exception as e:
            logger.error(f"Error in health check: {str(e)}", exc_info=True)
            return {'message': 'Internal server error'}, 500

# Request parsers for query parameters
quest_parser = ns.parser()
quest_parser.add_argument('page', type=int, default=1, help='Page number')
quest_parser.add_argument('per_page', type=int, default=10, help='Items per page')
quest_parser.add_argument('search', type=str, help='Search term')

@ns.route('/quests')
class QuestList(Resource):
    @ns.doc('list_quests')
    @ns.expect(quest_parser)
    @ns.marshal_with(quest_list_model)
    @ns.response(200, 'Success')
    @ns.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get all quests with pagination."""
        logger.info("GET /quests endpoint called")
        db = get_database()
        try:
            args = quest_parser.parse_args()
            page = args.get('page', 1)
            per_page = args.get('per_page', 10)
            search = args.get('search')
            
            # Get quests with pagination
            quests = db.get_quests(page=page, per_page=per_page, search=search)
            
            # Ensure all required fields are present with default values
            for quest in quests:
                quest.setdefault('approved_by', None)
                quest.setdefault('approved_at', None)
                quest.setdefault('tags', [])
            
            logger.debug(f"Found {len(quests)} quests")
            return {
                'quests': quests,
                'page': page,
                'per_page': per_page,
                'total': len(quests)  # This should be the total count, not just the current page
            }
            
        except Exception as e:
            logger.error(f'Error getting quests: {str(e)}', exc_info=True)
            return {'message': 'Failed to retrieve quests', 'details': str(e)}, 500

@ns.route('/quests')
class QuestSubmit(Resource):
    @ns.doc('submit_quest')
    @ns.expect(quest_model)
    @ns.response(201, 'Quest submitted successfully')
    @ns.response(400, 'Invalid input', error_model)
    def post(self):
        """Submit a new quest."""
        logger.info("POST /quests endpoint called")
        db = get_database()
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No input data provided'}, 400
                
            # Validate required fields
            required_fields = ['title', 'description', 'source', 'url']
            for field in required_fields:
                if field not in data:
                    return {'message': f'Missing required field: {field}'}, 400
                    
            # Create quest
            quest = {
                'title': data['title'],
                'description': data['description'],
                'source': data['source'],
                'url': data['url'],
                'posted_date': datetime.utcnow(),
                'difficulty': data.get('difficulty', 5.0),
                'reward': data.get('reward', 'Not specified'),
                'region': data.get('region', 'Unknown'),
                'tags': data.get('tags', []),
                'is_approved': False,
                'submitted_by': data.get('submitted_by')
            }
            
            # Save to database
            db.add_quest(quest)
            
            logger.info(f"Quest submitted: {quest['title']}")
            return {'message': 'Quest submitted successfully', 'quest': quest}, 201
            
        except Exception as e:
            logger.error(f'Error submitting quest: {str(e)}', exc_info=True)
            return {'message': 'Failed to submit quest', 'details': str(e)}, 500

@ns.route('/quests/<string:quest_id>/bookmark')
@ns.param('quest_id', 'The quest identifier')
class BookmarkQuest(Resource):
    def post(self, quest_id):
        """Bookmark a quest."""
        logger.info(f"POST /quests/{quest_id}/bookmark endpoint called")
        db = get_database()
        try:
            data = request.get_json()
            if not data or 'user_id' not in data or not data['user_id']:
                return {'message': 'User ID is required and cannot be empty'}, 400
                
            user_id = data['user_id'].strip()
            if not user_id:
                return {'message': 'User ID cannot be empty'}, 400
                
            logger.debug(f"Processing POST request for user: {user_id}, quest: {quest_id}")
            
            # Check if quest exists
            quest = db.get_quest(quest_id)
            if not quest:
                return {'message': 'Quest not found'}, 404
                
            # Add bookmark
            is_bookmarked = db.toggle_bookmark(user_id, quest_id)
            logger.info(f"Successfully added to bookmarks for user: {user_id}, quest: {quest_id}")
            
            return {'success': True, 'is_bookmarked': is_bookmarked, 'message': 'Bookmark added successfully'}
            
        except Exception as e:
            logger.error(f"Error processing POST request: {str(e)}", exc_info=True)
            return {'message': 'Failed to process POST request', 'details': str(e)}, 500
            
    def delete(self, quest_id):
        """Unbookmark a quest."""
        logger.info(f"DELETE /quests/{quest_id}/bookmark endpoint called")
        db = get_database()
        try:
            data = request.get_json()
            if not data or 'user_id' not in data or not data['user_id']:
                return {'message': 'User ID is required and cannot be empty'}, 400
                
            user_id = data['user_id'].strip()
            if not user_id:
                return {'message': 'User ID cannot be empty'}, 400
                
            logger.debug(f"Processing DELETE request for user: {user_id}, quest: {quest_id}")
            
            # Check if quest exists
            quest = db.get_quest(quest_id)
            if not quest:
                return {'message': 'Quest not found'}, 404
                
            # Remove bookmark
            is_bookmarked = db.toggle_bookmark(user_id, quest_id)
            logger.info(f"Successfully removed from bookmarks for user: {user_id}, quest: {quest_id}")
            
            return {'success': True, 'is_bookmarked': is_bookmarked, 'message': 'Bookmark removed successfully'}
            
        except Exception as e:
            logger.error(f"Error processing DELETE request: {str(e)}", exc_info=True)
            return {'message': 'Failed to process DELETE request', 'details': str(e)}, 500

@ns.route('/users/<string:user_id>/bookmarks')
@ns.param('user_id', 'The user identifier')
class UserBookmarks(Resource):
    def get(self, user_id):
        """Get all bookmarks for a user."""
        logger.info(f"GET /users/{user_id}/bookmarks endpoint called")
        db = get_database()
        try:
            logger.debug(f"Fetching bookmarks for user: {user_id}")
            bookmarks = db.get_user_bookmarks(user_id)
            
            logger.debug(f"Found {len(bookmarks)} bookmarks for user: {user_id}")
            
            # Convert bookmarks to a list of dictionaries if they're not already
            bookmarks_list = []
            for bookmark in bookmarks:
                if isinstance(bookmark, dict):
                    bookmarks_list.append(bookmark)
                else:
                    # Assuming bookmark has a to_dict() method or similar
                    bookmarks_list.append({
                        'id': getattr(bookmark, 'id', None),
                        'title': getattr(bookmark, 'title', ''),
                        'description': getattr(bookmark, 'description', ''),
                        'source': getattr(bookmark, 'source', ''),
                        'url': getattr(bookmark, 'url', ''),
                        'posted_date': getattr(bookmark, 'posted_date', None),
                        'difficulty': getattr(bookmark, 'difficulty', None),
                        'reward': getattr(bookmark, 'reward', None),
                        'region': getattr(bookmark, 'region', None),
                        'tags': getattr(bookmark, 'tags', []),
                        'is_approved': getattr(bookmark, 'is_approved', False)
                    })
            
            logger.info(f"Successfully retrieved {len(bookmarks_list)} bookmarks for user: {user_id}")
            return {
                'success': True,
                'bookmarks': bookmarks_list,
                'count': len(bookmarks_list)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving bookmarks for user {user_id}: {str(e)}", exc_info=True)
            return {'message': 'Failed to retrieve bookmarks', 'details': str(e)}, 500
