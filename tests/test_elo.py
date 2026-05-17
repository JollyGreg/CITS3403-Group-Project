# tests/test_elo.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import User, Match, Game, db
from app import app
from elo import record_match_with_elo

with app.app_context():

    white = User.query.filter_by(username='test_white').first()
    if not white:
        white = User(username='test_white', email='white@test.com', elo_rating=1200)
        white.set_password('test')
        db.session.add(white)
        print("Created user: test_white")

    black = User.query.filter_by(username='test_black').first()
    if not black:
        black = User(username='test_black', email='black@test.com', elo_rating=1200)
        black.set_password('test')
        db.session.add(black)
        print("Created user: test_black")

    db.session.flush()

    print(f"\nBefore:")
    print(f"  {white.username}: ELO {white.elo_rating}, W{white.wins}/L{white.losses}/D{white.draws}")
    print(f"  {black.username}: ELO {black.elo_rating}, W{black.wins}/L{black.losses}/D{black.draws}")

    result = 'black_win'  # 'white_win' | 'black_win' | 'draw'

    # Snapshot ELO BEFORE updating
    white_elo_before = white.elo_rating
    black_elo_before = black.elo_rating

    game = Game(player1_id=white.id, player2_id=black.id, status='finished')
    db.session.add(game)
    db.session.flush()

    changes = record_match_with_elo(white, black, result)

    # Now create Match with before AND after values
    match = Match(
        white_player_id=white.id,
        black_player_id=black.id,
        result=result,
        mode='1v1 Quick Match',
        white_elo_before=white_elo_before,
        white_elo_after=white.elo_rating,
        black_elo_before=black_elo_before,
        black_elo_after=black.elo_rating,
    )
    db.session.add(match)
    db.session.commit()

    print(f"\nResult: {result}")
    print(f"\nAfter:")
    print(f"  {white.username}: ELO {white.elo_rating} ({changes['white_change']:+}), W{white.wins}/L{white.losses}/D{white.draws}")
    print(f"  {black.username}: ELO {black.elo_rating} ({changes['black_change']:+}), W{black.wins}/L{black.losses}/D{black.draws}")
    print(f"\nGame ID: {game.id}, Match ID: {match.id}")
    print(f"  white_elo_before={match.white_elo_before}, white_elo_after={match.white_elo_after}")
    print(f"  black_elo_before={match.black_elo_before}, black_elo_after={match.black_elo_after}")
    print("Done — committed to database.")