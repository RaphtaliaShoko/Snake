"""Food module with different food types and effects."""

import random
from typing import List, Tuple, Optional
from enum import Enum

from .constants import FoodType
from .grid import Grid


class Food:
    """
    Represents a food item on the grid.

    Different food types have different effects on the snake.
    """

    POINTS = {
        FoodType.NORMAL: 10,
        FoodType.BONUS: 50,
        FoodType.POISON: -20,
    }

    EFFECT = {
        FoodType.NORMAL: 1,
        FoodType.BONUS: 2,
        FoodType.POISON: -1,
    }

    DURATION_BONUS = {
        FoodType.NORMAL: 0,
        FoodType.BONUS: 2000,
        FoodType.POISON: 0,
    }

    SPAWN_WEIGHTS = {
        FoodType.NORMAL: 70,
        FoodType.BONUS: 20,
        FoodType.POISON: 10,
    }

    def __init__(self, food_type: FoodType, row: int, col: int):
        self.food_type = food_type
        self.row = row
        self.col = col
        self._active = True

    @property
    def position(self) -> Tuple[int, int]:
        """Get food position as (row, col)."""
        return (self.row, self.col)

    @property
    def points(self) -> int:
        """Get points awarded for eating this food."""
        return self.POINTS.get(self.food_type, 10)

    @property
    def growth_effect(self) -> int:
        """Get growth effect (positive grows, negative shrinks)."""
        return self.EFFECT.get(self.food_type, 1)

    @property
    def bonus_time(self) -> int:
        """Get bonus time duration in milliseconds."""
        return self.DURATION_BONUS.get(self.food_type, 0)

    @property
    def is_active(self) -> bool:
        """Check if food is still on the grid."""
        return self._active

    def deactivate(self) -> None:
        """Mark food as consumed."""
        self._active = False

    @staticmethod
    def get_random_type(enabled_types: Optional[List[FoodType]] = None) -> FoodType:
        """
        Get a random food type based on spawn weights.

        Args:
            enabled_types: List of allowed food types, or None for all

        Returns:
            A random FoodType
        """
        if enabled_types is None:
            enabled_types = list(FoodType)

        weights = [Food.SPAWN_WEIGHTS.get(t, 0) for t in enabled_types]
        total = sum(weights)

        if total == 0:
            return FoodType.NORMAL

        r = random.randint(1, total)
        cumulative = 0
        for ftype, weight in zip(enabled_types, weights):
            cumulative += weight
            if r <= cumulative:
                return ftype

        return FoodType.NORMAL


class FoodManager:
    """
    Manages spawning and tracking of food items on the grid.
    """

    def __init__(self, grid: Grid):
        self.grid = grid
        self._foods: List[Food] = []
        self._enabled_types: List[FoodType] = [FoodType.NORMAL, FoodType.BONUS, FoodType.POISON]

    @property
    def foods(self) -> List[Food]:
        """Get list of active food items."""
        return [f for f in self._foods if f.is_active]

    @property
    def food_count(self) -> int:
        """Get number of active food items."""
        return len(self.foods)

    def set_enabled_types(self, types: List[FoodType]) -> None:
        """Set which food types can spawn."""
        self._enabled_types = types if types else [FoodType.NORMAL]

    def spawn_food(
        self,
        occupied_positions: List[Tuple[int, int]],
        prefer_center: bool = False
    ) -> Optional[Food]:
        """
        Spawn a new food item at a random position.

        Args:
            occupied_positions: Positions to avoid
            prefer_center: If True, prefer center of grid

        Returns:
            The spawned Food or None if grid is full
        """
        food_type = Food.get_random_type(self._enabled_types)
        position = self.grid.get_random_empty_cell(occupied_positions, prefer_center)

        if position is None:
            return None

        food = Food(food_type, position[0], position[1])
        self._foods.append(food)
        return food

    def check_food_at(self, row: int, col: int) -> Optional[Food]:
        """
        Check if there's food at the specified position.

        Returns:
            The Food if found, None otherwise
        """
        for food in self._foods:
            if food.is_active and food.row == row and food.col == col:
                return food
        return None

    def remove_food(self, food: Food) -> None:
        """Remove a specific food item."""
        food.deactivate()

    def clear(self) -> None:
        """Remove all food items."""
        for food in self._foods:
            food.deactivate()
        self._foods = []

    def get_all_positions(self) -> List[Tuple[int, int]]:
        """Get all active food positions."""
        return [f.position for f in self.foods]