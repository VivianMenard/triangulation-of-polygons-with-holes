from __future__ import annotations

from itertools import chain
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

    def find_nodes_to_split_in_direction(
        self, edge: Edge, up_direction: bool
    ) -> list[Node]:
        nodes_to_split: list[Node] = []
        current_trap: Trapezoid = self.trapezoid

        def is_the_end_of_edge(current_trap):
            relevant_vertex_attr = "top_vertex" if up_direction else "bottom_vertex"
            return getattr(current_trap, relevant_vertex_attr) == getattr(
                edge, relevant_vertex_attr
            )

        while not is_the_end_of_edge(current_trap):
            next_traps_in_direction = getattr(
                current_trap, "trapezoids_above" if up_direction else "trapezoids_below"
            )

            match len(next_traps_in_direction):
                case 1:
                    current_trap = next_traps_in_direction[0]

                case 2:
                    left_trap_in_direction = next_traps_in_direction[0]
                    left_trap_relevant_rightmost_pt = (
                        left_trap_in_direction.get_extreme_point(
                            top=not up_direction, right=True
                        )
                    )
                    trap_index = (
                        0
                        if edge.is_vertex_at_the_right(left_trap_relevant_rightmost_pt)
                        else 1
                    )
                    current_trap = next_traps_in_direction[trap_index]

                case _:
                    raise InconsistentTrapezoidNeighborhood

            nodes_to_split.append(current_trap.associated_node)

        return nodes_to_split

    def insert_edge(
        self,
        edge: Edge,
        top_vertex_just_inserted: bool,
        bottom_vertex_just_inserted: bool,
    ) -> None:
        self.make_sure_it_is_a_trapezoid()

        nodes_to_split_down_direction = self.find_nodes_to_split_in_direction(
            edge, up_direction=False
        )
        nodes_to_split_up_direction = self.find_nodes_to_split_in_direction(
            edge, up_direction=True
        )

        created_trap_couples: list[tuple[Trapezoid, Trapezoid]] = []
        for node_to_split in chain(
            reversed(nodes_to_split_up_direction), [self], nodes_to_split_down_direction
        ):  # iterates on nodes to split from top to bottom
            node_to_split.split_by_edge(edge, created_trap_couples)

        self.manage_adjacents_trap_after_edge_split(
            edge,
            created_trap_couples,
            top_vertex_just_inserted,
            bottom_vertex_just_inserted,
        )

        self.merge_redundant_trapezoids(created_trap_couples)

    def manage_adjacents_trap_after_edge_split(
        self,
        edge: Edge,
        created_trap_couples: list[tuple[Trapezoid, Trapezoid]],
        top_vertex_just_inserted: bool,
        bottom_vertex_just_inserted: bool,
    ) -> None:
        def get_edge_vertex(edge: Edge | None, top: bool) -> Vertex | None:
            if edge is None:
                return None

            return edge.get_vertex(top=top)

        # first handle adjacent trapezoids for both ends of the inserted edge
        for relevant_trap_couple_index, vertex_just_inserted, top in [
            [0, top_vertex_just_inserted, True],  # top end
            [-1, bottom_vertex_just_inserted, False],  # bottom end
        ]:
            end_trap_left, end_trap_right = created_trap_couples[
                relevant_trap_couple_index
            ]
            exterior_adjacent_traps = end_trap_right.get_adjacent_traps(top=top)

            if vertex_just_inserted:
                # only 1 exterior adjacent trapezoid and it needs to be adjacent for both
                # but already adjacent for right
                if len(exterior_adjacent_traps) != 1:
                    raise InconsistentTrapezoidNeighborhood

                end_trap_left.set_adjacent_traps(
                    exterior_adjacent_traps.copy(), top=top
                )
                adjacent_trap = exterior_adjacent_traps[0]
                adjacent_trap.set_adjacent_traps(
                    [end_trap_left, end_trap_right], top=not top
                )

            else:
                edge_relevant_end = get_edge_vertex(edge, top=top)
                if (
                    get_edge_vertex(end_trap_left.left_edge, top=top)
                    == edge_relevant_end
                ):  # left peak with an old edge
                    if len(exterior_adjacent_traps) != 1:
                        raise InconsistentTrapezoidNeighborhood

                    # nothing to do

                elif (
                    get_edge_vertex(end_trap_right.right_edge, top=top)
                    == edge_relevant_end
                ):  # right peak with an old edge
                    if len(exterior_adjacent_traps) != 1:
                        raise InconsistentTrapezoidNeighborhood

                    end_trap_left.set_adjacent_traps(exterior_adjacent_traps, top=top)
                    end_trap_right.set_adjacent_traps([], top=top)
                    replace(
                        exterior_adjacent_traps[0].get_adjacent_traps(top=not top),
                        end_trap_right,
                        end_trap_left,
                    )

                else:  # the new edge just extend an old edge
                    if len(exterior_adjacent_traps) != 2:
                        raise InconsistentTrapezoidNeighborhood

                    left_adjacent, right_adjacent = exterior_adjacent_traps
                    end_trap_left.set_adjacent_traps([left_adjacent], top=top)
                    end_trap_right.set_adjacent_traps([right_adjacent], top=top)
                    replace(
                        left_adjacent.get_adjacent_traps(top=not top),
                        end_trap_right,
                        end_trap_left,
                    )

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

    def merge_redundant_trapezoids(
        self, created_trap_couples: list[tuple[Trapezoid, Trapezoid]]
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
