from __future__ import annotations

from .vertex import Vertex


class Edge:
    bottom_vertex: Vertex
    top_vertex: Vertex

    def __init__(self, start: Vertex, end: Vertex) -> None:
        self.bottom_vertex, self.top_vertex = (
            (end, start) if start > end else (start, end)
        )

    @staticmethod
    def get_edge_vertex(edge: Edge | None, top: bool) -> Vertex | None:
        if edge is None:
            return None

        return edge.get_vertex(top=top)

    @property
    def mid_point(self) -> Vertex:
        bottom, top = self.bottom_vertex, self.top_vertex
        return Vertex((bottom.x + top.x) / 2, (bottom.y + top.y) / 2)

    def get_vertex(self, top: bool) -> Vertex:
        if top:
            return self.top_vertex

        return self.bottom_vertex

    def get_x_by_y(self, y: float) -> float:
        bottom_x = self.bottom_vertex.x
        top_x = self.top_vertex.x
        bottom_y = self.bottom_vertex.y
        top_y = self.top_vertex.y

        if bottom_y == top_y:
            return (bottom_x + top_x) / 2

        t = (y - bottom_y) / (top_y - bottom_y)
        return bottom_x + t * (top_x - bottom_x)

    def is_vertex_at_the_right(self, vertex: Vertex) -> bool:
        x_edge = self.get_x_by_y(vertex.y)

        return vertex.x > x_edge
