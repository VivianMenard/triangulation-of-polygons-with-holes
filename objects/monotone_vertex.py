from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from objects import Vertex


class MonotoneVertex:
    vertex: Vertex
    _above: MonotoneVertex | None
    _below: MonotoneVertex | None

    def __init__(
        self,
        vertex: Vertex,
        above: MonotoneVertex | None = None,
        below: MonotoneVertex | None = None,
    ) -> None:
        self.vertex = vertex

        self._above = None
        self._below = None
        self.above = above
        self.below = below

    @property
    def above(self):
        return self._above

    @property
    def below(self):
        return self._below

    @above.setter
    def above(self, new_above: MonotoneVertex | None) -> None:
        assert new_above is None or self.vertex < new_above.vertex
        self._above = new_above

    @below.setter
    def below(self, new_below: MonotoneVertex | None) -> None:
        assert new_below is None or self.vertex > new_below.vertex
        self._below = new_below

    @cached_property
    def is_base_vertex(self):
        return self.above is None or self.below is None
