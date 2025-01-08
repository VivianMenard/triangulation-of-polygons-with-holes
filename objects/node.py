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
    """
    Represents a node in the trapezoidal decomposition search structure.

    This structure is used as a binary tree to locate the trapezoid containing a point,
    though it is not strictly a tree since a node can have multiple parents (but all nodes
    are ultimately descended from a single root node).

    The leaves of this structure represent the trapezoids in the 2D space decomposition.
    Internal nodes represent vertices or edges that divide the space.

    - If the node represents a vertex, its right child represents the region above it,
    and its left child represents the region below it.
    - If the node represents an edge, its right child represents the region to the right
    of the edge, and its left child represents the region to the left of the edge.
    """

    __node_type: NodeType
    """The type of the node, indicating whether it represents a trapezoid, an edge, or a vertex."""
    __associated_obj: Trapezoid | Edge | Vertex
    """The object associated with the node, which can be a Trapezoid, an Edge, or a Vertex."""
    __left_child: Node | None
    """
    The left child of the node, if it exists. 
    - Represents the region below the vertex if the node is a vertex.
    - Represents the region to the left of the edge if the node is an edge.
    """
    __right_child: Node | None
    """
    The right child of the node, if it exists. 
    - Represents the region above the vertex if the node is a vertex.
    - Represents the region to the right of the edge if the node is an edge.
    """
    __parents: list[Node]
    """
    The parents of the node. A node may have:
    - 0 parents if it is the root node of the structure.
    - 1 parent in a normal case.
    - More than 1 parent if it results from the merging of multiple nodes.
    """

    def __init__(self, trapezoid: Trapezoid, parent: Node | None = None) -> None:
        """
        Initializes a new Node. A newly created node is always added at the bottom of the structure,
        and at the time of its creation, it is always a leaf node representing a trapezoid.

        Initially, a node always has a single parent, as multi-parent nodes result only from merging operations.

        Args:
            trapezoid (Trapezoid): The trapezoid associated with the new node.
            parent (Node | None): The parent node, if provided.
        """
        self.__node_type = NodeType.TRAPEZOID
        self.__associated_obj = trapezoid
        trapezoid.associated_node = self
        self.__left_child = None
        self.__right_child = None
        self.__parents = []

        if parent:
            self.__parents.append(parent)

    @property
    def trapezoid(self) -> Trapezoid:
        """
        Gets the trapezoid associated with this node.

        Returns:
            Trapezoid: The trapezoid if the node type is TRAPEZOID.

        Raises:
            NonExistingAttribute: If the node type is not TRAPEZOID.
        """
        if self.__node_type != NodeType.TRAPEZOID:
            raise NonExistingAttribute

        return cast(Trapezoid, self.__associated_obj)

    @property
    def vertex(self) -> Vertex:
        """
        Gets the vertex associated with this node.

        Returns:
            Vertex: The vertex if the node type is VERTEX.

        Raises:
            NonExistingAttribute: If the node type is not VERTEX.
        """
        if self.__node_type != NodeType.VERTEX:
            raise NonExistingAttribute

        return cast(Vertex, self.__associated_obj)

    @property
    def edge(self) -> Edge:
        """
        Gets the edge associated with this node.

        Returns:
            Edge: The edge if the node type is EDGE.

        Raises:
            NonExistingAttribute: If the node type is not EDGE.
        """
        if self.__node_type != NodeType.EDGE:
            raise NonExistingAttribute

        return cast(Edge, self.__associated_obj)

    @property
    def left_child(self) -> Node:
        """
        Gets the left child of the node.

        Returns:
            Node: The left child if the node is not a leaf.

        Raises:
            NonExistingAttribute: If the node is a leaf.
        """
        if self.__left_child is None:
            raise NonExistingAttribute

        return self.__left_child

    @property
    def right_child(self) -> Node:
        """
        Gets the right child of the node.

        Returns:
            Node: The right child if the node is not a leaf.

        Raises:
            NonExistingAttribute: If the node is a leaf.
        """
        if self.__right_child is None:
            raise NonExistingAttribute

        return self.__right_child

    def __make_sure_it_is_a_trapezoid(self) -> None:
        """
        Ensures that the node is a trapezoid node.

        Raises:
            NotATrapezoid: If the node type is not TRAPEZOID.
        """
        if self.__node_type != NodeType.TRAPEZOID:
            raise NotATrapezoid

    def __make_sure_it_is_the_root(self) -> None:
        """
        Ensures that the node is the root node of the search structure.

        Raises:
            NotTheRoot: If the node is the the root node.
        """
        if len(self.__parents):
            raise NotTheRoot

    def replace_by_another_node_in_tree(self, new_node: Node) -> None:
        """
        Redirects all parent pointers that refer to this node (as left_child or right_child) to a new node.

        This function is primarily used during the merging of trapezoids. When multiple trapezoids are merged,
        only one of their corresponding nodes is kept, and all others are replaced by the retained node.

        Only a trapezoid node can be replaced, and it must be replaced by another trapezoid node.

        Args:
            new_node (Node): The node that will replace this node.

        Raises:
            NotATrapezoid: If this node is not a trapezoid node.
            InconsistentArguments: If the provided new node is not a trapezoid node.
        """
        self.__make_sure_it_is_a_trapezoid()

        if new_node.__node_type != NodeType.TRAPEZOID:
            raise InconsistentArguments

        if new_node == self:
            return

        for parent in self.__parents:
            if parent.__left_child == self:
                parent.__left_child = new_node

            elif parent.__right_child == self:
                parent.__right_child = new_node

        new_node.__parents.extend(self.__parents)

    def __split_by_vertex(self, vertex: Vertex) -> None:
        """
        Splits the trapezoid represented by this node into two trapezoids using a vertex.

        This operation modifies the current node to represent the vertex that splits the trapezoid.
        Two new child nodes are created: the left child represents the trapezoid below the vertex,
        and the right child represents the trapezoid above the vertex.

        Args:
            vertex (Vertex): The vertex used to split the trapezoid.

        Raises:
            NotATrapezoid: If this node does not represent a trapezoid.
        """
        self.__make_sure_it_is_a_trapezoid()

        bottom_trapezoid, top_trapezoid = self.trapezoid.split_by_vertex(vertex)

        self.__node_type = NodeType.VERTEX
        self.__associated_obj = vertex

        self.__left_child = Node(trapezoid=bottom_trapezoid, parent=self)
        self.__right_child = Node(trapezoid=top_trapezoid, parent=self)

    def __split_by_edge(
        self, edge: Edge, created_trap_couples: list[tuple[Trapezoid, Trapezoid]]
    ) -> None:
        """
        Splits the trapezoid represented by this node into two trapezoids using an edge.

        This operation modifies the current node to represent the edge that splits the trapezoid.
        Two new child nodes are created: the left child represents the trapezoid to the left of the edge,
        and the right child represents the trapezoid to the right of the edge. The newly created trapezoids
        are also recorded in the provided list of trapezoid pairs for further operations.

        Args:
            edge (Edge): The edge used to split the trapezoid.
            created_trap_couples (list[tuple[Trapezoid, Trapezoid]]): A list to which the pair of newly
                created trapezoids (left and right) will be appended.

        Raises:
            NotATrapezoid: If this node does not represent a trapezoid.
        """
        self.__make_sure_it_is_a_trapezoid()

        left_trapezoid, right_trapezoid = self.trapezoid.split_by_edge(edge)

        created_trap_couples.append((left_trapezoid, right_trapezoid))

        self.__node_type = NodeType.EDGE
        self.__associated_obj = edge

        self.__left_child = Node(trapezoid=left_trapezoid, parent=self)
        self.__right_child = Node(trapezoid=right_trapezoid, parent=self)

    def insert_vertex(self, vertex: Vertex) -> None:
        """
        Inserts a vertex into the trapezoidal decomposition structure.

        This method must be called on the root node of the structure.

        This operation finds the trapezoid that contains the given vertex, then splits that trapezoid
        into two regions (above and below the vertex) by creating a new vertex node and two child nodes
        representing the resulting trapezoids.

        Args:
            vertex (Vertex): The vertex to insert into the trapezoidal decomposition.

        Raises:
            NotTheRoot: If this node is not the root of the structure.
        """
        self.__make_sure_it_is_the_root()

        area = self.__search_area_containing_vertex(vertex)
        area.__split_by_vertex(vertex)

    def __search_area_containing_vertex(self, vertex: Vertex) -> Node:
        """
        Finds the trapezoid node in the search structure that contains the given vertex.

        This method navigates the trapezoidal decomposition search structure starting from the current
        node, following the appropriate child nodes based on the type of the current node (vertex or edge)
        and the position of the vertex relative to the related vertex/edge.

        Args:
            vertex (Vertex): The vertex for which the containing trapezoid is to be found.

        Returns:
            Node: The trapezoid node containing the given vertex.
        """
        if self.__node_type == NodeType.TRAPEZOID:
            return self

        relevant_child: Node = self.left_child

        if (self.__node_type == NodeType.VERTEX and vertex > self.vertex) or (
            self.__node_type == NodeType.EDGE
            and self.edge.is_vertex_at_the_right(vertex)
        ):
            relevant_child = self.right_child

        return relevant_child.__search_area_containing_vertex(vertex)

    def __find_nodes_to_split_in_direction(
        self, edge: Edge, up_direction: bool
    ) -> list[Node]:
        """
        Finds the sequence of nodes to split along a given direction for an edge insertion.

        This method identifies the nodes in the trapezoidal decomposition that need to be split
        when an edge is being inserted, starting from the current node and moving either upwards
        or downwards.

        Details:
            - The method begins with the trapezoid associated with the current node.
            - It iteratively moves to adjacent trapezoids in the specified direction until the endpoint
            of the edge is reached.
            - If two adjacent trapezoids are found in the specified direction, the method determines the
            correct trapezoid to follow based on the edge's position relative to the rightmost point of the
            left trapezoid.
            - For each traversed trapezoid, its associated node is added to the list of nodes to be split.

        Args:
            edge (Edge): The edge being inserted into the trapezoidal decomposition.
            up_direction (bool): Direction of traversal. If True, moves upwards in the decomposition;
                otherwise, moves downwards.

        Returns:
            list[Node]: A list of nodes that need to be split along the specified direction.

        Raises:
            InconsistentTrapezoidNeighborhood: If the trapezoid neighborhood configuration is invalid.
        """
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
        """
        Inserts an edge into the trapezoidal decomposition structure.

        This method must be called on the root node of the structure.

        Detailled process:
            - The function starts by locating the trapezoid containing the midpoint of the edge.
            - It then determines the sequence of nodes to split, both upwards and downwards from the start node.
            - Each affected node is split by the edge, and the resulting trapezoid pairs are recorded.
            - The adjacency relationships of the trapezoids are adjusted to reflect the edge insertion.
            - Any redundant trapezoids resulting from the operation are merged to optimize the decomposition.

        Args:
            edge (Edge): The edge to be inserted into the trapezoidal decomposition.
            top_just_inserted (bool): Indicates if the top endpoint of the edge was recently inserted.
            bottom_just_inserted (bool): Indicates if the bottom endpoint of the edge was recently inserted.

        Raises:
            NotARootNode: If the current node is not the root of the search structure.
        """
        self.__make_sure_it_is_the_root()

        start_node = self.__search_area_containing_vertex(edge.mid_point)

        nodes_to_split_down_direction = start_node.__find_nodes_to_split_in_direction(
            edge, up_direction=False
        )
        nodes_to_split_up_direction = start_node.__find_nodes_to_split_in_direction(
            edge, up_direction=True
        )

        created_trap_couples: list[tuple[Trapezoid, Trapezoid]] = []
        for node_to_split in chain(
            reversed(nodes_to_split_up_direction),
            [start_node],
            nodes_to_split_down_direction,
        ):  # iterates on nodes to split from top to bottom
            node_to_split.__split_by_edge(edge, created_trap_couples)

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
        """
        Collects all trapezoids from the subtree rooted at this node.

        This method traverses the search structure starting from the current node and gathers all trapezoids
        represented by the leaf nodes in the subtree. If the current node is a trapezoid node, it is directly
        added to the accumulator list. For non-leaf nodes, the method recursively visits the left and right
        children to gather trapezoids.

        Args:
            trapezoids_acc (list[Trapezoid] | None, optional): A list to accumulate trapezoids. If None,
                a new list is created.

        Returns:
            list[Trapezoid]: A list of all trapezoids found in the subtree.
        """
        if trapezoids_acc is None:
            trapezoids_acc = []

        if self.__node_type == NodeType.TRAPEZOID:
            trapezoids_acc.append(self.trapezoid)

        else:
            self.left_child.get_all_traps(trapezoids_acc)
            self.right_child.get_all_traps(trapezoids_acc)

        return trapezoids_acc
