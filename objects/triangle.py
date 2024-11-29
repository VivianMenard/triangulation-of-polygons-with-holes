from __future__ import annotations

from typing import TYPE_CHECKING, cast

from utils import counter_clockwise

if TYPE_CHECKING:
    from .vertex import Vertex


class Triangle:
    vertices: list[Vertex]

    def __init__(self, vertices: list[Vertex]) -> None:
        assert len(vertices) == 3
        assert counter_clockwise(*vertices)

        self.vertices = vertices

    def get_hashable_key(self) -> tuple[int, int, int]:
        """
        Returns a hashable key that is unic for every set of vertices.
        """
        vertices_id = [vertex.id for vertex in self.vertices]
        vertices_id.sort()

        return cast(tuple[int, int, int], tuple(vertices_id))
