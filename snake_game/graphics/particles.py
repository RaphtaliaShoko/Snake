"""Particle system for game effects."""

from typing import List, Optional, Tuple
import pygame
import random
import math


class Particle:
    """A single particle for game effects."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        life: float,
        size: float = 4.0
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size

    def update(self, dt: float) -> bool:
        """Update particle, return False if dead."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= dt
        return self.life > 0

    def get_alpha(self) -> int:
        """Get current alpha based on remaining life."""
        return int(255 * max(0, self.life / self.max_life))

    def get_size(self) -> float:
        """Get current size based on remaining life."""
        return self.size * (0.5 + 0.5 * (self.life / self.max_life))


class ParticleSystem:
    """System to manage particles for eat/death effects."""

    MAX_PARTICLES = 150

    def __init__(self):
        self.particles: List[Particle] = []

    def emit_eat_particles(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        count: int = 8
    ) -> None:
        """Emit particles when food is eaten."""
        if len(self.particles) > self.MAX_PARTICLES - count:
            self.particles = self.particles[-self.MAX_PARTICLES + count:]
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.3, 0.6)
            size = random.uniform(3, 6)
            self.particles.append(Particle(x, y, vx, vy, color, life, size))

    def emit_death_particles(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        count: int = 20
    ) -> None:
        """Emit particles when snake dies."""
        if len(self.particles) > self.MAX_PARTICLES - count:
            self.particles = self.particles[-self.MAX_PARTICLES + count:]
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 250)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.5, 1.0)
            size = random.uniform(4, 8)
            self.particles.append(Particle(x, y, vx, vy, color, life, size))

    def emit_speed_particles(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        count: int = 5
    ) -> None:
        """Emit trail particles for speed effect."""
        if len(self.particles) > self.MAX_PARTICLES - count:
            self.particles = self.particles[-self.MAX_PARTICLES + count:]
        
        for _ in range(count):
            angle = random.uniform(-math.pi, math.pi)
            speed = random.uniform(20, 60)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.2, 0.4)
            size = random.uniform(2, 4)
            self.particles.append(Particle(x, y, vx, vy, color, life, size))

    def update(self, dt: float) -> None:
        """Update all particles, remove dead ones."""
        self.particles = [p for p in self.particles if p.update(dt)]

    def clear(self) -> None:
        """Clear all particles."""
        self.particles = []

    def render(self, screen: pygame.Surface) -> None:
        """Render all particles to screen."""
        for p in self.particles:
            alpha = p.get_alpha()
            size = int(p.get_size())
            if size > 0 and alpha > 0:
                color_with_alpha = (*p.color, alpha)
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color_with_alpha, (size, size), size)
                screen.blit(surf, (int(p.x - size), int(p.y - size)))

    def render_gl(self, screen: pygame.Surface) -> None:
        """Render particles using pygame.gfxdraw if available."""
        try:
            import pygame.gfxdraw
            for p in self.particles:
                alpha = p.get_alpha()
                size = int(p.get_size())
                if size > 0 and alpha > 0:
                    color = (*p.color, alpha)
                    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.gfxdraw.filled_circle(surf, size, size, size, color)
                    screen.blit(surf, (int(p.x - size), int(p.y - size)))
        except ImportError:
            self.render(screen)


particle_system = ParticleSystem()