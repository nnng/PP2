from __future__ import annotations

import sys
import pygame

from tools import ToolState, handle_tool_event
from ui import ColorPalette, build_toolbar, draw_status_bar, draw_toolbar, hit_test_color, hit_test_shape_button, hit_test_tool
from utils import create_canvas, create_status_font, save_canvas


WIDTH = 1200
HEIGHT = 800
TOOLBAR_HEIGHT = 88
STATUS_BAR_HEIGHT = 32
CANVAS_TOP = TOOLBAR_HEIGHT
CANVAS_RECT = pygame.Rect(0, CANVAS_TOP, WIDTH, HEIGHT - TOOLBAR_HEIGHT - STATUS_BAR_HEIGHT)
BACKGROUND_COLOR = pygame.Color(245, 245, 240)
PANEL_COLOR = pygame.Color(32, 36, 44)
STATUS_COLOR = pygame.Color(24, 27, 32)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Paint TSIS")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    status_font = create_status_font()

    canvas = create_canvas(CANVAS_RECT.size, BACKGROUND_COLOR)
    state = ToolState()
    toolbar = build_toolbar()
    palette = ColorPalette()
    status_message = "ЛКМ: рисование | 1/2/3: размер кисти | Ctrl+S: сохранить"
    preview_surface = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)

    running = True
    # main loop
    while running:
        # clear preview each frame; preview is repopulated during mousemove or text input
        preview_surface.fill((0, 0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state.is_text_input:
                        state.cancel_text_input()
                        status_message = "Ввод текста отменён"
                    else:
                        running = False
                    continue

                # handle text input first — skip all other hotkeys during text entry
                if state.is_text_input:
                    state.handle_text_keydown(event, canvas, CANVAS_RECT)
                    continue

                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    state.set_brush_size({pygame.K_1: 2, pygame.K_2: 5, pygame.K_3: 10}[event.key])
                    status_message = f"Размер кисти: {state.brush_size}px"
                    continue

                if event.key == pygame.K_4:
                    state.cycle_shape_mode()
                    status_message = f"Фигура: {state.shape_mode}"
                    continue

                # tool hotkeys (lowercase)
                key_name = pygame.key.name(event.key)
                key_map = {
                    'p': 'pencil',
                    'l': 'line',
                    'r': 'rectangle',
                    'c': 'circle',
                    'h': 'shapes',
                    'e': 'eraser',
                    'f': 'fill',
                    't': 'text',
                }
                if key_name in key_map:
                    state.set_active_tool(key_map[key_name])
                    status_message = f"Инструмент: {state.active_tool}"
                    continue

                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    saved_path = save_canvas(canvas)
                    status_message = f"Сохранено: {saved_path.name}"
                    continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # convert screen coords to canvas-relative
                    canvas_rel_x = event.pos[0] - CANVAS_RECT.left
                    canvas_rel_y = event.pos[1] - CANVAS_RECT.top
                    mouse_pos = pygame.Vector2(
                        max(0, min(int(canvas_rel_x), CANVAS_RECT.width - 1)),
                        max(0, min(int(canvas_rel_y), CANVAS_RECT.height - 1))
                    )
                    shape_hit = hit_test_shape_button(event.pos)
                    if shape_hit is not None:
                        state.set_shape_mode(shape_hit)
                        state.set_active_tool("shapes")
                        status_message = f"Фигура: {shape_hit}"
                        continue

                    tool_hit = hit_test_tool(toolbar, event.pos)
                    if tool_hit is not None:
                        state.set_active_tool(tool_hit)
                        status_message = f"Инструмент: {tool_hit}"
                        continue

                    color_hit = hit_test_color(palette, event.pos)
                    if color_hit is not None:
                        state.current_color = color_hit
                        status_message = f"Цвет: {color_hit}"
                        continue

                    if CANVAS_RECT.collidepoint(event.pos):
                        preview_surface.fill((0, 0, 0, 0))
                        status_message = handle_tool_event("mousedown", state, canvas, mouse_pos, preview_surface)

                elif event.button == 3:
                    if CANVAS_RECT.collidepoint(event.pos):
                        canvas_rel_x = event.pos[0] - CANVAS_RECT.left
                        canvas_rel_y = event.pos[1] - CANVAS_RECT.top
                        mouse_pos = pygame.Vector2(
                            max(0, min(int(canvas_rel_x), CANVAS_RECT.width - 1)),
                            max(0, min(int(canvas_rel_y), CANVAS_RECT.height - 1))
                        )
                        state.begin_temporary_tool("eraser")
                        status_message = handle_tool_event("mousedown", state, canvas, mouse_pos, preview_surface)

            elif event.type == pygame.MOUSEMOTION:
                if state.is_drawing or state.is_text_input:
                    canvas_rel_x = event.pos[0] - CANVAS_RECT.left
                    canvas_rel_y = event.pos[1] - CANVAS_RECT.top
                    mouse_pos = pygame.Vector2(
                        max(0, min(int(canvas_rel_x), CANVAS_RECT.width - 1)),
                        max(0, min(int(canvas_rel_y), CANVAS_RECT.height - 1))
                    )
                    state.last_end_pos = mouse_pos.copy()  # save for preview redraw
                    status_message = handle_tool_event("mousemove", state, canvas, mouse_pos, preview_surface)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and (state.is_drawing or state.is_text_input):
                    canvas_rel_x = event.pos[0] - CANVAS_RECT.left
                    canvas_rel_y = event.pos[1] - CANVAS_RECT.top
                    mouse_pos = pygame.Vector2(
                        max(0, min(int(canvas_rel_x), CANVAS_RECT.width - 1)),
                        max(0, min(int(canvas_rel_y), CANVAS_RECT.height - 1))
                    )
                    status_message = handle_tool_event("mouseup", state, canvas, mouse_pos, preview_surface)
                elif event.button == 3:
                    state.end_temporary_tool()

        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, PANEL_COLOR, pygame.Rect(0, 0, WIDTH, TOOLBAR_HEIGHT))
        pygame.draw.rect(screen, STATUS_COLOR, pygame.Rect(0, HEIGHT - STATUS_BAR_HEIGHT, WIDTH, STATUS_BAR_HEIGHT))

        draw_toolbar(screen, toolbar, palette, state)
        draw_status_bar(screen, status_font, status_message, state, HEIGHT - STATUS_BAR_HEIGHT)

        # draw canvas and live preview (preview_surface contains transient previews and text input)
        screen.blit(canvas, CANVAS_RECT.topleft)

        # redraw preview each frame if drawing a shape (maintains preview when mouse stops)
        if state.is_drawing and state.start_pos is not None and state.last_end_pos is not None:
            if state.active_tool in ['line', 'rectangle', 'circle', 'shapes']:
                from utils import draw_geometry_preview
                preview_surface.fill((0, 0, 0, 0))
                draw_geometry_preview(preview_surface, CANVAS_RECT, state.active_tool, state.shape_mode,
                                     state.start_pos, state.last_end_pos, state.current_color, state.brush_size)

        # if in text input mode, render the buffer onto preview_surface so user sees typing feedback
        if state.is_text_input and state.text_pos is not None:
            preview_surface.fill((0, 0, 0, 0))
            font = state.font or pygame.font.SysFont(None, 24)
            # render with current color
            text_surf = font.render(state.text_buffer or "|", True, state.current_color)
            # position is relative to canvas, preview_surface uses same coordinate space
            preview_surface.blit(text_surf, (int(state.text_pos.x - CANVAS_RECT.left), int(state.text_pos.y - CANVAS_RECT.top)))

        screen.blit(preview_surface, CANVAS_RECT.topleft)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()