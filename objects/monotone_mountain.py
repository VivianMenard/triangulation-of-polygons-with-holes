from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .edge import Edge
    from .monotone_vertex import MonotoneVertex


class MonotoneMountain:
    bottom_vertex: MonotoneVertex
    base: Edge

    def __init__(self, bottom_vertex: MonotoneVertex, base: Edge) -> None:
        self.bottom_vertex = bottom_vertex
        self.base = base

    @property
    def is_degenerated(self) -> bool:
        if (above := self.bottom_vertex.above) is None:
            return True

        if above.above is None:
            return True

        return False
