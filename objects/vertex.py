from __future__ import annotations

import math
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

    @staticmethod
    def angle(vertex_1: Vertex, vertex_2: Vertex, vertex_3: Vertex) -> float:
        def vector(pt_from: Vertex, pt_to: Vertex) -> tuple[float, float]:
            return (pt_to.x - pt_from.x, pt_to.y - pt_from.y)

        def norm(vector: tuple[float, float]) -> float:
            return math.sqrt(sum([component * component for component in vector]))

        vector_a = vector(pt_from=vertex_2, pt_to=vertex_1)
        vector_b = vector(pt_from=vertex_2, pt_to=vertex_3)

        dot_product = vector_a[0] * vector_b[0] + vector_a[1] * vector_b[1]

        cos_angle = dot_product / (norm(vector_a) * norm(vector_b))

        cos_angle = max(-1, min(1, cos_angle))

        return math.degrees(math.acos(cos_angle))
