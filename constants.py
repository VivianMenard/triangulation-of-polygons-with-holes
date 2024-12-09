from enum import Enum


class NodeType(Enum):
    VERTEX = 0
    EDGE = 1
    TRAPEZOID = 2


Color = tuple[int, int, int]
