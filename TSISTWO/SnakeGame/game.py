"""Core game loop logic and state transitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import pygame

from food import FoodManager
from snake import DOWN, LEFT, RIGHT, UP, Snake
from ui import draw_grid, draw_hud


class GameState(Enum):
    MENU = "menu"
    NAME_ENTRY = "name_entry"
    GAME = "game"
    GAME_OVER = "game_over"
    SETTINGS = "settings"
    LEADERBOARD = "leaderboard"


@dataclass
class GameData:
    state: GameState = GameState.MENU
    username: str = ""
    score: int = 0
    level: int = 1


class SnakeGame:
    def __init__(self, settings: dict) -> None:
        self.settings = settings
        self.cols = int(settings["grid_cols"])
        self.rows = int(settings["grid_rows"])
        self.window_width = int(settings["window_width"])
        self.window_height = int(settings["window_height"])
        self.cell_size = min(self.window_width // self.cols, self.window_height // self.rows)

        self.snake_color = tuple(settings["snake_color"])
        self.food_color = tuple(settings["food_color"])
        self.background_color = tuple(settings["background_color"])
        self.show_grid = bool(settings["show_grid"])
        self.base_fps = int(settings["base_fps"])
        self.level_up_food = int(settings["level_up_food"])

        self.data = GameData()
        self.snake: Snake | None = None
        self.food_manager: FoodManager | None = None

    def reset(self) -> None:
        self.data.score = 0
        self.data.level = 1
        self.data.state = GameState.GAME

        start_x = self.cols // 2
        start_y = self.rows // 2
        self.snake = Snake(start_x, start_y)
        self.food_manager = FoodManager(self.cols, self.rows)
        now = pygame.time.get_ticks()
        # spawn initial food(s)
        self.food_manager.spawn(self.snake.segments, now)

    def handle_key(self, key: int) -> None:
        if self.data.state == GameState.MENU and key == pygame.K_RETURN:
            self.data.state = GameState.NAME_ENTRY
            return

        if self.data.state == GameState.GAME_OVER and key == pygame.K_RETURN:
            self.data.state = GameState.MENU
            return

        if self.data.state != GameState.GAME or self.snake is None:
            return

        if key == pygame.K_UP:
            self.snake.set_direction(UP)
        elif key == pygame.K_DOWN:
            self.snake.set_direction(DOWN)
        elif key == pygame.K_LEFT:
            self.snake.set_direction(LEFT)
        elif key == pygame.K_RIGHT:
            self.snake.set_direction(RIGHT)

    def update(self) -> None:
        if self.data.state != GameState.GAME or self.snake is None or self.food_manager is None:
            return

        now = pygame.time.get_ticks()

        self.snake.move()
        hx, hy = self.snake.head

        if hx < 0 or hy < 0 or hx >= self.cols or hy >= self.rows:
            self.data.state = GameState.GAME_OVER
            return

        if self.snake.is_self_collision():
            self.data.state = GameState.GAME_OVER
            return

        # update foods TTL and remove expired
        if self.food_manager is not None:
            self.food_manager.update(now)
            item = self.food_manager.get_at(self.snake.head)
            if item is not None:
                # consume
                if item.kind == "poison":
                    # shrink by 2
                    self.snake.shrink(2)
                    if len(self.snake.segments) <= 1:
                        self.data.state = GameState.GAME_OVER
                        return
                else:
                    # normal/rare/disappearing: award points and grow
                    self.data.score += max(0, item.weight)
                    self.snake.grow(max(1, item.weight))

                # remove consumed item and spawn a new one
                self.food_manager.remove(item)
                self.food_manager.spawn(self.snake.segments, now)

                self.data.level = 1 + self.data.score // max(1, self.level_up_food)

    def current_fps(self) -> int:
        return self.base_fps + max(0, self.data.level - 1)

    def draw(self, surface: pygame.Surface, hud_font: pygame.font.Font) -> None:
        surface.fill(self.background_color)
        if self.data.state == GameState.GAME and self.snake is not None and self.food_manager is not None:
            if self.show_grid:
                draw_grid(surface, self.cols, self.rows, self.cell_size, (40, 40, 40))

            for x, y in self.snake.segments:
                pygame.draw.rect(
                    surface,
                    self.snake_color,
                    pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size),
                )

            # draw foods
            from ui import draw_foods
            if self.food_manager is not None:
                draw_foods(surface, self.food_manager.items, self.cell_size)

            draw_hud(surface, hud_font, self.data.score, self.data.level)
