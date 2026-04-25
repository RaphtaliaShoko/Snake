#!/usr/bin/env python3
"""
Snake Game - Main Entry Point

Run this file to start the game:
    python run_game.py

Or use the module syntax:
    python -m snake_game.run
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

from snake_game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


def main() -> None:
    """Initialize and run the Snake game."""
    pygame.init()

    try:
        icon = pygame.Surface((32, 32))
        icon.fill((0, 200, 0))
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Snake Game")
    except pygame.error:
        pass

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Game - Classic Arcade")

    from snake_game.game import Game

    try:
        game = Game(screen)
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        pygame.quit()
        raise


if __name__ == "__main__":
    main()