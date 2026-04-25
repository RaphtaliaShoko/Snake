"""Graphics upgrade verification script."""

import os
import sys
import tempfile
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((1, 1))


def verify_gradient_utilities():
    """Test gradient building functions."""
    print("  Verifying gradient utilities...")
    from snake_game.graphics.gradients import (
        build_lengthwise_gradient,
        apply_gradient_mask,
        get_snake_gradient,
        SNAKE_GRADIENT_STOPS,
    )

    grad = build_lengthwise_gradient(256, 8, SNAKE_GRADIENT_STOPS)
    assert grad.get_width() == 256
    assert grad.get_height() == 8

    gradient = get_snake_gradient(100, colorblind=False, height=8)
    assert gradient.get_width() == 100
    assert gradient.get_height() == 8

    print("    Gradient utilities: OK")
    return True


def verify_particle_system():
    """Test particle system."""
    print("  Verifying particle system...")
    from snake_game.graphics.particles import ParticleSystem

    ps = ParticleSystem()
    ps.emit_eat_particles(50, 50, (255, 0, 0), 5)
    ps.update(0.1)
    assert len(ps.particles) > 0

    ps.clear()
    assert len(ps.particles) == 0

    print("    Particle system: OK")
    return True


def verify_theme():
    """Test theme palette."""
    print("  Verifying theme...")
    from snake_game.theme import get_palette, MODERN_PALETTE, MODERN_PALETTE_CB

    palette = get_palette()
    assert "deep_teal" in palette
    assert "teal" in palette
    assert "warm_yellow" in palette
    assert "warm_orange" in palette
    assert "coral" in palette

    palette_cb = get_palette(colorblind=True)
    assert palette_cb == MODERN_PALETTE_CB

    print("    Theme palette: OK")
    return True


def verify_settings():
    """Test graphics settings."""
    print("  Verifying graphics settings...")
    from snake_game.settings import GameSettings

    settings = GameSettings()
    assert hasattr(settings, "snake_style")
    assert hasattr(settings, "particle_effects")
    assert hasattr(settings, "gradient_intensity")
    assert hasattr(settings, "outline_glow")
    assert hasattr(settings, "grid_visible")
    assert hasattr(settings, "colorblind_mode")
    assert hasattr(settings, "vignette")

    assert settings.snake_style == "modern"
    assert settings.particle_effects == True

    print("    Graphics settings: OK")
    return True


def verify_renderer():
    """Test renderer snake styles."""
    print("  Verifying renderer...")
    from snake_game.renderer import Renderer
    from snake_game.theme import get_theme
    from snake_game.constants import Theme

    screen = pygame.Surface((400, 400))
    theme = get_theme(Theme.MODERN)
    renderer = Renderer(screen, theme)

    assert hasattr(renderer, "render_snake")
    assert hasattr(renderer, "_render_snake_modern")
    assert hasattr(renderer, "_render_snake_classic")

    grid_surf = pygame.Surface((400, 400))
    body = [(5, 5), (5, 6), (5, 7), (5, 8)]
    renderer.render_snake(grid_surf, body, 20, (0, 1), 0, style="modern")
    renderer.render_snake(grid_surf, body, 20, (0, 1), 0, style="classic")

    print("    Renderer styles: OK")
    return True


def main():
    print("==================================================")
    print("Graphics Upgrade Verification Script")
    print("==================================================")

    results = []

    try:
        from snake_game.graphics import gradients, particles
    except ImportError as e:
        print(f"  Failed to import graphics modules: {e}")
        return 1

    tests = [
        ("Gradient utilities", verify_gradient_utilities),
        ("Particle system", verify_particle_system),
        ("Theme palette", verify_theme),
        ("Graphics settings", verify_settings),
        ("Renderer", verify_renderer),
    ]

    for name, test_fn in tests:
        try:
            result = test_fn()
            results.append((name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"    ERROR: {e}")
            results.append((name, f"FAIL ({e})"))

    print()
    print("==================================================")
    print("Verification Results:")
    print("==================================================")
    all_passed = True
    for name, status in results:
        print(f"  {name}: {status}")
        if status != "PASS":
            all_passed = False

    if all_passed:
        print()
        print("GRAPHICS_VERIFY_OK")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())