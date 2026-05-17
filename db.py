"""Database initialization and management utilities"""
from app import app
from models import db, User, Match
import os

def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")

def reset_db():
    """Drop and recreate all tables (WARNING: deletes all data)"""
    with app.app_context():
        confirm = input("⚠️  This will delete ALL data. Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            db.drop_all()
            db.create_all()
            print("✓ Database reset successfully")
        else:
            print("✗ Database reset cancelled")

def create_test_user():
    """Create a test user for development"""
    with app.app_context():
        if User.query.filter_by(username='testuser').first():
            print("✗ Test user already exists")
            return
        
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print("✓ Test user created: username='testuser', password='password123'")

def create_test_match(white_username, black_username, result):
    """Create a test match and update ELO ratings"""
    from elo import record_match_with_elo
    
    with app.app_context():
        white_player = User.query.filter_by(username=white_username).first()
        black_player = User.query.filter_by(username=black_username).first()
        
        if not white_player:
            print(f"✗ White player '{white_username}' not found")
            return
        if not black_player:
            print(f"✗ Black player '{black_username}' not found")
            return
        if result not in ['white_win', 'black_win', 'draw']:
            print(f"✗ Invalid result: {result}. Must be 'white_win', 'black_win', or 'draw'")
            return
        
        # Record match and update ELO
        elo_changes = record_match_with_elo(white_player, black_player, result)
        
        print(f"✓ Match recorded: {white_username} vs {black_username} - {result}")
        print(f"  White: {elo_changes['white_change']:+d} ELO ({elo_changes['white_new_rating']})")
        print(f"  Black: {elo_changes['black_change']:+d} ELO ({elo_changes['black_new_rating']})")

def show_player_stats(username):
    """Display a player's statistics"""
    with app.app_context():
        player = User.query.filter_by(username=username).first()
        if not player:
            print(f"✗ Player '{username}' not found")
            return
        
        print(f"\n--- {player.username} ---")
        print(f"ELO Rating: {player.elo_rating}")
        print(f"Matches Played: {player.matches_played}")
        print(f"Wins: {player.wins}")
        print(f"Win Rate: {player.win_rate}%")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            create_test_user()
        elif command == 'match':
            if len(sys.argv) < 5:
                print("Usage: python db.py match <white_player> <black_player> <result>")
                print("  result: white_win, black_win, or draw")
                sys.exit(1)
            create_test_match(sys.argv[2], sys.argv[3], sys.argv[4])
        elif command == 'stats':
            if len(sys.argv) < 3:
                print("Usage: python db.py stats <username>")
                sys.exit(1)
            show_player_stats(sys.argv[2])
        elif command == 'reset':
            reset_db()
        else:
            init_db()
    else:
        init_db()
