# tests/test_routes.py

def test_index_page_loads(client):
    """
    Test that the home page (index) loads successfully with a 200 OK status,
    and contains the core branding text.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Chess Master' in response.data


def test_play_route_unauthorized(client):
    """
    Test that an unauthenticated user cannot access the '/play' route.
    Flask-Login should intercept this and return a 302 Redirect to the login view.
    """
    response = client.get('/play', follow_redirects=False)
    # 302 means the user is being redirected (likely to the login/index page)
    assert response.status_code == 302


def test_profile_route_unauthorized(client):
    """
    Test that an unauthenticated user cannot access the '/profile' route.
    """
    response = client.get('/profile', follow_redirects=False)
    assert response.status_code == 302


def test_api_messages_unauthorized(client):
    """
    Test that the chat API endpoints are protected and cannot be 
    accessed without being logged in.
    """
    response = client.get('/api/messages', follow_redirects=False)
    assert response.status_code == 302