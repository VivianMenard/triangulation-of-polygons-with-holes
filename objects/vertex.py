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

    @staticmethod
    def counter_clockwise(pt_a: Vertex, pt_b: Vertex, pt_c: Vertex) -> bool:
        return (pt_c.y - pt_a.y) * (pt_b.x - pt_a.x) > (pt_b.y - pt_a.y) * (
            pt_c.x - pt_a.x
        )

    @staticmethod
    def segment_intersect(
        pt_a: Vertex, pt_b: Vertex, pt_c: Vertex, pt_d: Vertex
    ) -> bool:
        return Vertex.counter_clockwise(pt_a, pt_b, pt_c) != Vertex.counter_clockwise(
            pt_a, pt_b, pt_d
        ) and Vertex.counter_clockwise(pt_c, pt_d, pt_a) != Vertex.counter_clockwise(
            pt_c, pt_d, pt_b
        )
