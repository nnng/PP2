"""UI rendering helpers for screens and HUD."""

from __future__ import annotations

import pygame


def draw_grid(surface: pygame.Surface, cols: int, rows: int, cell_size: int, color: tuple[int, int, int]) -> None:
    width = cols * cell_size
    height = rows * cell_size
    for x in range(0, width, cell_size):
        pygame.draw.line(surface, color, (x, 0), (x, height))
    for y in range(0, height, cell_size):
        pygame.draw.line(surface, color, (0, y), (width, y))


def draw_text_center(surface: pygame.Surface, text: str, font: pygame.font.Font, color: tuple[int, int, int], y: int) -> None:
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(text_surface, rect)


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, score: int, level: int) -> None:
    hud = f"Score: {score}    Level: {level}"
    text_surface = font.render(hud, True, (240, 240, 240))
    surface.blit(text_surface, (12, 8))


def draw_foods(surface: pygame.Surface, items, cell_size: int) -> None:
    """Draw FoodItem list created by FoodManager with distinct colors per type."""
    for it in items:
        x, y = it.position
        rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
        if it.kind == "normal":
            color = (231, 76, 60)
        elif it.kind == "rare":
            color = (241, 196, 15)  # gold
        elif it.kind == "disappearing":
            color = (230, 126, 34)  # orange
        elif it.kind == "poison":
            color = (150, 0, 0)  # dark red
        else:
            color = (200, 200, 200)
        pygame.draw.rect(surface, color, rect)
