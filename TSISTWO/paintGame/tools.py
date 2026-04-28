"""Tool implementations and application state for the Paint app.

This module defines ToolState (current active tool, brush size, text buffer,
etc.) and the central handler `handle_tool_event` which implements
the contract: mousedown / mousemove / mouseup events affecting the canvas
and an optional preview surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import pygame

from utils import apply_fill, draw_anti_aliased_line, draw_geometry_preview, draw_text_entry


TOOL_ORDER = [
    "pencil",
    "line",
    "rectangle",
    "circle",
    "shapes",
    "fill",
    "text",
    "eraser",
]

SHAPE_CHOICES = ["square", "right_triangle", "equilateral_triangle", "rhombus"]


@dataclass
class ToolState:
    active_tool: str = "pencil"
    shape_mode: str = "square"
    current_color: pygame.Color = field(default_factory=lambda: pygame.Color(35, 85, 160))
    brush_size: int = 5
    is_drawing: bool = False
    is_text_input: bool = False
    start_pos: pygame.Vector2 | None = None
    last_pos: pygame.Vector2 | None = None
    text_pos: pygame.Vector2 | None = None
    text_buffer: str = ""
    font: pygame.font.Font | None = None
    previous_tool: str | None = None
    last_end_pos: pygame.Vector2 | None = None  # for maintaining preview when not moving mouse

    def set_active_tool(self, tool_name: str) -> None:
        if tool_name in TOOL_ORDER:
            self.active_tool = tool_name
            if tool_name != "text":
                self.is_text_input = False

    def set_brush_size(self, brush_size: int) -> None:
        self.brush_size = brush_size

    def cycle_shape_mode(self) -> None:
        current_index = SHAPE_CHOICES.index(self.shape_mode)
        self.shape_mode = SHAPE_CHOICES[(current_index + 1) % len(SHAPE_CHOICES)]

    def set_shape_mode(self, shape_mode: str) -> None:
        if shape_mode in SHAPE_CHOICES:
            self.shape_mode = shape_mode

    def begin_temporary_tool(self, tool_name: str) -> None:
        self.previous_tool = self.active_tool
        self.set_active_tool(tool_name)

    def end_temporary_tool(self) -> None:
        if self.previous_tool is not None:
            self.active_tool = self.previous_tool
            self.previous_tool = None

    def start_text_input(self, position: pygame.Vector2, font: pygame.font.Font) -> None:
        self.active_tool = "text"
        self.is_text_input = True
        self.text_pos = position.copy()
        self.text_buffer = ""
        self.font = font

    def cancel_text_input(self) -> None:
        self.is_text_input = False
        self.text_buffer = ""
        self.text_pos = None
        self.last_end_pos = None

    def commit_text_input(self, canvas: pygame.Surface, canvas_topleft: tuple[int, int]) -> None:
        """Draw the buffered text onto the provided canvas.

        canvas_topleft is the screen coordinate of the canvas' top-left so the
        stored absolute text_pos can be converted into canvas-local coordinates.
        """
        if self.text_pos is not None and self.font is not None:
            local_pos = pygame.Vector2(int(self.text_pos.x - canvas_topleft[0]), int(self.text_pos.y - canvas_topleft[1]))
            draw_text_entry(canvas, self.font, self.text_buffer, local_pos, self.current_color)
        self.cancel_text_input()

    def handle_text_keydown(self, event: pygame.event.Event, canvas: pygame.Surface, canvas_rect: pygame.Rect) -> None:
        if not self.is_text_input:
            return
        if event.key == pygame.K_RETURN:
            self.commit_text_input(canvas, canvas_rect.topleft)
            return
        if event.key == pygame.K_BACKSPACE:
            self.text_buffer = self.text_buffer[:-1]
            return
        if event.unicode:
            self.text_buffer += event.unicode


def handle_tool_event(action: str, state: ToolState, canvas: pygame.Surface, position: pygame.Vector2, preview_surface: pygame.Surface) -> str:
    if state.active_tool == "fill" and action == "mousedown":
        apply_fill(canvas, position, state.current_color)
        return "Заливка выполнена"

    if state.active_tool == "text":
        if action == "mousedown" and not state.is_text_input:
            state.start_text_input(position, pygame.font.SysFont(None, 24))
            return "Введите текст и нажмите Enter"
        if action == "mousemove" and state.is_text_input:
            state.text_pos = position.copy()
            return "Позиция текста обновлена"
        if action == "mouseup" and state.is_text_input:
            return "Текст готов к вводу"
        return ""

    if action == "mousedown":
        state.is_drawing = True
        state.start_pos = position.copy()
        state.last_pos = position.copy()
        if state.active_tool == "pencil":
            pygame.draw.circle(canvas, state.current_color, position, max(1, state.brush_size // 2))
            return "Карандаш активен"
        if state.active_tool == "eraser":
            pygame.draw.circle(canvas, pygame.Color(245, 245, 240), position, max(1, state.brush_size // 2))
            return "Ластик активен"
        return f"Начало {state.active_tool}"

    if action == "mousemove" and state.is_drawing:
        if state.active_tool == "pencil":
            draw_anti_aliased_line(canvas, state.current_color, state.last_pos, position, state.brush_size)
            state.last_pos = position.copy()
            return "Рисование"
        if state.active_tool == "eraser":
            draw_anti_aliased_line(canvas, pygame.Color(245, 245, 240), state.last_pos, position, state.brush_size)
            state.last_pos = position.copy()
            return "Стирание"
        # for shapes: update last_end_pos to maintain preview when mouse stops
        state.last_end_pos = position.copy()
        draw_geometry_preview(preview_surface, canvas.get_rect().move(0, 0), state.active_tool, state.shape_mode, state.start_pos, position, state.current_color, state.brush_size)
        return "Предпросмотр фигуры"

    if action == "mouseup" and state.is_drawing:
        if state.active_tool == "line":
            pygame.draw.line(canvas, state.current_color, state.start_pos, position, state.brush_size)
        elif state.active_tool == "rectangle":
            draw_geometry_preview(preview_surface, canvas.get_rect().move(0, 0), state.active_tool, state.shape_mode, state.start_pos, position, state.current_color, state.brush_size, commit_to_canvas=canvas)
        elif state.active_tool == "circle":
            draw_geometry_preview(preview_surface, canvas.get_rect().move(0, 0), state.active_tool, state.shape_mode, state.start_pos, position, state.current_color, state.brush_size, commit_to_canvas=canvas)
        elif state.active_tool == "shapes":
            draw_geometry_preview(preview_surface, canvas.get_rect().move(0, 0), state.active_tool, state.shape_mode, state.start_pos, position, state.current_color, state.brush_size, commit_to_canvas=canvas)
        elif state.active_tool == "pencil":
            draw_anti_aliased_line(canvas, state.current_color, state.last_pos, position, state.brush_size)
        elif state.active_tool == "eraser":
            draw_anti_aliased_line(canvas, pygame.Color(245, 245, 240), state.last_pos, position, state.brush_size)
        state.is_drawing = False
        state.start_pos = None
        state.last_pos = None
        state.last_end_pos = None  # clear preview state
        preview_surface.fill((0, 0, 0, 0))
        return f"{state.active_tool} завершён"

    return ""