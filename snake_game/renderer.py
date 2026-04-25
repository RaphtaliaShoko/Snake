"""Renderer module for all game visuals."""

import math
import time
from typing import List, Optional, Tuple, Any
import pygame
import random

from .constants import FoodType, SCREEN_WIDTH, SCREEN_HEIGHT, CELL_PADDING
from .theme import GameTheme, get_theme
from .constants import Theme


class Particle:
    """A simple particle for visual effects."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        lifetime: float,
        size: float
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size

    def update(self, dt: float) -> bool:
        """Update particle position. Returns False if dead."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.vx *= 0.98
        self.vy *= 0.98
        return self.lifetime > 0

    @property
    def alpha(self) -> int:
        """Get current alpha based on lifetime."""
        return int(255 * (self.lifetime / self.max_lifetime))


class ParticleSystem:
    """Manages visual particle effects."""

    def __init__(self, max_particles: int = 200):
        self.particles: List[Particle] = []
        self.max_particles = max_particles

    def spawn(
        self,
        x: float,
        y: float,
        count: int,
        color: Tuple[int, int, int],
        speed: float = 100.0,
        lifetime: float = 0.5,
        size: float = 4.0
    ) -> None:
        """Spawn particles at a position."""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                self.particles.pop(0)

            angle = random.uniform(0, 2 * math.pi)
            velocity = random.uniform(speed * 0.5, speed)
            vx = math.cos(angle) * velocity
            vy = math.sin(angle) * velocity

            particle = Particle(x, y, vx, vy, color, lifetime, size)
            self.particles.append(particle)

    def update(self, dt: float) -> None:
        """Update all particles."""
        self.particles = [p for p in self.particles if p.update(dt)]

    def clear(self) -> None:
        """Clear all particles."""
        self.particles = []


