"""Snake entity module with movement and collision logic."""

from typing import List, Tuple, Optional, Deque
from collections import deque

from .constants import Direction, WallBehavior
from .grid import Grid


class Snake:
    """
    Represents the snake entity with body segments and movement logic.

    The snake consists of a head position followed by body segments.
    Movement is controlled by changing direction, which is applied
    when update() is called.
    """

    def __init__(
        self,
        head_row: int,
        head_col: int,
        initial_length: int = 3,
        direction: Direction = Direction.RIGHT
    ):
        self._body: Deque[Tuple[int, int]] = deque()
        self._direction = direction
        self._next_direction: Optional[Direction] = None
        self._grow_pending: int = 0

        for i in range(initial_length):
            self._body.append((head_row, head_col - i))

        self._head_row = head_row
        self._head_col = head_col

    @property
    def head(self) -> Tuple[int, int]:
        """Get the head position."""
        return self._body[0]

    @property
    def body(self) -> List[Tuple[int, int]]:
        """Get a list of all body segment positions (head first)."""
        return list(self._body)

    @property
    def length(self) -> int:
        """Get current snake length."""
        return len(self._body)

    @property
    def direction(self) -> Direction:
        """Get current movement direction."""
        return self._direction

    def set_direction(self, direction: Direction) -> None:
        """
        Set the next direction to move.
        Prevents 180-degree turns (can't go directly backwards).
        """
        if direction is None:
            return

        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }

        if direction != opposite_directions.get(self._direction):
            self._next_direction = direction

    def grow(self, amount: int = 1) -> None:
        """Schedule growth for the next update."""
        self._grow_pending += amount

    def shrink(self, amount: int = 1) -> None:
        """Remove segments from the tail."""
        for _ in range(min(amount, len(self._body) - 1)):
            self._body.pop()

    def update(self, grid: Grid, wall_behavior: WallBehavior) -> bool:
        """
        Update snake position by one cell.

        Args:
            grid: The game grid for wrap collision handling
            wall_behavior: How to handle wall collisions

        Returns:
            True if move was successful, False if snake died
        """
        if self._next_direction is not None:
            self._direction = self._next_direction
            self._next_direction = None

        dx, dy = self._direction.value
        new_head_row = self._head_row + dy
        new_head_col = self._head_col + dx

        result = grid.resolve_wall_collision(
            new_head_row, new_head_col, wall_behavior
        )

        if result is None:
            return False

        self._head_row, self._head_col = result

        if (self._head_row, self._head_col) in self._body:
            return False

        self._body.appendleft((self._head_row, self._head_col))

        if self._grow_pending > 0:
            self._grow_pending -= 1
        else:
            self._body.pop()

        return True

    def check_self_collision(self) -> bool:
        """
        Check if the head collides with any body segment (excluding the head itself).

        Returns:
            True if collision detected
        """
        head = self.head
        body_segments = list(self._body)[1:]
        return any(seg == head for seg in body_segments)

    def check_obstacle_collision(self, obstacles: List[Tuple[int, int]]) -> bool:
        """
        Check if the head collides with any obstacle.

        Returns:
            True if collision detected
        """
        return self.head in obstacles

    def check_collision(
        self,
        grid: Grid,
        wall_behavior: WallBehavior,
        obstacles: List[Tuple[int, int]]
    ) -> Tuple[bool, str]:
        """
        Check all collision types.

        Returns:
            Tuple of (collision_occurred, collision_type)
        """
        if self.check_self_collision():
            return True, "self"

        if self.check_obstacle_collision(obstacles):
            return True, "obstacle"

        return False, ""

    def reset(
        self,
        head_row: int,
        head_col: int,
        initial_length: int = 3,
        direction: Direction = Direction.RIGHT
    ) -> None:
        """Reset the snake to initial state."""
        self._body = deque()
        self._direction = direction
        self._next_direction = None
        self._grow_pending = 0

        for i in range(initial_length):
            self._body.append((head_row, head_col - i))

        self._head_row = head_row
        self._head_col = head_col

    def get_direction_vector(self) -> Tuple[int, int]:
        """Get the current direction as a vector."""
        return self._direction.value