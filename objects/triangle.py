from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from exceptions import BadVertexOrder
from utils import counter_clockwise

if TYPE_CHECKING:
    from .vertex import Vertex


class Triangle:
    vertices: tuple[Vertex, Vertex, Vertex]

    def __init__(self, vertices: tuple[Vertex, Vertex, Vertex]) -> None:
        if not counter_clockwise(*vertices):
            raise BadVertexOrder

        self.vertices = vertices

    @cached_property
    def color_str(self):
        r, g, b = [
            int(sum([vertex.color[i] for vertex in self.vertices]) / 3)
            for i in range(3)
        ]
        return f"#{r:02x}{g:02x}{b:02x}"
