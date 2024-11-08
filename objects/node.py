from __future__ import annotations

from objects import Vertex
from objects import Edge
from objects import Trapezoid

from utils import replace
from constants import NodeType



class Node:
    node_type:NodeType
    associated_obj:Trapezoid|Edge|Vertex
    left_child:"Node"|None
    right_child:"Node"|None
    parent:"Node"|None


    def __init__(
        self,
        trapezoid:Trapezoid,
        parent:"Node"|None = None
    ) -> None:
        # At the time of its creation a Node is always a leaf, ie a Trapezoid node
        self.node_type = NodeType.TRAPEZOID
        self.associated_obj = trapezoid
        trapezoid.associated_node = self
        self.left_child = None
        self.right_child = None
        self.parent = parent


    def replace_by_another_node_in_tree(self, new_node:"Node") -> None:
        assert(self.node_type == NodeType.TRAPEZOID)

        if self.parent.left_child == self:
            self.parent.left_child = new_node
        else: # I think that a same node can't be left and right child of a same parent but not sure for the moment...
            assert(self.parent.right_child == self)
            self.parent.right_child = new_node


    def split_by_vertex(self, vertex:Vertex) -> None:
        assert(self.node_type == NodeType.TRAPEZOID)
        bottom_trapezoid, top_trapezoid = self.associated_obj.split_by_vertex(vertex)

        self.node_type = NodeType.VERTEX
        self.associated_obj = vertex

        self.left_child = Node(
            trapezoid=bottom_trapezoid,
            parent=self
        )
        self.right_child = Node(
            trapezoid=top_trapezoid,
            parent=self
        )


    def split_by_edge(self, edge:Edge, created_trap_couples:list[tuple[Trapezoid, Trapezoid]]) -> None:
        assert(self.node_type == NodeType.TRAPEZOID)
        left_trapezoid, right_trapezoid = self.associated_obj.split_by_edge(edge)

        created_trap_couples.append((left_trapezoid, right_trapezoid))

        self.node_type = NodeType.EDGE
        self.associated_obj = edge

        self.left_child = Node(
            trapezoid=left_trapezoid,
            parent=self
        )
        self.right_child = Node(
            trapezoid=right_trapezoid,
            parent=self
        )


    def insert_vertex(self, vertex:Vertex) -> None:
        area = self.search_area_containing_vertex(vertex)
        area.split_by_vertex(vertex)
    

    def search_area_containing_vertex(self, vertex:Vertex) -> "Node":
        if self.node_type == NodeType.TRAPEZOID:
            return self

        relevant_child = self.left_child
        
        if (
            (
                self.node_type == NodeType.VERTEX 
                and vertex > self.associated_obj
            ) or (
                self.node_type == NodeType.EDGE 
                and self.associated_obj.is_vertex_at_the_right(vertex)
            )
        ):
            relevant_child = self.right_child

        return relevant_child.search_area_containing_vertex(vertex)


    def display(self, debug:bool=False) -> None:
        if self.node_type == NodeType.TRAPEZOID:
            self.associated_obj.display(debug=debug)
            return

        self.left_child.display(debug)
        self.right_child.display(debug)

    
    def insert_edge(self, edge:Edge, top_vertex_just_inserted:bool, bottom_vertex_just_inserted:bool) -> None:
        assert(self.node_type == NodeType.TRAPEZOID)

        nodes_to_split_down_direction:list["Node"] = []
        current_trap:Trapezoid = self.associated_obj

        while current_trap.bottom_vertex != edge.bottom_vertex:
            below = current_trap.trapezoids_below
            match len(below):
                case 1:
                    current_trap = below[0]

                case 2:
                    left_trap_below = below[0]
                    left_trap_top_rightmost_pt = left_trap_below.get_extreme_point(top=True, right=True)
                    trap_index = 0 if edge.is_vertex_at_the_right(left_trap_top_rightmost_pt) else 1
                    current_trap = below[trap_index]

                case _:
                    raise ValueError("Very strange...")

            nodes_to_split_down_direction.append(current_trap.associated_node)

        nodes_to_split_up_direction:list["Node"] = []
        current_trap:Trapezoid = self.associated_obj

        while current_trap.top_vertex != edge.top_vertex:
            above = current_trap.trapezoids_above
            match len(above):
                case 1:
                    current_trap = above[0]

                case 2:
                    left_trap_above = above[0]
                    left_trap_bottom_rightmost_pt = left_trap_above.get_extreme_point(top=False, right=True)
                    trap_index = 0 if edge.is_vertex_at_the_right(left_trap_bottom_rightmost_pt) else 1
                    current_trap = above[trap_index]

                case _:
                    raise ValueError("Very strange...")

            nodes_to_split_up_direction.append(current_trap.associated_node)

        nodes_to_split_up_direction.reverse()

        nodes_to_split = nodes_to_split_up_direction + [self] + nodes_to_split_down_direction

        created_trap_couples:list[tuple[Trapezoid, Trapezoid]] = []
        for node_to_split in nodes_to_split:
            node_to_split.split_by_edge(edge, created_trap_couples)

        self.manage_adjacents_trap_after_edge_split(edge, created_trap_couples, top_vertex_just_inserted, bottom_vertex_just_inserted)

        self.merge_trapezoids_if_necessary(created_trap_couples)


    def manage_adjacents_trap_after_edge_split(
        self, 
        edge:Edge,
        created_trap_couples:list[tuple[Trapezoid, Trapezoid]], 
        top_vertex_just_inserted:bool, 
        bottom_vertex_just_inserted:bool
    ) -> None:
        first_trap_left, first_trap_right = created_trap_couples[0]
        if top_vertex_just_inserted:
            # only 1 trap above and it needs to be above for both
            # but already above for right
            assert(len(first_trap_right.trapezoids_above) == 1)
            first_trap_left.trapezoids_above = first_trap_right.trapezoids_above.copy()
            trap_above = first_trap_right.trapezoids_above[0]
            trap_above.trapezoids_below = [first_trap_left, first_trap_right]

        else:
            if getattr(first_trap_left.left_edge, "top_vertex", None) == edge.top_vertex: # left upward peak with an old edge
                assert(len(first_trap_right.trapezoids_above) == 1)
                # nothing to do

            elif getattr(first_trap_right.right_edge, "top_vertex", None) == edge.top_vertex: # right upward peak with an old edge
                assert(len(first_trap_right.trapezoids_above) == 1)
                first_trap_left.trapezoids_above = first_trap_right.trapezoids_above.copy()
                first_trap_right.trapezoids_above = []
                replace(first_trap_left.trapezoids_above[0].trapezoids_below, first_trap_right, first_trap_left)

            else: # the new edge just extend an old edge above
                assert(len(first_trap_right.trapezoids_above) == 2)
                left_above, right_above = first_trap_right.trapezoids_above
                first_trap_left.trapezoids_above = [left_above]
                first_trap_right.trapezoids_above = [right_above]
                replace(left_above.trapezoids_below, first_trap_right, first_trap_left)


        last_trap_left, last_trap_right = created_trap_couples[-1]
        if bottom_vertex_just_inserted:
            # only 1 trap below and it needs to be below for both
            # but already below for right
            assert(len(last_trap_right.trapezoids_below) == 1)
            last_trap_left.trapezoids_below = last_trap_right.trapezoids_below.copy()
            trap_below = last_trap_right.trapezoids_below[0]
            trap_below.trapezoids_above = [last_trap_left, last_trap_right]

        else:
            if getattr(last_trap_left.left_edge, "bottom_vertex", None) == edge.bottom_vertex: # left downward peak with an old edge
                assert(len(last_trap_right.trapezoids_below) == 1)
                # nothing to do

            elif getattr(last_trap_right.right_edge, "bottom_vertex", None) == edge.bottom_vertex: # right downward peak with an old edge
                assert(len(last_trap_right.trapezoids_below) == 1)
                last_trap_left.trapezoids_below = last_trap_right.trapezoids_below.copy()
                last_trap_right.trapezoids_below = []
                replace(last_trap_left.trapezoids_below[0].trapezoids_above, last_trap_right, last_trap_left)

            else: # the new edge just extend an old edge below
                assert(len(last_trap_right.trapezoids_below) == 2)
                left_below, right_below = last_trap_right.trapezoids_below
                last_trap_left.trapezoids_below = [left_below]
                last_trap_right.trapezoids_below = [right_below]
                replace(left_below.trapezoids_above, last_trap_right, last_trap_left)


        for i in range(len(created_trap_couples) - 1): # iterates on the borders between splited trapezoids
            top_left_trap, top_right_trap = created_trap_couples[i]
            bottom_left_trap, bottom_right_trap = created_trap_couples[i + 1]

            if len(top_right_trap.trapezoids_below) == 2: # downward branch
                assert(len(bottom_right_trap.trapezoids_above) == 1)

                branch_point = top_right_trap.trapezoids_below[0].get_extreme_point(top=True, right=True)
                if edge.is_vertex_at_the_right(branch_point):
                    top_left_trap.trapezoids_below = [bottom_left_trap]
                    bottom_left_trap.trapezoids_above = [top_left_trap]

                else:
                    additional_bottom_left_trap = top_right_trap.trapezoids_below[0]

                    top_right_trap.trapezoids_below = [bottom_right_trap]
                    bottom_right_trap.trapezoids_above = [top_right_trap]

                    top_left_trap.trapezoids_below = [additional_bottom_left_trap, bottom_left_trap]
                    bottom_left_trap.trapezoids_above = [top_left_trap]
                    additional_bottom_left_trap.trapezoids_above = [top_left_trap]

            else:
                assert(len(top_right_trap.trapezoids_below) == 1)
                if len(bottom_right_trap.trapezoids_above) == 2: # upward branch
                    assert(len(top_right_trap.trapezoids_below) == 1)

                    branch_point = bottom_right_trap.trapezoids_above[0].get_extreme_point(top=False, right=True)
                    if edge.is_vertex_at_the_right(branch_point):
                        top_left_trap.trapezoids_below = [bottom_left_trap]
                        bottom_left_trap.trapezoids_above = [top_left_trap]

                    else:
                        additional_top_left_trap = bottom_right_trap.trapezoids_above[0]

                        top_right_trap.trapezoids_below = [bottom_right_trap]
                        bottom_right_trap.trapezoids_above = [top_right_trap]

                        bottom_left_trap.trapezoids_above = [additional_top_left_trap, top_left_trap]
                        top_left_trap.trapezoids_below = [bottom_left_trap]
                        additional_top_left_trap.trapezoids_below = [bottom_left_trap]

                else:
                    assert(len(top_right_trap.trapezoids_below) == 1)
                    assert(len(bottom_right_trap.trapezoids_above) == 1)

                    top_left_trap.trapezoids_below = [bottom_left_trap]
                    bottom_left_trap.trapezoids_above = [top_left_trap]


    def merge_trapezoids_if_necessary(self,created_trap_couples:list[tuple[Trapezoid, Trapezoid]]) -> None:
        """
        The insertion of an edge can create stacked trapezoids that share the same left and right edes, these function
        detect them and merge them.
        """
        for left_or_right in [0,1]:
            distance_to_top_neighbor = 1 
            # When we merge top trap the top one is the one we keep, if we keep the bottom we could remove that
            # another method could be to iterate in reverse order

            for trap_couple_index in range(1, len(created_trap_couples)):
                top_trap = created_trap_couples[trap_couple_index - distance_to_top_neighbor][left_or_right]
                bottom_trap = created_trap_couples[trap_couple_index][left_or_right]

                # maybe we can avoid doing the two comparison as we know the the splitting edge is shared
                if top_trap.left_edge == bottom_trap.left_edge and top_trap.right_edge == bottom_trap.right_edge:
                    Trapezoid.merge(top_trap, bottom_trap)
                    distance_to_top_neighbor += 1

                else:
                    distance_to_top_neighbor = 1        


    def get_all_traps(self, trapezoids_acc:list[Trapezoid]|None = None)->None:
        if trapezoids_acc is None:
            trapezoids_acc = []

        if self.node_type == NodeType.TRAPEZOID:
            trapezoids_acc.append(self.associated_obj)
            return

        self.left_child.get_all_traps(trapezoids_acc)
        self.right_child.get_all_traps(trapezoids_acc)

    
    def check_consistency(self) -> bool:
        left_consistency = (
            not self.left_child or
            (
                self.left_child.parent == self and
                self.left_child.check_consistency()
            )
        ) 

        right_consistency = (
            not self.right_child or
            (
                self.right_child.parent == self and
                self.right_child.check_consistency()
            )
        ) 

        return left_consistency and right_consistency
