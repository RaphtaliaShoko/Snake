"""Grid module for managing the game board."""

from typing import List, Tuple, Optional
import random

from .constants import WallBehavior


class Grid:
    """
    Manages the game grid and cell calculations.

    The grid is a 2D coordinate system where (0, 0) is the top-left cell.
    """

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self._obstacles: List[Tuple[int, int]] = []
        self._obstacle_active = False

    @property
    def size(self) -> int:
        """Total number of cells in the grid."""
        return self.rows * self.cols

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if a position is within grid bounds."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def wrap_position(self, row: int, col: int) -> Tuple[int, int]:
        """
        Apply wrap-around logic to a position.
        Positions that go off one edge appear on the opposite edge.
        """
        new_row = row % self.rows
        new_col = col % self.cols
        return new_row, new_col

    def resolve_wall_collision(
        self, row: int, col: int, behavior: WallBehavior
    ) -> Optional[Tuple[int, int]]:
        """
        Handle wall collision based on the specified behavior.

        Returns the new position or None if collision should end the game.
        """
        if behavior == WallBehavior.WRAP:
            return self.wrap_position(row, col)
        elif behavior == WallBehavior.SOLID:
            if not self.is_valid_position(row, col):
                return None
            return row, col
        return row, col

    def get_random_empty_cell(
        self,
        occupied_positions: List[Tuple[int, int]],
        prefer_center: bool = False
    ) -> Optional[Tuple[int, int]]:
        """
        Get a random empty cell not occupied by the snake or obstacles.

        Args:
            occupied_positions: List of (row, col) positions to avoid
            prefer_center: If True, prioritize cells near the center

        Returns:
            A random empty position or None if grid is full
        """
        occupied_set = set(occupied_positions)
        if self._obstacle_active:
            occupied_set.update(self._obstacles)

        available: List[Tuple[int, int]] = []
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in occupied_set:
                    available.append((r, c))

        if not available:
            return None

        if prefer_center:
            center_row = self.rows // 2
            center_col = self.cols // 2
            available.sort(
                key=lambda pos: abs(pos[0] - center_row) + abs(pos[1] - center_col)
            )
            return random.choice(available[:len(available) // 2])

        return random.choice(available)

    def generate_obstacles(self, count: int) -> List[Tuple[int, int]]:
        """
        Generate random obstacle positions avoiding grid edges and center.

        Returns:
            List of obstacle positions as (row, col) tuples
        """
        obstacles: List[Tuple[int, int]] = []
        margin = 2
        center_row = self.rows // 2
        center_col = self.cols // 2

        attempts = 0
        max_attempts = count * 10

        while len(obstacles) < count and attempts < max_attempts:
            attempts += 1
            row = random.randint(margin, self.rows - 1 - margin)
            col = random.randint(margin, self.cols - 1 - margin)

            if abs(row - center_row) < 3 and abs(col - center_col) < 3:
                continue

            if (row, col) not in obstacles:
                obstacles.append((row, col))

        return obstacles

    def set_obstacles(self, obstacles: List[Tuple[int, int]]) -> None:
        """Set obstacle positions and activate them."""
        self._obstacles = list(obstacles)
        self._obstacle_active = True

    def clear_obstacles(self) -> None:
        """Remove all obstacles from the grid."""
        self._obstacles = []
        self._obstacle_active = False

    def is_obstacle(self, row: int, col: int) -> bool:
        """Check if a cell contains an obstacle."""
        return (row, col) in self._obstacles

    def get_obstacles(self) -> List[Tuple[int, int]]:
        """Get a copy of the current obstacle positions."""
        return list(self._obstacles)