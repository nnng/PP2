"""
Entities module: defines all in-game object classes and world constants.

This file contains simple data classes representing the Player, EnemyCar,
Coin, Obstacle and PowerUp. Each entity exposes `update` and `draw` methods
that the game loop calls every frame.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from random import choice

import pygame

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
ROAD_LEFT = 80
ROAD_RIGHT = 400
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_COUNT = 3
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT

CAR_COLORS = {
    "red": (220, 50, 50),
    "blue": (70, 100, 220),
    "green": (60, 180, 90),
    "yellow": (220, 180, 70),
}


@dataclass
class BaseEntity:
    rect: pygame.Rect
    speed: float
    color: tuple[int, int, int]

    def update(self, dt: float) -> None:
        self.rect.y += int(self.speed * dt)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)


@dataclass
class Player(BaseEntity):
    move_speed: float = 280.0
    control_multiplier: float = 1.0
    drift_velocity_x: float = 0.0

    def move(self, direction_x: float, direction_y: float, dt: float) -> None:
        delta_x = int((direction_x * self.move_speed * self.control_multiplier + self.drift_velocity_x) * dt)
        delta_y = int(direction_y * self.move_speed * dt)
        self.rect.x += delta_x
        self.rect.y += delta_y
        self.rect.x = max(ROAD_LEFT + 6, min(self.rect.x, ROAD_RIGHT - self.rect.width - 6))
        self.rect.y = max(40, min(self.rect.y, SCREEN_HEIGHT - self.rect.height - 30))


@dataclass
class EnemyCar(BaseEntity):
    pass


@dataclass
class Coin(BaseEntity):
    value: int = 1
    radius: int = 10

    def draw(self, surface: pygame.Surface) -> None:
        center = self.rect.center
        pygame.draw.circle(surface, self.color, center, self.radius)
        pygame.draw.circle(surface, (40, 40, 40), center, self.radius, 2)


@dataclass
class Obstacle(BaseEntity):
    kind: str = "pothole"
    dx: float = 0.0

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.kind == "moving_barrier":
            self.rect.x += int(self.dx * dt)
            if self.rect.left <= ROAD_LEFT + 4:
                self.rect.left = ROAD_LEFT + 4
                self.dx *= -1
            if self.rect.right >= ROAD_RIGHT - 4:
                self.rect.right = ROAD_RIGHT - 4
                self.dx *= -1


@dataclass
class PowerUp(BaseEntity):
    kind: str = "nitro"
    # lifetime in seconds: how long the power-up remains on the road
    life: float = 8.0

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        icon = {
            "nitro": "N",
            "shield": "S",
            "repair": "R",
        }.get(self.kind, "?")
        font = pygame.font.SysFont("arial", 16, bold=True)
        text = font.render(icon, True, (10, 10, 10))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def update(self, dt: float) -> None:
        """Move the power-up downwards and decrease its lifetime.

        When `life` reaches zero the game should remove this object.
        """
        # Move like a standard BaseEntity
        super().update(dt)
        # Decrease lifetime
        self.life -= dt


@dataclass
class ActivePower:
    kind: str
    remaining_time: float


@dataclass
class EffectTimers:
    oil_slip: float = 0.0
    slow_zone: float = 0.0
    nitro_strip: float = 0.0

    def decay(self, dt: float) -> None:
        self.oil_slip = max(0.0, self.oil_slip - dt)
        self.slow_zone = max(0.0, self.slow_zone - dt)
        self.nitro_strip = max(0.0, self.nitro_strip - dt)


def lane_centers() -> list[int]:
    return [ROAD_LEFT + LANE_WIDTH // 2 + LANE_WIDTH * idx for idx in range(LANE_COUNT)]


def make_player(car_color_name: str = "red") -> Player:
    width, height = 48, 84
    rect = pygame.Rect(0, 0, width, height)
    rect.centerx = lane_centers()[1]
    rect.bottom = SCREEN_HEIGHT - 35
    color = CAR_COLORS.get(car_color_name, CAR_COLORS["red"])
    return Player(rect=rect, speed=0.0, color=color)


def random_car_color() -> tuple[int, int, int]:
    return choice(list(CAR_COLORS.values()))
