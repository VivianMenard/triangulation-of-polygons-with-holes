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
    """
    Represents a trapezoid in the 2D trapezoidal decomposition.

    A trapezoid is a geometric region defined by its top and bottom vertices,
    as well as its left and right edges. Any of these vertices or edges can be absent,
    indicating that the trapezoid extends infinitely in that direction.

    For efficient calculations, a trapezoid keeps track of its neighboring trapezoids
    (directly above and below) and its corresponding node in the search structure.
    """

    traps_by_right_edge: ClassVar[DefaultDict[Edge, set[Trapezoid]]] = defaultdict(set)
    """
    Class-level mapping of right edges to the set of trapezoids using them as a right boundary.
    This is used to efficiently identify trapezoids inside the polygonal area.
    """

    top_vertex: Vertex | None
    """
    The top vertex of the trapezoid. If None, the trapezoid extends infinitely upward.
    """
    bottom_vertex: Vertex | None
    """
    The bottom vertex of the trapezoid. If None, the trapezoid extends infinitely downward.
    """
    trapezoids_above: list[Trapezoid]
    """
    A list of up to two trapezoids directly above this trapezoid.
    If there are two trapezoids, the first is positioned to the left.
    """
    trapezoids_below: list[Trapezoid]
    """
    A list of up to two trapezoids directly below this trapezoid.
    If there are two trapezoids, the first is positioned to the left.
    """
    left_edge: Edge | None
    """
    The left boundary of the trapezoid. If None, the trapezoid extends infinitely to the left.
    """
    _right_edge: Edge | None
    """
    The right boundary of the trapezoid. If None, the trapezoid extends infinitely to the right.

    This attribute is private. Use the `right_edge` setter to modify it, as the setter ensures
    that `traps_by_right_edge` is updated accordingly.
    """
    _associated_node: Node | None
    """
    The node in the search structure corresponding to this trapezoid.
    """

    def __init__(
        self,
        top_vertex: Vertex | None = None,
        bottom_vertex: Vertex | None = None,
        trapezoids_above: list[Trapezoid] | None = None,
        trapezoids_below: list[Trapezoid] | None = None,
        left_edge: Edge | None = None,
        right_edge: Edge | None = None,
    ) -> None:
        """
        Initializes a new Trapezoid object.

        A trapezoid is defined by its boundaries (vertices/edges), and its relationships with neighboring trapezoids.

        Args:
            top_vertex (Vertex | None): The top vertex of the trapezoid. Defaults to None, indicating infinite extension upward.
            bottom_vertex (Vertex | None): The bottom vertex of the trapezoid. Defaults to None, indicating infinite extension downward.
            trapezoids_above (list[Trapezoid] | None): The trapezoids directly above this one. Defaults to an empty list if not provided.
            trapezoids_below (list[Trapezoid] | None): The trapezoids directly below this one. Defaults to an empty list if not provided.
            left_edge (Edge | None): The left edge of the trapezoid. Defaults to None, indicating infinite extension to the left.
            right_edge (Edge | None): The right edge of the trapezoid. Defaults to None, indicating infinite extension to the right.
        """
        self.top_vertex = top_vertex
        self.bottom_vertex = bottom_vertex
        self.trapezoids_above = [] if trapezoids_above is None else trapezoids_above
        self.trapezoids_below = [] if trapezoids_below is None else trapezoids_below
        self.left_edge = left_edge
        self._right_edge = None
        self.right_edge = right_edge
        self._associated_node = None

    @property
    def associated_node(self) -> Node:
        """
        Gets or sets the node associated with this trapezoid in the search structure.

        - Getter: Returns the node currently associated with the trapezoid.
            Raises `NonExistingAttribute` if no node is set.
        - Setter: Associates a new node with the trapezoid.

        Args (for setter):
            new_node (Node): The node to associate with the trapezoid.

        Returns (for getter):
            Node: The associated node .

        Raises:
            NonExistingAttribute: If no node is currently associated when accessing.
        """
        if self._associated_node is None:
            raise NonExistingAttribute

        return self._associated_node

    @associated_node.setter
    def associated_node(self, new_node: Node) -> None:
        self._associated_node = new_node

    @property
    def right_edge(self) -> Edge | None:
        """
        Gets or sets the right edge of the trapezoid.

        - Getter: Returns the current right edge of the trapezoid.
        - Setter: Updates the right edge and ensures the trapezoid is correctly registered in the edge registry.

        Args (for setter):
            new_right_edge (Edge | None): The new right edge for the trapezoid,
                or None if the trapezoid extends infinitely to the right.

        Returns (for getter):
            Edge | None: The current right edge of the trapezoid or None if the trapezoid extends infinitely
                to the right.
        """
        return self._right_edge

    @right_edge.setter
    def right_edge(self, new_right_edge: Edge | None) -> None:
        self.remove_from_edge_registry()

        self._right_edge = new_right_edge

        self.register_in_edge_registry()

    def get_adjacent_traps(self, top: bool) -> list[Trapezoid]:
        """
        Retrieves the trapezoids adjacent to this one in the specified direction.

        Args:
            top (bool): If True, retrieves trapezoids above this one; if False, retrieves trapezoids below.

        Returns:
            list[Trapezoid]: A list of up to two adjacent trapezoids in the specified direction.
        """
        if top:
            return self.trapezoids_above

        return self.trapezoids_below

    def set_adjacent_traps(self, new_traps: list[Trapezoid], top: bool) -> None:
        """
        Updates the trapezoids adjacent to this one in the specified direction.

        Args:
            new_traps (list[Trapezoid]): The new list of adjacent trapezoids.
            top (bool): If True, updates trapezoids above; if False, updates trapezoids below.
        """
        if top:
            self.trapezoids_above = new_traps
        else:
            self.trapezoids_below = new_traps

    def remove_from_edge_registry(self) -> None:
        """
        Removes this trapezoid from the global registry of trapezoids mapped by their right edge.
        """
        if self._right_edge is not None:
            Trapezoid.traps_by_right_edge[self._right_edge].remove(self)

    def register_in_edge_registry(self) -> None:
        """
        Adds this trapezoid to the global registry of trapezoids mapped by their right edge.
        """
        if self._right_edge is not None:
            Trapezoid.traps_by_right_edge[self._right_edge].add(self)

    @cached_property
    def is_inside(self) -> bool:
        """
        Determines whether the trapezoid lies inside the polygonal area.

        This method is analogous to the point-in-polygon algorithm: a point is inside a polygon
        if the number of crossings of the polygon's boundary along a horizontal line to the left of the point is odd.
        If the trapezoid extends infinitely on either side, it is outside (the polygonal area is finite,
        so an infinite trapezoid cannot be inside). Otherwise, we can locate a trapezoid to its left using
        the `traps_by_right_edge` mapping. Since the two trapezoids are separated by an edge, we know by parity
        that this trapezoid is outside if the other is inside, and vice versa. The "is_inside" property can then
        be determined recursively.

        Thanks to caching, the calculation of this property across all trapezoids is linear in complexity, as the result
        for each trapezoid is computed only once.

        Returns:
            bool: True if the trapezoid is inside the polygonal area, False otherwise.
        """
        if self.right_edge is None or self.left_edge is None:
            return False

        left_traps = Trapezoid.traps_by_right_edge[self.left_edge]
        left_trap = next(iter(left_traps))

        return not left_trap.is_inside

    def duplicate(self) -> Trapezoid:
        """
        Creates a duplicate of the current trapezoid with the same vertices and edges.

        The duplicated trapezoid retains the same top and bottom vertices, as well as the same left and right edges.
        The adjacency information (`trapezoids_above` and `trapezoids_below`) and the associated node are not copied.

        Returns:
            Trapezoid: A new trapezoid instance with the same boundaries.
        """
        return Trapezoid(
            top_vertex=self.top_vertex,
            bottom_vertex=self.bottom_vertex,
            left_edge=self.left_edge,
            right_edge=self.right_edge,
        )

    def split_by_vertex(self, vertex: Vertex) -> tuple[Trapezoid, Trapezoid]:
        """
        Splits the trapezoid horizontally into two trapezoids using a given vertex as the dividing point.

        This operation reuses the current trapezoid as top trapezoid and creates a new bottom trapezoid:
        - The top trapezoid is updated to have the provided vertex as its bottom vertex, and its `trapezoids_below` list
        is updated to reference the newly created bottom trapezoid.
        - The bottom trapezoid is a duplicate of the original trapezoid, with its top vertex set to the provided vertex.

        The adjacency relationships of the bottom trapezoid are defined as follows:
        - The top trapezoid is its only neighbor above.
        - It inherits the neighbors below from the original trapezoid, and those neighbors are updated to reference
        the bottom trapezoid instead of the original trapezoid as above them.

        Args:
            vertex (Vertex): The vertex used to split the trapezoid.

        Returns:
            tuple[Trapezoid, Trapezoid]: A tuple containing the bottom trapezoid (newly created) and the top trapezoid (modified original).
        """
        top_trapezoid = self
        bottom_trapezoid = self.duplicate()

        top_trapezoid.bottom_vertex = vertex
        bottom_trapezoid.top_vertex = vertex

        bottom_trapezoid.trapezoids_above = [top_trapezoid]
        bottom_trapezoid.trapezoids_below = self.trapezoids_below
        for trap in self.trapezoids_below:
            replace(trap.trapezoids_above, self, bottom_trapezoid)
        top_trapezoid.trapezoids_below = [bottom_trapezoid]

        return (bottom_trapezoid, top_trapezoid)

    def split_by_edge(self, edge: Edge) -> tuple[Trapezoid, Trapezoid]:
        """
        Splits the trapezoid obliquely into two trapezoids using a given edge as the dividing boundary.

        This operation creates a left trapezoid and reuses the current trapezoid as the right trapezoid:
        - The left trapezoid is a duplicate of the original trapezoid with its right edge set to the provided edge.
        - The right trapezoid (the original trapezoid) is updated with its left edge set to the provided edge.

        WARNING: This method does not handle the adjacency relationships. Managing these relationships is a
        responsibility of the `manage_adjacent_trapezoids_after_edge_split` method, which performs the intricate
        work of ensuring proper connections between trapezoids.

        Args:
            edge (Edge): The edge used to divide the trapezoid into two parts.

        Returns:
            tuple[Trapezoid, Trapezoid]: A tuple containing the left trapezoid (newly created) and the right trapezoid (modified original).
        """
        right_trapezoid = self
        left_trapezoid = self.duplicate()

        left_trapezoid.right_edge = edge
        right_trapezoid.left_edge = edge

        return (left_trapezoid, right_trapezoid)

    def get_extreme_point(self, top: bool, right: bool) -> Vertex:
        """
        Calculates one of the four extreme points of the trapezoid.

        The trapezoid has four extreme points (if it is degenerated two of these points can be the same):
        top-left, top-right, bottom-left, and bottom-right. By setting top and right arguments you can pick
        the one you want.

        Args:
            top (bool): If True, choose the top extreme points; if False, choose the bottom extreme points.
            right (bool): If True, choose the right extreme points; if False, choose the left extreme points.

        Raises:
            NonExistingExtremePoint: If the requested extreme point does not exist.

        Returns:
            Vertex: The selected extreme point of the trapezoid.
        """
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
