from __future__ import annotations

from typing import TYPE_CHECKING

from .edge import Edge

if TYPE_CHECKING:
    from .vertex import Vertex


class Polygon:
    contours: list[list[Vertex]]

    def __init__(self, contours: list[list[Vertex]]) -> None:
        self.contours = contours

    def get_edges(self) -> list[Edge]:
        return [
            Edge(contour[vertex_index], contour[(vertex_index + 1) % len(contour)])
            for contour in self.contours
            for vertex_index in range(len(contour))
        ]
