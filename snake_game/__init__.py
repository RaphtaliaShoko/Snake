"""Snake Game Package - Entry Point Module."""

__version__ = "1.0.0"
__author__ = "Snake Game Project"
__license__ = "MIT"

from .game import Game
from .constants import GameState, Direction, Theme, Difficulty, WallBehavior, SpeedMode, FoodType

__all__ = [
    "Game",
    "GameState",
    "Direction",
    "Theme",
    "Difficulty",
    "WallBehavior",
    "SpeedMode",
    "FoodType",
]