"""
Mechanics layer: spawning, difficulty scaling and road drawing.

This module implements game-specific rules such as safe-spawn checks,
coin type selection, obstacle and power-up generation and difficulty
scaling based on player progress.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from entities import (
    LANE_COUNT,
    LANE_WIDTH,
    ROAD_LEFT,
    ROAD_RIGHT,
    Coin,
    EnemyCar,
    Obstacle,
    PowerUp,
    lane_centers,
)

COIN_TYPES: list[tuple[str, int, tuple[int, int, int], float]] = [
    ("common", 1, (246, 208, 92), 0.72),
    ("rare", 5, (123, 208, 255), 0.22),
    ("epic", 10, (255, 140, 90), 0.06),
]

POWERUP_TYPES: dict[str, tuple[int, int, int]] = {
    "nitro": (255, 130, 70),
    "shield": (120, 210, 255),
    "repair": (140, 220, 130),
}

OBSTACLE_COLORS = {
    "pothole": (80, 80, 80),
    "oil": (25, 25, 25),
    "slow_zone": (110, 80, 130),
    "moving_barrier": (220, 130, 60),
    "nitro_strip": (255, 180, 70),
}


@dataclass
class SpawnState:
    enemy_timer: float = 0.0
    coin_timer: float = 0.0
    obstacle_timer: float = 0.0
    powerup_timer: float = 0.0


@dataclass
class DifficultyState:
    enemy_speed_bonus: float = 0.0
    spawn_multiplier: float = 1.0


def _lane_x(lane_index: int, width: int) -> int:
    center = lane_centers()[lane_index]
    return center - width // 2


def _safe_lane_indexes(forbidden_rect: pygame.Rect, y_spawn: int, object_width: int, object_height: int) -> list[int]:
    safe: list[int] = []
    for lane_idx in range(LANE_COUNT):
        probe = pygame.Rect(_lane_x(lane_idx, object_width), y_spawn, object_width, object_height)
        if not probe.colliderect(forbidden_rect.inflate(12, 140)):
            safe.append(lane_idx)
    return safe


def spawn_enemy(forbidden_rect: pygame.Rect, base_speed: float, speed_bonus: float) -> EnemyCar | None:
    width, height = 46, 80
    y_spawn = -height - random.randint(10, 120)
    safe_lanes = _safe_lane_indexes(forbidden_rect, y_spawn, width, height)
    if not safe_lanes:
        return None
    lane = random.choice(safe_lanes)
    rect = pygame.Rect(_lane_x(lane, width), y_spawn, width, height)
    speed = base_speed + speed_bonus + random.uniform(-18, 28)
    return EnemyCar(rect=rect, speed=speed, color=(190, 60, 60))


def choose_coin_type() -> tuple[str, int, tuple[int, int, int]]:
    roll = random.random()
    threshold = 0.0
    for name, value, color, chance in COIN_TYPES:
        threshold += chance
        if roll <= threshold:
            return name, value, color
    name, value, color, _ = COIN_TYPES[0]
    return name, value, color


def spawn_coin(forbidden_rect: pygame.Rect, world_speed: float) -> Coin | None:
    width = height = 22
    y_spawn = -height - random.randint(15, 140)
    safe_lanes = _safe_lane_indexes(forbidden_rect, y_spawn, width, height)
    if not safe_lanes:
        return None
    lane = random.choice(safe_lanes)
    _, value, color = choose_coin_type()
    rect = pygame.Rect(_lane_x(lane, width), y_spawn, width, height)
    return Coin(rect=rect, speed=world_speed, color=color, value=value, radius=width // 2)


def spawn_obstacle(forbidden_rect: pygame.Rect, world_speed: float) -> Obstacle | None:
    obstacle_kind = random.choices(
        population=["pothole", "oil", "slow_zone", "moving_barrier", "nitro_strip"],
        weights=[0.28, 0.23, 0.2, 0.18, 0.11],
        k=1,
    )[0]

    if obstacle_kind == "moving_barrier":
        width, height = 86, 26
    elif obstacle_kind == "nitro_strip":
        width, height = 78, 18
    else:
        width, height = 52, 32

    y_spawn = -height - random.randint(20, 180)
    safe_lanes = _safe_lane_indexes(forbidden_rect, y_spawn, width, height)
    if not safe_lanes:
        return None

    lane = random.choice(safe_lanes)
    rect = pygame.Rect(_lane_x(lane, width), y_spawn, width, height)
    dx = random.choice([-160.0, 160.0]) if obstacle_kind == "moving_barrier" else 0.0
    return Obstacle(rect=rect, speed=world_speed, color=OBSTACLE_COLORS[obstacle_kind], kind=obstacle_kind, dx=dx)


def spawn_powerup(forbidden_rect: pygame.Rect, world_speed: float) -> PowerUp | None:
    width = height = 28
    y_spawn = -height - random.randint(40, 220)
    safe_lanes = _safe_lane_indexes(forbidden_rect, y_spawn, width, height)
    if not safe_lanes:
        return None

    lane = random.choice(safe_lanes)
    kind = random.choice(list(POWERUP_TYPES.keys()))
    rect = pygame.Rect(_lane_x(lane, width), y_spawn, width, height)
    # Give spawned power-ups a limited lifetime (seconds)
    power = PowerUp(rect=rect, speed=world_speed - 25, color=POWERUP_TYPES[kind], kind=kind)
    # Default life: 8 seconds on the road before it vanishes
    power.life = 8.0
    return power


def update_difficulty(coins_collected: int) -> DifficultyState:
    stage = coins_collected // 8
    speed_bonus = min(140.0, stage * 12.0)
    spawn_multiplier = min(1.8, 1.0 + stage * 0.05)
    return DifficultyState(enemy_speed_bonus=speed_bonus, spawn_multiplier=spawn_multiplier)


def apply_obstacle_effect(kind: str, timers: dict[str, float]) -> None:
    if kind == "oil":
        timers["oil_slip"] = max(timers.get("oil_slip", 0.0), 1.2)
    elif kind == "slow_zone":
        timers["slow_zone"] = max(timers.get("slow_zone", 0.0), 1.8)
    elif kind == "nitro_strip":
        timers["nitro_strip"] = max(timers.get("nitro_strip", 0.0), 1.5)


def clean_offscreen(items: list, screen_height: int) -> list:
    return [item for item in items if item.rect.top <= screen_height + 40]


def draw_road(surface: pygame.Surface, offset: float) -> None:
    surface.fill((20, 125, 30))
    pygame.draw.rect(surface, (55, 55, 55), (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, surface.get_height()))

    stripe_color = (230, 230, 230)
    stripe_w = 8
    stripe_h = 34
    gap = 30

    for lane in range(1, LANE_COUNT):
        x = ROAD_LEFT + lane * LANE_WIDTH - stripe_w // 2
        y = int(-offset % (stripe_h + gap)) - (stripe_h + gap)
        while y < surface.get_height():
            pygame.draw.rect(surface, stripe_color, (x, y, stripe_w, stripe_h), border_radius=3)
            y += stripe_h + gap
