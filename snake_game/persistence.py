"""Persistence module for high scores and game data."""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import shutil

from .constants import Difficulty


@dataclass
class ScoreEntry:
    """A single high score entry."""
    score: int
    timestamp: str
    difficulty: str
    grid_size: str
    max_speed: float
    snake_length: int


@dataclass
class HighScores:
    """Container for all high scores."""
    scores: List[ScoreEntry] = field(default_factory=list)
    max_entries: int = 10

    def add_score(self, entry: ScoreEntry) -> bool:
        """
        Add a new score entry.

        Returns True if the score made the high score list.
        """
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x.score, reverse=True)
        self.scores = self.scores[:self.max_entries]

        return entry in self.scores

    def get_top_scores(self, count: int = 10) -> List[ScoreEntry]:
        """Get the top N scores."""
        return self.scores[:count]

    def is_high_score(self, score: int) -> bool:
        """Check if a score would make the high score list."""
        if len(self.scores) < self.max_entries:
            return True
        return score > self.scores[-1].score


@dataclass
class GameStats:
    """Statistics about gameplay sessions."""
    games_played: int = 0
    total_score: int = 0
    total_food_eaten: int = 0
    total_time_played: int = 0
    longest_snake: int = 0


class PersistenceManager:
    """Manages saving and loading of game data."""

    def __init__(self):
        self._save_dir = self._get_save_directory()
        self._scores_file = self._save_dir / "high_scores.json"
        self._stats_file = self._save_dir / "game_stats.json"
        self._scores: Optional[HighScores] = None
        self._stats: Optional[GameStats] = None

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

    def get_save_directory(self) -> Path:
        """Get the save directory path."""
        return self._save_dir

    def load_scores(self) -> HighScores:
        """Load high scores from disk."""
        if self._scores is not None:
            return self._scores

        self._scores = HighScores()

        try:
            if self._scores_file.exists():
                with open(self._scores_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._scores = HighScores(
                    scores=[ScoreEntry(**s) for s in data.get("scores", [])],
                    max_entries=data.get("max_entries", 10)
                )
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Warning: Failed to load scores: {e}")
            self._scores = HighScores()

        return self._scores

    def save_scores(self) -> bool:
        """Save high scores to disk."""
        if self._scores is None:
            return False

        try:
            data = {
                "scores": [asdict(s) for s in self._scores.scores],
                "max_entries": self._scores.max_entries
            }
            with open(self._scores_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except IOError as e:
            print(f"Warning: Failed to save scores: {e}")
            return False

    def add_high_score(
        self,
        score: int,
        difficulty: Difficulty,
        grid_rows: int,
        grid_cols: int,
        max_speed: float,
        snake_length: int
    ) -> bool:
        """
        Add a new high score entry.

        Returns True if the score made the list.
        """
        scores = self.load_scores()

        entry = ScoreEntry(
            score=score,
            timestamp=datetime.now().isoformat(),
            difficulty=difficulty.value,
            grid_size=f"{grid_rows}x{grid_cols}",
            max_speed=max_speed,
            snake_length=snake_length
        )

        is_high = scores.add_score(entry)
        self.save_scores()
        return is_high

    def get_high_scores(self, count: int = 10) -> List[ScoreEntry]:
        """Get top scores."""
        return self.load_scores().get_top_scores(count)

    def load_stats(self) -> GameStats:
        """Load game statistics from disk."""
        if self._stats is not None:
            return self._stats

        self._stats = GameStats()

        try:
            if self._stats_file.exists():
                with open(self._stats_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._stats = GameStats(**data)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Warning: Failed to load stats: {e}")
            self._stats = GameStats()

        return self._stats

    def save_stats(self) -> bool:
        """Save game statistics to disk."""
        if self._stats is None:
            return False

        try:
            with open(self._stats_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self._stats), f, indent=2)
            return True
        except IOError as e:
            print(f"Warning: Failed to save stats: {e}")
            return False

    def update_stats(
        self,
        score: int,
        food_eaten: int,
        time_played: int,
        snake_length: int
    ) -> None:
        """Update game statistics after a session."""
        stats = self.load_stats()
        stats.games_played += 1
        stats.total_score += score
        stats.total_food_eaten += food_eaten
        stats.total_time_played += time_played
        if snake_length > stats.longest_snake:
            stats.longest_snake = snake_length
        self.save_stats()

    def clear_all_data(self) -> bool:
        """Clear all saved data."""
        try:
            for file in [self._scores_file, self._stats_file]:
                if file.exists():
                    file.unlink()
            self._scores = None
            self._stats = None
            return True
        except IOError as e:
            print(f"Warning: Failed to clear data: {e}")
            return False