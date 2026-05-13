"""ELO Rating System Implementation

This module implements the standard ELO rating system for chess,
using the "algorithm of 400" where 400 is the key constant in the calculation.
"""

class ELOCalculator:
    """Calculates ELO rating changes based on match results"""
    
    # Constants
    K_FACTOR = 32  # Standard K-factor for rating volatility
    RATING_CONSTANT = 400  # The "algorithm of 400" constant
    DEFAULT_RATING = 1600  # Starting rating for new players
    
    @staticmethod
    def calculate_expected_score(player_rating, opponent_rating):
        """
        Calculate the expected score (win probability) for a player.
        
        Formula: Expected Score = 1 / (1 + 10^((opponent_rating - player_rating) / 400))
        
        Args:
            player_rating: The player's current ELO rating
            opponent_rating: The opponent's current ELO rating
            
        Returns:
            Expected score as a float between 0 and 1
        """
        rating_difference = opponent_rating - player_rating
        expected_score = 1 / (1 + (10 ** (rating_difference / ELOCalculator.RATING_CONSTANT)))
        return expected_score
    
    @staticmethod
    def calculate_rating_change(player_rating, opponent_rating, score):
        """
        Calculate the ELO rating change for a player.
        
        Formula: Rating Change = K * (Score - Expected Score)
        
        Args:
            player_rating: The player's current ELO rating
            opponent_rating: The opponent's current ELO rating
            score: The player's score (1 for win, 0.5 for draw, 0 for loss)
            
        Returns:
            The rating change (can be positive or negative)
        """
        expected_score = ELOCalculator.calculate_expected_score(player_rating, opponent_rating)
        rating_change = ELOCalculator.K_FACTOR * (score - expected_score)
        return round(rating_change)
    
    @staticmethod
    def calculate_match_elo_changes(white_rating, black_rating, result):
        """
        Calculate ELO changes for both players after a match.
        
        Args:
            white_rating: White player's current ELO rating
            black_rating: Black player's current ELO rating
            result: Match result - 'white_win', 'black_win', or 'draw'
            
        Returns:
            Dictionary with keys:
            - 'white_change': ELO change for white player
            - 'black_change': ELO change for black player
            - 'white_new_rating': White player's new ELO rating
            - 'black_new_rating': Black player's new ELO rating
        """
        if result == 'white_win':
            white_score = 1
            black_score = 0
        elif result == 'black_win':
            white_score = 0
            black_score = 1
        elif result == 'draw':
            white_score = 0.5
            black_score = 0.5
        else:
            raise ValueError(f"Invalid result: {result}. Must be 'white_win', 'black_win', or 'draw'")
        
        white_change = ELOCalculator.calculate_rating_change(white_rating, black_rating, white_score)
        black_change = ELOCalculator.calculate_rating_change(black_rating, white_rating, black_score)
        
        return {
            'white_change': white_change,
            'black_change': black_change,
            'white_new_rating': white_rating + white_change,
            'black_new_rating': black_rating + black_change
        }


def update_player_elo(player, elo_change):
    """
    Update a player's ELO rating.
    
    Args:
        player: User object
        elo_change: Amount to change the rating by
    """
    player.elo_rating += elo_change


def record_match_with_elo(white_player, black_player, result):
    """
    Record a match and update both players' ELO ratings.
    
    Args:
        white_player: User object for white player
        black_player: User object for black player
        result: Match result - 'white_win', 'black_win', or 'draw'
        
    Returns:
        Dictionary with ELO change information
    """
    from models import db, Match
    
    # Calculate ELO changes
    elo_changes = ELOCalculator.calculate_match_elo_changes(
        white_player.elo_rating,
        black_player.elo_rating,
        result
    )
    
    # Store ELO before update
    white_elo_before = white_player.elo_rating
    black_elo_before = black_player.elo_rating
    
    # Update player ratings
    white_player.elo_rating = elo_changes['white_new_rating']
    black_player.elo_rating = elo_changes['black_new_rating']
    
    # Update match statistics
    if result == 'white_win':
        white_player.wins += 1
    elif result == 'black_win':
        black_player.wins += 1
    
    white_player.matches_played += 1
    black_player.matches_played += 1
    
    # Create match record
    match = Match(
        white_player_id=white_player.id,
        black_player_id=black_player.id,
        result=result,
        white_elo_before=white_elo_before,
        white_elo_after=white_player.elo_rating,
        black_elo_before=black_elo_before,
        black_elo_after=black_player.elo_rating
    )
    
    # Save to database
    db.session.add(match)
    db.session.commit()
    
    return elo_changes
