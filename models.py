from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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