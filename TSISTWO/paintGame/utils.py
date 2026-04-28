"""Utility helpers: canvas creation, saving, simple geometry helpers and flood-fill.

These helpers are intentionally small and self-contained so they can be
unit-tested independently from the UI.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime
from pathlib import Path

import pygame


def create_canvas(size: tuple[int, int], fill_color: pygame.Color) -> pygame.Surface:
    canvas = pygame.Surface(size)
    canvas.fill(fill_color)
    return canvas.convert()


def create_status_font() -> pygame.font.Font:
    return pygame.font.SysFont(None, 22)


def format_color(color: pygame.Color) -> str:
    return f"rgb({color.r}, {color.g}, {color.b})"


def clamp_point(position: tuple[int, int], rect: pygame.Rect) -> pygame.Vector2:
    x = min(max(position[0], rect.left), rect.right - 1)
    y = min(max(position[1], rect.top), rect.bottom - 1)
    return pygame.Vector2(x, y)


def save_canvas(canvas: pygame.Surface, folder: Path | None = None) -> Path:
    target_folder = folder or Path.cwd() / "exports"
    target_folder.mkdir(parents=True, exist_ok=True)
    filename = datetime.now().strftime("paint_%Y-%m-%d_%H-%M-%S.png")
    target_path = target_folder / filename
    pygame.image.save(canvas, target_path)
    return target_path


def draw_anti_aliased_line(canvas: pygame.Surface, color: pygame.Color, start: pygame.Vector2 | None, end: pygame.Vector2, thickness: int) -> None:
    if start is None:
        return
    pygame.draw.line(canvas, color, start, end, thickness)


def normalize_drag(start_pos: pygame.Vector2, end_pos: pygame.Vector2) -> pygame.Rect:
    rect = pygame.Rect(int(start_pos.x), int(start_pos.y), int(end_pos.x - start_pos.x), int(end_pos.y - start_pos.y))
    rect.normalize()
    return rect


def shape_rect_for_square(start_pos: pygame.Vector2, end_pos: pygame.Vector2) -> pygame.Rect:
    width = abs(int(end_pos.x - start_pos.x))
    height = abs(int(end_pos.y - start_pos.y))
    size = max(1, min(width, height))
    left = int(start_pos.x) if end_pos.x >= start_pos.x else int(start_pos.x) - size
    top = int(start_pos.y) if end_pos.y >= start_pos.y else int(start_pos.y) - size
    return pygame.Rect(left, top, size, size)


def shape_points(shape_mode: str, start_pos: pygame.Vector2, end_pos: pygame.Vector2) -> list[tuple[int, int]]:
    rect = normalize_drag(start_pos, end_pos)
    if shape_mode == "right_triangle":
        return [(rect.left, rect.bottom), (rect.left, rect.top), (rect.right, rect.bottom)]
    if shape_mode == "equilateral_triangle":
        return [(rect.centerx, rect.top), (rect.left, rect.bottom), (rect.right, rect.bottom)]
    if shape_mode == "rhombus":
        return [(rect.centerx, rect.top), (rect.right, rect.centery), (rect.centerx, rect.bottom), (rect.left, rect.centery)]
    return []


def apply_fill(canvas: pygame.Surface, start_pos: pygame.Vector2, new_color: pygame.Color) -> None:
    """Flood fill starting from start_pos replacing pixels similar to the
    start pixel with new_color. Uses a simple RGB distance threshold to avoid
    leaking through anti-aliased edges.

    The tolerance is small by default (0) and can be increased by editing
    the `tol` variable below.
    """
    sx = int(start_pos.x)
    sy = int(start_pos.y)
    width, height = canvas.get_size()
    if sx < 0 or sy < 0 or sx >= width or sy >= height:
        return

    target_color = canvas.get_at((sx, sy))
    # tolerance for color difference (0 = exact match)
    tol = 10
    if color_close(target_color, new_color, tol):
        return

    queue = deque([(sx, sy)])
    visited = set()
    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        current_color = canvas.get_at((x, y))
        if not color_close(current_color, target_color, tol):
            continue
        canvas.set_at((x, y), new_color)
        queue.append((x + 1, y))
        queue.append((x - 1, y))
        queue.append((x, y + 1))
        queue.append((x, y - 1))


def color_close(c1: pygame.Color, c2: pygame.Color, tol: int) -> bool:
    dr = c1.r - c2.r
    dg = c1.g - c2.g
    db = c1.b - c2.b
    return (dr * dr + dg * dg + db * db) <= (tol * tol)


def draw_geometry_preview(
    preview_surface: pygame.Surface,
    canvas_rect: pygame.Rect,
    active_tool: str,
    shape_mode: str,
    start_pos: pygame.Vector2 | None,
    end_pos: pygame.Vector2,
    color: pygame.Color,
    thickness: int,
    commit_to_canvas: pygame.Surface | None = None,
) -> None:
    preview_surface.fill((0, 0, 0, 0))
    if start_pos is None:
        return

    target = commit_to_canvas or preview_surface
    rect = normalize_drag(start_pos, end_pos)

    if active_tool == "line":
        pygame.draw.line(target, color, (int(start_pos.x), int(start_pos.y)), (int(end_pos.x), int(end_pos.y)), thickness)
    elif active_tool == "rectangle":
        pygame.draw.rect(target, color, rect, thickness)
    elif active_tool == "circle":
        pygame.draw.ellipse(target, color, rect, thickness)
    elif active_tool == "shapes":
        if shape_mode == "square":
            square = shape_rect_for_square(start_pos, end_pos)
            pygame.draw.rect(target, color, square, thickness)
        elif shape_mode == "right_triangle":
            points = shape_points(shape_mode, start_pos, end_pos)
            pygame.draw.polygon(target, color, points, thickness)
        elif shape_mode == "equilateral_triangle":
            points = shape_points(shape_mode, start_pos, end_pos)
            pygame.draw.polygon(target, color, points, thickness)
        elif shape_mode == "rhombus":
            points = shape_points(shape_mode, start_pos, end_pos)
            pygame.draw.polygon(target, color, points, thickness)


def draw_text_entry(canvas: pygame.Surface, font: pygame.font.Font, text: str, position: pygame.Vector2, color: pygame.Color) -> None:
    text_surface = font.render(text, True, color)
    canvas.blit(text_surface, position)
