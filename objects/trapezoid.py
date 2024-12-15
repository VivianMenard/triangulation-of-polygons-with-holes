from __future__ import annotations

from collections import defaultdict
from functools import cached_property
from typing import TYPE_CHECKING, ClassVar, DefaultDict

from exceptions import (
    NonExistingAttribute,
    NonExistingExtremePoint,
)
from utils import replace

from .vertex import Vertex

if TYPE_CHECKING:
    from .edge import Edge
    from .node import Node


class Trapezoid:
    next_id: ClassVar[int] = 0
    traps_by_right_edge: ClassVar[DefaultDict[Edge, set[Trapezoid]]] = defaultdict(set)

    top_vertex: Vertex | None
    bottom_vertex: Vertex | None
    # up to 2 trap above, if 2 the first is the one at the left
    trapezoids_above: list[Trapezoid]
    # up to 2 trap below, if 2 the first is the one at the left
    trapezoids_below: list[Trapezoid]
    left_edge: Edge | None
    _right_edge: Edge | None
    _associated_node: Node | None
    inside: bool

    def __init__(
        self,
        top_vertex: Vertex | None = None,
        bottom_vertex: Vertex | None = None,
        trapezoids_above: list[Trapezoid] | None = None,
        trapezoids_below: list[Trapezoid] | None = None,
        left_edge: Edge | None = None,
        right_edge: Edge | None = None,
    ) -> None:
        self.id = Trapezoid.next_id
        Trapezoid.next_id += 1

        self.top_vertex = top_vertex
        self.bottom_vertex = bottom_vertex
        self.trapezoids_above = [] if trapezoids_above is None else trapezoids_above
        self.trapezoids_below = [] if trapezoids_below is None else trapezoids_below
        self.left_edge = left_edge
        self._right_edge = None
        self.right_edge = right_edge
        self._associated_node = None
        self.inside = False

    @staticmethod
    def merge_trapezoids_stack(trapezoids_stack: list[Trapezoid]) -> None:
        if len(trapezoids_stack) < 2:
            return

        top_trap = trapezoids_stack[0]
        bottom_trap = trapezoids_stack[-1]

        top_trap.bottom_vertex = bottom_trap.bottom_vertex
        top_trap.trapezoids_below = bottom_trap.trapezoids_below

        for trap in bottom_trap.trapezoids_below:
            replace(trap.trapezoids_above, bottom_trap, top_trap)

        for trap in trapezoids_stack[1:]:
            trap.associated_node.replace_by_another_node_in_tree(
                top_trap.associated_node
            )
            trap.remove_from_edge_registry()

    @property
    def associated_node(self) -> Node:
        if self._associated_node is None:
            raise NonExistingAttribute

        return self._associated_node

    @associated_node.setter
    def associated_node(self, new_node: Node) -> None:
        self._associated_node = new_node

    @property
    def right_edge(self) -> Edge | None:
        return self._right_edge

    @right_edge.setter
    def right_edge(self, new_right_edge: Edge | None) -> None:
        self.remove_from_edge_registry()

        self._right_edge = new_right_edge

        self.register_in_edge_registry()

    def get_adjacent_traps(self, top: bool) -> list[Trapezoid]:
        if top:
            return self.trapezoids_above

        return self.trapezoids_below

    def set_adjacent_traps(self, new_traps: list[Trapezoid], top: bool) -> None:
        if top:
            self.trapezoids_above = new_traps
        else:
            self.trapezoids_below = new_traps

    def remove_from_edge_registry(self) -> None:
        if self._right_edge is not None:
            Trapezoid.traps_by_right_edge[self._right_edge].remove(self)

    def register_in_edge_registry(self) -> None:
        if self._right_edge is not None:
            Trapezoid.traps_by_right_edge[self._right_edge].add(self)

    @cached_property
    def is_inside(self) -> bool:
        if self.right_edge is None or self.left_edge is None:
            return False

        left_traps = Trapezoid.traps_by_right_edge[self.left_edge]
        left_trap = next(iter(left_traps))

        return not left_trap.is_inside

    def duplicate(self) -> Trapezoid:
        return Trapezoid(
            top_vertex=self.top_vertex,
            bottom_vertex=self.bottom_vertex,
            left_edge=self.left_edge,
            right_edge=self.right_edge,
        )

    def split_by_vertex(self, vertex: Vertex) -> tuple[Trapezoid, Trapezoid]:
        top_trapezoid = self
        bottom_trapezoid = self.duplicate()

        top_trapezoid.bottom_vertex = vertex
        bottom_trapezoid.top_vertex = vertex

        # top_trapezoid = self -> no need to change trapezoids_above
        bottom_trapezoid.trapezoids_above = [top_trapezoid]
        bottom_trapezoid.trapezoids_below = self.trapezoids_below
        for trap in self.trapezoids_below:
            replace(trap.trapezoids_above, self, bottom_trapezoid)
        top_trapezoid.trapezoids_below = [bottom_trapezoid]

        return (bottom_trapezoid, top_trapezoid)

    def split_by_edge(self, edge: Edge) -> tuple[Trapezoid, Trapezoid]:
        right_trapezoid = self
        left_trapezoid = self.duplicate()

        left_trapezoid.right_edge = edge
        right_trapezoid.left_edge = edge

        return (left_trapezoid, right_trapezoid)

    def get_extreme_point(self, top: bool, right: bool) -> Vertex:
        relevant_vertex = self.top_vertex if top else self.bottom_vertex
        relevant_edge = self.right_edge if right else self.left_edge

        if relevant_vertex is None or relevant_edge is None:
            raise NonExistingExtremePoint

        extreme_y = relevant_vertex.y
        extreme_x = relevant_edge.get_x_by_y(extreme_y)

        return Vertex(extreme_x, extreme_y)
