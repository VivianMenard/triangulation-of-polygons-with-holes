from __future__ import annotations

import math

from constants import Color
from utils import get_random_pastel_color


class Vertex:
    """
    Represents a vertex in a 2D space with (x, y) coordinates and an associated color
    used to choose the color of neighboring triangles.
    """

    x: float
    """The x-coordinate of the vertex."""
    y: float
    """The y-coordinate of the vertex."""
    color: Color
    """A randomly generated pastel color for the vertex."""

    def __init__(self, x: float, y: float) -> None:
        """
        Initializes a vertex with given coordinates and a random pastel color.

        Args:
            x (float): The x-coordinate of the vertex.
            y (float): The y-coordinate of the vertex.
        """
        self.x = x
        self.y = y

        self.color = get_random_pastel_color()

    def __gt__(self, other: Vertex) -> bool:
        """
        Compares two vertices based on their vertical (y) position,
        and their horizontal (x) position in case of a tie.

        Args:
            other (Vertex): Another vertex to compare against.

        Returns:
            bool: True if the current vertex is "greater" than the other, False otherwise.
        """
        return self.y > other.y or (self.y == other.y and self.x > other.x)

    @staticmethod
    def counter_clockwise(pt_a: Vertex, pt_b: Vertex, pt_c: Vertex) -> bool:
        """
        Determines if three vertices are arranged in a counter-clockwise order.

        Args:
            pt_a (Vertex): The first vertex.
            pt_b (Vertex): The second vertex.
            pt_c (Vertex): The third vertex.

        Returns:
            bool: True if the vertices are in counter-clockwise order, False otherwise.
        """
        return (pt_c.y - pt_a.y) * (pt_b.x - pt_a.x) > (pt_b.y - pt_a.y) * (
            pt_c.x - pt_a.x
        )

    @staticmethod
    def segment_intersect(
        pt_a: Vertex, pt_b: Vertex, pt_c: Vertex, pt_d: Vertex
    ) -> bool:
        """
        Checks if two segments, defined by four vertices, intersect.

        Args:
            pt_a (Vertex): The first vertex of the first segment.
            pt_b (Vertex): The second vertex of the first segment.
            pt_c (Vertex): The first vertex of the second segment.
            pt_d (Vertex): The second vertex of the second segment.

        Returns:
            bool: True if the segments intersect, False otherwise.
        """
        return Vertex.counter_clockwise(pt_a, pt_b, pt_c) != Vertex.counter_clockwise(
            pt_a, pt_b, pt_d
        ) and Vertex.counter_clockwise(pt_c, pt_d, pt_a) != Vertex.counter_clockwise(
            pt_c, pt_d, pt_b
        )

    @staticmethod
    def angle(vertex_1: Vertex, vertex_2: Vertex, vertex_3: Vertex) -> float:
        """
        Calculates the angle in degrees between three vertices, measured at vertex_2.

        Args:
            vertex_1 (Vertex): The first vertex.
            vertex_2 (Vertex): The central vertex where the angle is measured.
            vertex_3 (Vertex): The third vertex.

        Returns:
            float: The angle in degrees between vectors vertex_2->vertex_1 and vertex_2->vertex_3.
        """

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
