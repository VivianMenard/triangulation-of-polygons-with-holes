from __future__ import annotations

from typing import cast

from constants import NodeType
from exceptions import (
    InconsistentArguments,
    InconsistentTrapezoidNeighborhood,
    NonExistingAttribute,
    NotATrapezoid,
)
from utils import replace

from .edge import Edge
from .trapezoid import Trapezoid
from .vertex import Vertex


class Node:
    node_type: NodeType
    associated_obj: Trapezoid | Edge | Vertex
    _left_child: Node | None
    _right_child: Node | None
    parents: list[Node]

    def __init__(self, trapezoid: Trapezoid, parent: Node | None = None) -> None:
        # At the time of its creation a Node is always a leaf, ie a Trapezoid node
        self.node_type = NodeType.TRAPEZOID
        self.associated_obj = trapezoid
        trapezoid.associated_node = self
        self._left_child = None
        self._right_child = None
        self.parents = []

        # at the time of its creation a Node can't have more thant one parent
        if parent:
            self.parents.append(parent)

    @property
    def trapezoid(self) -> Trapezoid:
        if self.node_type != NodeType.TRAPEZOID:
            raise NonExistingAttribute

        return cast(Trapezoid, self.associated_obj)

    @property
    def vertex(self) -> Vertex:
        if self.node_type != NodeType.VERTEX:
            raise NonExistingAttribute

        return cast(Vertex, self.associated_obj)

    @property
    def edge(self) -> Edge:
        if self.node_type != NodeType.EDGE:
            raise NonExistingAttribute

        return cast(Edge, self.associated_obj)

    @property
    def left_child(self) -> Node:
        if self._left_child is None:
            raise NonExistingAttribute

        return self._left_child

    @property
    def right_child(self) -> Node:
        if self._right_child is None:
            raise NonExistingAttribute

        return self._right_child

    def make_sure_it_is_a_trapezoid(self) -> None:
        if self.node_type != NodeType.TRAPEZOID:
            raise NotATrapezoid

    def replace_by_another_node_in_tree(self, new_node: Node) -> None:
        self.make_sure_it_is_a_trapezoid()

        if new_node.node_type != NodeType.TRAPEZOID:
            raise InconsistentArguments

        if new_node == self:
            return

        for parent in self.parents:
            if parent._left_child == self:
                parent._left_child = new_node

            elif parent._right_child == self:
                parent._right_child = new_node

        new_node.parents.extend(self.parents)

    def split_by_vertex(self, vertex: Vertex) -> None:
        self.make_sure_it_is_a_trapezoid()

        bottom_trapezoid, top_trapezoid = self.trapezoid.split_by_vertex(vertex)

        self.node_type = NodeType.VERTEX
        self.associated_obj = vertex

        self._left_child = Node(trapezoid=bottom_trapezoid, parent=self)
        self._right_child = Node(trapezoid=top_trapezoid, parent=self)

    def split_by_edge(
        self, edge: Edge, created_trap_couples: list[tuple[Trapezoid, Trapezoid]]
    ) -> None:
        self.make_sure_it_is_a_trapezoid()

        left_trapezoid, right_trapezoid = self.trapezoid.split_by_edge(edge)

        created_trap_couples.append((left_trapezoid, right_trapezoid))

        self.node_type = NodeType.EDGE
        self.associated_obj = edge

        self._left_child = Node(trapezoid=left_trapezoid, parent=self)
        self._right_child = Node(trapezoid=right_trapezoid, parent=self)

    def insert_vertex(self, vertex: Vertex) -> None:
        area = self.search_area_containing_vertex(vertex)
        area.split_by_vertex(vertex)

    def search_area_containing_vertex(self, vertex: Vertex) -> Node:
        if self.node_type == NodeType.TRAPEZOID:
            return self

        relevant_child: Node = self.left_child

        if (self.node_type == NodeType.VERTEX and vertex > self.vertex) or (
            self.node_type == NodeType.EDGE and self.edge.is_vertex_at_the_right(vertex)
        ):
            relevant_child = self.right_child

        return relevant_child.search_area_containing_vertex(vertex)

    def insert_edge(
        self,
        edge: Edge,
        top_vertex_just_inserted: bool,
        bottom_vertex_just_inserted: bool,
    ) -> None:
        self.make_sure_it_is_a_trapezoid()

        nodes_to_split_down_direction: list[Node] = []
        current_trap: Trapezoid = self.trapezoid

        while current_trap.bottom_vertex != edge.bottom_vertex:
            below = current_trap.trapezoids_below
            match len(below):
                case 1:
                    current_trap = below[0]

                case 2:
                    left_trap_below = below[0]
                    left_trap_top_rightmost_pt = left_trap_below.get_extreme_point(
                        top=True, right=True
                    )
                    trap_index = (
                        0
                        if edge.is_vertex_at_the_right(left_trap_top_rightmost_pt)
                        else 1
                    )
                    current_trap = below[trap_index]

                case _:
                    raise InconsistentTrapezoidNeighborhood

            nodes_to_split_down_direction.append(current_trap.associated_node)

        nodes_to_split_up_direction: list[Node] = []
        current_trap: Trapezoid = self.trapezoid

        while current_trap.top_vertex != edge.top_vertex:
            above = current_trap.trapezoids_above
            match len(above):
                case 1:
                    current_trap = above[0]

                case 2:
                    left_trap_above = above[0]
                    left_trap_bottom_rightmost_pt = left_trap_above.get_extreme_point(
                        top=False, right=True
                    )
                    trap_index = (
                        0
                        if edge.is_vertex_at_the_right(left_trap_bottom_rightmost_pt)
                        else 1
                    )
                    current_trap = above[trap_index]

                case _:
                    raise InconsistentTrapezoidNeighborhood

            nodes_to_split_up_direction.append(current_trap.associated_node)

        nodes_to_split_up_direction.reverse()

        nodes_to_split = (
            nodes_to_split_up_direction + [self] + nodes_to_split_down_direction
        )

        created_trap_couples: list[tuple[Trapezoid, Trapezoid]] = []
        for node_to_split in nodes_to_split:
            node_to_split.split_by_edge(edge, created_trap_couples)

        self.manage_adjacents_trap_after_edge_split(
            edge,
            created_trap_couples,
            top_vertex_just_inserted,
            bottom_vertex_just_inserted,
        )

        self.merge_trapezoids_if_necessary(created_trap_couples)

    def manage_adjacents_trap_after_edge_split(
        self,
        edge: Edge,
        created_trap_couples: list[tuple[Trapezoid, Trapezoid]],
        top_vertex_just_inserted: bool,
        bottom_vertex_just_inserted: bool,
    ) -> None:
        first_trap_left, first_trap_right = created_trap_couples[0]
        if top_vertex_just_inserted:
            # only 1 trap above and it needs to be above for both
            # but already above for right
            if len(first_trap_right.trapezoids_above) != 1:
                raise InconsistentTrapezoidNeighborhood

            first_trap_left.trapezoids_above = first_trap_right.trapezoids_above.copy()
            trap_above = first_trap_right.trapezoids_above[0]
            trap_above.trapezoids_below = [first_trap_left, first_trap_right]

        else:
            if (
                getattr(first_trap_left.left_edge, "top_vertex", None)
                == edge.top_vertex
            ):  # left upward peak with an old edge
                if len(first_trap_right.trapezoids_above) != 1:
                    raise InconsistentTrapezoidNeighborhood

                # nothing to do

            elif (
                getattr(first_trap_right.right_edge, "top_vertex", None)
                == edge.top_vertex
            ):  # right upward peak with an old edge
                if len(first_trap_right.trapezoids_above) != 1:
                    raise InconsistentTrapezoidNeighborhood

                first_trap_left.trapezoids_above = first_trap_right.trapezoids_above
                first_trap_right.trapezoids_above = []
                replace(
                    first_trap_left.trapezoids_above[0].trapezoids_below,
                    first_trap_right,
                    first_trap_left,
                )

            else:  # the new edge just extend an old edge above
                if len(first_trap_right.trapezoids_above) != 2:
                    raise InconsistentTrapezoidNeighborhood

                left_above, right_above = first_trap_right.trapezoids_above
                first_trap_left.trapezoids_above = [left_above]
                first_trap_right.trapezoids_above = [right_above]
                replace(left_above.trapezoids_below, first_trap_right, first_trap_left)

        last_trap_left, last_trap_right = created_trap_couples[-1]
        if bottom_vertex_just_inserted:
            # only 1 trap below and it needs to be below for both
            # but already below for right
            if len(last_trap_right.trapezoids_below) != 1:
                raise InconsistentTrapezoidNeighborhood

            last_trap_left.trapezoids_below = last_trap_right.trapezoids_below.copy()
            trap_below = last_trap_right.trapezoids_below[0]
            trap_below.trapezoids_above = [last_trap_left, last_trap_right]

        else:
            if (
                getattr(last_trap_left.left_edge, "bottom_vertex", None)
                == edge.bottom_vertex
            ):  # left downward peak with an old edge
                if len(last_trap_right.trapezoids_below) != 1:
                    raise InconsistentTrapezoidNeighborhood

                # nothing to do

            elif (
                getattr(last_trap_right.right_edge, "bottom_vertex", None)
                == edge.bottom_vertex
            ):  # right downward peak with an old edge
                if len(last_trap_right.trapezoids_below) != 1:
                    raise InconsistentTrapezoidNeighborhood

                last_trap_left.trapezoids_below = last_trap_right.trapezoids_below
                last_trap_right.trapezoids_below = []
                replace(
                    last_trap_left.trapezoids_below[0].trapezoids_above,
                    last_trap_right,
                    last_trap_left,
                )

            else:  # the new edge just extend an old edge below
                if len(last_trap_right.trapezoids_below) != 2:
                    raise InconsistentTrapezoidNeighborhood

                left_below, right_below = last_trap_right.trapezoids_below
                last_trap_left.trapezoids_below = [left_below]
                last_trap_right.trapezoids_below = [right_below]
                replace(left_below.trapezoids_above, last_trap_right, last_trap_left)

        for i in range(
            len(created_trap_couples) - 1
        ):  # iterates on the borders between splited trapezoids
            top_left_trap, top_right_trap = created_trap_couples[i]
            bottom_left_trap, bottom_right_trap = created_trap_couples[i + 1]

            if len(top_right_trap.trapezoids_below) == 2:  # downward branch
                if len(bottom_right_trap.trapezoids_above) != 1:
                    raise InconsistentTrapezoidNeighborhood

                branch_point = top_right_trap.trapezoids_below[0].get_extreme_point(
                    top=True, right=True
                )
                if edge.is_vertex_at_the_right(branch_point):
                    top_left_trap.trapezoids_below = [bottom_left_trap]
                    bottom_left_trap.trapezoids_above = [top_left_trap]

                else:
                    additional_bottom_left_trap = top_right_trap.trapezoids_below[0]

                    top_right_trap.trapezoids_below = [bottom_right_trap]
                    bottom_right_trap.trapezoids_above = [top_right_trap]

                    top_left_trap.trapezoids_below = [
                        additional_bottom_left_trap,
                        bottom_left_trap,
                    ]
                    bottom_left_trap.trapezoids_above = [top_left_trap]
                    additional_bottom_left_trap.trapezoids_above = [top_left_trap]

            else:
                if len(top_right_trap.trapezoids_below) != 1:
                    raise InconsistentTrapezoidNeighborhood

                if len(bottom_right_trap.trapezoids_above) == 2:  # upward branch
                    if len(top_right_trap.trapezoids_below) != 1:
                        raise InconsistentTrapezoidNeighborhood

                    branch_point = bottom_right_trap.trapezoids_above[
                        0
                    ].get_extreme_point(top=False, right=True)
                    if edge.is_vertex_at_the_right(branch_point):
                        top_left_trap.trapezoids_below = [bottom_left_trap]
                        bottom_left_trap.trapezoids_above = [top_left_trap]

                    else:
                        additional_top_left_trap = bottom_right_trap.trapezoids_above[0]

                        top_right_trap.trapezoids_below = [bottom_right_trap]
                        bottom_right_trap.trapezoids_above = [top_right_trap]

                        bottom_left_trap.trapezoids_above = [
                            additional_top_left_trap,
                            top_left_trap,
                        ]
                        top_left_trap.trapezoids_below = [bottom_left_trap]
                        additional_top_left_trap.trapezoids_below = [bottom_left_trap]

                else:
                    if len(bottom_right_trap.trapezoids_above) != 1:
                        raise InconsistentTrapezoidNeighborhood

                    top_left_trap.trapezoids_below = [bottom_left_trap]
                    bottom_left_trap.trapezoids_above = [top_left_trap]

    def merge_trapezoids_if_necessary(
        self, created_trap_couples: list[tuple[Trapezoid, Trapezoid]]
    ) -> None:
        """
        The insertion of an edge can create stacked trapezoids that share the same left and right edes, these function
        detect them and merge them.
        """
        for left_or_right in [0, 1]:
            distance_to_top_neighbor = 1
            # When we merge top trap the top one is the one we keep, if we keep the bottom we could remove that
            # another method could be to iterate in reverse order

            for trap_couple_index in range(1, len(created_trap_couples)):
                top_trap = created_trap_couples[
                    trap_couple_index - distance_to_top_neighbor
                ][left_or_right]
                bottom_trap = created_trap_couples[trap_couple_index][left_or_right]

                # maybe we can avoid doing the two comparison as we know the the splitting edge is shared
                if (
                    top_trap.left_edge == bottom_trap.left_edge
                    and top_trap.right_edge == bottom_trap.right_edge
                ):
                    Trapezoid.merge(top_trap, bottom_trap)
                    distance_to_top_neighbor += 1

                else:
                    distance_to_top_neighbor = 1

    def get_all_traps(
        self, trapezoids_acc: list[Trapezoid] | None = None
    ) -> list[Trapezoid]:
        if trapezoids_acc is None:
            trapezoids_acc = []

        if self.node_type == NodeType.TRAPEZOID:
            trapezoids_acc.append(self.trapezoid)

        else:
            self.left_child.get_all_traps(trapezoids_acc)
            self.right_child.get_all_traps(trapezoids_acc)

        return trapezoids_acc
