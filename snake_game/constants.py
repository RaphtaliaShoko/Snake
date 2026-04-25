"""Constants used throughout the Snake game."""

from enum import Enum
from typing import Final

SCREEN_WIDTH: Final[int] = 1280
SCREEN_HEIGHT: Final[int] = 720
FPS: Final[int] = 60

DEFAULT_GRID_ROWS: Final[int] = 20
DEFAULT_GRID_COLS: Final[int] = 20

CELL_PADDING: Final[float] = 2.0

MIN_GRID_SIZE: Final[int] = 10
MAX_GRID_SIZE: Final[int] = 50

MIN_SNAKE_LENGTH: Final[int] = 3
MAX_SNAKE_LENGTH: Final[int] = 50

MIN_SPEED: Final[int] = 1
MAX_SPEED: Final[int] = 30

DEFAULT_SNAKE_LENGTH: Final[int] = 3
DEFAULT_BASE_SPEED: Final[int] = 10
DEFAULT_SPEED_INCREMENT: Final[float] = 0.5

DIRECTION_DELAY_MS: Final[int] = 100


class Direction(Enum):
    """Represents the direction of snake movement."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class GameState(Enum):
    """Represents the current state of the game."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    SETTINGS = "settings"
    HIGH_SCORES = "high_scores"
    QUIT = "quit"


class WallBehavior(Enum):
    """Defines how the snake interacts with walls."""
    SOLID = "solid"
    WRAP = "wrap"


class SpeedMode(Enum):
    """Defines how speed scales during gameplay."""
    FIXED = "fixed"
    ACCELERATING = "accelerating"


class FoodType(Enum):
    """Types of food with different effects."""
    NORMAL = "normal"
    BONUS = "bonus"
    POISON = "poison"


class Difficulty(Enum):
    """Predefined difficulty levels."""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"


class Theme(Enum):
    """Available visual themes."""
    CLASSIC = "classic"
    NEON = "neon"
    COLORBLIND = "colorblind"
    MODERN = "modern"