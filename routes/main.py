# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Main application routes."""
from flask import Blueprint, render_template, jsonify, request, current_app
from services.quest_fetcher import fetch_gigs
from services.difficulty_engine import calculate_difficulty_scores
from database import get_database

main_bp = Blueprint('main', __name__)

def render_questboard(quests):
    """Render the questboard with the given quests."""
    return render_template('questboard.html', quests=quests)

@main_bp.route('/')
def index():
    """Main page with quest listings."""
    try:
        quests = fetch_gigs()
        quests = calculate_difficulty_scores(quests)
        
        # Get bookmarked status for each quest
        db = get_database()
        bookmarks = db.get_bookmarked_quests()
        bookmarked_ids = {b[0] for b in bookmarks}
        
        for quest in quests:
            quest['bookmarked'] = quest.get('link', '') in bookmarked_ids
            
        return render_questboard(quests)
    except Exception as e:
        current_app.logger.error(f"Error in index route: {e}", exc_info=True)
        return render_template('error.html', error="Failed to load quests"), 500

@main_bp.route('/toggle_bookmark/<quest_id>', methods=['POST'])
def toggle_bookmark(quest_id):
    """Toggle bookmark status for a quest."""
    try:
        db = get_database()
        # Check if quest exists in database first
        quest = db.get_quest_by_link(quest_id)
        
        if not quest:
            # If quest not in database, fetch it
            quests = fetch_gigs()
            quest = next((q for q in quests if q.get('link') == quest_id), None)
            if not quest:
                return jsonify({"error": "Quest not found"}), 404
            
            # Cache the quest
            db.cache_quest(quest)
        
        # Toggle bookmark status
        is_bookmarked = db.toggle_bookmark(quest_id)
        return jsonify({"status": "success", "bookmarked": is_bookmarked})
    except Exception as e:
        current_app.logger.error(f"Error toggling bookmark: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@main_bp.route('/submit_quest', methods=['GET', 'POST'])
def submit_quest():
    """Handle user-submitted quests."""
    if request.method == 'POST':
        try:
            data = request.get_json() or {}
            db = get_database()
            
            quest = {
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'link': data.get('link', ''),
                'source': 'user_submitted',
                'date_posted': data.get('date_posted'),
                'location': data.get('location', '')
            }
            
            # Validate required fields
            if not all([quest['title'], quest['description']]):
                return jsonify({"error": "Title and description are required"}), 400
            
            # Save to database
            db.cache_quest(quest)
            return jsonify({"status": "success", "message": "Quest submitted for review"})
            
        except Exception as e:
            current_app.logger.error(f"Error submitting quest: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    # GET request - show submission form
    return render_template('submit_quest.html')
