"""Theme module for visual styling of the game."""

from typing import Dict, Tuple, Any
from dataclasses import dataclass

from .constants import Theme


MODERN_PALETTE = {
    "deep_teal": (38, 70, 83),
    "teal": (42, 157, 143),
    "warm_yellow": (233, 196, 106),
    "warm_orange": (244, 162, 97),
    "coral": (231, 111, 81),
}

MODERN_PALETTE_CB = {
    "deep_teal": (38, 70, 83),
    "teal": (42, 157, 143),
    "warm_yellow": (244, 162, 97),
    "warm_orange": (42, 157, 143),
    "coral": (231, 111, 81),
}


@dataclass
class ThemeColors:
    """Color palette for a theme."""
    background: Tuple[int, int, int]
    grid_bg: Tuple[int, int, int]
    grid_line: Tuple[int, int, int]
    snake_head: Tuple[int, int, int]
    snake_body: Tuple[int, int, int]
    snake_body_alt: Tuple[int, int, int]
    food_normal: Tuple[int, int, int]
    food_bonus: Tuple[int, int, int]
    food_poison: Tuple[int, int, int]
    obstacle: Tuple[int, int, int]
    text_primary: Tuple[int, int, int]
    text_secondary: Tuple[int, int, int]
    accent: Tuple[int, int, int]
    menu_bg: Tuple[int, int, int]
    menu_selected: Tuple[int, int, int]
    hud_bg: Tuple[int, int, int]


@dataclass
class ThemeSounds:
    """Sound settings for a theme."""
    music_tempo: float
    eat_pitch: float
    death_pitch: float


class GameTheme:
    """
    Defines the visual appearance of the game.

    Contains colors, fonts, and other visual properties.
    """

    def __init__(
        self,
        name: str,
        colors: ThemeColors,
        sounds: ThemeSounds,
        corner_radius: int = 8,
        shadow_offset: int = 3,
        particle_count: int = 10
    ):
        self.name = name
        self.colors = colors
        self.sounds = sounds
        self.corner_radius = corner_radius
        self.shadow_offset = shadow_offset
        self.particle_count = particle_count


THEMES: Dict[Theme, GameTheme] = {
    Theme.CLASSIC: GameTheme(
        name="Classic",
        colors=ThemeColors(
            background=(34, 34, 34),
            grid_bg=(50, 50, 50),
            grid_line=(70, 70, 70),
            snake_head=(0, 180, 0),
            snake_body=(0, 200, 0),
            snake_body_alt=(0, 160, 0),
            food_normal=(220, 50, 50),
            food_bonus=(255, 215, 0),
            food_poison=(128, 0, 128),
            obstacle=(80, 80, 80),
            text_primary=(255, 255, 255),
            text_secondary=(180, 180, 180),
            accent=(100, 200, 100),
            menu_bg=(40, 40, 40),
            menu_selected=(60, 60, 60),
            hud_bg=(30, 30, 30),
        ),
        sounds=ThemeSounds(
            music_tempo=1.0,
            eat_pitch=1.0,
            death_pitch=1.0
        ),
        corner_radius=8,
        shadow_offset=3,
        particle_count=10
    ),
    Theme.NEON: GameTheme(
        name="Neon",
        colors=ThemeColors(
            background=(10, 10, 20),
            grid_bg=(15, 15, 30),
            grid_line=(30, 30, 60),
            snake_head=(0, 255, 255),
            snake_body=(0, 200, 255),
            snake_body_alt=(0, 150, 255),
            food_normal=(255, 0, 128),
            food_bonus=(255, 255, 0),
            food_poison=(255, 0, 0),
            obstacle=(60, 20, 80),
            text_primary=(255, 255, 255),
            text_secondary=(150, 150, 200),
            accent=(255, 0, 255),
            menu_bg=(15, 10, 25),
            menu_selected=(40, 20, 60),
            hud_bg=(20, 15, 35),
        ),
        sounds=ThemeSounds(
            music_tempo=1.2,
            eat_pitch=1.2,
            death_pitch=0.8
        ),
        corner_radius=4,
        shadow_offset=5,
        particle_count=15
    ),
    Theme.COLORBLIND: GameTheme(
        name="Colorblind",
        colors=ThemeColors(
            background=(40, 40, 40),
            grid_bg=(60, 60, 60),
            grid_line=(90, 90, 90),
            snake_head=(0, 120, 200),
            snake_body=(50, 150, 255),
            snake_body_alt=(100, 180, 255),
            food_normal=(255, 150, 0),
            food_bonus=(255, 255, 100),
            food_poison=(180, 180, 180),
            obstacle=(100, 100, 100),
            text_primary=(255, 255, 255),
            text_secondary=(200, 200, 200),
            accent=(100, 200, 255),
            menu_bg=(50, 50, 50),
            menu_selected=(70, 70, 70),
            hud_bg=(35, 35, 35),
        ),
        sounds=ThemeSounds(
            music_tempo=1.0,
            eat_pitch=1.0,
            death_pitch=1.0
        ),
        corner_radius=6,
        shadow_offset=4,
        particle_count=10
    ),
    Theme.MODERN: GameTheme(
        name="Modern",
        colors=ThemeColors(
            background=MODERN_PALETTE["deep_teal"],
            grid_bg=(51, 90, 100),
            grid_line=(60, 100, 115),
            snake_head=MODERN_PALETTE["teal"],
            snake_body=MODERN_PALETTE["warm_orange"],
            snake_body_alt=MODERN_PALETTE["coral"],
            food_normal=MODERN_PALETTE["warm_yellow"],
            food_bonus=MODERN_PALETTE["warm_orange"],
            food_poison=MODERN_PALETTE["coral"],
            obstacle=(55, 80, 95),
            text_primary=MODERN_PALETTE["warm_yellow"],
            text_secondary=(150, 180, 170),
            accent=MODERN_PALETTE["teal"],
            menu_bg=(30, 55, 65),
            menu_selected=(45, 80, 90),
            hud_bg=(38, 70, 83, 191),
        ),
        sounds=ThemeSounds(
            music_tempo=0.9,
            eat_pitch=1.1,
            death_pitch=0.7
        ),
        corner_radius=4,
        shadow_offset=6,
        particle_count=12
    ),
}


def get_theme(theme_type: Theme) -> GameTheme:
    """Get the theme for the given theme type."""
    return THEMES.get(theme_type, THEMES[Theme.CLASSIC])


def get_palette(theme_type: Theme = Theme.MODERN, colorblind: bool = False) -> Dict[str, Tuple[int, int, int]]:
    """Get the color palette for the given theme."""
    if colorblind:
        return MODERN_PALETTE_CB
    return MODERN_PALETTE