"""
ELO Rating System — pure calculation, no DB access.

All database writes (Match creation, session commits) are handled
in app.py so this module stays import-free and testable in isolation.
"""

K_FACTOR = 32          # Rating volatility — standard for club-level play
RATING_CONSTANT = 400  # The classic "algorithm of 400" constant
DEFAULT_RATING = 1200  # Starting ELO for new players


def expected_score(player_rating: float, opponent_rating: float) -> float:
    """Return the expected score (win probability) for a player.

    Formula: E = 1 / (1 + 10^((opponent - player) / 400))
    """
    return 1 / (1 + 10 ** ((opponent_rating - player_rating) / RATING_CONSTANT))


def calculate_elo_changes(white_rating: float, black_rating: float, result: str) -> dict:
    """Return ELO changes for both players given a result.

    Args:
        white_rating: White player's current ELO rating.
        black_rating: Black player's current ELO rating.
        result:       'white_win' | 'black_win' | 'draw'

    Returns:
        {
            'white_change':      int,   # delta (can be negative)
            'black_change':      int,
            'white_new_rating':  int,
            'black_new_rating':  int,
        }
    """
    if result == 'white_win':
        white_score, black_score = 1.0, 0.0
    elif result == 'black_win':
        white_score, black_score = 0.0, 1.0
    elif result == 'draw':
        white_score, black_score = 0.5, 0.5
    else:
        raise ValueError(f"Invalid result '{result}'. Must be 'white_win', 'black_win', or 'draw'.")

    white_change = round(K_FACTOR * (white_score - expected_score(white_rating, black_rating)))
    black_change = round(K_FACTOR * (black_score - expected_score(black_rating, white_rating)))

    return {
        'white_change':     white_change,
        'black_change':     black_change,
        'white_new_rating': int(white_rating) + white_change,
        'black_new_rating': int(black_rating) + black_change,
    }


def record_match_with_elo(white_player, black_player, result: str) -> dict:
    """Update both players' ELO ratings and record counters in-place.

    Does NOT touch the database — call db.session.commit() in the caller.

    Args:
        white_player: User model instance (player1 / white pieces).
        black_player: User model instance (player2 / black pieces).
        result:       'white_win' | 'black_win' | 'draw'

    Returns:
        Dict with 'white_change' and 'black_change' (integer ELO deltas).
    """
    # Seed rating for brand-new players
    if white_player.elo_rating is None:
        white_player.elo_rating = DEFAULT_RATING
    if black_player.elo_rating is None:
        black_player.elo_rating = DEFAULT_RATING

    changes = calculate_elo_changes(white_player.elo_rating, black_player.elo_rating, result)

    # Apply new ratings
    white_player.elo_rating = changes['white_new_rating']
    black_player.elo_rating = changes['black_new_rating']

    # Update win / loss / draw counters
    if result == 'white_win':
        white_player.wins += 1
        black_player.losses += 1
    elif result == 'black_win':
        black_player.wins += 1
        white_player.losses += 1
    else:  # draw
        white_player.draws += 1
        black_player.draws += 1

    # Update total games played
    white_player.matches_played += 1
    black_player.matches_played += 1

    return {'white_change': changes['white_change'], 'black_change': changes['black_change']}