class Renderer:
    """
    Handles all game rendering including grid, snake, food, and UI.
    """

    def __init__(self, screen: pygame.Surface, theme: GameTheme, font_scale: float = 1.0):
        self.screen = screen
        self.theme = theme
        self.font_scale = font_scale
        self._font_cache: dict = {}
        self.particles = ParticleSystem()
        self._animation_time = 0.0
        self._food_animation = {}

        self._setup_fonts()

    def _setup_fonts(self) -> None:
        """Setup font system with fallbacks."""
        try:
            self._font_cache["title"] = pygame.font.SysFont(
                "arial", int(48 * self.font_scale), bold=True
            )
            self._font_cache["large"] = pygame.font.SysFont(
                "arial", int(32 * self.font_scale)
            )
            self._font_cache["medium"] = pygame.font.SysFont(
                "arial", int(24 * self.font_scale)
            )
            self._font_cache["small"] = pygame.font.SysFont(
                "arial", int(18 * self.font_scale)
            )
            self._font_cache["hud"] = pygame.font.SysFont(
                "monospace", int(20 * self.font_scale), bold=True
            )
        except Exception:
            self._font_cache["title"] = pygame.font.Font(None, int(48 * self.font_scale))
            self._font_cache["large"] = pygame.font.Font(None, int(32 * self.font_scale))
            self._font_cache["medium"] = pygame.font.Font(None, int(24 * self.font_scale))
            self._font_cache["small"] = pygame.font.Font(None, int(18 * self.font_scale))
            self._font_cache["hud"] = pygame.font.Font(None, int(20 * self.font_scale))

    def get_font(self, name: str) -> pygame.font.Font:
        """Get a cached font."""
        return self._font_cache.get(name, self._font_cache.get("medium"))

    def set_theme(self, theme: GameTheme) -> None:
        """Change the current theme."""
        self.theme = theme

    def set_font_scale(self, scale: float) -> None:
        """Change the font scale."""
        if abs(self.font_scale - scale) > 0.01:
            self.font_scale = scale
            self._setup_fonts()

    def clear(self) -> None:
        """Clear the screen."""
        self.screen.fill(self.theme.colors.background)

    def render_grid(
        self,
        grid_surface: pygame.Surface,
        cell_size: float,
        obstacles: List[Tuple[int, int]] = None
    ) -> None:
        """Render the game grid to a surface."""
        if obstacles is None:
            obstacles = []

        colors = self.theme.colors
        radius = self.theme.corner_radius

        grid_surface.fill(colors.grid_bg)

        for row in range(int(grid_surface.get_height() / cell_size)):
            for col in range(int(grid_surface.get_width() / cell_size)):
                x = col * cell_size + CELL_PADDING
                y = row * cell_size + CELL_PADDING
                size = cell_size - CELL_PADDING * 2

                if (row, col) in obstacles:
                    pygame.draw.rect(
                        grid_surface,
                        colors.obstacle,
                        (x, y, size, size),
                        border_radius=radius
                    )

        line_width = 1
        for i in range(0, int(grid_surface.get_height() / cell_size) + 1):
            y = i * cell_size
            pygame.draw.line(
                grid_surface,
                colors.grid_line,
                (0, y),
                (grid_surface.get_width(), y),
                line_width
            )

        for i in range(0, int(grid_surface.get_width() / cell_size) + 1):
            x = i * cell_size
            pygame.draw.line(
                grid_surface,
                colors.grid_line,
                (x, 0),
                (x, grid_surface.get_height()),
                line_width
            )

    def render_snake(
        self,
        grid_surface: pygame.Surface,
        body: List[Tuple[int, int]],
        cell_size: float,
        direction: Tuple[int, int],
        animation_offset: float = 0.0
    ) -> None:
        """Render the snake onto a grid surface."""
        colors = self.theme.colors
        radius = self.theme.corner_radius

        for i, (row, col) in enumerate(body):
            x = col * cell_size + CELL_PADDING
            y = row * cell_size + CELL_PADDING
            size = cell_size - CELL_PADDING * 2

            if i == 0:
                color = colors.snake_head
            else:
                color = colors.snake_body if i % 2 == 0 else colors.snake_body_alt

            offset_x = 0.0
            offset_y = 0.0
            if i == 0 and animation_offset > 0:
                offset_x = direction[0] * animation_offset * cell_size * 0.3
                offset_y = direction[1] * animation_offset * cell_size * 0.3

            rect = pygame.Rect(
                x + offset_x,
                y + offset_y,
                size,
                size
            )
            pygame.draw.rect(grid_surface, color, rect, border_radius=radius)

            if i == 0:
                eye_size = max(3, size * 0.15)
                eye_offset = size * 0.25

                center_x = x + size / 2 + offset_x
                center_y = y + size / 2 + offset_y

                if direction == (1, 0):
                    eye1 = (center_x + eye_offset - eye_size / 2, center_y - eye_offset)
                    eye2 = (center_x + eye_offset - eye_size / 2, center_y + eye_offset)
                elif direction == (-1, 0):
                    eye1 = (center_x - eye_offset - eye_size / 2, center_y - eye_offset)
                    eye2 = (center_x - eye_offset - eye_size / 2, center_y + eye_offset)
                elif direction == (0, -1):
                    eye1 = (center_x - eye_offset, center_y - eye_offset - eye_size / 2)
                    eye2 = (center_x + eye_offset, center_y - eye_offset - eye_size / 2)
                else:
                    eye1 = (center_x - eye_offset, center_y + eye_offset - eye_size / 2)
                    eye2 = (center_x + eye_offset, center_y + eye_offset - eye_size / 2)

                pygame.draw.circle(grid_surface, (255, 255, 255), eye1, int(eye_size))
                pygame.draw.circle(grid_surface, (255, 255, 255), eye2, int(eye_size))

    def render_food(
        self,
        grid_surface: pygame.Surface,
        foods: List[Tuple[int, int, FoodType]],
        cell_size: float,
        time: float
    ) -> None:
        """Render food items onto a grid surface."""
        colors = self.theme.colors

        food_colors = {
            FoodType.NORMAL: colors.food_normal,
            FoodType.BONUS: colors.food_bonus,
            FoodType.POISON: colors.food_poison,
        }

        for row, col, food_type in foods:
            x = col * cell_size + cell_size / 2
            y = row * cell_size + cell_size / 2
            base_radius = (cell_size - CELL_PADDING * 4) / 2

            bounce = math.sin(time * 5 + row + col) * 2
            radius = max(2, base_radius + bounce)

            color = food_colors.get(food_type, colors.food_normal)

            glow_radius = radius + 5
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface,
                (*color, 50),
                (glow_radius, glow_radius),
                int(glow_radius)
            )
            grid_surface.blit(
                glow_surface,
                (x - glow_radius, y - glow_radius)
            )

            pygame.draw.circle(grid_surface, color, (int(x), int(y)), int(radius))

            if food_type == FoodType.BONUS:
                inner_color = (255, 255, 255)
                pygame.draw.circle(
                    grid_surface,
                    inner_color,
                    (int(x), int(y)),
                    int(radius * 0.4)
                )

    def render_text(
        self,
        text: str,
        position: Tuple[int, int],
        font_name: str = "medium",
        color: Tuple[int, int, int] = None,
        align: str = "left"
    ) -> None:
        """Render text at a position."""
        if color is None:
            color = self.theme.colors.text_primary

        font = self.get_font(font_name)
        surface = font.render(text, True, color)

        x, y = position
        if align == "center":
            x -= surface.get_width() // 2
        elif align == "right":
            x -= surface.get_width()

        self.screen.blit(surface, (x, y))

    def render_hud(
        self,
        score: int,
        high_score: int,
        level: int,
        speed: float,
        paused: bool,
        grid_rect: pygame.Rect
    ) -> None:
        """Render the heads-up display."""
        colors = self.theme.colors
        padding = 15
        hud_height = 50

        hud_rect = pygame.Rect(
            grid_rect.left,
            grid_rect.top - hud_height - padding,
            grid_rect.width,
            hud_height
        )

        pygame.draw.rect(self.screen, colors.hud_bg, hud_rect, border_radius=10)

        font = self.get_font("hud")
        texts = [
            f"SCORE: {score}",
            f"HIGH: {high_score}",
            f"LVL: {level}",
            f"SPEED: {speed:.1f}",
        ]

        if paused:
            texts.append("PAUSED")

        total_width = sum(font.size(t + "  ")[0] for t in texts)
        spacing = hud_rect.width / (len(texts) + 1)

        for i, text in enumerate(texts):
            x = hud_rect.left + spacing * (i + 1)
            y = hud_rect.centery
            surface = font.render(text, True, colors.text_primary)
            rect = surface.get_rect(center=(x, y))
            self.screen.blit(surface, rect)

    def render_game_over(self, score: int, high_score: int, new_high_score: bool) -> None:
        """Render the game over overlay."""
        overlay = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height()),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))

        self.screen.blit(overlay, (0, 0))

        colors = self.theme.colors

        title_font = self.get_font("title")
        medium_font = self.get_font("medium")

        title = title_font.render("GAME OVER", True, colors.food_normal)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 80))
        self.screen.blit(title, title_rect)

        score_text = medium_font.render(f"Score: {score}", True, colors.text_primary)
        score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(score_text, score_rect)

        if new_high_score:
            hs_text = medium_font.render("NEW HIGH SCORE!", True, colors.food_bonus)
        else:
            hs_text = medium_font.render(f"High Score: {high_score}", True, colors.text_secondary)
        hs_rect = hs_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 40))
        self.screen.blit(hs_text, hs_rect)

        restart_text = self.get_font("small").render("Press SPACE or ENTER to restart", True, colors.text_secondary)
        restart_rect = restart_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 100))
        self.screen.blit(restart_text, restart_rect)

    def render_pause_overlay(self) -> None:
        """Render pause overlay."""
        overlay = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height()),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        colors = self.theme.colors
        pause_font = self.get_font("title")

        text = pause_font.render("PAUSED", True, colors.text_primary)
        rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text, rect)

        hint = self.get_font("small").render("Press P or ESC to resume", True, colors.text_secondary)
        hint_rect = hint.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))
        self.screen.blit(hint, hint_rect)

    def update(self, dt: float) -> None:
        """Update renderer state."""
        self._animation_time += dt
        self.particles.update(dt)
        for key in list(self._food_animation.keys()):
            self._food_animation[key] -= dt
            if self._food_animation[key] <= 0:
                del self._food_animation[key]

    def spawn_eat_effect(self, x: float, y: float, food_type: FoodType) -> None:
        """Spawn particle effect for eating food."""
        color = {
            FoodType.NORMAL: self.theme.colors.food_normal,
            FoodType.BONUS: self.theme.colors.food_bonus,
            FoodType.POISON: self.theme.colors.food_poison,
        }.get(food_type, self.theme.colors.food_normal)

        self.particles.spawn(
            x, y,
            self.theme.particle_count,
            color,
            speed=150.0,
            lifetime=0.4,
            size=5.0
        )

    def spawn_death_effect(self, x: float, y: float) -> None:
        """Spawn particle effect for death."""
        self.particles.spawn(
            x, y,
            self.theme.particle_count * 2,
            self.theme.colors.snake_head,
            speed=200.0,
            lifetime=0.6,
            size=6.0
        )

    def render_particles(self, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render all active particles."""
        for p in self.particles.particles:
            color_with_alpha = (*p.color[:3], p.alpha)
            surface = pygame.Surface((int(p.size * 2), int(p.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surface, color_with_alpha, (int(p.size), int(p.size)), int(p.size))
            self.screen.blit(surface, (p.x - p.size - offset_x, p.y - p.size - offset_y))