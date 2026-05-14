from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Fields for match statistics
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)

    # Dynamic property to calculate win rate for the frontend
    @property
    def win_rate(self):
        if self.matches_played == 0:
            return 0
        return round((self.wins / self.matches_played) * 100)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Table for recording match history
class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    white_player_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    black_player_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Result of the match (e.g., 'Victory', 'Defeat', 'Draw')
    result = db.Column(db.String(50)) 
    mode = db.Column(db.String(50), default='1v1 Quick Match')
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    white_player = db.relationship('User', foreign_keys=[white_player_id])
    black_player = db.relationship('User', foreign_keys=[black_player_id])

# Table for active and completed games
class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    
    # The two players in the game
    player1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Game status: waiting, active, finished
    status = db.Column(db.String(20), default='waiting')
    
    # Board state stored as JSON string for server-side sync
    board_state = db.Column(db.Text, nullable=True)
    
    # Whose turn it is
    current_turn = db.Column(db.String(10), default='white')
    
    # When the game was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    player1 = db.relationship('User', foreign_keys=[player1_id])
    player2 = db.relationship('User', foreign_keys=[player2_id])
    
    # Messages in this game
    messages = db.relationship('Message', backref='game', lazy=True)

    def get_board(self):
        """Return board state as a dictionary"""
        if self.board_state:
            return json.loads(self.board_state)
        return None

    def set_board(self, board_dict):
        """Save board state as JSON string"""
        self.board_state = json.dumps(board_dict)

    def __repr__(self):
        return f'<Game {self.id}: {self.player1_id} vs {self.player2_id}>'


# Table for storing in-game chat messages
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    
    # Link message to a specific game
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # The text content of the message
    content = db.Column(db.String(200), nullable=False)
    
    # When the message was sent
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to get the sender's user object
    sender = db.relationship('User', foreign_keys=[sender_id])

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id}>'
 
# Table for storing in-game chat messages
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # The text content of the message
    content = db.Column(db.String(200), nullable=False)
    
    # When the message was sent
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to get the sender's user object
    sender = db.relationship('User', foreign_keys=[sender_id])

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id}>'