# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
from flask import request, current_app
from datetime import datetime
from flask_restx import Resource, Namespace, fields, reqparse
from ..database import get_database
from ..api_docs import api, quest_model, bookmark_model, handle_errors

# Set up logging
logger = logging.getLogger(__name__)

# Create API namespace
ns = Namespace('api', description='QuestBoard API operations')
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
            return jsonify({
                'error': 'Quest not found'
            }), 404
            
        # Ensure all required fields are present with default values
        quest.setdefault('approved_by', None)
        quest.setdefault('approved_at', None)
        quest.setdefault('tags', [])
        
        logger.debug(f"Found quest: {quest_id}")
        return jsonify(quest)
        
    except Exception as e:
        logger.error(f'Error getting quest {quest_id}: {str(e)}', exc_info=True)
        return jsonify({
            'error': 'Failed to retrieve quest',
            'details': str(e)
        }), 500

@api_bp.route('/quests', methods=['POST'])
def submit_quest():
    """Submit a new quest."""
    logger.info("POST /quests endpoint called")
    db = get_database()
    try:
        data = request.get_json()
        logger.debug(f"Received quest submission data: {data}")
        
        if not data:
            logger.warning("No JSON data provided in request")
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'description', 'source', 'url']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            error_msg = f'Missing required fields: {", ".join(missing_fields)}'
            logger.warning(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Prepare quest data
        quest_data = {
            'title': data['title'],
            'description': data['description'],
            'source': data['source'],
            'url': data['url'],
            'difficulty': data.get('difficulty', 'medium'),
            'reward': data.get('reward', ''),
            'region': data.get('region', ''),
            'tags': data.get('tags', []),
            'submitted_by': data.get('submitted_by', 'anonymous'),
            'is_approved': data.get('is_approved', False)
        }
        
        logger.debug(f"Attempting to add quest: {quest_data['title']}")
        
        # Add to database
        quest = db.add_quest(quest_data)
        if not quest:
            logger.error("Failed to add quest to database")
            return jsonify({'error': 'Failed to add quest'}), 500
            
        response = {
            'id': quest['id'],
            'title': quest['title'],
            'is_approved': bool(quest.get('is_approved', False))
        }
        
        logger.info(f"Successfully added quest: {quest['id']} - {quest['title']}")
        logger.debug(f"Quest details: {response}")
        
        return jsonify(response), 201
        
    except Exception as e:
        logger.error(f"Error submitting quest: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to submit quest',
            'details': str(e)
        }), 500

@api_bp.route('/quests/<quest_id>/bookmark', methods=['POST', 'DELETE'])
def bookmark_quest(quest_id):
    """Bookmark or unbookmark a quest."""
    method = request.method
    logger.info(f"{method} /quests/{quest_id}/bookmark endpoint called")
    
    db = get_database()
    try:
        data = request.get_json()
        logger.debug(f"Bookmark request data: {data}")
        
        if not data or 'user_id' not in data or not data['user_id']:
            logger.warning("User ID missing or empty in bookmark request")
            return jsonify({'error': 'User ID is required and cannot be empty'}), 400
            
        user_id = data['user_id'].strip()
        if not user_id:
            logger.warning("User ID is empty after stripping whitespace")
            return jsonify({'error': 'User ID cannot be empty'}), 400
            
        logger.debug(f"Processing {method} request for user: {user_id}, quest: {quest_id}")
        
        # Check if quest exists
        quest = db.get_quest(quest_id)
        if not quest:
            logger.warning(f"Quest not found: {quest_id}")
            return jsonify({'error': 'Quest not found'}), 404
            
        # Handle DELETE request (unbookmark)
        if method == 'DELETE':
            if not db.is_bookmarked(user_id, quest_id):
                logger.info(f"Quest {quest_id} is not bookmarked by user {user_id}")
                return jsonify({
                    'success': False,
                    'message': 'Quest is not bookmarked',
                    'is_bookmarked': False
                })
                
            is_bookmarked = db.toggle_bookmark(user_id, quest_id)
            logger.info(f"Successfully removed from bookmarks for user: {user_id}, quest: {quest_id}")
            return jsonify({
                'success': True,
                'is_bookmarked': is_bookmarked,
                'message': 'Bookmark removed successfully'
            })
        
        # Handle POST request (bookmark)
        if db.is_bookmarked(user_id, quest_id):
            logger.info(f"Quest {quest_id} is already bookmarked by user {user_id}")
            return jsonify({
                'success': False,
                'message': 'Quest is already bookmarked',
                'is_bookmarked': True
            })
            
        # Add bookmark
        is_bookmarked = db.toggle_bookmark(user_id, quest_id)
        logger.info(f"Successfully added to bookmarks for user: {user_id}, quest: {quest_id}")
        
        return jsonify({
            'success': True,
            'is_bookmarked': is_bookmarked,
            'message': 'Bookmark added successfully'
        })
        
    except Exception as e:
        logger.error(f"Error processing {method} request: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Failed to process {method} request',
            'details': str(e)
        }), 500

@api_bp.route('/users/<user_id>/bookmarks', methods=['GET'])
def get_user_bookmarks(user_id):
    """Get all bookmarks for a user."""
    logger.info(f"GET /users/{user_id}/bookmarks endpoint called")
    db = get_database()
    try:
        logger.debug(f"Fetching bookmarks for user: {user_id}")
        bookmarks = db.get_user_bookmarks(user_id)
        
        logger.debug(f"Found {len(bookmarks)} bookmarks for user: {user_id}")
        
        # Ensure all bookmarks have required fields
        for bookmark in bookmarks:
            bookmark.setdefault('approved_by', None)
            bookmark.setdefault('approved_at', None)
            bookmark.setdefault('tags', [])
            
        response = {
            'bookmarks': bookmarks,
            'count': len(bookmarks)
        }
        
        logger.debug(f"Returning bookmarks for user: {user_id}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error fetching bookmarks for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to retrieve bookmarks',
            'details': str(e)
        }), 500

# Convert tags from JSON string to list if needed
        for bookmark in bookmarks:
            if 'tags' in bookmark and isinstance(bookmark['tags'], str):
                try:
                    bookmark['tags'] = json.loads(bookmark['tags'])
                except (json.JSONDecodeError, TypeError):
                    bookmark['tags'] = []
        
        return jsonify({
            'bookmarks': bookmarks,
            'count': len(bookmarks),
            'user_id': user_id
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
