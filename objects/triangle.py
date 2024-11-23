from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .vertex import Vertex


class Triangle:
    vertices: list[Vertex]

    def __init__(self, vertices: list[Vertex]) -> None:
        assert len(vertices) == 3

        self.vertices = vertices
