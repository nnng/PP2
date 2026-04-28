# Racer Game

Arcade racing game prototype built with Python + Pygame.

## Features in current build

- Multiple screens: Main Menu, Game, Game Over, Leaderboard, Settings
- Player car movement on scrolling road
- Enemy car spawning and collision loss condition
- Weighted coins (`1`, `5`, `10`) and score gain
- Dynamic difficulty scaling based on collected coins
- Obstacles and road events:
  - `pothole`
  - `oil` (reduced control)
  - `slow_zone`
  - `moving_barrier`
  - `nitro_strip`
- Power-ups (`nitro`, `shield`, `repair`) with one active at a time and timer
- HUD: score, coins, distance, remaining distance, active power-up
- Persistent settings and leaderboard (`top 10`) via JSON
- Safe spawn logic that avoids direct spawn over player lane collision zone

## Run

These instructions assume you're on Windows. Pygame provides prebuilt wheels for specific
Python versions — using Python 3.13 in a virtual environment avoids the common "build from
source" error on newer system Pythons.

1. Create and activate a Python 3.13 virtual environment (recommended):

PowerShell (recommended if you have the `py` launcher):

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Or using cmd.exe:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\activate.bat
```

If you don't have `py -3.13`, install Python 3.13 from python.org and replace `py -3.13`
with the full path to the Python 3.13 executable.

2. Upgrade packaging tools and install dependencies inside the venv:

```powershell
.venv\Scripts\python -m pip install --upgrade pip setuptools wheel
.venv\Scripts\python -m pip install -r requirements.txt
```

If installation fails with errors about building pygame (compilation / Visual Studio /
distutils), use the prebuilt wheel for pygame when possible:

```powershell
.venv\Scripts\python -m pip install pygame==2.6.1 --only-binary :all:
```

3. Run the game:

```powershell
.venv\Scripts\python main.py
```

Troubleshooting

- If pip tries to compile pygame and fails with MSVC/distutils errors, ensure you're using
  a Python version with available binary wheels (Python 3.13 is recommended on Windows).
- If you can't use Python 3.13, you can install the system dependencies described at
  https://www.pygame.org/wiki/CompileWindows (requires Visual Studio tools and SDL dev libs).
- If audio or other assets are missing, check the `assets/` folder for `.wav` files.

## Project structure

- `main.py` - entry point and screen/state management
- `game.py` - gameplay loop and runtime game session state
- `entities.py` - player, enemies, coins, obstacles, power-ups
- `mechanics.py` - spawning, difficulty scaling, road drawing, effects
- `ui.py` - UI state enum, reusable widgets, HUD rendering
- `persistence.py` - JSON load/save with fallback behavior
- `settings.json` - default gameplay and profile configuration
- `leaderboard.json` - top-10 results store
- `assets/` - reserved for images/sounds
