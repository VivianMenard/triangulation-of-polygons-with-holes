from __future__ import annotations

from collections import defaultdict
from random import shuffle
from typing import TYPE_CHECKING, cast

from constants import ANGLE_EPSILON, ANGLE_THRESHOLD
from exceptions import InconsistentTrapezoid
from objects import (
    Edge,
    MonotoneMountain,
    MonotoneVertex,
    Node,
    Trapezoid,
    Triangle,
    Vertex,
)

if TYPE_CHECKING:
    from objects import PolygonalArea


def trapezoidation(polygonal_area: PolygonalArea) -> Node:
    """
    Divides the 2D space into trapezoids according to the polygonal area.

    The decomposition is a tree structure where all edges of the polygonal area are inserted
    one after the other in a randomized order (for performances purpose).
    For each edge, both vertices are first inserted (if not already inserted), then the
    edge itself is inserted.

    Args:
        polygonal_area (PolygonalArea): The polygonal area to use for trapezoid decomposition of the 2D space.

    Returns:
        Node: The root node of the trapezoidal decomposition tree.
    """
    edges: list[Edge] = polygonal_area.get_edges()
    shuffle(edges)

    search_tree = Node(trapezoid=Trapezoid())
    already_inserted: set[Vertex] = set()

    def insert_vertex_if_necessary(vertex: Vertex) -> bool:
        if vertex not in already_inserted:
            search_tree.insert_vertex(vertex)
            already_inserted.add(vertex)
            return True

        return False

    for edge in edges:
        top_just_inserted = insert_vertex_if_necessary(edge.top_vertex)
        bottom_just_inserted = insert_vertex_if_necessary(edge.bottom_vertex)

        search_tree.insert_edge(edge, top_just_inserted, bottom_just_inserted)

    return search_tree


def select_inside_trapezoids(all_trapezoids: list[Trapezoid]) -> list[Trapezoid]:
    """
    Filters the trapezoids to select only those that are inside the polygonal area.

    Args:
        all_trapezoids (list[Trapezoid]): The list of all trapezoids to be filtered.

    Returns:
        list[Trapezoid]: A list of trapezoids that are inside the polygonal area.
    """
    return [trap for trap in all_trapezoids if trap.is_inside]


def group_vertices_by_mountain(
    trapezoids: list[Trapezoid],
) -> dict[Edge, dict[Vertex, Vertex]]:
    """
    Performs the first part of the transformation of a trapezoids partition into
    a monotone mountains partition.

    It iterates on all the trapezoids grouping vertices by monotone mountains.
    The result of this step is a dictionnary that maps every mountain base edge with a dictionnary that gives
    the successor of each vertex in the monotone chain.

    Args:
        trapezoids (list[Trapezoid]): A list of trapezoids partitioning the polygonal area.

    Returns:
        dict[Edge, dict[Vertex, Vertex]]: A dictionary mapping mountain base edges to a dictionnary that gives
            the successor of each vertex in the monotone chain.

    Raises:
        InconsistentTrapezoid: If a trapezoid have an inconsistent structure.
    """
    above_vertex_by_base_edge: dict[Edge, dict[Vertex, Vertex]] = defaultdict(dict)

    for trap in trapezoids:
        mountain_bases: list[Edge] = []

        for edge in [trap.left_edge, trap.right_edge]:
            edge = cast(Edge, edge)
            if (
                trap.bottom_vertex != edge.bottom_vertex
                or trap.top_vertex != edge.top_vertex
            ):
                mountain_bases.append(edge)

        if not len(mountain_bases):
            raise InconsistentTrapezoid

        for mountain_base in mountain_bases:
            above_vertex_by_base_edge[mountain_base][
                cast(Vertex, trap.bottom_vertex)
            ] = cast(Vertex, trap.top_vertex)

    return above_vertex_by_base_edge


def make_monotone_mountains(
    trapezoids: list[Trapezoid],
) -> list[MonotoneMountain]:
    """
    Transforms a trapezoids partition of the polygonal area into a monotone mountains partition of the same area.

    The idea behind this transformation is to draw a line between top and bottom vertices of each trapezoid
    if this line is not already an edge of the polygonal area. The lines newly drawn divide the polygonal
    area into monotone mountains.

    Args:
        trapezoids (list[Trapezoid]): A list of trapezoids partitioning the polygonal area.

    Returns:
        list[MonotoneMountain]: A list of monotone mountains partitioning the polygonal area.
    """
    above_vertex_by_base_edge: dict[Edge, dict[Vertex, Vertex]] = (
        group_vertices_by_mountain(trapezoids)
    )

    monotone_mountains: list[MonotoneMountain] = []

    for base, above_vertex_mapping in above_vertex_by_base_edge.items():
        below_monotone_vertex: MonotoneVertex | None = None
        current_vertex = base.bottom_vertex
        monotone_mountain_created = False

        while current_vertex is not None:
            current_monotone_vertex = MonotoneVertex(
                vertex=current_vertex, below=below_monotone_vertex
            )
            if below_monotone_vertex:
                below_monotone_vertex.above = current_monotone_vertex

            above_vertex = above_vertex_mapping.get(current_vertex, None)
            current_vertex = above_vertex
            below_monotone_vertex = current_monotone_vertex

            if not monotone_mountain_created:
                monotone_mountains.append(
                    MonotoneMountain(current_monotone_vertex, base)
                )
                monotone_mountain_created = True

    return monotone_mountains


