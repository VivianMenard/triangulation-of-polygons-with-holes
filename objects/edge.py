from __future__ import annotations

from .vertex import Vertex


class Edge:
    """
    Represents an edge in 2D space, defined by two vertices.
    """

    bottom_vertex: Vertex
    """The vertex with the smaller y-coordinate (or x-coordinate in case of a tie)."""
    top_vertex: Vertex
    """The vertex with the larger y-coordinate (or x-coordinate in case of a tie)."""

    def __init__(self, start: Vertex, end: Vertex) -> None:
        """
        Initializes an edge by determining its bottom and top vertices.

        Args:
            start (Vertex): The first vertex of the edge.
            end (Vertex): The second vertex of the edge.
        """
        self.bottom_vertex, self.top_vertex = (
            (end, start) if start > end else (start, end)
        )

    @staticmethod
    def get_edge_vertex(edge: Edge | None, top: bool) -> Vertex | None:
        """
        Retrieves the top or bottom vertex of a given edge, or None if the edge is None.

        Args:
            edge (Edge | None): The edge to retrieve the vertex from.
            top (bool): If True, retrieves the top vertex; otherwise, the bottom vertex.

        Returns:
            Vertex | None: The requested vertex, or None if the edge is None.
        """
        if edge is None:
            return None

        return edge.get_vertex(top=top)

    @property
    def mid_point(self) -> Vertex:
        """
        Calculates the midpoint of the edge.

        Returns:
            Vertex: A vertex representing the midpoint of the edge.
        """
        bottom, top = self.bottom_vertex, self.top_vertex
        return Vertex((bottom.x + top.x) / 2, (bottom.y + top.y) / 2)

    def get_vertex(self, top: bool) -> Vertex:
        """
        Retrieves either the top or bottom vertex of the edge.

        Args:
            top (bool): If True, retrieves the top vertex; otherwise, the bottom vertex.

        Returns:
            Vertex: The requested vertex.
        """
        if top:
            return self.top_vertex

        return self.bottom_vertex

    def get_x_by_y(self, y: float) -> float:
        """
        Calculates the x-coordinate on the edge corresponding to a given y-coordinate.

        If the edge is horizontal (both vertices have the same y-coordinate), the
        average of the x-coordinates of the two vertices is returned.

        Args:
            y (float): The y-coordinate to use for the calculation.

        Returns:
            float: The x-coordinate on the edge at the given y-coordinate.
        """
        bottom_x = self.bottom_vertex.x
        top_x = self.top_vertex.x
        bottom_y = self.bottom_vertex.y
        top_y = self.top_vertex.y

        if bottom_y == top_y:
            return (bottom_x + top_x) / 2

        t = (y - bottom_y) / (top_y - bottom_y)
        return bottom_x + t * (top_x - bottom_x)

    def is_vertex_at_the_right(self, vertex: Vertex) -> bool:
        """
        Determines if a given vertex is to the right of the edge at the vertex's y-coordinate.

        Args:
            vertex (Vertex): The vertex to check.

        Returns:
            bool: True if the vertex is to the right of the edge, False otherwise.
        """
        x_edge = self.get_x_by_y(vertex.y)

        return vertex.x > x_edge
