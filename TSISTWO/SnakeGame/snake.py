"""Snake entity and movement rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

GridPos = Tuple[int, int]


@dataclass(frozen=True)
class Direction:
    x: int
    y: int


UP = Direction(0, -1)
DOWN = Direction(0, 1)
LEFT = Direction(-1, 0)
RIGHT = Direction(1, 0)

OPPOSITES = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}


class Snake:
    def __init__(self, start_x: int, start_y: int) -> None:
        self.segments: List[GridPos] = [
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y),
        ]
        self.direction = RIGHT
        self._next_direction = RIGHT
        self._grow_pending = 0

    @property
    def head(self) -> GridPos:
        return self.segments[0]

    def set_direction(self, new_direction: Direction) -> None:
        if OPPOSITES[self.direction] == new_direction:
            return
        self._next_direction = new_direction

    def move(self) -> None:
        self.direction = self._next_direction
        hx, hy = self.head
        new_head = (hx + self.direction.x, hy + self.direction.y)
        self.segments.insert(0, new_head)

        if self._grow_pending > 0:
            self._grow_pending -= 1
        else:
            self.segments.pop()

    def grow(self, amount: int = 1) -> None:
        self._grow_pending += max(0, amount)

    def shrink(self, amount: int = 1) -> None:
        """Remove `amount` segments from the tail. Does not remove the head.

        If the snake becomes length <= 1, caller should handle game over.
        """
        for _ in range(amount):
            if len(self.segments) > 1:
                self.segments.pop()
            else:
                break

    def is_self_collision(self) -> bool:
        return self.head in self.segments[1:]

    def occupies(self, pos: GridPos) -> bool:
        return pos in self.segments
