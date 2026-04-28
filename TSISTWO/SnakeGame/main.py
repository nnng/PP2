"""Entry point and screen switching."""

from __future__ import annotations

import sys

import pygame

from db import DatabaseClient, DatabaseError
from game import GameState, SnakeGame
from settings import SettingsManager
from ui import draw_text_center


def main() -> None:
    pygame.init()

    settings = SettingsManager().load()
    game = SnakeGame(settings)
    db = DatabaseClient.from_settings(settings)
    db_available = False
    last_save_status = ""

    try:
        db.connect()
        db_available = True
        try:
            db.ensure_tables()
        except DatabaseError as exc:
            # If schema already exists but current user is not owner,
            # inserts may still work, so we keep DB enabled.
            last_save_status = "DB connected (schema check warning)"
            print(f"Database schema check warning: {exc}")
    except DatabaseError as exc:
        last_save_status = "DB unavailable"
        print(f"Database is unavailable or not configured yet: {exc}")

    screen = pygame.display.set_mode((int(settings["window_width"]), int(settings["window_height"])))
    pygame.display.set_caption("Snake Game")

    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("consolas", 44)
    text_font = pygame.font.SysFont("consolas", 26)
    small_font = pygame.font.SysFont("consolas", 22)

    username_buffer = ""
    score_saved = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game.data.state == GameState.NAME_ENTRY:
                    if event.key == pygame.K_RETURN:
                        cleaned = username_buffer.strip()
                        if cleaned:
                            game.data.username = cleaned
                            username_buffer = cleaned
                            game.reset()
                            score_saved = False
                    elif event.key == pygame.K_BACKSPACE:
                        username_buffer = username_buffer[:-1]
                    else:
                        char = event.unicode
                        if char.isprintable() and len(username_buffer) < 20:
                            if char.isalnum() or char in "_-.":
                                username_buffer += char
                else:
                    game.handle_key(event.key)

        game.update()

        if game.data.state == GameState.GAME_OVER and not score_saved and game.data.username:
            try:
                if db_available:
                    db.save_session(game.data.username, game.data.score, game.data.level)
                    last_save_status = "Saved to DB"
                else:
                    last_save_status = "Not saved (DB offline)"
                score_saved = True
            except DatabaseError as exc:
                last_save_status = "Save failed"
                print(f"Failed to save session: {exc}")
                score_saved = True

        game.draw(screen, text_font)

        if game.data.state == GameState.MENU:
            draw_text_center(screen, "SNAKE", title_font, (245, 245, 245), screen.get_height() // 2 - 40)
            draw_text_center(screen, "Press Enter to enter username", text_font, (220, 220, 220), screen.get_height() // 2 + 20)
            draw_text_center(screen, "Esc to exit", text_font, (180, 180, 180), screen.get_height() // 2 + 60)
            if game.data.username:
                draw_text_center(screen, f"Current user: {game.data.username}", small_font, (190, 190, 190), screen.get_height() // 2 + 100)
        elif game.data.state == GameState.NAME_ENTRY:
            draw_text_center(screen, "Enter player name", title_font, (245, 245, 245), screen.get_height() // 2 - 60)
            draw_text_center(screen, username_buffer or "_", title_font, (120, 220, 120), screen.get_height() // 2)
            draw_text_center(screen, "Enter - start game", text_font, (220, 220, 220), screen.get_height() // 2 + 50)
            draw_text_center(screen, "Backspace - delete", small_font, (180, 180, 180), screen.get_height() // 2 + 88)
        elif game.data.state == GameState.GAME_OVER:
            draw_text_center(screen, "Game Over", title_font, (245, 120, 120), screen.get_height() // 2 - 50)
            draw_text_center(screen, f"Score: {game.data.score}", text_font, (230, 230, 230), screen.get_height() // 2)
            draw_text_center(screen, f"Saved as: {game.data.username or 'unknown'}", small_font, (200, 200, 200), screen.get_height() // 2 + 34)
            if last_save_status:
                draw_text_center(screen, last_save_status, small_font, (180, 210, 180), screen.get_height() // 2 + 52)
            draw_text_center(screen, "Press Enter for menu", text_font, (220, 220, 220), screen.get_height() // 2 + 70)

        pygame.display.flip()
        clock.tick(game.current_fps())

    db.close()
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
