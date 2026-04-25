"""UI module for menus and interface components."""

import pygame
from typing import List, Optional, Tuple, Callable, Dict
from dataclasses import dataclass

from .constants import (
    GameState, Difficulty, WallBehavior, SpeedMode, Theme, FoodType
)
from .settings import SettingsManager, GameSettings
from .theme import GameTheme, get_theme
from .persistence import PersistenceManager, ScoreEntry


@dataclass
class MenuItem:
    """A single menu item."""
    text: str
    action: str
    subtext: str = ""


class UIManager:
    """
    Manages all user interface elements including menus and overlays.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        settings: SettingsManager,
        persistence: PersistenceManager
    ):
        self.screen = screen
        self.settings = settings
        self.persistence = persistence
        self._theme = get_theme(Theme.MODERN)
        self._font_scale = 1.0
        self._menu_stack: List[GameState] = []
        self._selected_index = 0
        self._transition_progress = 1.0
        self._transition_target = None
        self._callback_map: Dict[str, Callable] = {}

        self._setup_fonts()
        self._setup_callbacks()

    def _setup_fonts(self) -> None:
        """Setup fonts with fallbacks."""
        try:
            self._fonts = {
                "title": pygame.font.SysFont("arial", int(48 * self._font_scale), bold=True),
                "large": pygame.font.SysFont("arial", int(36 * self._font_scale), bold=True),
                "medium": pygame.font.SysFont("arial", int(28 * self._font_scale)),
                "small": pygame.font.SysFont("arial", int(22 * self._font_scale)),
                "hud": pygame.font.SysFont("monospace", int(20 * self._font_scale), bold=True),
            }
        except Exception:
            self._fonts = {
                "title": pygame.font.Font(None, int(48 * self._font_scale)),
                "large": pygame.font.Font(None, int(36 * self._font_scale)),
                "medium": pygame.font.Font(None, int(28 * self._font_scale)),
                "small": pygame.font.Font(None, int(22 * self._font_scale)),
                "hud": pygame.font.Font(None, int(20 * self._font_scale)),
            }

    def _setup_callbacks(self) -> None:
        """Setup menu action callbacks."""
        self._callback_map = {
            "play": self._on_play,
            "settings": self._on_settings,
            "high_scores": self._on_high_scores,
            "quit": self._on_quit,
        }

    def set_theme(self, theme: Theme) -> None:
        """Change the current theme."""
        self._theme = get_theme(theme)
        self.settings.settings.theme = theme.value
        self.settings.save()

    def set_font_scale(self, scale: float) -> None:
        """Change the font scale."""
        if abs(self._font_scale - scale) > 0.01:
            self._font_scale = scale
            self._setup_fonts()

    def get_font(self, name: str) -> pygame.font.Font:
        """Get a font by name."""
        return self._fonts.get(name, self._fonts.get("medium"))

    def register_callback(self, action: str, callback: Callable) -> None:
        """Register a callback for a menu action."""
        self._callback_map[action] = callback

    def _on_play(self) -> None:
        """Handle play action."""
        pass

    def _render_snake_logo(self, center_x: int, center_y: int, size: int, color: Tuple[int, int, int]) -> None:
        """Render the modern Snake logo - glowing teal bar with dot."""
        r, g, b = color
        teal_bright = (min(255, r + 60), min(255, g + 60), min(255, b + 40))
        teal_dim = (max(0, r - 40), max(0, g - 20), max(0, b - 20))
        
        bar_width = size // 8
        vertical_height = int(size * 0.65)
        horizontal_width = int(size * 0.45)
        
        for glow_pass in range(3, -1, -1):
            glow_alpha = max(20, 80 - glow_pass * 20)
            glow_size = bar_width + glow_pass * 8
            
            glow_surface = pygame.Surface((bar_width + 24, vertical_height + horizontal_width + 24), pygame.SRCALPHA)
            
            pygame.draw.rect(
                glow_surface,
                (*teal_dim, glow_alpha),
                (12, 0, glow_size, vertical_height),
                border_radius=bar_width // 2
            )
            pygame.draw.rect(
                glow_surface,
                (*teal_dim, glow_alpha),
                (12, vertical_height - glow_size // 2, horizontal_width + glow_size // 2, glow_size),
                border_radius=bar_width // 2
            )
            
            self.screen.blit(glow_surface, (center_x - bar_width // 2 - 12, center_y - vertical_height // 2 - 12))
        
        pygame.draw.rect(
            self.screen,
            color,
            (center_x - bar_width // 2, center_y - vertical_height // 2, bar_width, vertical_height),
            border_radius=bar_width // 2
        )
        
        pygame.draw.rect(
            self.screen,
            color,
            (center_x - bar_width // 2, center_y + vertical_height // 2 - horizontal_width // 2 - bar_width // 2, horizontal_width + bar_width // 2, bar_width),
            border_radius=bar_width // 2
        )
        
        highlight = pygame.Surface((bar_width - 4, vertical_height - 8), pygame.SRCALPHA)
        for y in range(0, vertical_height - 8, 4):
            alpha = int(200 * (1 - y / vertical_height))
            pygame.draw.rect(highlight, (*teal_bright, alpha), (0, y, bar_width - 4, 2))
        self.screen.blit(highlight, (center_x - bar_width // 2 + 2, center_y - vertical_height // 2 + 4))
        
        dot_radius = bar_width // 2 + 2
        for glow_pass in range(3, -1, -1):
            glow_alpha = max(30, 100 - glow_pass * 25)
            glow_radius = dot_radius + glow_pass * 6
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*teal_dim, glow_alpha), (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surf, (center_x - glow_radius, center_y - vertical_height // 2 - dot_radius - 8 - glow_radius))
        
        pygame.draw.circle(self.screen, color, (center_x, center_y - vertical_height // 2 - dot_radius - 8), dot_radius)
        pygame.draw.circle(self.screen, teal_bright, (center_x - dot_radius // 3, center_y - vertical_height // 2 - dot_radius - 8 - dot_radius // 3), dot_radius // 3)

    def _on_settings(self) -> None:
        """Handle settings action."""
        pass

    def _on_high_scores(self) -> None:
        """Handle high scores action."""
        pass

    def _on_quit(self) -> None:
        """Handle quit action."""
        pass

    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle menu navigation input."""
        if event.type != pygame.KEYDOWN:
            return None

        if event.key in (pygame.K_UP, pygame.K_w):
            self._selected_index = max(0, self._selected_index - 1)
            return "navigate"
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self._selected_index = min(self._selected_index + 1, 4)
            return "navigate"
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            menu_items = self._get_main_menu_items()
            if 0 <= self._selected_index < len(menu_items):
                return menu_items[self._selected_index].action
        elif event.key == pygame.K_ESCAPE:
            if self._menu_stack:
                self._menu_stack.pop()
                self._selected_index = 0
            return "back"

        return None

    def _get_main_menu_items(self) -> List[MenuItem]:
        """Get main menu items."""
        return [
            MenuItem("Play", "play", "Start a new game"),
            MenuItem("Settings", "settings", "Configure game options"),
            MenuItem("High Scores", "high_scores", "View best scores"),
            MenuItem("Quit", "quit", "Exit the game"),
        ]

    def render_main_menu(self) -> None:
        """Render the main menu."""
        colors = self._theme.colors
        teal = colors.accent
        width, height = self.screen.get_size()

        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        self.screen.blit(bg_surface, (0, 0))

        menu_items = self._get_main_menu_items()

        start_y = height // 2 - 20
        item_height = 70

        for i, item in enumerate(menu_items):
            is_selected = i == self._selected_index
            y = start_y + i * item_height

            bg_color = colors.menu_selected if is_selected else (0, 0, 0, 0)
            if is_selected:
                item_bg = pygame.Surface((400, 60), pygame.SRCALPHA)
                item_bg.fill((*bg_color, 150))
                item_rect = item_bg.get_rect(center=(width // 2, y))
                pygame.draw.rect(item_bg, colors.accent, item_bg.get_rect(), 2, border_radius=10)
                self.screen.blit(item_bg, item_rect)

            text_color = colors.accent if is_selected else colors.text_primary
            main_text = self.get_font("medium").render(item.text, True, text_color)
            main_rect = main_text.get_rect(center=(width // 2, y))
            self.screen.blit(main_text, main_rect)

        controls = self.get_font("small").render(
            "Arrow Keys/WASD to Navigate | Enter to Select | Esc to Back",
            True,
            colors.text_secondary
        )
        controls_rect = controls.get_rect(center=(width // 2, height - 50))
        self.screen.blit(controls, controls_rect)

    def render_settings_menu(self) -> None:
        """Render the settings menu."""
        colors = self._theme.colors
        width, height = self.screen.get_size()
        settings = self.settings.settings

        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        self.screen.blit(bg_surface, (0, 0))

        title = self.get_font("large").render("Settings", True, colors.text_primary)
        title_rect = title.get_rect(center=(width // 2, 80))
        self.screen.blit(title, title_rect)

        menu_items = [
            ("Theme", settings.theme.title()),
            ("Difficulty", settings.difficulty.title()),
            (f"Grid Size", f"{settings.grid_rows}x{settings.grid_cols}"),
            ("Initial Snake", str(settings.initial_snake_length)),
            ("Base Speed", str(settings.base_speed)),
            ("Speed Mode", settings.speed_mode.title()),
            ("Wall Behavior", settings.wall_behavior.title()),
            ("Obstacles", "On" if settings.enable_obstacles else "Off"),
            ("Music Volume", f"{int(settings.music_volume * 100)}%"),
            ("SFX Volume", f"{int(settings.sfx_volume * 100)}%"),
            ("Font Scale", f"{settings.font_scale:.1f}x"),
            ("Clear Data", "Reset all saved data"),
            ("Back", "Return to main menu"),
        ]

        start_y = 140
        item_height = 45
        visible_items = 12
        scroll_offset = max(0, min(self._selected_index - 5, len(menu_items) - visible_items))

        for i in range(min(visible_items, len(menu_items))):
            idx = i + scroll_offset
            if idx >= len(menu_items):
                break

            label, value = menu_items[idx]
            y = start_y + i * item_height

            is_selected = idx == self._selected_index

            if is_selected:
                item_bg = pygame.Surface((600, 40), pygame.SRCALPHA)
                item_bg.fill((*colors.menu_selected, 150))
                item_rect = item_bg.get_rect(center=(width // 2, y))
                pygame.draw.rect(item_bg, colors.accent, item_bg.get_rect(), 2, border_radius=8)
                self.screen.blit(item_bg, item_rect)

            label_font = self.get_font("small")
            value_font = self.get_font("small")

            label_color = colors.accent if is_selected else colors.text_primary
            label_text = label_font.render(label + ":", True, label_color)
            label_rect = label_text.get_rect(midright=(width // 2 - 20, y))
            self.screen.blit(label_text, label_rect)

            value_color = colors.text_secondary if not is_selected else colors.text_primary
            value_text = value_font.render(str(value), True, value_color)
            value_rect = value_text.get_rect(midleft=(width // 2 + 20, y))
            self.screen.blit(value_text, value_rect)

        hint = self.get_font("small").render(
            "Arrow Keys to Navigate | Left/Right to Adjust | Enter to Select",
            True,
            colors.text_secondary
        )
        hint_rect = hint.get_rect(center=(width // 2, height - 40))
        self.screen.blit(hint, hint_rect)

    def render_high_scores(self) -> None:
        """Render the high scores screen."""
        colors = self._theme.colors
        width, height = self.screen.get_size()

        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        self.screen.blit(bg_surface, (0, 0))

        title = self.get_font("large").render("High Scores", True, colors.text_primary)
        title_rect = title.get_rect(center=(width // 2, 80))
        self.screen.blit(title, title_rect)

        scores = self.persistence.get_high_scores(10)

        if not scores:
            no_scores = self.get_font("medium").render("No scores yet!", True, colors.text_secondary)
            no_scores_rect = no_scores.get_rect(center=(width // 2, height // 2))
            self.screen.blit(no_scores, no_scores_rect)
        else:
            headers = ["Rank", "Score", "Difficulty", "Grid", "Speed", "Length"]
            col_widths = [80, 100, 120, 100, 100, 100]
            start_x = width // 2 - sum(col_widths) // 2
            start_y = 140
            row_height = 40

            for i, header in enumerate(headers):
                x = start_x + sum(col_widths[:i]) + col_widths[i] // 2
                text = self.get_font("small").render(header, True, colors.accent)
                rect = text.get_rect(center=(x, start_y))
                self.screen.blit(text, rect)

            pygame.draw.line(
                self.screen,
                colors.grid_line,
                (start_x, start_y + 20),
                (start_x + sum(col_widths), start_y + 20),
                2
            )

            for row_idx, entry in enumerate(scores):
                y = start_y + 30 + row_idx * row_height
                values = [
                    f"#{row_idx + 1}",
                    str(entry.score),
                    entry.difficulty.title(),
                    entry.grid_size,
                    f"{entry.max_speed:.1f}",
                    str(entry.snake_length),
                ]

                for col_idx, value in enumerate(values):
                    x = start_x + sum(col_widths[:col_idx]) + col_widths[col_idx] // 2
                    text = self.get_font("small").render(value, True, colors.text_primary)
                    rect = text.get_rect(center=(x, y))
                    self.screen.blit(text, rect)

        hint = self.get_font("small").render("Press ESC or Enter to go back", True, colors.text_secondary)
        hint_rect = hint.get_rect(center=(width // 2, height - 40))
        self.screen.blit(hint, hint_rect)

    def handle_settings_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle settings menu navigation."""
        if event.type != pygame.KEYDOWN:
            return None

        settings = self.settings.settings
        total_items = 13

        if event.key in (pygame.K_UP, pygame.K_w):
            self._selected_index = max(0, self._selected_index - 1)
            return "navigate"
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self._selected_index = min(self._selected_index + 1, total_items - 1)
            return "navigate"
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self._adjust_setting(-1)
            return "adjust"
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self._adjust_setting(1)
            return "adjust"
        elif event.key == pygame.K_RETURN:
            return self._confirm_setting()
        elif event.key == pygame.K_ESCAPE:
            self._selected_index = 0
            return "back"

        return None

    def _adjust_setting(self, direction: int) -> None:
        """Adjust the currently selected setting."""
        settings = self.settings.settings
        idx = self._selected_index

        adjustments = {
            0: lambda d: self._cycle_theme(d),
            1: lambda d: self._cycle_difficulty(d),
            2: lambda d: self._cycle_grid_size(d),
            3: lambda d: self._cycle_snake_length(d),
            4: lambda d: self._cycle_speed(d),
            5: lambda d: self._cycle_speed_mode(d),
            6: lambda d: self._cycle_wall_behavior(d),
            7: lambda d: self._toggle_obstacles(),
            8: lambda d: self._cycle_volume("music", d),
            9: lambda d: self._cycle_volume("sfx", d),
            10: lambda d: self._cycle_font_scale(d),
        }

        if idx in adjustments:
            adjustments[idx](direction)
            self.settings.save()

    def _cycle_theme(self, direction: int) -> None:
        themes = list(Theme)
        current = Theme(self.settings.settings.theme)
        idx = themes.index(current)
        new_idx = (idx + direction) % len(themes)
        self.settings.settings.theme = themes[new_idx].value

    def _cycle_difficulty(self, direction: int) -> None:
        difficulties = list(Difficulty)
        current = Difficulty(self.settings.settings.difficulty)
        idx = difficulties.index(current)
        new_idx = (idx + direction) % len(difficulties)
        self.settings.apply_difficulty(difficulties[new_idx])

    def _cycle_grid_size(self, direction: int) -> None:
        sizes = [(15, 15), (20, 20), (25, 25), (30, 30)]
        current = (self.settings.settings.grid_rows, self.settings.settings.grid_cols)
        if current in sizes:
            idx = sizes.index(current)
            new_idx = (idx + direction) % len(sizes)
        else:
            new_idx = 1
        self.settings.settings.grid_rows, self.settings.settings.grid_cols = sizes[new_idx]

    def _cycle_snake_length(self, direction: int) -> None:
        self.settings.settings.initial_snake_length = max(
            3, min(10, self.settings.settings.initial_snake_length + direction)
        )

    def _cycle_speed(self, direction: int) -> None:
        self.settings.settings.base_speed = max(
            1, min(20, self.settings.settings.base_speed + direction * 2)
        )

    def _cycle_speed_mode(self, direction: int) -> None:
        self.settings.settings.speed_mode = (
            SpeedMode.ACCELERATING.value
            if self.settings.settings.speed_mode == SpeedMode.FIXED.value
            else SpeedMode.FIXED.value
        )

    def _cycle_wall_behavior(self, direction: int) -> None:
        self.settings.settings.wall_behavior = (
            WallBehavior.WRAP.value
            if self.settings.settings.wall_behavior == WallBehavior.SOLID.value
            else WallBehavior.SOLID.value
        )

    def _toggle_obstacles(self) -> None:
        self.settings.settings.enable_obstacles = not self.settings.settings.enable_obstacles

    def _cycle_volume(self, channel: str, direction: int) -> None:
        if channel == "music":
            self.settings.settings.music_volume = max(
                0, min(1, self.settings.settings.music_volume + direction * 0.1)
            )
        else:
            self.settings.settings.sfx_volume = max(
                0, min(1, self.settings.settings.sfx_volume + direction * 0.1)
            )

    def _cycle_font_scale(self, direction: int) -> None:
        self.settings.settings.font_scale = max(
            0.5, min(2.0, self.settings.settings.font_scale + direction * 0.1)
        )
        self.set_font_scale(self.settings.settings.font_scale)

    def _confirm_setting(self) -> Optional[str]:
        if self._selected_index == 11:
            self.settings.clear_saved_data()
            return "clear"
        elif self._selected_index == 12:
            self._selected_index = 0
            return "back"
        return None

    def handle_high_scores_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle high scores screen input."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                return "back"
        return None