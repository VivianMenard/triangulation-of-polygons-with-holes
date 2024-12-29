from __future__ import annotations

from collections import defaultdict
from functools import cached_property
from typing import TYPE_CHECKING, ClassVar, DefaultDict

from exceptions import (
    InconsistentTrapezoidNeighborhood,
    NonExistingAttribute,
    NonExistingExtremePoint,
)
from utils import replace

from .edge import Edge
from .vertex import Vertex

if TYPE_CHECKING:
    from .node import Node


class Trapezoid:
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
        self.top_vertex = top_vertex
        self.bottom_vertex = bottom_vertex
        self.trapezoids_above = [] if trapezoids_above is None else trapezoids_above
        self.trapezoids_below = [] if trapezoids_below is None else trapezoids_below
        self.left_edge = left_edge
        self._right_edge = None
        self.right_edge = right_edge
        self._associated_node = None
        self.inside = False

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

    @staticmethod
    def manage_adjacent_trapezoids_on_branch(
        edge: Edge,
        left_trap_A: Trapezoid,
        right_trap_A: Trapezoid,
        left_trap_B: Trapezoid,
        right_trap_B: Trapezoid,
        upward_branch: bool,
    ) -> None:
        """branch opened in A and closed in B."""
        if (
            len(right_trap_A.get_adjacent_traps(top=not upward_branch)) != 1
        ):  # as two vertices can be at the same height (because lexicographic order)
            raise InconsistentTrapezoidNeighborhood

        left_trap_A.set_adjacent_traps([left_trap_B], top=not upward_branch)

        branch_point = right_trap_B.get_adjacent_traps(top=upward_branch)[
            0
        ].get_extreme_point(top=not upward_branch, right=True)

        if edge.is_vertex_at_the_right(branch_point):
            left_trap_B.set_adjacent_traps([left_trap_A], top=upward_branch)
            return

        additional_left_trap_A = right_trap_B.get_adjacent_traps(top=upward_branch)[0]

        right_trap_A.set_adjacent_traps([right_trap_B], top=not upward_branch)
        right_trap_B.set_adjacent_traps([right_trap_A], top=upward_branch)

        left_trap_B.set_adjacent_traps(
            [
                additional_left_trap_A,
                left_trap_A,
            ],
            top=upward_branch,
        )
        additional_left_trap_A.set_adjacent_traps([left_trap_B], top=not upward_branch)

    @staticmethod
    def manage_adjacent_trapezoid_at_inserted_edge_end(
        edge: Edge,
        end_trap_left: Trapezoid,
        end_trap_right: Trapezoid,
        end_just_inserted: bool,
        top_end: bool,
    ) -> None:
        exterior_adjacent_traps = end_trap_right.get_adjacent_traps(top=top_end)

        if end_just_inserted:
            # only 1 exterior adjacent trapezoid and it needs to be adjacent for both
            # but already adjacent for right
            if len(exterior_adjacent_traps) != 1:
                raise InconsistentTrapezoidNeighborhood

            end_trap_left.set_adjacent_traps(
                exterior_adjacent_traps.copy(), top=top_end
            )
            adjacent_trap = exterior_adjacent_traps[0]
            adjacent_trap.set_adjacent_traps(
                [end_trap_left, end_trap_right], top=not top_end
            )

            return

        edge_relevant_end = Edge.get_edge_vertex(edge, top=top_end)
        if (
            Edge.get_edge_vertex(end_trap_left.left_edge, top=top_end)
            == edge_relevant_end
        ):  # left peak with an old edge
            if len(exterior_adjacent_traps) != 1:
                raise InconsistentTrapezoidNeighborhood

            # nothing to do

        elif (
            Edge.get_edge_vertex(end_trap_right.right_edge, top=top_end)
            == edge_relevant_end
        ):  # right peak with an old edge
            if len(exterior_adjacent_traps) != 1:
                raise InconsistentTrapezoidNeighborhood

            end_trap_left.set_adjacent_traps(exterior_adjacent_traps, top=top_end)
            end_trap_right.set_adjacent_traps([], top=top_end)
            replace(
                exterior_adjacent_traps[0].get_adjacent_traps(top=not top_end),
                end_trap_right,
                end_trap_left,
            )

        else:  # the new edge just extend an old edge
            if len(exterior_adjacent_traps) != 2:
                raise InconsistentTrapezoidNeighborhood

            left_adjacent, right_adjacent = exterior_adjacent_traps
            end_trap_left.set_adjacent_traps([left_adjacent], top=top_end)
            end_trap_right.set_adjacent_traps([right_adjacent], top=top_end)
            replace(
                left_adjacent.get_adjacent_traps(top=not top_end),
                end_trap_right,
                end_trap_left,
            )

    @staticmethod
    def manage_adjacent_trapezoids_after_edge_split(
        edge: Edge,
        created_trap_couples: list[tuple[Trapezoid, Trapezoid]],
        top_just_inserted: bool,
        bottom_just_inserted: bool,
    ) -> None:
        Trapezoid.manage_adjacent_trapezoid_at_inserted_edge_end(
            edge, *created_trap_couples[0], top_just_inserted, top_end=True
        )
        Trapezoid.manage_adjacent_trapezoid_at_inserted_edge_end(
            edge, *created_trap_couples[-1], bottom_just_inserted, top_end=False
        )

        for trap_couple_index in range(
            len(created_trap_couples) - 1
        ):  # iterates on horizontal borders between splited traps to correctly set their new adjacent traps
            top_left_trap, top_right_trap = created_trap_couples[
                trap_couple_index
            ]  # trapezoids above the horizontal border
            bottom_left_trap, bottom_right_trap = created_trap_couples[
                trap_couple_index + 1
            ]  # trapezoids below the horizontal border

            if (
                len(top_right_trap.trapezoids_below) == 2
            ):  # downward branch, ie before the insertion the initial top trap had 2 below adjacent traps
                Trapezoid.manage_adjacent_trapezoids_on_branch(
                    edge,
                    bottom_left_trap,
                    bottom_right_trap,
                    top_left_trap,
                    top_right_trap,
                    upward_branch=False,
                )

            elif (
                len(bottom_right_trap.trapezoids_above) == 2
            ):  # upward branch, ie before the edge insertion the initial bottom trap had 2 above adjacent traps
                Trapezoid.manage_adjacent_trapezoids_on_branch(
                    edge,
                    top_left_trap,
                    top_right_trap,
                    bottom_left_trap,
                    bottom_right_trap,
                    upward_branch=True,
                )

            else:  # no branch, ie before the insertion top and bottom traps were just the only adjacent trap of each other
                if (
                    len(bottom_right_trap.trapezoids_above) != 1
                    or len(top_right_trap.trapezoids_below) != 1
                ):
                    raise InconsistentTrapezoidNeighborhood

                top_left_trap.trapezoids_below = [bottom_left_trap]
                bottom_left_trap.trapezoids_above = [top_left_trap]

    @staticmethod
    def merge_redundant_trapezoids(
        created_trap_couples: list[tuple[Trapezoid, Trapezoid]],
    ) -> None:
        """
        The insertion of an edge can create stacked trapezoids that share the same left and right edes, these function
        detect them and merge them.
        """
        for left_or_right in [0, 1]:
            stack_to_merge: list[Trapezoid] = [created_trap_couples[0][left_or_right]]

            for trap_couple in created_trap_couples[1:]:
                trap = trap_couple[left_or_right]

                if (
                    stack_to_merge[-1].left_edge != trap.left_edge
                    or stack_to_merge[-1].right_edge != trap.right_edge
                ):
                    Trapezoid.merge_trapezoids_stack(stack_to_merge)
                    stack_to_merge = []

                stack_to_merge.append(trap)

            Trapezoid.merge_trapezoids_stack(stack_to_merge)

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
