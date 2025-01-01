from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .edge import Edge
    from .monotone_vertex import MonotoneVertex


class MonotoneMountain:
    """
    Represents a monotone mountain polygon.

    A monotone mountain is a specific type of monotone polygon where one of its
    two chains contains exactly two vertices: the top vertex and the bottom vertex.
    This simplified "mountain" shape is particularly efficient to triangulate.

    The degenerate chain (containing only two vertices) is stored as an edge, while
    the other chain is represented as a sequence of MonotoneVertex objects. In this
    structure, only one endpoint of the chain, the bottom vertex, is explicitly stored.
    """

    bottom_vertex: MonotoneVertex
    """The bottom vertex of the monotone chain."""
    base: Edge
    """The edge that connects the two vertices of the degenerated chain."""

    def __init__(self, bottom_vertex: MonotoneVertex, base: Edge) -> None:
        """
        Initializes a monotone mountain with its bottom vertex and base edge.

        Args:
            bottom_vertex (MonotoneVertex): The bottom vertex of the monotone chain.
            base (Edge): The edge connecting the two vertices of the degenerated chain.
        """
        self.bottom_vertex = bottom_vertex
        self.base = base

    @property
    def is_degenerated(self) -> bool:
        """
        Checks if the monotone mountain is degenerated.

        A degenerated monotone mountain is defined as one where the main chain contains
        fewer than two vertices above the base vertex. This typically occurs when the
        polygon is reduced to a single edge or point.

        Returns:
            bool: True if the mountain is degenerated, False otherwise.
        """
        if (above := self.bottom_vertex.above) is None:
            return True

        if above.above is None:
            return True

        return False
