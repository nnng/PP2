# Snake Game — TSIS4

Project implementing a modular Snake game using pygame with optional PostgreSQL leaderboard integration.

## Status

Implemented:

- Grid-based Snake movement, menu, name entry, HUD (score/level)
- Food spawning avoiding snake
- Level progression and speed increase
- PostgreSQL client (`db.py`) and `save_score.py` CLI
- Game saves session to DB after Game Over (requires DB user rights)

Partially implemented / TODO:

- Food weights and disappearing food: basic food exists; advanced types to add
- Poison food: not yet implemented
- Power-ups (speed boost, slow motion, shield): not yet implemented
- Obstacles (level >=3): not yet implemented
- Leaderboard UI inside game: not yet implemented (use `save_score.py` to verify DB)
- Settings screen UI: not yet implemented

## Files

- `main.py` — entry point and screens
- `game.py` — game loop and logic
- `snake.py` — snake entity
- `food.py` — food spawning (basic)
- `db.py` — PostgreSQL client
- `save_score.py` — CLI to test saving scores
- `settings.py`, `settings.json` — settings manager and defaults
- `ui.py` — simple drawing helpers
- `requirements.txt` — dependencies
- `README_DB.md` — instructions to create DB/schema

## Quick start (recommended: use Python 3.13)

Windows (PowerShell):

```powershell
# create and activate venv
cd C:\PP2\PP2\TSISTWO\SnakeGame
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
# upgrade pip and install deps
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# optionally set DATABASE_URL (or edit settings.json)
$env:DATABASE_URL = "postgresql://snake_user:your_password@localhost:5432/snake_db"
# run game
py -3.13 main.py
```

macOS / Linux (bash/zsh):

```bash
cd /path/to/SnakeGame
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
export DATABASE_URL="postgresql://snake_user:your_password@localhost:5432/snake_db"
python main.py
```

Running in-editor (VS Code):

- Open the folder in VS Code.
- Select the Python interpreter inside `.venv` (Python 3.13).
- Open a terminal and activate the venv (see above commands), then run `py -3.13 main.py`.

## Database setup

See `README_DB.md` for step-by-step SQL and pgAdmin instructions.

## Notes about permissions

If `save_score.py` or the game prints errors like "need to be owner of table" or "no access to table", run the `ALTER TABLE ... OWNER TO snake_user;` or grant the required permissions in the DB as described in `README_DB.md`.

## Next steps I can implement for you

- Add poison food and power-ups (timed effects)
- Add obstacles spawning from level 3 with flood-fill reachability check
- Implement in-game Leaderboard screen showing top-10
- Implement Settings and Leaderboard UI screens

Tell me which of these to implement next and I will continue.
