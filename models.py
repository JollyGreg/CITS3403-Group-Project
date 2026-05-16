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
    matches_played = db.Column(db.Integer, default=0, nullable=False)
    wins           = db.Column(db.Integer, default=0, nullable=False)
    losses         = db.Column(db.Integer, default=0, nullable=False)
    draws          = db.Column(db.Integer, default=0, nullable=False)

    # ELO rating system
    elo_rating  = db.Column(db.Integer, default=1200, nullable=False)
    elo_history = db.Column(db.Text, default='[]')  # JSON array of ELO changes

    @property
    def win_rate(self):
        """Win percentage, shown on the frontend profile page."""
        if self.matches_played == 0:
            return 0
        return round((self.wins / self.matches_played) * 100)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ELO={self.elo_rating}>'


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    white_player_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    black_player_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # 'white_win' | 'black_win' | 'draw'
    result = db.Column(db.String(50))
    mode   = db.Column(db.String(50), default='1v1 Quick Match')
    date   = db.Column(db.DateTime, default=datetime.utcnow)

    # ELO snapshots so match history shows rating movement over time
    white_elo_before = db.Column(db.Integer, nullable=True)
    white_elo_after  = db.Column(db.Integer, nullable=True)
    black_elo_before = db.Column(db.Integer, nullable=True)
    black_elo_after  = db.Column(db.Integer, nullable=True)

    white_player = db.relationship('User', foreign_keys=[white_player_id])
    black_player = db.relationship('User', foreign_keys=[black_player_id])


class Game(db.Model):
    __tablename__ = 'games'

    id         = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # 'waiting' | 'active' | 'finished'
    status       = db.Column(db.String(20), default='waiting')
    board_state  = db.Column(db.Text, nullable=True)
    current_turn = db.Column(db.String(10), default='white')
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    player1  = db.relationship('User', foreign_keys=[player1_id])
    player2  = db.relationship('User', foreign_keys=[player2_id])
    messages = db.relationship('Message', backref='game', lazy=True)

    def get_board(self):
        if self.board_state:
            return json.loads(self.board_state)
        return None

    def set_board(self, board_dict):
        self.board_state = json.dumps(board_dict)

    def __repr__(self):
        return f'<Game {self.id}: {self.player1_id} vs {self.player2_id}>'


class Message(db.Model):
    __tablename__ = 'messages'

    id        = db.Column(db.Integer, primary_key=True)
    game_id   = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content   = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id}>'