from __future__ import annotations

from .edge import Edge
from .vertex import Vertex

Polygon = list[Vertex]


class PolygonArea:
    polygons: list[Polygon]

    def __init__(self, polygons: list[Polygon]) -> None:
        self.polygons = polygons

    def get_edges(self) -> list[Edge]:
        return [
            Edge(polygon[vertex_index], polygon[(vertex_index + 1) % len(polygon)])
            for polygon in self.polygons
            for vertex_index in range(len(polygon))
        ]
