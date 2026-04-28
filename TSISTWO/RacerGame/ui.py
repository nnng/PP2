"""
UI helpers: buttons, game state enum and HUD rendering.

This module centralizes small UI primitives used by `main.py`:
- `GameState` enum describing the application screens
- `Button` helper with `draw` and `contains`
- helper functions to draw title, panels and the HUD
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import pygame


class GameState(Enum):
    MENU = auto()
    GAME = auto()
    GAME_OVER = auto()
    LEADERBOARD = auto()
    SETTINGS = auto()


@dataclass
class Button:
    rect: pygame.Rect
    text: str

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, hovered: bool = False) -> None:
        bg_color = (90, 100, 150) if hovered else (70, 80, 120)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (210, 220, 245), self.rect, 2, border_radius=10)
        label = font.render(self.text, True, (240, 245, 255))
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


def draw_title(surface: pygame.Surface, title_font: pygame.font.Font, subtitle_font: pygame.font.Font) -> None:
    title = title_font.render("RACER GAME", True, (245, 245, 255))
    subtitle = subtitle_font.render("Dodge, collect, survive", True, (210, 220, 240))
    surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, 80))
    surface.blit(subtitle, (surface.get_width() // 2 - subtitle.get_width() // 2, 130))


def draw_panel(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surface, (28, 33, 47), rect, border_radius=14)
    pygame.draw.rect(surface, (105, 123, 170), rect, 2, border_radius=14)


def draw_hud(
    surface: pygame.Surface,
    font: pygame.font.Font,
    username: str,
    score: int,
    coins: int,
    distance: int,
    remaining: int,
    active_power: str | None,
    active_power_time: float,
) -> None:
    texts = [
        f"Player: {username}",
        f"Score: {score}",
        f"Coins: {coins}",
        f"Distance: {distance}",
        f"Remaining: {remaining}",
    ]

    if active_power:
        texts.append(f"Power: {active_power} ({active_power_time:.1f}s)")
    else:
        texts.append("Power: none")

    y = 10
    for line in texts:
        label = font.render(line, True, (240, 240, 250))
        bg_rect = pygame.Rect(surface.get_width() - 190, y - 2, 180, 22)
        pygame.draw.rect(surface, (20, 25, 35), bg_rect, border_radius=5)
        surface.blit(label, (surface.get_width() - 184, y))
        y += 24
