from __future__ import annotations

import sys
from pathlib import Path

import pygame

from entities import CAR_COLORS, SCREEN_HEIGHT, SCREEN_WIDTH
from game import GameSession, InputState
from persistence import add_leaderboard_entry, load_leaderboard, load_settings, save_settings
from ui import Button, GameState, draw_hud, draw_panel, draw_title


def _build_menu_buttons() -> dict[str, Button]:
    center_x = SCREEN_WIDTH // 2 - 95
    return {
        "start": Button(pygame.Rect(center_x, 250, 190, 52), "Start Game"),
        "leaderboard": Button(pygame.Rect(center_x, 320, 190, 52), "Leaderboard"),
        "settings": Button(pygame.Rect(center_x, 390, 190, 52), "Settings"),
        "quit": Button(pygame.Rect(center_x, 460, 190, 52), "Quit"),
    }


def _build_back_button(y: int = 690) -> Button:
    return Button(pygame.Rect(20, y, 140, 46), "Back to Menu")


def _init_audio(assets_dir: Path) -> tuple[bool, pygame.mixer.Sound | None, pygame.mixer.Sound | None, pygame.mixer.Sound | None, pygame.mixer.Sound | None]:
    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
    except pygame.error:
        return False, None

    music_file = assets_dir / "bg_loop.wav"
    click_file = assets_dir / "ui_click.wav"
    coin_file = assets_dir / "coin.wav"
    hit_file = assets_dir / "hit.wav"
    power_file = assets_dir / "power.wav"

    click_sound: pygame.mixer.Sound | None = None
    coin_sound: pygame.mixer.Sound | None = None
    hit_sound: pygame.mixer.Sound | None = None
    power_sound: pygame.mixer.Sound | None = None

    try:
        if music_file.exists():
            pygame.mixer.music.load(str(music_file))
        if click_file.exists():
            click_sound = pygame.mixer.Sound(str(click_file))
        if coin_file.exists():
            coin_sound = pygame.mixer.Sound(str(coin_file))
        if hit_file.exists():
            hit_sound = pygame.mixer.Sound(str(hit_file))
        if power_file.exists():
            power_sound = pygame.mixer.Sound(str(power_file))
        return music_file.exists(), click_sound, coin_sound, hit_sound, power_sound
    except pygame.error:
        return False, None, None, None, None


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Racer Game")
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("arial", 48, bold=True)
    subtitle_font = pygame.font.SysFont("arial", 22)
    ui_font = pygame.font.SysFont("arial", 24)
    hud_font = pygame.font.SysFont("arial", 18)

    settings = load_settings()
    leaderboard = load_leaderboard()
    assets_dir = Path(__file__).resolve().parent / "assets"
    music_ready, click_sound, coin_sound, hit_sound, power_sound = _init_audio(assets_dir)

    def apply_sound_state() -> None:
        if not music_ready:
            return
        sound_on = bool(settings.get("sound", True))
        if sound_on:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()

    def play_click() -> None:
        if click_sound and bool(settings.get("sound", True)):
            click_sound.play()

    apply_sound_state()

    state = GameState.MENU
    username = "Player"
    username_active = False

    session: GameSession | None = None
    last_results: dict | None = None

    menu_buttons = _build_menu_buttons()
    back_button = _build_back_button()
    restart_button = Button(pygame.Rect(SCREEN_WIDTH // 2 - 95, 580, 190, 52), "Restart")

    car_colors = list(CAR_COLORS.keys())
    difficulties = ["easy", "normal", "hard"]

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        inputs = InputState()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if state == GameState.GAME:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = GameState.MENU
                    session = None

            elif state == GameState.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    name_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 185, 260, 40)
                    username_active = name_rect.collidepoint(event.pos)

                    if menu_buttons["start"].contains(event.pos):
                        play_click()
                        sfx = {"coin": coin_sound, "hit": hit_sound, "power": power_sound}
                        session = GameSession(settings, username, sfx=sfx)
                        state = GameState.GAME
                    elif menu_buttons["leaderboard"].contains(event.pos):
                        play_click()
                        leaderboard = load_leaderboard()
                        state = GameState.LEADERBOARD
                    elif menu_buttons["settings"].contains(event.pos):
                        play_click()
                        state = GameState.SETTINGS
                    elif menu_buttons["quit"].contains(event.pos):
                        play_click()
                        running = False

                if event.type == pygame.KEYDOWN and username_active:
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.key == pygame.K_RETURN:
                        username_active = False
                    elif len(username) < 16 and event.unicode.isprintable():
                        username += event.unicode

            elif state == GameState.GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_button.contains(event.pos):
                        play_click()
                        sfx = {"coin": coin_sound, "hit": hit_sound, "power": power_sound}
                        session = GameSession(settings, username, sfx=sfx)
                        state = GameState.GAME
                    elif back_button.contains(event.pos):
                        play_click()
                        state = GameState.MENU

            elif state in (GameState.LEADERBOARD, GameState.SETTINGS):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_button.contains(event.pos):
                        play_click()
                        state = GameState.MENU
                    elif state == GameState.SETTINGS:
                        sound_rect = pygame.Rect(80, 250, 320, 50)
                        color_rect = pygame.Rect(80, 320, 320, 50)
                        diff_rect = pygame.Rect(80, 390, 320, 50)

                        if sound_rect.collidepoint(event.pos):
                            play_click()
                            settings["sound"] = not bool(settings.get("sound", True))
                            save_settings(settings)
                            apply_sound_state()
                        elif color_rect.collidepoint(event.pos):
                            play_click()
                            current_color = settings.get("car_color", "red")
                            idx = car_colors.index(current_color) if current_color in car_colors else 0
                            settings["car_color"] = car_colors[(idx + 1) % len(car_colors)]
                            save_settings(settings)
                        elif diff_rect.collidepoint(event.pos):
                            play_click()
                            current_diff = settings.get("difficulty", "normal")
                            idx = difficulties.index(current_diff) if current_diff in difficulties else 1
                            settings["difficulty"] = difficulties[(idx + 1) % len(difficulties)]
                            save_settings(settings)

        if state == GameState.GAME and session:
            keys = pygame.key.get_pressed()
            inputs.move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            inputs.move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            inputs.move_up = keys[pygame.K_UP] or keys[pygame.K_w]
            inputs.move_down = keys[pygame.K_DOWN] or keys[pygame.K_s]

            session.update(dt, inputs)
            if session.finished:
                last_results = session.results()
                add_leaderboard_entry(
                    name=str(last_results["name"]),
                    score=int(last_results["score"]),
                    distance=int(last_results["distance"]),
                )
                leaderboard = load_leaderboard()
                state = GameState.GAME_OVER

        screen.fill((18, 22, 34))

        if state == GameState.MENU:
            draw_title(screen, title_font, subtitle_font)

            name_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 185, 260, 40)
            draw_panel(screen, pygame.Rect(52, 150, 376, 410))
            pygame.draw.rect(screen, (35, 45, 70), name_rect, border_radius=8)
            pygame.draw.rect(screen, (170, 190, 245), name_rect, 2, border_radius=8)
            name_label = ui_font.render(f"Username: {username or 'Player'}", True, (238, 243, 255))
            screen.blit(name_label, (name_rect.x + 8, name_rect.y + 8))

            for button in menu_buttons.values():
                button.draw(screen, ui_font, button.contains(mouse_pos))

        elif state == GameState.GAME and session:
            session.draw(screen)
            draw_hud(
                surface=screen,
                font=hud_font,
                username=str(session.username),
                score=int(session.score),
                coins=int(session.coins_collected),
                distance=int(session.distance),
                remaining=int(session.remaining_distance),
                active_power=session.active_power_kind,
                active_power_time=session.active_power_time,
            )

        elif state == GameState.GAME_OVER:
            draw_title(screen, title_font, subtitle_font)
            draw_panel(screen, pygame.Rect(52, 220, 376, 420))

            summary = last_results or {"score": 0, "distance": 0, "coins": 0}
            lines = [
                "Game Over",
                f"Score: {summary['score']}",
                f"Distance: {summary['distance']}",
                f"Coins: {summary['coins']}",
            ]
            y = 270
            for line in lines:
                label = ui_font.render(line, True, (240, 244, 255))
                screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, y))
                y += 48

            restart_button.draw(screen, ui_font, restart_button.contains(mouse_pos))
            back_button.draw(screen, ui_font, back_button.contains(mouse_pos))

        elif state == GameState.LEADERBOARD:
            draw_title(screen, title_font, subtitle_font)
            draw_panel(screen, pygame.Rect(40, 170, 400, 500))

            header = ui_font.render("Top 10 Players", True, (240, 244, 255))
            screen.blit(header, (SCREEN_WIDTH // 2 - header.get_width() // 2, 190))

            y = 240
            for idx, row in enumerate(leaderboard[:10], start=1):
                line = f"{idx:>2}. {row['name']:<16}  Score {row['score']:<5} Dist {row['distance']}"
                label = hud_font.render(line, True, (225, 230, 245))
                screen.blit(label, (56, y))
                y += 34

            back_button.draw(screen, ui_font, back_button.contains(mouse_pos))

        elif state == GameState.SETTINGS:
            draw_title(screen, title_font, subtitle_font)
            draw_panel(screen, pygame.Rect(52, 190, 376, 470))

            sound_rect = pygame.Rect(80, 250, 320, 50)
            color_rect = pygame.Rect(80, 320, 320, 50)
            diff_rect = pygame.Rect(80, 390, 320, 50)

            entries = [
                (sound_rect, f"Sound: {'On' if settings.get('sound', True) else 'Off'}"),
                (color_rect, f"Car Color: {settings.get('car_color', 'red')}"),
                (diff_rect, f"Difficulty: {settings.get('difficulty', 'normal')}"),
            ]

            for rect, text in entries:
                pygame.draw.rect(screen, (48, 62, 92), rect, border_radius=8)
                pygame.draw.rect(screen, (180, 200, 245), rect, 2, border_radius=8)
                label = ui_font.render(text, True, (242, 245, 255))
                screen.blit(label, (rect.x + 12, rect.y + 12))

            hint = hud_font.render("Click setting row to cycle values", True, (208, 220, 240))
            screen.blit(hint, (92, 470))
            back_button.draw(screen, ui_font, back_button.contains(mouse_pos))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
