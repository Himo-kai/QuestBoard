"""
Tests for admin routes and functionality.
"""
import pytest
from flask import url_for
from werkzeug.datastructures import Headers

class TestAdminRoutes:
    """Test cases for admin routes."""

    def test_admin_dashboard_requires_auth(self, client):
        """Test that admin dashboard requires authentication."""
        response = client.get(url_for('admin.dashboard'))
        assert response.status_code == 401  # Or 302 if using redirect to login

    def test_approve_quest_requires_auth(self, client, sample_quest):
        """Test that approving a quest requires authentication."""
        response = client.post(
            url_for('admin.approve_quest', quest_id=sample_quest.id),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code in [401, 403]

    @pytest.mark.usefixtures('login_admin')
    def test_approve_quest(self, client, sample_quest):
        """Test approving a quest as an admin."""
        response = client.post(
            url_for('admin.approve_quest', quest_id=sample_quest.id),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert sample_quest.is_approved is True

    @pytest.mark.usefixtures('login_admin')
    def test_reject_quest(self, client, sample_quest):
        """Test rejecting a quest with a reason."""
        rejection_reason = "Inappropriate content"
        response = client.post(
            url_for('admin.reject_quest', quest_id=sample_quest.id),
            json={"reason": rejection_reason},
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert sample_quest.is_approved is False
        assert sample_quest.rejection_reason == rejection_reason

    @pytest.mark.parametrize('page,per_page', [
        (1, 10),
        (2, 5),
        (None, None)  # Test defaults
    ])
    @pytest.mark.usefixtures('login_admin')
    def test_list_quests_pagination(self, client, create_quests, page, per_page):
        """Test quest listing with pagination."""
        # Create test quests
        create_quests(15)  # Create 15 test quests
        
        # Build query parameters
        params = {}
        if page is not None:
            params['page'] = page
        if per_page is not None:
            params['per_page'] = per_page
            
        response = client.get(
            url_for('admin.list_quests'),
            query_string=params,
            headers={'Accept': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json['data']
        
        # Verify pagination metadata
        expected_per_page = per_page or 10  # Default per_page is 10
        expected_page = page or 1  # Default page is 1
        
        assert 'pagination' in data
        assert data['pagination']['page'] == expected_page
        assert data['pagination']['per_page'] == expected_per_page
        assert len(data['items']) <= expected_per_page
