from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from objects import Vertex


class MonotoneVertex:
    """
    Represents a vertex in a monotone mountain polygon.

    Each MonotoneVertex is linked to its neighboring vertices within the monotone
    structure, which allows for efficient navigation along the polygon's edges.
    """

    vertex: Vertex
    """The geometric vertex represented by this monotone vertex."""
    above: MonotoneVertex | None
    """The vertex directly above in the monotone structure, or None if this vertex is at the top of its chain."""
    below: MonotoneVertex | None
    """The vertex directly below in the monotone structure, or None if this vertex is at the bottom of its chain."""

    def __init__(
        self,
        vertex: Vertex,
        above: MonotoneVertex | None = None,
        below: MonotoneVertex | None = None,
    ) -> None:
        """
        Initializes a MonotoneVertex with its geometric vertex and optionally its
        adjacent vertices in the monotone mountain structure.

        Args:
            vertex (Vertex): The geometric vertex represented by this monotone vertex.
            above (MonotoneVertex | None, optional): The vertex directly above in the monotone structure.
                Defaults to None.
            below (MonotoneVertex | None, optional): The vertex directly below in the monotone structure.
                Defaults to None.
        """
        self.vertex = vertex

        self.above = above
        self.below = below

    @cached_property
    def is_base_vertex(self) -> bool:
        """
        Determines if this vertex is a base vertex in the monotone mountain, i.e. if the vertex is one of
        the ends of the chain.

        Returns:
            bool: True if this vertex is a base vertex, False otherwise.
        """
        return self.above is None or self.below is None
