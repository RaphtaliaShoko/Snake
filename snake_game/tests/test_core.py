"""Unit tests for core game logic."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from snake_game.grid import Grid
from snake_game.snake import Snake
from snake_game.food import Food, FoodManager, FoodType
from snake_game.constants import Direction, WallBehavior, SpeedMode, Theme, Difficulty


class TestGrid(unittest.TestCase):
    """Tests for the Grid class."""

    def setUp(self):
        self.grid = Grid(20, 20)

    def test_grid_initialization(self):
        """Test grid is created with correct dimensions."""
        self.assertEqual(self.grid.rows, 20)
        self.assertEqual(self.grid.cols, 20)
        self.assertEqual(self.grid.size, 400)

    def test_is_valid_position(self):
        """Test position validation."""
        self.assertTrue(self.grid.is_valid_position(0, 0))
        self.assertTrue(self.grid.is_valid_position(19, 19))
        self.assertFalse(self.grid.is_valid_position(-1, 0))
        self.assertFalse(self.grid.is_valid_position(0, -1))
        self.assertFalse(self.grid.is_valid_position(20, 0))
        self.assertFalse(self.grid.is_valid_position(0, 20))

    def test_wrap_position(self):
        """Test wrap-around logic."""
        self.assertEqual(self.grid.wrap_position(0, 0), (0, 0))
        self.assertEqual(self.grid.wrap_position(20, 0), (0, 0))
        self.assertEqual(self.grid.wrap_position(0, 20), (0, 0))
        self.assertEqual(self.grid.wrap_position(-1, 0), (19, 0))
        self.assertEqual(self.grid.wrap_position(0, -1), (0, 19))
        self.assertEqual(self.grid.wrap_position(21, 21), (1, 1))

    def test_resolve_wall_collision_solid(self):
        """Test solid wall behavior."""
        result = self.grid.resolve_wall_collision(5, 5, WallBehavior.SOLID)
        self.assertEqual(result, (5, 5))

        result = self.grid.resolve_wall_collision(-1, 5, WallBehavior.SOLID)
        self.assertIsNone(result)

        result = self.grid.resolve_wall_collision(5, -1, WallBehavior.SOLID)
        self.assertIsNone(result)

        result = self.grid.resolve_wall_collision(20, 5, WallBehavior.SOLID)
        self.assertIsNone(result)

    def test_resolve_wall_collision_wrap(self):
        """Test wrap wall behavior."""
        result = self.grid.resolve_wall_collision(5, 5, WallBehavior.WRAP)
        self.assertEqual(result, (5, 5))

        result = self.grid.resolve_wall_collision(-1, 5, WallBehavior.WRAP)
        self.assertEqual(result, (19, 5))

        result = self.grid.resolve_wall_collision(5, -1, WallBehavior.WRAP)
        self.assertEqual(result, (5, 19))

        result = self.grid.resolve_wall_collision(20, 5, WallBehavior.WRAP)
        self.assertEqual(result, (0, 5))

    def test_get_random_empty_cell(self):
        """Test random empty cell selection."""
        occupied = [(0, 0), (1, 1), (2, 2)]
        cell = self.grid.get_random_empty_cell(occupied)
        self.assertIsNotNone(cell)
        self.assertNotIn(cell, occupied)

        all_positions = [(r, c) for r in range(20) for c in range(20)]
        cell = self.grid.get_random_empty_cell(all_positions)
        self.assertIsNone(cell)

    def test_obstacle_operations(self):
        """Test obstacle setting and checking."""
        obstacles = [(5, 5), (10, 10), (15, 15)]
        self.grid.set_obstacles(obstacles)

        self.assertTrue(self.grid.is_obstacle(5, 5))
        self.assertTrue(self.grid.is_obstacle(10, 10))
        self.assertFalse(self.grid.is_obstacle(0, 0))

        self.grid.clear_obstacles()
        self.assertFalse(self.grid.is_obstacle(5, 5))


class TestSnake(unittest.TestCase):
    """Tests for the Snake class."""

    def setUp(self):
        self.grid = Grid(20, 20)
        self.snake = Snake(10, 10, 3, Direction.RIGHT)

    def test_snake_initialization(self):
        """Test snake is created correctly."""
        self.assertEqual(self.snake.length, 3)
        self.assertEqual(self.snake.head, (10, 10))
        self.assertEqual(self.snake.direction, Direction.RIGHT)

    def test_snake_body_positions(self):
        """Test snake body segments are positioned correctly."""
        body = self.snake.body
        self.assertEqual(len(body), 3)
        self.assertEqual(body[0], (10, 10))
        self.assertEqual(body[1], (10, 9))
        self.assertEqual(body[2], (10, 8))

    def test_set_direction(self):
        """Test direction changes."""
        self.snake.set_direction(Direction.UP)
        self.snake.update(self.grid, WallBehavior.SOLID)
        self.assertEqual(self.snake.direction, Direction.UP)

    def test_set_direction_prevents_180_turn(self):
        """Test that 180 degree turns are prevented."""
        snake = Snake(10, 10, 3, Direction.RIGHT)
        snake.set_direction(Direction.LEFT)
        self.assertEqual(snake.direction, Direction.RIGHT)

    def test_grow(self):
        """Test snake growth."""
        self.snake.grow(2)
        for _ in range(3):
            self.snake.update(self.grid, WallBehavior.SOLID)
        self.assertEqual(self.snake.length, 5)

    def test_shrink(self):
        """Test snake shrinking."""
        initial_length = self.snake.length
        self.snake.shrink(1)
        self.assertEqual(self.snake.length, initial_length - 1)

        self.snake.shrink(10)
        self.assertEqual(self.snake.length, 1)

    def test_update_movement(self):
        """Test snake movement updates."""
        initial_head = self.snake.head
        self.snake.update(self.grid, WallBehavior.SOLID)
        new_head = self.snake.head

        self.assertEqual(new_head[0], initial_head[0])
        self.assertEqual(new_head[1], initial_head[1] + 1)

    def test_update_and_body_integrity(self):
        """Test that update maintains snake body integrity."""
        snake = Snake(5, 5, 3, Direction.RIGHT)
        snake.update(self.grid, WallBehavior.SOLID)
        snake.set_direction(Direction.UP)
        snake.update(self.grid, WallBehavior.SOLID)
        self.assertEqual(snake.length, 3)

    def test_reset(self):
        """Test snake reset functionality."""
        self.snake.grow(5)
        self.snake.update(self.grid, WallBehavior.SOLID)

        self.snake.reset(5, 5, 4, Direction.UP)

        self.assertEqual(self.snake.length, 4)
        self.assertEqual(self.snake.head, (5, 5))
        self.assertEqual(self.snake.direction, Direction.UP)


class TestFood(unittest.TestCase):
    """Tests for the Food classes."""

    def setUp(self):
        self.grid = Grid(20, 20)
        self.food_manager = FoodManager(self.grid)

    def test_food_creation(self):
        """Test food creation."""
        food = Food(FoodType.NORMAL, 5, 5)
        self.assertEqual(food.position, (5, 5))
        self.assertEqual(food.food_type, FoodType.NORMAL)
        self.assertTrue(food.is_active)

    def test_food_points(self):
        """Test food point values."""
        self.assertEqual(Food(FoodType.NORMAL, 0, 0).points, 10)
        self.assertEqual(Food(FoodType.BONUS, 0, 0).points, 50)
        self.assertEqual(Food(FoodType.POISON, 0, 0).points, -20)

    def test_food_growth_effect(self):
        """Test food growth effects."""
        self.assertEqual(Food(FoodType.NORMAL, 0, 0).growth_effect, 1)
        self.assertEqual(Food(FoodType.BONUS, 0, 0).growth_effect, 2)
        self.assertEqual(Food(FoodType.POISON, 0, 0).growth_effect, -1)

    def test_food_deactivation(self):
        """Test food deactivation."""
        food = Food(FoodType.NORMAL, 5, 5)
        food.deactivate()
        self.assertFalse(food.is_active)

    def test_food_manager_spawn(self):
        """Test food spawning."""
        occupied = [(10, 10), (10, 9), (10, 8)]
        food = self.food_manager.spawn_food(occupied)

        self.assertIsNotNone(food)
        self.assertNotIn(food.position, occupied)

    def test_food_manager_check_food_at(self):
        """Test checking food at position."""
        food = Food(FoodType.NORMAL, 5, 5)
        self.food_manager._foods.append(food)

        result = self.food_manager.check_food_at(5, 5)
        self.assertEqual(result, food)

        result = self.food_manager.check_food_at(0, 0)
        self.assertIsNone(result)

    def test_food_manager_remove(self):
        """Test food removal."""
        food = Food(FoodType.NORMAL, 5, 5)
        self.food_manager._foods.append(food)

        self.assertEqual(self.food_manager.food_count, 1)
        self.food_manager.remove_food(food)
        self.assertEqual(self.food_manager.food_count, 0)


class TestSettings(unittest.TestCase):
    """Tests for settings validation."""

    def test_game_settings_validation(self):
        """Test settings validation."""
        from snake_game.settings import GameSettings

        settings = GameSettings()
        is_valid, error = settings.validate()
        self.assertTrue(is_valid)
        self.assertIsNone(error)

        settings.grid_rows = 5
        is_valid, error = settings.validate()
        self.assertFalse(is_valid)
        self.assertIn("Grid rows", error)

        settings.grid_rows = 20
        settings.music_volume = 1.5
        is_valid, error = settings.validate()
        self.assertFalse(is_valid)
        self.assertIn("volume", error)

    def test_difficulty_presets(self):
        """Test difficulty preset application."""
        from snake_game.settings import SettingsManager

        manager = SettingsManager()
        manager.apply_difficulty(Difficulty.EASY)

        self.assertEqual(manager.settings.base_speed, 6)
        self.assertEqual(manager.settings.grid_rows, 15)

        manager.apply_difficulty(Difficulty.HARD)

        self.assertEqual(manager.settings.base_speed, 15)
        self.assertEqual(manager.settings.enable_obstacles, True)


if __name__ == "__main__":
    unittest.main()