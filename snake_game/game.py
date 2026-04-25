"""
Snake Game - Main Module

A modern, feature-rich implementation of the classic Snake game with:
- Customizable game parameters (grid size, speed, obstacles, etc.)
- Multiple visual themes (Classic, Neon, Colorblind, Modern)
- Procedural audio (no external files required)
- High score persistence
- Gamepad support
- Smooth animations and particle effects

Architecture:
- constants.py: Game constants and enumerations
- settings.py: Configuration management with persistence
- grid.py: Grid/board management
- snake.py: Snake entity with movement and collision
- food.py: Food system with multiple types
- theme.py: Visual theme definitions
- renderer.py: All game rendering and effects
- audio.py: Procedural audio generation
- input_handler.py: Keyboard and gamepad input
- persistence.py: High scores and stats persistence
- ui.py: Menu and interface management
- game.py: Main game logic and loop

Author: Snake Game Project
License: MIT
"""

import sys
import time
from typing import Optional, Tuple
import pygame

from .constants import (
    GameState, Direction, WallBehavior, SpeedMode, Theme, Difficulty, FoodType
)
from .settings import SettingsManager, GameSettings
from .grid import Grid
from .snake import Snake
from .food import FoodManager
from .theme import get_theme
from .renderer import Renderer
from .audio import AudioManager
from .input_handler import InputHandler
from .persistence import PersistenceManager
from .ui import UIManager


