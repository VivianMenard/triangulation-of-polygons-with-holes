from __future__ import annotations

from typing import ClassVar

from constants import Color
from utils import get_random_pastel_color


class Vertex:
    next_id: ClassVar[int] = 0

    id: int
    x: float
    y: float
    color: Color

    def __init__(self, x: float, y: float) -> None:
        self.id = Vertex.next_id
        Vertex.next_id += 1

        self.x = x
        self.y = y

        self.color = get_random_pastel_color()

    def __gt__(self, other: Vertex) -> bool:
        return self.y > other.y or (self.y == other.y and self.x > other.x)
