from enum import Enum


class NodeType(Enum):
    """
    Represents the type of a node, specifying what it actually represents:
    a vertex, an edge, or a trapezoid.
    """

    VERTEX = 0
    EDGE = 1
    TRAPEZOID = 2


Color = tuple[int, int, int]
"""
Represents a color as a tuple of integers (r, g, b), where:
- `r` (int): Red component (0-255).
- `g` (int): Green component (0-255).
- `b` (int): Blue component (0-255).
"""

ANGLE_THRESHOLD = 150
"""
Defines the maximum angle threshold (in degrees) for the triangulation algorithm.

- Valid range: 0 to 180.
- Purpose: The algorithm avoids generating triangles with angles above this threshold 
  to ensure better-quality triangulations.
- Notes: 
  - The threshold must remain below 180 to prevent the creation of flat triangles.
  - Setting this value too low may degrade performance as the algorithm retries to find 
    valid configurations that respect the threshold.
"""

ANGLE_EPSILON = 0.1
"""
A small angle value (in degrees) used as a tolerance to avoid numerical errors 
or rounding issues during angle calculations.
"""
