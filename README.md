# Snake Game

A modern, feature-rich implementation of the classic Snake arcade game written in Python 3.10+.

## Features

- **Customizable Gameplay**: Adjust grid size, speed, obstacles, and more
- **Multiple Food Types**: Normal, bonus, and poison food with different effects
- **Visual Themes**: Classic, Neon, and Colorblind-friendly themes
- **Procedural Audio**: No external files needed - all sounds generated in code
- **High Score Persistence**: Save and track your best scores across sessions
- **Gamepad Support**: Play with keyboard or a connected gamepad
- **Smooth Animations**: 60 FPS rendering with particle effects
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

Start the game by running:
```bash
python run_game.py
```

Or use module syntax:
```bash
python -m snake_game.run
```

## Controls

### Keyboard
- **Arrow Keys** or **WASD**: Move the snake
- **P** or **ESC**: Pause/Resume
- **SPACE** or **ENTER**: Select/Restart
- **ESC**: Go back/Quit

### Gamepad (if connected)
- **D-Pad** or **Left Stick**: Move
- **A Button**: Select/Start
- **Start**: Pause
- **B Button**: Back

## Settings

### Game Parameters
- **Grid Size**: 15x15, 20x20, 25x25, 30x30
- **Initial Snake Length**: 3-10 segments
- **Base Speed**: 1-20 (higher is faster)
- **Speed Mode**: Fixed or Accelerating
- **Wall Behavior**: Solid (die) or Wrap-around
- **Obstacles**: Enable random obstacles with adjustable count

### Difficulty Presets
- **Easy**: Smaller grid, slower speed, wrap walls
- **Normal**: Balanced gameplay (default)
- **Hard**: Larger grid, faster speed, obstacles

### Visual Options
- **Theme**: Classic, Neon, Colorblind
- **Font Scale**: 0.5x - 2.0x
- **Music Volume**: 0-100%
- **SFX Volume**: 0-100%

## Project Structure

```
snake_game/
├── __init__.py          # Package initialization
├── constants.py         # Game constants and enumerations
├── settings.py          # Configuration management
├── grid.py              # Grid/board management
├── snake.py             # Snake entity with movement logic
├── food.py              # Food system with multiple types
├── theme.py             # Visual theme definitions
├── renderer.py          # Rendering and visual effects
├── audio.py             # Procedural audio generation
├── input_handler.py     # Keyboard and gamepad input
├── persistence.py       # High scores and stats
├── ui.py                # Menu and interface management
├── game.py              # Main game logic
└── tests/
    └── test_core.py     # Unit tests
```

## Food Types

| Type | Color | Effect | Points |
|------|-------|--------|--------|
| Normal | Red | Grow +1 | 10 |
| Bonus | Gold | Grow +2 | 50 |
| Poison | Purple | Shrink -1 | -20 |

## File Locations

Save data is stored in platform-specific locations:
- **Windows**: `%APPDATA%\SnakeGame\`
- **Linux/macOS**: `~/.local/share/SnakeGame/`

Contains:
- `settings.json`: Game settings
- `high_scores.json`: High scores
- `game_stats.json`: Game statistics

## Running Tests

Execute the test suite:
```bash
python -m pytest snake_game/tests/test_core.py
```

Or run the verification script:
```bash
python verify_run.py
```

## Extending the Game

### Adding New Food Types

1. Add the food type to `constants.py`:
```python
class FoodType(Enum):
    NORMAL = "normal"
    BONUS = "bonus"
    POISON = "poison"
    NEW_TYPE = "new_type"  # Add here
```

2. Update `food.py` to handle the new type:
```python
POINTS = {
    FoodType.NORMAL: 10,
    FoodType.BONUS: 50,
    FoodType.POISON: -20,
    FoodType.NEW_TYPE: 25,  # Add points
}

EFFECT = {
    FoodType.NORMAL: 1,
    FoodType.BONUS: 2,
    FoodType.POISON: -1,
    FoodType.NEW_TYPE: 3,  # Add effect
}
```

3. Update `renderer.py` for visual appearance:
```python
food_colors = {
    FoodType.NORMAL: colors.food_normal,
    FoodType.BONUS: colors.food_bonus,
    FoodType.POISON: colors.food_poison,
    FoodType.NEW_TYPE: (128, 128, 255),  # Add color
}
```

### Adding New Themes

1. Define colors in `theme.py`:
```python
Theme.NEW_THEME: GameTheme(
    name="New Theme",
    colors=ThemeColors(
        background=(...),
        # ... all colors ...
    ),
    sounds=ThemeSounds(...),
)
```

2. Register the theme in `constants.py`:
```python
class Theme(Enum):
    CLASSIC = "classic"
    NEON = "neon"
    COLORBLIND = "colorblind"
    NEW_THEME = "new_theme"  # Add here
```

### Adding Power-ups

Create a new power-up class that extends the food system:
```python
class PowerUp:
    def __init__(self, row, col, duration):
        self.row = row
        self.col = col
        self.duration = duration

    def apply(self, game):
        # Modify game state
        pass

    def remove(self, game):
        # Restore original state
        pass
```

## License

MIT License

Copyright (c) 2024 Snake Game Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.