def triangulate_monotone_mountain(
    mountain: MonotoneMountain,
    triangles: list[Triangle],
    angle_threshold: float = ANGLE_THRESHOLD,
) -> None:
    """
    Decomposes a monotone mountain into triangles, append the resulting triangles in the `triangles` list
    provided as argument.

    It will try to avoid creating triangle from vertices that form an angle above the angle_threshold,
    if not possible it will retry with an adjusted threshold.

    Args:
        mountain (MonotoneMountain): The monotone mountain to be triangulated.
        triangles (list[Triangle]): The list of triangles to append the results to.
        angle_threshold (float, optional): The angle threshold for triangulation. Defaults to ANGLE_THRESHOLD.
    """
    if mountain.is_degenerated:
        return

    first_non_base_vertex: MonotoneVertex = cast(
        MonotoneVertex, mountain.bottom_vertex.above
    )

    convex_order: bool = Vertex.counter_clockwise(
        mountain.base.top_vertex,
        mountain.base.bottom_vertex,
        first_non_base_vertex.vertex,
    )

    current_vertex: MonotoneVertex = first_non_base_vertex

    angle_closer_to_threshold: float = 180

    while not current_vertex.is_base_vertex:
        below = cast(MonotoneVertex, current_vertex.below)
        above = cast(MonotoneVertex, current_vertex.above)
        current_vertex_convex: bool = (
            Vertex.counter_clockwise(below.vertex, current_vertex.vertex, above.vertex)
            == convex_order
        )

        if not current_vertex_convex:
            current_vertex = above
            continue

        angle: float = Vertex.angle(below.vertex, current_vertex.vertex, above.vertex)

        if angle > angle_threshold:
            current_vertex = above

            if angle < angle_closer_to_threshold:
                angle_closer_to_threshold = angle

            continue

        vertices_counter_clockwise = (
            (below.vertex, current_vertex.vertex, above.vertex)
            if convex_order
            else (below.vertex, above.vertex, current_vertex.vertex)
        )
        triangles.append(Triangle(vertices_counter_clockwise))
        below.above = above
        above.below = below
        current_vertex = above if below.is_base_vertex else below

    # if it's not possible to triangulate the mountain with the current threshold,
    # we retry the triangulation, adjusting the threshold to the best angle found.
    if not mountain.is_degenerated:
        triangulate_monotone_mountain(
            mountain,
            triangles,
            angle_threshold=angle_closer_to_threshold + ANGLE_EPSILON,
        )


def make_triangles(monotone_mountains: list[MonotoneMountain]) -> list[Triangle]:
    """
    Generates triangles from a list of monotone mountains.

    This function takes a list of monotone mountains and applies triangulation to each one,
    returning a list of all the resulting triangles.

    Args:
        monotone_mountains (list[MonotoneMountain]): The list of monotone mountains to be triangulated.

    Returns:
        list[Triangle]: A list of triangles created from the monotone mountains.
    """
    triangles: list[Triangle] = []

    for monotone_mountain in monotone_mountains:
        triangulate_monotone_mountain(monotone_mountain, triangles)

    return triangles


def triangulate_polygonal_area(polygonal_area: PolygonalArea) -> list[Triangle]:
    """
    Triangulates a polygonal area.

    This function first decomposes the polygonal area into trapezoids, then selects the
    trapezoids that are inside, generates monotone mountains from the inside trapezoids
    and then triangulate each monotone mountain to produce a list of triangles that cover
    the polygonal area.

    Args:
        polygonal_area (PolygonalArea): The polygonal area to be triangulated.

    Returns:
        list[Triangle]: A list of triangles resulting from the triangulation of the polygonal area.
    """
    search_tree = trapezoidation(polygonal_area)

    all_trapezoids = search_tree.get_all_traps()

    inside_trapezoids = select_inside_trapezoids(all_trapezoids)

    monotone_mountains = make_monotone_mountains(inside_trapezoids)

    return make_triangles(monotone_mountains)
