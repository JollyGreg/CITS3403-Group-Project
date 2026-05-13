# ELO Rating System Implementation

This document describes the ELO rating system implementation for Chess Master.

## Overview

The system implements the standard ELO rating algorithm with the following parameters:

- **K-Factor**: 32 (standard volatility for all players)
- **Default Starting Rating**: 1600 
- **Rating Constant**: 400 (the "algorithm of 400")

## Formula

### Expected Score
```
Expected Score = 1 / (1 + 10^((opponent_rating - player_rating) / 400))
```

This gives the probability of a player winning against their opponent.

### Rating Change
```
Rating Change = K × (Actual Score - Expected Score)
Rating Change = 32 × (Actual Score - Expected Score)
```

Where:
- **K = 32** (constant factor)
- **Actual Score**: 1 for win, 0.5 for draw, 0 for loss

## Files

### `elo.py`
Contains the `ELOCalculator` class with the following methods:

- `calculate_expected_score(player_rating, opponent_rating)` - Calculates win probability
- `calculate_rating_change(player_rating, opponent_rating, score)` - Calculates ELO change
- `calculate_match_elo_changes(white_rating, black_rating, result)` - Calculates changes for both players

And helper functions:
- `update_player_elo(player, elo_change)` - Updates player's ELO
- `record_match_with_elo(white_player, black_player, result)` - Records match and updates both players

### `models.py` Updates
Added to the `User` model:
- `elo_rating` (default: 1600)
- `elo_history` (tracks ELO changes)

Added to the `Match` model:
- `white_elo_before`, `white_elo_after`
- `black_elo_before`, `black_elo_after`
- `result` field updated to support: 'white_win', 'black_win', 'draw'

### `app.py` Updates
Updated the `/api/game/<game_id>/end` endpoint to:
1. Accept `result` parameter (white_win, black_win, or draw)
2. Calculate ELO changes using the ELO system
3. Update both players' ratings
4. Record match with full ELO history

### `db.py` Updates
Added new commands:

```bash
# Record a test match
python db.py match <white_player> <black_player> <result>
# Example: python db.py match player1 player2 white_win

# Show player statistics
python db.py stats <username>
# Example: python db.py stats player1
```

## Usage Examples

### Recording a Match via Database
```bash
# Create two test users
python db.py test
# (Repeat to create another test user with different username)

# Record a match
python db.py match testuser1 testuser2 white_win

# Check stats
python db.py stats testuser1
```

### Recording a Match via API
Send a POST request to `/api/game/<game_id>/end` with:
```json
{
  "result": "white_win"  // or "black_win" or "draw"
}
```

Response will include ELO changes:
```json
{
  "success": true,
  "elo_changes": {
    "white_change": 12,
    "black_change": -12,
    "white_new_rating": 1612,
    "black_new_rating": 1588
  }
}
```

## Example Scenarios

### Scenario 1: Higher Rated Player Wins
- White: 1600 ELO
- Black: 1400 ELO
- Result: White wins
- Expected Score for White: ~76% (0.76)
- Rating Change: 32 × (1 - 0.76) = +7.68 ≈ +8
- White's new rating: 1608
- Black's new rating: 1392

### Scenario 2: Lower Rated Player Wins (Upset)
- White: 1400 ELO
- Black: 1600 ELO
- Result: White wins
- Expected Score for White: ~24% (0.24)
- Rating Change: 32 × (1 - 0.24) = +24.32 ≈ +24
- White's new rating: 1424
- Black's new rating: 1576

### Scenario 3: Draw Between Equal Players
- White: 1600 ELO
- Black: 1600 ELO
- Result: Draw
- Expected Score for both: ~50% (0.5)
- Rating Change: 32 × (0.5 - 0.5) = 0
- Both ratings unchanged

## Database Schema

The Match table now includes:
- `result`: VARCHAR(50) - 'white_win', 'black_win', or 'draw'
- `white_elo_before`: INTEGER - White player's ELO before the match
- `white_elo_after`: INTEGER - White player's ELO after the match
- `black_elo_before`: INTEGER - Black player's ELO before the match
- `black_elo_after`: INTEGER - Black player's ELO after the match

## Testing

To verify the implementation:

```bash
# Initialize database
python db.py

# Create test user
python db.py test

# Create another test user (manual edit of db or create via UI)

# Record a match
python db.py match testuser testuser2 white_win

# View stats
python db.py stats testuser
```

Expected output shows ELO rating changes based on the algorithm.
