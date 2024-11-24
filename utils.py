from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from objects import Vertex


def replace(l: list, to_replace, replace_by) -> None:
    for i in range(len(l)):
        if l[i] == to_replace:
            l[i] = replace_by


def counter_clockwise(ptA: Vertex, ptB: Vertex, ptC: Vertex) -> bool:
    return (ptC.y - ptA.y) * (ptB.x - ptA.x) > (ptB.y - ptA.y) * (ptC.x - ptA.x)


def segment_intersect(ptA: Vertex, ptB: Vertex, ptC: Vertex, ptD: Vertex) -> bool:
    return counter_clockwise(ptA, ptB, ptC) != counter_clockwise(
        ptA, ptB, ptD
    ) and counter_clockwise(ptC, ptD, ptA) != counter_clockwise(ptC, ptD, ptB)


def get_random_pastel_color() -> str:
    return f"#{random.randint(100, 255):02x}{random.randint(100, 255):02x}{random.randint(100, 255):02x}"