class Game:
    """
    Main game class that orchestrates all game systems.

    Manages the game loop, state transitions, and coordinates
    between rendering, input, audio, and game logic.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.settings = SettingsManager()
        self.settings.load()

        self.persistence = PersistenceManager()
        self.persistence.load_stats()

        self.state = GameState.MENU
        self._previous_state = GameState.MENU

        theme_type = Theme(self.settings.settings.theme)
        self._theme = get_theme(theme_type)

        self.renderer = Renderer(screen, self._theme, self.settings.settings.font_scale)
        self.audio = AudioManager()
        self.audio.initialize(self._theme)

        self.input_handler = InputHandler()
        if self.input_handler.has_gamepad():
            self.input_handler.calibrate_gamepad()

        self.ui = UIManager(screen, self.settings, self.persistence)
        self.ui.set_theme(theme_type)
        self.ui.set_font_scale(self.settings.settings.font_scale)

        self.grid: Optional[Grid] = None
        self.snake: Optional[Snake] = None
        self.food_manager: Optional[FoodManager] = None

        self.score = 0
        self.level = 1
        self.max_speed = 0.0

        self._last_update_time = 0.0
        self._update_interval = 0.1
        self._elapsed_time = 0.0
        self._game_start_time = 0.0
        self._food_eaten = 0

        self._movement_animation = 0.0
        self._animation_target = 1.0

        self._new_high_score = False
        self._death_effect_played = False

        self._setup_input_callbacks()

    def _setup_input_callbacks(self) -> None:
        """Setup input handling callbacks."""
        self.input_handler.register_action("pause", self.toggle_pause)
        self.input_handler.register_action("restart", self.restart_game)
        self.input_handler.register_action("menu", lambda: self.set_state(GameState.MENU))

    def set_state(self, state: GameState) -> None:
        """Change the game state."""
        self._previous_state = self.state
        self.state = state

        if state == GameState.PLAYING and self._previous_state in (GameState.MENU, GameState.GAME_OVER):
            self._start_new_game()

    def _start_new_game(self) -> None:
        """Initialize a new game session."""
        settings = self.settings.settings

        self.grid = Grid(settings.grid_rows, settings.grid_cols)

        if settings.enable_obstacles:
            obstacles = self.grid.generate_obstacles(settings.obstacle_count)
            self.grid.set_obstacles(obstacles)

        center_row = settings.grid_rows // 2
        center_col = settings.grid_cols // 2

        self.snake = Snake(
            center_row,
            center_col,
            settings.initial_snake_length,
            Direction.RIGHT
        )

        self.food_manager = FoodManager(self.grid)
        self.food_manager.set_enabled_types([FoodType.NORMAL, FoodType.BONUS, FoodType.POISON])

        self._spawn_initial_food()

        self.score = 0
        self.level = 1
        self.max_speed = float(settings.base_speed)
        self._update_interval = 1.0 / self.max_speed
        self._game_start_time = time.time()
        self._food_eaten = 0
        self._new_high_score = False
        self._death_effect_played = False

        self.renderer.particles.clear()
        self.input_handler.clear_queues()

    def _spawn_initial_food(self) -> None:
        """Spawn initial food items."""
        occupied = self.snake.body.copy()
        occupied.extend(self.grid.get_obstacles())

        for _ in range(3):
            self.food_manager.spawn_food(occupied, prefer_center=True)
            if self.food_manager.foods:
                for food in self.food_manager.foods:
                    occupied.append(food.position)

    def _calculate_current_speed(self) -> float:
        """Calculate current snake speed based on settings and progress."""
        settings = self.settings.settings
        base = float(settings.base_speed)

        if settings.speed_mode == SpeedMode.FIXED:
            return base

        speed = base + (self.level - 1) * settings.speed_increment
        return min(speed, float(MAX_SPEED := 30))

    def toggle_pause(self) -> None:
        """Toggle pause state."""
        if self.state == GameState.PLAYING:
            self.set_state(GameState.PAUSED)
        elif self.state == GameState.PAUSED:
            self.set_state(GameState.PLAYING)

    def restart_game(self) -> None:
        """Restart the current game."""
        self.set_state(GameState.PLAYING)

    def handle_events(self) -> None:
        """Process all pending events."""
        for event in pygame.event.get():
            if self.input_handler.is_quit_key(event):
                self.set_state(GameState.QUIT)
                continue

            if self.state == GameState.MENU:
                action = self.ui.handle_input(event)
                if action:
                    if action == "navigate":
                        self.audio.play_menu_select()
                    elif action == "play":
                        self.set_state(GameState.PLAYING)
                    elif action == "settings":
                        self.state = GameState.SETTINGS
                    elif action == "high_scores":
                        self.state = GameState.HIGH_SCORES
                    elif action == "quit":
                        self.set_state(GameState.QUIT)
                    elif action == "back":
                        self.state = GameState.MENU

            elif self.state == GameState.SETTINGS:
                action = self.ui.handle_settings_input(event)
                if action:
                    if action == "navigate":
                        self.audio.play_menu_select()
                    elif action == "adjust":
                        pass
                    elif action == "clear":
                        self.audio.play_menu_select()
                    elif action == "back":
                        self.state = GameState.MENU

            elif self.state == GameState.HIGH_SCORES:
                action = self.ui.handle_high_scores_input(event)
                if action == "back":
                    self.state = GameState.MENU

            elif self.state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    direction = self.input_handler.process_keyboard(event)
                    if direction:
                        self.snake.set_direction(direction)

            elif self.state == GameState.GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.set_state(GameState.PLAYING)
                    elif event.key == pygame.K_ESCAPE:
                        self.set_state(GameState.MENU)

            if self.input_handler.has_gamepad():
                self.input_handler.process_event(event)

    def update(self, dt: float) -> None:
        """Update game state."""
        self.renderer.update(dt)
        self._animation_time = getattr(self, "_animation_time", 0.0) + dt

        if self.state == GameState.MENU:
            pass

        elif self.state == GameState.PLAYING:
            self._update_gameplay(dt)

        elif self.state == GameState.PAUSED:
            pass

        elif self.state == GameState.GAME_OVER:
            if not self._death_effect_played:
                self._death_effect_played = True

    def _update_gameplay(self, dt: float) -> None:
        """Update gameplay logic."""
        self._elapsed_time += dt

        direction = self.input_handler.get_next_direction()
        if direction:
            self.snake.set_direction(direction)

        if self._elapsed_time >= self._update_interval:
            self._elapsed_time = 0.0
            self._movement_animation = 0.0
            self._animation_target = 1.0

            if not self._update_snake():
                self._handle_death()
                return

            self._check_food_collision()
            self._check_level_up()

            self.max_speed = max(self.max_speed, self._calculate_current_speed())

        self._movement_animation = min(1.0, self._movement_animation + dt * 10)

    def _update_snake(self) -> bool:
        """Update snake position and check collisions."""
        wall_behavior = WallBehavior(self.settings.settings.wall_behavior)

        success = self.snake.update(self.grid, wall_behavior)
        if not success:
            return False

        collision, _ = self.snake.check_collision(
            self.grid,
            wall_behavior,
            self.grid.get_obstacles()
        )

        if collision:
            return False

        return True

    def _check_food_collision(self) -> None:
        """Check if snake head is on food."""
        head = self.snake.head
        food = self.food_manager.check_food_at(head[0], head[1])

        if food:
            if food.food_type == FoodType.NORMAL:
                self.snake.grow(food.growth_effect)
                self.score += food.points
                self._food_eaten += 1
                self.audio.play_eat()
            elif food.food_type == FoodType.BONUS:
                self.snake.grow(food.growth_effect)
                self.score += food.points
                self._food_eaten += 1
                self.audio.play_bonus()
            elif food.food_type == FoodType.POISON:
                self.snake.shrink(abs(food.growth_effect))
                self.score = max(0, self.score + food.points)
                if self.snake.length <= 1:
                    self._handle_death()
                    return

            cell_size = self.renderer.screen.get_width() * 0.7 / self.grid.cols
            x = self.grid.cols // 2 * cell_size
            y = self.grid.rows // 2 * cell_size
            self.renderer.spawn_eat_effect(x, y, food.food_type)

            self.food_manager.remove_food(food)

            occupied = self.snake.body.copy()
            occupied.extend(self.grid.get_obstacles())
            occupied.extend(self.food_manager.get_all_positions())
            self.food_manager.spawn_food(occupied)

    def _check_level_up(self) -> None:
        """Check if player has leveled up."""
        new_level = (self.score // 100) + 1
        if new_level > self.level:
            self.level = new_level
            self.max_speed = self._calculate_current_speed()
            self._update_interval = 1.0 / self.max_speed

    def _handle_death(self) -> None:
        """Handle snake death."""
        self.audio.play_death()

        cell_size = self.renderer.screen.get_width() * 0.7 / self.grid.cols
        x = self.grid.cols // 2 * cell_size
        y = self.grid.rows // 2 * cell_size
        self.renderer.spawn_death_effect(x, y)

        difficulty = Difficulty(self.settings.settings.difficulty)
        self._new_high_score = self.persistence.add_high_score(
            self.score,
            difficulty,
            self.settings.settings.grid_rows,
            self.settings.settings.grid_cols,
            self.max_speed,
            self.snake.length
        )

        time_played = int(time.time() - self._game_start_time)
        self.persistence.update_stats(self.score, self._food_eaten, time_played, self.snake.length)

        self.state = GameState.GAME_OVER

    def render(self) -> None:
        """Render the current frame."""
        self.renderer.clear()

        if self.state == GameState.MENU:
            self._render_game_preview()
            self.ui.render_main_menu()

        elif self.state == GameState.SETTINGS:
            self._render_game_preview()
            self.ui.render_settings_menu()

        elif self.state == GameState.HIGH_SCORES:
            self._render_game_preview()
            self.ui.render_high_scores()

        elif self.state in (GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER):
            self._render_game()

            if self.state == GameState.PAUSED:
                self.renderer.render_pause_overlay()
            elif self.state == GameState.GAME_OVER:
                self.renderer.render_game_over(
                    self.score,
                    self.persistence.get_high_scores(1)[0].score
                    if self.persistence.get_high_scores(1) else 0,
                    self._new_high_score
                )

    def _render_game_preview(self) -> None:
        """Render a small game preview for menu backgrounds."""
        preview_size = 200
        preview_surface = pygame.Surface((preview_size, preview_size))
        preview_surface.fill(self._theme.colors.grid_bg)

        colors = self._theme.colors
        cell_size = preview_size / 10

        for r in range(10):
            for c in range(10):
                x = c * cell_size + 2
                y = r * cell_size + 2
                size = cell_size - 4

                pygame.draw.rect(
                    preview_surface,
                    colors.grid_line,
                    (x, y, size, size),
                    1
                )

        snake_positions = [
            (5, 3), (5, 4), (5, 5), (5, 6)
        ]
        for i, (r, c) in enumerate(snake_positions):
            x = c * cell_size + 2
            y = r * cell_size + 2
            size = cell_size - 4
            color = colors.snake_head if i == 0 else colors.snake_body
            pygame.draw.rect(preview_surface, color, (x, y, size, size), border_radius=3)

        fx, fy = 3 * cell_size + cell_size / 2, 3 * cell_size + cell_size / 2
        pygame.draw.circle(preview_surface, colors.food_normal, (int(fx), int(fy)), int(cell_size / 3))

        x = (self.screen.get_width() - preview_size) // 2
        y = (self.screen.get_height() - preview_size) // 2 + 50
        self.screen.blit(preview_surface, (x, y))

    def _render_game(self) -> None:
        """Render the main game view."""
        settings = self.settings.settings
        padding = 50

        available_width = self.screen.get_width() - padding * 2
        available_height = self.screen.get_height() - padding * 2 - 60

        cell_size = min(
            available_width / settings.grid_cols,
            available_height / settings.grid_rows
        )

        grid_width = int(settings.grid_cols * cell_size)
        grid_height = int(settings.grid_rows * cell_size)

        grid_x = (self.screen.get_width() - grid_width) // 2
        grid_y = (self.screen.get_height() - grid_height) // 2 + 20

        grid_surface = pygame.Surface((grid_width, grid_height))

        self.renderer.render_grid(grid_surface, cell_size, self.grid.get_obstacles())

        if self.snake:
            direction = self.snake.get_direction_vector()
            self.renderer.render_snake(
                grid_surface,
                self.snake.body,
                cell_size,
                direction,
                self._movement_animation
            )

        if self.food_manager:
            foods = [(f.row, f.col, f.food_type) for f in self.food_manager.foods]
            self.renderer.render_food(grid_surface, foods, cell_size, self._animation_time)

        self.screen.blit(grid_surface, (grid_x, grid_y))

        self.renderer.render_particles(grid_x, grid_y)

        self.renderer.render_hud(
            self.score,
            self.persistence.get_high_scores(1)[0].score
            if self.persistence.get_high_scores(1) else 0,
            self.level,
            self.max_speed,
            self.state == GameState.PAUSED,
            pygame.Rect(grid_x, grid_y, grid_width, grid_height)
        )

    def run(self) -> None:
        """Main game loop."""
        running = True

        while running:
            dt = self.clock.tick(60) / 1000.0

            self.handle_events()

            if self.state == GameState.QUIT:
                running = False
                continue

            self.update(dt)
            self.render()

            pygame.display.flip()

        self._cleanup()

    def _cleanup(self) -> None:
        """Clean up resources before exit."""
        self.audio.cleanup()
        pygame.quit()