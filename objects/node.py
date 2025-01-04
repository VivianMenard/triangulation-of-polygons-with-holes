from __future__ import annotations

from itertools import chain
from typing import cast

from constants import NodeType
from exceptions import (
    InconsistentArguments,
    InconsistentTrapezoidNeighborhood,
    NonExistingAttribute,
    NotATrapezoid,
    NotTheRoot,
)

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

    def make_sure_it_is_the_root(self) -> None:
        if len(self.parents):
            raise NotTheRoot

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
        self.make_sure_it_is_the_root()

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
            next_traps_in_direction = current_trap.get_adjacent_traps(top=up_direction)

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
        top_just_inserted: bool,
        bottom_just_inserted: bool,
    ) -> None:
        self.make_sure_it_is_the_root()

        start_node = self.search_area_containing_vertex(edge.mid_point)

        nodes_to_split_down_direction = start_node.find_nodes_to_split_in_direction(
            edge, up_direction=False
        )
        nodes_to_split_up_direction = start_node.find_nodes_to_split_in_direction(
            edge, up_direction=True
        )

        created_trap_couples: list[tuple[Trapezoid, Trapezoid]] = []
        for node_to_split in chain(
            reversed(nodes_to_split_up_direction),
            [start_node],
            nodes_to_split_down_direction,
        ):  # iterates on nodes to split from top to bottom
            node_to_split.split_by_edge(edge, created_trap_couples)

        Trapezoid.manage_adjacent_trapezoids_after_edge_split(
            edge,
            created_trap_couples,
            top_just_inserted,
            bottom_just_inserted,
        )

        Trapezoid.merge_redundant_trapezoids(created_trap_couples)

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
