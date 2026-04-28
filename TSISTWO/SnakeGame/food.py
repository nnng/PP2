"""Advanced food manager supporting multiple food types.

Provides weighted food, disappearing food (TTL) and poison food.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Set, Tuple

GridPos = Tuple[int, int]


@dataclass
class FoodItem:
    kind: str  # 'normal', 'rare', 'disappearing', 'poison'
    position: GridPos
    weight: int
    spawn_tick: int
    ttl: Optional[int] = None  # milliseconds


class FoodManager:
    """Manages multiple food items on the grid."""

    def __init__(self, cols: int, rows: int) -> None:
        self.cols = cols
        self.rows = rows
        self.items: List[FoodItem] = []

    def _random_free_cell(self, blocked: Set[GridPos]) -> Optional[GridPos]:
        free = [
            (x, y)
            for x in range(self.cols)
            for y in range(self.rows)
            if (x, y) not in blocked
        ]
        if not free:
            return None
        return random.choice(free)

    def spawn(self, blocked: Iterable[GridPos], now_tick: int) -> Optional[FoodItem]:
        """Spawn a single food item avoiding blocked cells.

        Probabilities (example): normal 65%, rare 10%, disappearing 15%, poison 10%.
        """
        blocked_set = set(blocked)
        pos = self._random_free_cell(blocked_set)
        if pos is None:
            return None

        r = random.random()
        if r < 0.65:
            kind = "normal"
            weight = 1
            ttl = None
        elif r < 0.75:
            kind = "rare"
            weight = 5
            ttl = None
        elif r < 0.9:
            kind = "disappearing"
            weight = 2
            ttl = 5000
        else:
            kind = "poison"
            weight = -2
            ttl = None

        item = FoodItem(kind=kind, position=pos, weight=weight, spawn_tick=now_tick, ttl=ttl)
        self.items.append(item)
        return item

    def remove(self, item: FoodItem) -> None:
        try:
            self.items.remove(item)
        except ValueError:
            pass

    def get_at(self, pos: GridPos) -> Optional[FoodItem]:
        for it in self.items:
            if it.position == pos:
                return it
        return None

    def update(self, now_tick: int) -> None:
        # Remove expired disappearing foods
        expired: List[FoodItem] = []
        for it in self.items:
            if it.ttl is not None:
                if now_tick - it.spawn_tick >= it.ttl:
                    expired.append(it)
        for it in expired:
            self.remove(it)

