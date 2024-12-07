from __future__ import annotations

from typing import TYPE_CHECKING, cast

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

    def get_hashable_key(self) -> tuple[int, int, int]:
        """
        Returns a hashable key that is unic for every set of vertices.
        """
        vertices_id = [vertex.id for vertex in self.vertices]
        vertices_id.sort()

        return cast(tuple[int, int, int], tuple(vertices_id))
