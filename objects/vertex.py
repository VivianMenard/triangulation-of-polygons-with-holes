from __future__ import annotations


class Vertex:
    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __gt__(self, other: "Vertex") -> bool:
        return self.y > other.y or (self.y == other.y and self.x > other.x)
