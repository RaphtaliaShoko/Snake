#!/usr/bin/env python3
"""
Verification script to ensure the game can be imported and basic components work.

Run this to verify the game is correctly installed:
    python verify_run.py

Expected output: "VERIFY_OK"
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verify_imports():
    """Verify all modules can be imported."""
    print("Verifying imports...")
    try:
        from snake_game import constants
        from snake_game import settings
        from snake_game import grid
        from snake_game import snake
        from snake_game import food
        from snake_game import theme
        from snake_game import renderer
        from snake_game import audio
        from snake_game import input_handler
        from snake_game import persistence
        from snake_game import ui
        from snake_game import game
        print("  All imports successful")
        return True
    except ImportError as e:
        print(f"  Import failed: {e}")
        return False


def verify_core_logic():
    """Verify core game logic works."""
    print("Verifying core logic...")
    try:
        from snake_game.grid import Grid
        from snake_game.snake import Snake
        from snake_game.food import FoodManager, FoodType
        from snake_game.constants import Direction, WallBehavior

        grid = Grid(20, 20)
        assert grid.size == 400, "Grid size mismatch"

        assert grid.is_valid_position(10, 10), "Valid position check failed"
        assert not grid.is_valid_position(25, 10), "Invalid position check failed"

        assert grid.wrap_position(20, 10) == (0, 10), "Wrap position failed"

        snake = Snake(10, 10, 3, Direction.RIGHT)
        assert snake.length == 3, "Snake length mismatch"
        assert snake.head == (10, 10), "Snake head position mismatch"

        snake.set_direction(Direction.UP)
        snake.update(grid, WallBehavior.SOLID)
        assert snake.direction == Direction.UP, "Direction change failed"

        success = snake.update(grid, WallBehavior.SOLID)
        assert success, "Snake update failed"

        assert not snake.check_self_collision(), "Self collision check failed"

        food_manager = FoodManager(grid)
        food = food_manager.spawn_food([(10, 10)], prefer_center=True)
        assert food is not None, "Food spawning failed"

        print("  Core logic verified")
        return True
    except Exception as e:
        print(f"  Core logic verification failed: {e}")
        return False


def verify_pygame_components():
    """Verify pygame components can be created."""
    print("Verifying pygame components...")
    try:
        import pygame
        pygame.init()

        screen = pygame.Surface((800, 600))

        from snake_game.renderer import Renderer
        from snake_game.theme import get_theme, Theme

        theme = get_theme(Theme.CLASSIC)
        renderer = Renderer(screen, theme, 1.0)
        assert renderer is not None, "Renderer creation failed"

        from snake_game.settings import SettingsManager
        from snake_game.persistence import PersistenceManager

        settings = SettingsManager()
        persistence = PersistenceManager()
        assert settings is not None, "Settings creation failed"
        assert persistence is not None, "Persistence creation failed"

        from snake_game.ui import UIManager

        ui = UIManager(screen, settings, persistence)
        assert ui is not None, "UI creation failed"

        pygame.quit()
        print("  Pygame components verified")
        return True
    except Exception as e:
        print(f"  Pygame verification failed: {e}")
        return False


def verify_game_creation():
    """Verify Game object can be created."""
    print("Verifying Game creation...")
    try:
        import pygame
        pygame.init()

        screen = pygame.Surface((1280, 720))

        from snake_game.game import Game

        game = Game(screen)
        assert game is not None, "Game creation failed"
        assert game.state is not None, "Game state not initialized"

        pygame.quit()
        print("  Game creation verified")
        return True
    except Exception as e:
        print(f"  Game creation failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 50)
    print("Snake Game Verification Script")
    print("=" * 50)

    results = []

    results.append(("Imports", verify_imports()))
    results.append(("Core Logic", verify_core_logic()))
    results.append(("Pygame Components", verify_pygame_components()))
    results.append(("Game Creation", verify_game_creation()))

    print()
    print("=" * 50)
    print("Verification Results:")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("VERIFY_OK")
        return 0
    else:
        print("VERIFY_FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())