# tests/test_security.py
from models import User, db

def test_user_registration_flow(client, app):
    """
    Test the user registration process. It should successfully create 
    a new user in the database and hash their password.
    """
    # Simulate submitting the registration form
    response = client.post('/register', data={
        'username': 'new_secure_user',
        'email': 'secure@test.com',
        'password': 'StrongPassword123!',
        'confirm_password': 'StrongPassword123!'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify the user actually exists in the database
    with app.app_context():
        user = User.query.filter_by(username='new_secure_user').first()
        assert user is not None
        # Verify that the password was NOT stored in plain text
        assert user.password_hash != 'StrongPassword123!'
        # Verify the hash can validate the correct password
        assert user.check_password('StrongPassword123!') is True


def test_duplicate_username_registration(client, app):
    """
    Test that the system prevents registering a new account with an 
    already existing username.
    """
    with app.app_context():
        # First, ensure a user exists
        existing_user = User(username='taken_name', email='first@test.com')
        existing_user.set_password('pass123')
        db.session.add(existing_user)
        db.session.commit()

    # Attempt to register with the SAME username
    response = client.post('/register', data={
        'username': 'taken_name',
        'email': 'second@test.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword'
    }, follow_redirects=True)
    
    # Check that a flash message or error occurred
    assert b'Username already exists' in response.data