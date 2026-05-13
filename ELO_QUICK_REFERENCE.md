# ELO System - Quick Reference

## Quick Start

### Test the System
```bash
# 1. Initialize fresh database
python db.py reset

# 2. Create test user
python db.py test

# 3. Create another user via UI or duplicate testuser

# 4. Record a match
python db.py match testuser testuser2 white_win

# 5. Check results
python db.py stats testuser
```

## Using the API

### End a Game with ELO
```bash
POST /api/game/<game_id>/end
Content-Type: application/json

{
  "result": "white_win"
}
```

### Response
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

## Key Constants

| Parameter | Value | Description |
|-----------|-------|-------------|
| K-Factor | 32 | How much rating changes per match |
| Starting Rating | 1600 | New player's initial ELO |
| Rating Constant | 400 | Used in probability calculation |

## Database Commands

```bash
# Record match
python db.py match <white_player> <black_player> <result>
python db.py match alice bob white_win

# View stats
python db.py stats <username>
python db.py stats alice

# Initialize DB
python db.py

# Reset DB (WARNING: deletes all data)
python db.py reset

# Create test user
python db.py test
```

## Result Types
- `white_win` - White player won
- `black_win` - Black player won
- `draw` - Game ended in draw

## Match Model Fields
```python
Match.result              # 'white_win', 'black_win', or 'draw'
Match.white_elo_before   # White's ELO at start of match
Match.white_elo_after    # White's ELO at end of match
Match.black_elo_before   # Black's ELO at start of match
Match.black_elo_after    # Black's ELO at end of match
```

## User Model Fields
```python
User.elo_rating          # Current ELO rating (default: 1600)
User.elo_history         # JSON array of ELO changes (optional)
User.wins                # Total wins
User.matches_played      # Total matches
User.win_rate            # Calculated win percentage
```

## Common Questions

**Q: Why did my rating go up even though I lost?**
A: If you were heavily favored (much higher rating than opponent), the loss is expected and only drops a few points.

**Q: Why does beating a higher-rated player give more points?**
A: The formula rewards upsets - beating a favored opponent is worth more than beating a weaker player.

**Q: Can I change K-Factor?**
A: Yes, edit `elo.py` line 11: `K_FACTOR = 32`

**Q: Can I change the starting rating?**
A: Yes, edit `elo.py` line 13: `DEFAULT_RATING = 1600`

Or in `models.py` line 24: `elo_rating = db.Column(db.Integer, default=1600)`
