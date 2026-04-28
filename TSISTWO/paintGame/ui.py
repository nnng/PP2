from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from tools import SHAPE_CHOICES, TOOL_ORDER, ToolState


@dataclass
class ToolButton:
    label: str
    tool_name: str
    rect: pygame.Rect


@dataclass
class ColorPalette:
    colors: list[pygame.Color] = field(default_factory=lambda: [
        pygame.Color(35, 85, 160),
        pygame.Color(220, 60, 60),
        pygame.Color(40, 150, 90),
        pygame.Color(25, 25, 25),
        pygame.Color(245, 245, 240),
    ])
    rects: list[pygame.Rect] = field(default_factory=list)


@dataclass
class ShapeButton:
    label: str
    shape_mode: str
    rect: pygame.Rect


def build_shape_buttons() -> list[ShapeButton]:
    labels = [
        ("Sq", "square"),
        ("Rt", "right_triangle"),
        ("Eq", "equilateral_triangle"),
        ("Rh", "rhombus"),
    ]
    buttons: list[ShapeButton] = []
    left = 560
    top = 18
    width = 66
    height = 26
    gap = 8
    for index, (label, shape_mode) in enumerate(labels):
        rect = pygame.Rect(left + index * (width + gap), top, width, height)
        buttons.append(ShapeButton(label=label, shape_mode=shape_mode, rect=rect))
    return buttons


def build_toolbar() -> list[ToolButton]:
    buttons: list[ToolButton] = []
    left = 16
    top = 18
    width = 118
    height = 34
    gap = 10
    for index, tool_name in enumerate(TOOL_ORDER):
        row = index // 4
        col = index % 4
        rect = pygame.Rect(left + col * (width + gap), top + row * (height + gap), width, height)
        buttons.append(ToolButton(label=tool_name.title(), tool_name=tool_name, rect=rect))
    return buttons


def draw_toolbar(screen: pygame.Surface, toolbar: list[ToolButton], palette: ColorPalette, state: ToolState) -> None:
    font = pygame.font.SysFont(None, 22)
    for button in toolbar:
        active = button.tool_name == state.active_tool
        color = pygame.Color(76, 140, 255) if active else pygame.Color(58, 64, 76)
        pygame.draw.rect(screen, color, button.rect, border_radius=10)
        pygame.draw.rect(screen, pygame.Color(235, 235, 240), button.rect, 1, border_radius=10)
        text = font.render(button.label, True, pygame.Color(255, 255, 255))
        screen.blit(text, text.get_rect(center=button.rect.center))

    palette.rects = []
    palette_top = 58
    palette_left = 560
    for index, color in enumerate(palette.colors):
        rect = pygame.Rect(palette_left + index * 42, palette_top, 30, 30)
        palette.rects.append(rect)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        border = pygame.Color(255, 255, 255) if color != state.current_color else pygame.Color(255, 210, 90)
        pygame.draw.rect(screen, border, rect, 2, border_radius=8)

    shape_buttons = build_shape_buttons()
    for shape_button in shape_buttons:
        active = state.shape_mode == shape_button.shape_mode
        color = pygame.Color(78, 168, 126) if active else pygame.Color(58, 64, 76)
        pygame.draw.rect(screen, color, shape_button.rect, border_radius=8)
        pygame.draw.rect(screen, pygame.Color(235, 235, 240), shape_button.rect, 1, border_radius=8)
        text = font.render(shape_button.label, True, pygame.Color(255, 255, 255))
        screen.blit(text, text.get_rect(center=shape_button.rect.center))

    if state.active_tool == "shapes":
        shapes_text = font.render("4: cycle shape", True, pygame.Color(220, 225, 235))
        screen.blit(shapes_text, (760, 50))


def draw_status_bar(screen: pygame.Surface, font: pygame.font.Font, message: str, state: ToolState, top: int) -> None:
    status = f"Tool: {state.active_tool} | Shape: {state.shape_mode} | Brush: {state.brush_size}px | Color: {state.current_color.r},{state.current_color.g},{state.current_color.b} | {message}"
    text = font.render(status, True, pygame.Color(235, 235, 240))
    screen.blit(text, (16, top + 6))


def hit_test_tool(toolbar: list[ToolButton], position: tuple[int, int]) -> str | None:
    for button in toolbar:
        if button.rect.collidepoint(position):
            return button.tool_name
    return None


def hit_test_color(palette: ColorPalette, position: tuple[int, int]) -> pygame.Color | None:
    for rect, color in zip(palette.rects, palette.colors):
        if rect.collidepoint(position):
            return color
    return None


def hit_test_shape_button(position: tuple[int, int]) -> str | None:
    for button in build_shape_buttons():
        if button.rect.collidepoint(position):
            return button.shape_mode
    return None