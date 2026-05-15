# tests/test_model.py
from models import User, Match, Message, db

def test_user_creation_and_password(app):
    """
    Test that a User object can be created with basic attributes
    and that the password hashing mechanism works correctly.
    """
    with app.app_context():
        # Create a test user
        user = User(username='test_player', email='player@test.com')
        user.set_password('secure_password_123')
        
        # Save to the in-memory database
        db.session.add(user)
        db.session.commit()

        # Retrieve the user from the database
        fetched_user = User.query.filter_by(username='test_player').first()

        # Assertions to verify data integrity
        assert fetched_user is not None
        assert fetched_user.email == 'player@test.com'
        
        # Verify the password hashing logic
        assert fetched_user.check_password('secure_password_123') is True
        assert fetched_user.check_password('wrong_password') is False


def test_user_win_rate_calculation(app):
    """
    Test the dynamic 'win_rate' property of the User model.
    It should handle both 0 matches (avoiding division by zero) and normal calculations.
    """
    with app.app_context():
        # Test case 1: No matches played (should default to 0% to prevent errors)
        new_user = User(username='rookie', email='rookie@test.com', matches_played=0, wins=0)
        assert new_user.win_rate == 0

        # Test case 2: Played matches with wins (e.g., 4 wins out of 10 matches = 40%)
        veteran_user = User(username='veteran', email='vet@test.com', matches_played=10, wins=4)
        assert veteran_user.win_rate == 40

        # Test case 3: Rounding check (e.g., 2 wins out of 3 matches = 66.66...% -> 67%)
        pro_user = User(username='pro', email='pro@test.com', matches_played=3, wins=2)
        assert pro_user.win_rate == 67


def test_match_recording(app):
    """
    Test the creation of a Match record and verify that the 
    foreign key relationships to the User model work correctly.
    """
    with app.app_context():
        # Setup two players with passwords to satisfy the NOT NULL constraint
        player1 = User(username='white_player', email='white@test.com')
        player1.set_password('123')
        player2 = User(username='black_player', email='black@test.com')
        player2.set_password('123')
        
        db.session.add_all([player1, player2])
        db.session.commit()

        # Record a match between them
        new_match = Match(
            white_player_id=player1.id,
            black_player_id=player2.id,
            result='Victory',
            mode='1v1 Quick Match'
        )
        db.session.add(new_match)
        db.session.commit()

        # Fetch the match and verify relationships
        fetched_match = Match.query.first()
        assert fetched_match is not None
        assert fetched_match.white_player.username == 'white_player'
        assert fetched_match.black_player.username == 'black_player'
        assert fetched_match.result == 'Victory'


def test_message_creation(app):
    """
    Test that a chat message can be created and properly linked
    to the user who sent it via the foreign key.
    """
    with app.app_context():
        # Setup a sender with a password
        sender = User(username='chatter', email='chat@test.com')
        sender.set_password('123')
        
        db.session.add(sender)
        db.session.commit()

        # Create a chat message
        msg = Message(sender_id=sender.id, content='Hello, opponent!')
        db.session.add(msg)
        db.session.commit()

        # Fetch the message and verify the relationship
        fetched_msg = Message.query.first()
        assert fetched_msg is not None
        assert fetched_msg.content == 'Hello, opponent!'
        assert fetched_msg.sender.username == 'chatter'