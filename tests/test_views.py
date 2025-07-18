"""Tests for the application views."""

def test_index_route(client):
    """Test the index route returns a 200 status code."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to QuestBoard' in response.data

def test_about_route(client):
    """Test the about route returns a 200 status code."""
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About' in response.data

def test_quests_route_unauthorized(client):
    """Test that the quests route requires authentication."""
    response = client.get('/quests', follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to login page
    assert b'Login' in response.data

def test_create_quest_route_unauthorized(client):
    """Test that the create quest route requires authentication."""
    response = client.get('/quests/create', follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to login page
    assert b'Login' in response.data

def test_register_route(client):
    """Test the registration page is accessible."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_login_route(client):
    """Test the login page is accessible."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data
