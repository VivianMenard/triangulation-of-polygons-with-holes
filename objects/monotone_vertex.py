from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from exceptions import MonotonyRuleNotRespected, NonExistingAttribute

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
    def above(self) -> MonotoneVertex:
        if not self._above:
            raise NonExistingAttribute

        return self._above

    @property
    def below(self) -> MonotoneVertex:
        if not self._below:
            raise NonExistingAttribute

        return self._below

    @above.setter
    def above(self, new_above: MonotoneVertex | None) -> None:
        if new_above is not None and self.vertex > new_above.vertex:
            raise MonotonyRuleNotRespected

        self._above = new_above

    @below.setter
    def below(self, new_below: MonotoneVertex | None) -> None:
        if new_below is not None and self.vertex < new_below.vertex:
            raise MonotonyRuleNotRespected

        self._below = new_below

    @cached_property
    def is_base_vertex(self):
        return self._above is None or self._below is None
