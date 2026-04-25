"""Settings module for game configuration with persistence."""

import json
import os
import shutil
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from .constants import (
    DEFAULT_GRID_ROWS, DEFAULT_GRID_COLS,
    DEFAULT_SNAKE_LENGTH, DEFAULT_BASE_SPEED,
    DEFAULT_SPEED_INCREMENT, WallBehavior, SpeedMode, Difficulty, Theme
)


@dataclass
class GameSettings:
    """Main settings container for the Snake game."""

    grid_rows: int = DEFAULT_GRID_ROWS
    grid_cols: int = DEFAULT_GRID_COLS
    initial_snake_length: int = DEFAULT_SNAKE_LENGTH
    base_speed: int = DEFAULT_BASE_SPEED
    speed_increment: float = DEFAULT_SPEED_INCREMENT
    speed_mode: str = SpeedMode.ACCELERATING.value
    wall_behavior: str = WallBehavior.SOLID.value
    enable_obstacles: bool = False
    obstacle_count: int = 5
    difficulty: str = Difficulty.NORMAL.value
    theme: str = Theme.CLASSIC.value
    music_volume: float = 0.5
    sfx_volume: float = 0.7
    gamepad_enabled: bool = True
    font_scale: float = 1.0

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate all settings values.
        Returns (is_valid, error_message).
        """
        from .constants import MIN_GRID_SIZE, MAX_GRID_SIZE, MIN_SNAKE_LENGTH, MAX_SNAKE_LENGTH, MIN_SPEED, MAX_SPEED

        if not (MIN_GRID_SIZE <= self.grid_rows <= MAX_GRID_SIZE):
            return False, f"Grid rows must be between {MIN_GRID_SIZE} and {MAX_GRID_SIZE}"

        if not (MIN_GRID_SIZE <= self.grid_cols <= MAX_GRID_SIZE):
            return False, f"Grid cols must be between {MIN_GRID_SIZE} and {MAX_GRID_SIZE}"

        max_snake = min(self.grid_rows, self.grid_cols) ** 2
        if not (MIN_SNAKE_LENGTH <= self.initial_snake_length <= min(MAX_SNAKE_LENGTH, max_snake)):
            return False, f"Initial snake length must be between {MIN_SNAKE_LENGTH} and {min(MAX_SNAKE_LENGTH, max_snake)}"

        if not (MIN_SPEED <= self.base_speed <= MAX_SPEED):
            return False, f"Base speed must be between {MIN_SPEED} and {MAX_SPEED}"

        if not (0 <= self.music_volume <= 1):
            return False, "Music volume must be between 0 and 1"

        if not (0 <= self.sfx_volume <= 1):
            return False, "SFX volume must be between 0 and 1"

        if not (0.5 <= self.font_scale <= 2.0):
            return False, "Font scale must be between 0.5 and 2.0"

        return True, None

    @classmethod
    def from_dict(cls, data: dict) -> "GameSettings":
        """Create settings from a dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


class SettingsManager:
    """Manages loading, saving, and applying game settings."""

    def __init__(self):
        self.settings = GameSettings()
        self._save_dir = self._get_save_directory()
        self._settings_file = self._save_dir / "settings.json"

    def _get_save_directory(self) -> Path:
        """Get the platform-appropriate save directory."""
        if os.name == "nt":
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif os.name == "posix":
            if os.environ.get("XDG_DATA_HOME"):
                base = Path(os.environ["XDG_DATA_HOME"])
            else:
                base = Path.home() / ".local" / "share"
        else:
            base = Path.home() / ".snake_game"

        save_dir = base / "SnakeGame"
        save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir

    def load(self) -> bool:
        """Load settings from disk. Returns True if successful."""
        try:
            if self._settings_file.exists():
                with open(self._settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.settings = GameSettings.from_dict(data)
                return True
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Warning: Failed to load settings: {e}")
        return False

    def save(self) -> bool:
        """Save settings to disk. Returns True if successful."""
        try:
            with open(self._settings_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.settings), f, indent=2)
            return True
        except IOError as e:
            print(f"Warning: Failed to save settings: {e}")
            return False

    def apply_difficulty(self, difficulty: Difficulty) -> None:
        """Apply preset difficulty settings."""
        presets = {
            Difficulty.EASY: {
                "grid_rows": 15,
                "grid_cols": 15,
                "initial_snake_length": 3,
                "base_speed": 6,
                "speed_increment": 0.2,
                "speed_mode": SpeedMode.FIXED.value,
                "wall_behavior": WallBehavior.WRAP.value,
                "enable_obstacles": False,
                "obstacle_count": 0,
            },
            Difficulty.NORMAL: {
                "grid_rows": 20,
                "grid_cols": 20,
                "initial_snake_length": 3,
                "base_speed": 10,
                "speed_increment": 0.5,
                "speed_mode": SpeedMode.ACCELERATING.value,
                "wall_behavior": WallBehavior.SOLID.value,
                "enable_obstacles": False,
                "obstacle_count": 0,
            },
            Difficulty.HARD: {
                "grid_rows": 25,
                "grid_cols": 25,
                "initial_snake_length": 3,
                "base_speed": 15,
                "speed_increment": 1.0,
                "speed_mode": SpeedMode.ACCELERATING.value,
                "wall_behavior": WallBehavior.SOLID.value,
                "enable_obstacles": True,
                "obstacle_count": 10,
            },
        }
        if difficulty in presets:
            for key, value in presets[difficulty].items():
                setattr(self.settings, key, value)
            self.settings.difficulty = difficulty.value

    def clear_saved_data(self) -> bool:
        """Clear all saved data including settings and high scores."""
        try:
            if self._settings_file.exists():
                self._settings_file.unlink()
            scores_file = self._save_dir / "high_scores.json"
            if scores_file.exists():
                scores_file.unlink()
            self.settings = GameSettings()
            return True
        except IOError as e:
            print(f"Warning: Failed to clear saved data: {e}")
            return False