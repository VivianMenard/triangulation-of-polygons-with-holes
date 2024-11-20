import matplotlib.pyplot as plt

from .vertex import Vertex


class Edge:
    start: Vertex
    end: Vertex
    bottom_vertex: Vertex
    top_vertex: Vertex

    def __init__(self, start: Vertex, end: Vertex) -> None:
        self.start = start
        self.end = end
        self.bottom_vertex, self.top_vertex = self.get_ordered_vertices()

    def display(self, color: str = "blue") -> None:
        x = [self.start.x, self.end.x]
        y = [self.start.y, self.end.y]

        plt.plot(x, y, color=color)

    def get_x_by_y(self, y: float) -> float:
        start_x = self.start.x
        end_x = self.end.x
        start_y = self.start.y
        end_y = self.end.y

        if start_y == end_y:
            return (start_x + end_x) / 2

        t = (y - start_y) / (end_y - start_y)
        return start_x + t * (end_x - start_x)

    def get_ordered_vertices(self) -> tuple[Vertex, Vertex]:
        if self.start > self.end:
            return self.end, self.start

        return self.start, self.end

    def is_vertex_at_the_right(self, vertex: Vertex) -> bool:
        x_edge = self.get_x_by_y(vertex.y)

        return vertex.x > x_edge

    def get_mid_point(self) -> Vertex:
        return Vertex((self.start.x + self.end.x) / 2, (self.start.y + self.end.y) / 2)
