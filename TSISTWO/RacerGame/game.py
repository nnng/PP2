"""
Game runtime: `GameSession` represents one playthrough.

Responsibilities:
- maintain lists of entities (enemies, coins, obstacles, powerups)
- update world state and handle collisions
- apply power-up effects and timers
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from entities import SCREEN_HEIGHT, SCREEN_WIDTH, Coin, EnemyCar, Obstacle, PowerUp, make_player
from mechanics import (
    SpawnState,
    apply_obstacle_effect,
    clean_offscreen,
    draw_road,
    spawn_coin,
    spawn_enemy,
    spawn_obstacle,
    spawn_powerup,
    update_difficulty,
)


@dataclass
class InputState:
    move_left: bool = False
    move_right: bool = False
    move_up: bool = False
    move_down: bool = False


class GameSession:
    def __init__(self, settings: dict, username: str, sfx: dict | None = None) -> None:
        self.settings = settings
        self.username = username if username.strip() else "Player"

        self.player = make_player(settings.get("car_color", "red"))
        self.enemies: list[EnemyCar] = []
        self.coins: list[Coin] = []
        self.obstacles: list[Obstacle] = []
        self.powerups: list[PowerUp] = []

        self.spawn_state = SpawnState()
        self.road_offset = 0.0
        self.timer_effects = {"oil_slip": 0.0, "slow_zone": 0.0, "nitro_strip": 0.0}

        self.coins_collected = 0
        self.coin_score = 0
        self.bonus_score = 0
        self.distance = 0.0

        self.active_power_kind: str | None = None
        self.active_power_time = 0.0
        self.has_shield_charge = False

        self.finished = False
        self.target_distance = int(settings.get("target_distance", 5000))
        # optional sound effects mapping: names -> pygame.mixer.Sound
        self.sfx = sfx or {}

        difficulty_name = settings.get("difficulty", "normal")
        profiles = settings.get("difficulty_profiles", {})
        profile = profiles.get(difficulty_name, profiles.get("normal", {}))

        self.base_enemy_speed = float(profile.get("enemy_speed_base", 220))
        self.enemy_spawn_interval = float(profile.get("enemy_spawn_interval", 1.0))
        self.obstacle_spawn_interval = float(profile.get("obstacle_spawn_interval", 1.7))
        self.coin_spawn_interval = float(profile.get("coin_spawn_interval", 0.8))
        self.powerup_spawn_interval = float(profile.get("powerup_spawn_interval", 6.5))

    @property
    def score(self) -> int:
        distance_points = int(self.distance // 8)
        return self.coin_score + distance_points + self.bonus_score

    @property
    def remaining_distance(self) -> int:
        return max(0, self.target_distance - int(self.distance))

    def _handle_player_input(self, inputs: InputState, dt: float) -> None:
        direction_x = float(inputs.move_right) - float(inputs.move_left)
        direction_y = float(inputs.move_down) - float(inputs.move_up)

        control_mult = 1.0
        drift = 0.0

        if self.timer_effects["oil_slip"] > 0:
            control_mult = 0.65
            drift = 75.0
        if self.timer_effects["slow_zone"] > 0:
            control_mult *= 0.75
        if self.timer_effects["nitro_strip"] > 0:
            control_mult *= 1.2

        if self.active_power_kind == "nitro":
            control_mult *= 1.35

        self.player.control_multiplier = control_mult
        self.player.drift_velocity_x = drift if direction_x >= 0 else -drift
        self.player.move(direction_x, direction_y, dt)

    def _decay_timers(self, dt: float) -> None:
        for key in self.timer_effects:
            self.timer_effects[key] = max(0.0, self.timer_effects[key] - dt)

        if self.active_power_kind:
            self.active_power_time -= dt
            if self.active_power_time <= 0:
                self.active_power_kind = None
                self.active_power_time = 0.0

    def _spawn_entities(self, dt: float) -> None:
        difficulty = update_difficulty(self.coins_collected)
        spawn_factor = difficulty.spawn_multiplier

        self.spawn_state.enemy_timer += dt
        self.spawn_state.coin_timer += dt
        self.spawn_state.obstacle_timer += dt
        self.spawn_state.powerup_timer += dt

        if self.spawn_state.enemy_timer >= self.enemy_spawn_interval / spawn_factor:
            enemy = spawn_enemy(self.player.rect, self.base_enemy_speed, difficulty.enemy_speed_bonus)
            if enemy:
                self.enemies.append(enemy)
            self.spawn_state.enemy_timer = 0.0

        if self.spawn_state.coin_timer >= self.coin_spawn_interval:
            coin = spawn_coin(self.player.rect, self.base_enemy_speed * 0.95)
            if coin:
                self.coins.append(coin)
            self.spawn_state.coin_timer = 0.0

        if self.spawn_state.obstacle_timer >= self.obstacle_spawn_interval / max(1.0, spawn_factor * 0.9):
            obstacle = spawn_obstacle(self.player.rect, self.base_enemy_speed * 0.9)
            if obstacle:
                self.obstacles.append(obstacle)
            self.spawn_state.obstacle_timer = 0.0

        if self.spawn_state.powerup_timer >= self.powerup_spawn_interval:
            power = spawn_powerup(self.player.rect, self.base_enemy_speed * 0.75)
            if power:
                self.powerups.append(power)
            self.spawn_state.powerup_timer = 0.0

    def _update_world(self, dt: float) -> None:
        world_speed = self.base_enemy_speed
        if self.active_power_kind == "nitro":
            world_speed *= 1.1
        if self.timer_effects["slow_zone"] > 0:
            world_speed *= 0.85

        self.road_offset += world_speed * dt
        self.distance += world_speed * dt * 0.15

        for group in (self.enemies, self.coins, self.obstacles, self.powerups):
            for item in group:
                item.update(dt)

        # Remove objects that went off-screen
        self.enemies = clean_offscreen(self.enemies, SCREEN_HEIGHT)
        self.coins = clean_offscreen(self.coins, SCREEN_HEIGHT)
        self.obstacles = clean_offscreen(self.obstacles, SCREEN_HEIGHT)

        # Power-ups also expire after their lifetime elapses; remove if expired or offscreen
        remaining_powerups: list[PowerUp] = []
        for p in self.powerups:
            life = getattr(p, "life", None)
            if life is not None and life <= 0:
                # expired
                continue
            if p.rect.top > SCREEN_HEIGHT + 40:
                continue
            remaining_powerups.append(p)
        self.powerups = remaining_powerups

    def _activate_powerup(self, kind: str) -> None:
        self.active_power_kind = kind
        durations = {"nitro": 3.0, "shield": 5.0, "repair": 0.2}
        self.active_power_time = durations.get(kind, 2.0)

        if kind == "shield":
            self.has_shield_charge = True
            self.bonus_score += 20
        elif kind == "nitro":
            self.bonus_score += 15
        elif kind == "repair":
            # Repair clears current debuffs and gives a small score bonus.
            self.timer_effects["oil_slip"] = 0.0
            self.timer_effects["slow_zone"] = 0.0
            self.bonus_score += 25

    def _handle_collisions(self) -> None:
        for coin in list(self.coins):
            if coin.rect.colliderect(self.player.rect):
                self.coins.remove(coin)
                self.coins_collected += 1
                self.coin_score += coin.value * 10
                # play coin SFX if available and sound enabled
                snd = self.sfx.get("coin")
                if snd and bool(self.settings.get("sound", True)):
                    try:
                        snd.play()
                    except Exception:
                        pass

        for power in list(self.powerups):
            if power.rect.colliderect(self.player.rect):
                self.powerups.remove(power)
                self._activate_powerup(power.kind)
                snd = self.sfx.get("power")
                if snd and bool(self.settings.get("sound", True)):
                    try:
                        snd.play()
                    except Exception:
                        pass

        for obstacle in list(self.obstacles):
            if obstacle.rect.colliderect(self.player.rect):
                if obstacle.kind == "pothole":
                    self.bonus_score = max(0, self.bonus_score - 10)
                apply_obstacle_effect(obstacle.kind, self.timer_effects)
                self.obstacles.remove(obstacle)
                snd = self.sfx.get("hit")
                if snd and bool(self.settings.get("sound", True)):
                    try:
                        snd.play()
                    except Exception:
                        pass

        for enemy in list(self.enemies):
            if enemy.rect.colliderect(self.player.rect):
                if self.has_shield_charge or self.active_power_kind == "shield":
                    self.has_shield_charge = False
                    self.active_power_kind = None
                    self.active_power_time = 0.0
                    self.enemies.remove(enemy)
                    self.bonus_score += 10
                    snd = self.sfx.get("hit")
                    if snd and bool(self.settings.get("sound", True)):
                        try:
                            snd.play()
                        except Exception:
                            pass
                else:
                    self.finished = True
                    return

    def update(self, dt: float, inputs: InputState) -> None:
        if self.finished:
            return

        self._decay_timers(dt)
        self._handle_player_input(inputs, dt)
        self._spawn_entities(dt)
        self._update_world(dt)
        self._handle_collisions()

    def draw(self, surface: pygame.Surface) -> None:
        draw_road(surface, self.road_offset)
        for group in (self.obstacles, self.coins, self.powerups, self.enemies):
            for item in group:
                item.draw(surface)
        self.player.draw(surface)

    def results(self) -> dict[str, int | str]:
        return {
            "name": self.username,
            "score": self.score,
            "distance": int(self.distance),
            "coins": self.coins_collected,
        }
