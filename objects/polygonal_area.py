from __future__ import annotations

from .edge import Edge
from .vertex import Vertex

Polygon = list[Vertex]
"""
Represents a polygon in the 2D space, as an ordered sequence of vertices, where the last 
vertex is implicitly connected to the first to form a closed shape. The order of vertices 
must follow a consistent direction (clockwise or counter-clockwise) to ensure correct 
representation.
"""


class PolygonalArea:
    """
    Represents a polygonal area in 2D space, which may include holes or disjoint regions.

    A polygonal area is defined by a list of non-intersecting polygons, where:
    - Each polygon is represented by an ordered list of vertices forming a closed loop.
    - The interior of the area is determined using the "odd-even rule":
        A point is inside the polygonal area if it is inside an odd number of the polygons.

    Attributes:
        polygons (list[Polygon]): A list of polygons defining the polygonal area. Each polygon
            must not intersect with any other polygon in the list.
    """

    polygons: list[Polygon]
    """
    A list of polygons defining the polygonal area. Each polygon must not intersect with any other 
    polygon in the list.
    """

    def __init__(self, polygons: list[Polygon]) -> None:
        """
        Initializes a PolygonalArea with a list of non-intersecting polygons.

        Args:
            polygons (list[Polygon]): A list of polygons, where each polygon is represented
                as an ordered list of vertices.
        """
        self.polygons = polygons

    def get_edges(self) -> list[Edge]:
        """
        Extracts all edges from the polygons in the polygonal area.

        Each polygon is treated as a closed shape, so the last vertex is connected to the first.

        Returns:
            list[Edge]: A list of edges representing the edges of all polygons in the polygonal area.
        """
        return [
            Edge(polygon[vertex_index], polygon[(vertex_index + 1) % len(polygon)])
            for polygon in self.polygons
            for vertex_index in range(len(polygon))
        ]
