from enum import Enum

X_MIN = -10
X_MAX = 10
Y_MIN = -10
Y_MAX = 10


class NodeType(Enum):
    VERTEX = 0
    EDGE = 1
    TRAPEZOID = 2
