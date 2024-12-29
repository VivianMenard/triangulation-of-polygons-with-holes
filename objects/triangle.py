from __future__ import annotations

from functools import cached_property

from exceptions import BadVertexOrder

from .vertex import Vertex


class Triangle:
    """
    Represents a triangle defined by three vertices in a 2D space.
    """

    vertices: tuple[Vertex, Vertex, Vertex]
    """The three vertices that form the triangle."""

    def __init__(self, vertices: tuple[Vertex, Vertex, Vertex]) -> None:
        """
        Initializes a triangle with the given vertices. Ensures that the vertices
        are in counter-clockwise order to define a valid triangle.

        Args:
            vertices (tuple[Vertex, Vertex, Vertex]): A tuple of three vertices
                defining the triangle.

        Raises:
            BadVertexOrder: If the vertices are not in counter-clockwise order.
        """
        if not Vertex.counter_clockwise(*vertices):
            raise BadVertexOrder

        self.vertices = vertices

    @cached_property
    def color_str(self):
        """
        Computes the average color of the triangle by averaging the RGB values of
        its vertices and returns it as a hexadecimal color string.

        Returns:
            str: The average color of the triangle in hexadecimal format (e.g., "#rrggbb").
        """
        r, g, b = [
            int(sum([vertex.color[i] for vertex in self.vertices]) / 3)
            for i in range(3)
        ]
        return f"#{r:02x}{g:02x}{b:02x}"
