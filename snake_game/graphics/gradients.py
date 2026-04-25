"""Gradient utilities for the modern snake graphics."""

from typing import List, Tuple
import pygame


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def build_lengthwise_gradient(
    width: int,
    height: int,
    stops: List[Tuple[float, Tuple[int, int, int]]]
) -> pygame.Surface:
    """
    Build a 1D gradient surface with multiple color stops.
    
    Args:
        width: Width of the gradient in pixels
        height: Height of the gradient in pixels
        stops: List of (position, color) tuples where position is 0.0 to 1.0
    
    Returns:
        pygame.Surface with the gradient applied
    """
    gradient = pygame.Surface((width, height), pygame.SRCALPHA)
    gradient.fill((0, 0, 0, 0))
    
    sorted_stops = sorted(stops, key=lambda x: x[0])
    
    for x in range(width):
        t = x / width if width > 0 else 0
        
        start_idx = 0
        for i, (pos, _) in enumerate(sorted_stops):
            if t >= pos:
                start_idx = i
            else:
                break
        
        if start_idx >= len(sorted_stops) - 1:
            color = sorted_stops[-1][1]
        else:
            pos1, color1 = sorted_stops[start_idx]
            pos2, color2 = sorted_stops[start_idx + 1]
            
            if pos2 - pos1 > 0:
                local_t = (t - pos1) / (pos2 - pos1)
            else:
                local_t = 0
            
            color = tuple(
                int(color1[i] + (color2[i] - color1[i]) * local_t)
                for i in range(3)
            )
        
        for y in range(height):
            gradient.set_at((x, y), (*color, 255))
    
    return gradient


def apply_gradient_mask(
    gradient_surf: pygame.Surface,
    mask_surf: pygame.Surface
) -> pygame.Surface:
    """
    Apply a gradient surface to a mask surface.
    
    Args:
        gradient_surf: Gradient surface with alpha
        mask_surf: Mask surface (white = visible, transparent = hidden)
    
    Returns:
        Resulting surface with gradient applied within mask bounds
    """
    mask_rect = mask_surf.get_rect()
    grad_rect = gradient_surf.get_rect()
    
    if grad_rect.width < mask_rect.width or grad_rect.height < mask_rect.height:
        scaled = pygame.transform.scale(
            gradient_surf,
            (max(grad_rect.width, mask_rect.width), max(grad_rect.height, mask_rect.height))
        )
        gradient_surf = scaled
    
    result = pygame.Surface(mask_rect.size, pygame.SRCALPHA)
    result.fill((0, 0, 0, 0))
    
    mask_array = pygame.surfarray.pixels_alpha(mask_surf)
    grad_array = pygame.surfarray.pixels3(gradient_surf)
    result_array = pygame.surfarray.pixels3(result)
    result_alpha = pygame.surfarray.pixels_alpha(result)
    
    h, w = mask_rect.height, mask_rect.width
    gh, gw = gradient_surf.get_height(), gradient_surf.get_width()
    
    for y in range(h):
        for x in range(w):
            if mask_array[y, x] > 0:
                gx = int(x * gw / w) if w > 0 else 0
                gy = int(y * gh / h) if h > 0 else 0
                gx = min(gx, gw - 1)
                gy = min(gy, gh - 1)
                
                result_array[y, x] = grad_array[gy, gx]
                result_alpha[y, x] = mask_array[y, x]
    
    del mask_array, grad_array, result_array, result_alpha
    
    return result


def create_vignette(size: Tuple[int, int], strength: float = 0.3) -> pygame.Surface:
    """
    Create a radial vignette effect surface.
    
    Args:
        size: (width, height) of the surface
        strength: Opacity of the vignette at edges (0.0 to 1.0)
    
    Returns:
        Surface with vignette applied
    """
    width, height = size
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    
    center_x, center_y = width // 2, height // 2
    max_dist = ((width // 2) ** 2 + (height // 2) ** 2) ** 0.5
    
    for y in range(height):
        for x in range(width):
            dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            factor = min(1.0, dist / max_dist) * strength
            alpha = int(factor * 255)
            if alpha > 0:
                surface.set_at((x, y), (0, 0, 0, alpha))
    
    return surface


SNAKE_GRADIENT_STOPS = [
    (0.0, (42, 157, 143)),
    (0.5, (244, 162, 97)),
    (1.0, (231, 111, 81)),
]

SNAKE_GRADIENT_STOPS_CB = [
    (0.0, (42, 157, 143)),
    (0.5, (42, 157, 143)),
    (1.0, (231, 111, 81)),
]


def get_snake_gradient(
    length_px: int,
    colorblind: bool = False,
    height: int = 8
) -> pygame.Surface:
    """Get a gradient surface for the snake of given pixel length."""
    stops = SNAKE_GRADIENT_STOPS_CB if colorblind else SNAKE_GRADIENT_STOPS
    return build_lengthwise_gradient(length_px, height, stops)