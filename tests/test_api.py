# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import pytest
from datetime import datetime, timedelta, timezone
from questboard.models.quest import Quest

class TestAPI:
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.json == {'status': 'ok', 'timestamp': pytest.approx(datetime.now(timezone.utc).timestamp(), rel=1)}

    def test_get_quests(self, client, sample_quest):
        """Test getting a list of quests."""
        # Add a test quest
        response = client.post('/api/quests', json=sample_quest)
        assert response.status_code == 201

        # Get quests
        response = client.get('/api/quests')
        assert response.status_code == 200
        assert isinstance(response.json, dict)
        assert 'quests' in response.json
        assert 'total' in response.json
        assert 'page' in response.json
        assert 'per_page' in response.json
        assert isinstance(response.json['quests'], list)

        # Test search
        response = client.get('/api/quests?search=test')
        assert response.status_code == 200
        assert len(response.json['quests']) > 0

        # Test pagination
        response = client.get('/api/quests?page=1&per_page=1')
        assert response.status_code == 200
        assert len(response.json['quests']) == 1
        assert response.json['page'] == 1
        assert response.json['per_page'] == 1

    def test_get_quest(self, client, sample_quest):
        """Test getting a single quest."""
        # Add a test quest
        response = client.post('/api/quests', json=sample_quest)
        assert response.status_code == 201
        quest_data = response.json
        quest_id = quest_data['id']

        # Get the quest
        response = client.get(f'/api/quests/{quest_id}')
        assert response.status_code == 200
        assert response.json['id'] == quest_id
        assert response.json['title'] == sample_quest['title']

        # Verify all required fields are present
        required_fields = ['id', 'title', 'description', 'source', 'url', 
                          'posted_date', 'created_at', 'updated_at', 'difficulty',
                          'reward', 'region', 'tags', 'is_approved', 'approved_by',
                          'approved_at', 'submitted_by']

        for field in required_fields:
            assert field in response.json, f"Missing required field: {field}"

        # Test non-existent quest
        response = client.get('/api/quests/non-existent-id')
        assert response.status_code == 404

    def test_submit_quest(self, client, db):
        """Test submitting a new quest."""
        quest_data = {
            'title': 'New Test Quest',
            'description': 'This is a test quest',
            'source': 'test',
            'url': 'http://example.com/new-quest',
            'difficulty': 'easy',
            'reward': '100 gold',
            'region': 'Test Region',
            'tags': ['test', 'quest'],
            'submitted_by': 'test-user'
        }

        response = client.post('/api/quests', json=quest_data)
        assert response.status_code == 201
        data = response.json
        assert 'id' in data
        assert data['title'] == quest_data['title']
        assert data['is_approved'] is False  # Should default to not approved

    def test_bookmark_quest(self, client, db, sample_quest):
        """Test bookmarking a quest."""
        # Add a test quest
        response = client.post('/api/quests', json=sample_quest)
        assert response.status_code == 201
        quest_id = response.json['id']
        user_id = 'test-user-1'

        # Test bookmarking
        response = client.post(
            f'/api/quests/{quest_id}/bookmark',
            json={'user_id': user_id}
        )
        assert response.status_code == 200
        assert response.json['success'] is True

        # Verify the bookmark exists
        response = client.get(f'/api/users/{user_id}/bookmarks')
        assert response.status_code == 200
        bookmarks = response.json.get('bookmarks', [])
        assert any(q['id'] == quest_id for q in bookmarks)

        # Test duplicate bookmark
        response = client.post(
            f'/api/quests/{quest_id}/bookmark',
            json={'user_id': user_id}
        )
        assert response.status_code == 200
        assert response.json['success'] is False
        assert 'already bookmarked' in response.json.get('message', '').lower()

        # Test removing bookmark
        response = client.delete(
            f'/api/quests/{quest_id}/bookmark',
            json={'user_id': user_id}
        )
        assert response.status_code == 200
        assert response.json['success'] is True

        # Verify bookmark was removed
        response = client.get(f'/api/users/{user_id}/bookmarks')
        assert response.status_code == 200
        bookmarks = response.json.get('bookmarks', [])
        assert not any(q['id'] == quest_id for q in bookmarks)

        # Test removing non-existent bookmark
        response = client.delete(
            f'/api/quests/{quest_id}/bookmark',
            json={'user_id': user_id}
        )
        assert response.status_code == 200
        assert response.json['success'] is False
        assert 'not bookmarked' in response.json.get('message', '').lower()

        # Test with invalid user_id
        response = client.post(
            f'/api/quests/{quest_id}/bookmark',
            json={'user_id': ''}
        )
        assert response.status_code == 400

        # Test with non-existent quest
        response = client.post(
            '/api/quests/non-existent-id/bookmark',
            json={'user_id': user_id}
        )
        assert response.status_code == 404
        
        # Verify the bookmark was not added for non-existent quest
        bookmarks = db.get_user_bookmarks(user_id)
        assert not any(b['id'] == 'non-existent-id' for b in bookmarks)
