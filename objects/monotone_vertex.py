from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from objects import Vertex


class MonotoneVertex:
    vertex: Vertex
    above: MonotoneVertex | None
    below: MonotoneVertex | None

    def __init__(
        self,
        vertex: Vertex,
        above: MonotoneVertex | None = None,
        below: MonotoneVertex | None = None,
    ) -> None:
        self.vertex = vertex

        self.above = above
        self.below = below

    @cached_property
    def is_base_vertex(self):
        return self.above is None or self.below is None
