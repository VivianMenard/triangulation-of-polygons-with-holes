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
    from objects import PolygonArea


def trapezoidation(polygon_area: PolygonArea) -> Node:
    edges: list[Edge] = polygon_area.get_edges()
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
        bottom_vertex, top_vertex = edge.get_ordered_vertices()

        top_just_inserted = insert_vertex_if_necessary(top_vertex)
        bottom_just_inserted = insert_vertex_if_necessary(bottom_vertex)

        start_node = search_tree.search_area_containing_vertex(edge.mid_point)

        start_node.insert_edge(edge, top_just_inserted, bottom_just_inserted)

    return search_tree


def select_inside_trapezoids(all_trapezoids: list[Trapezoid]) -> list[Trapezoid]:
    return [trap for trap in all_trapezoids if trap.is_inside]


def group_vertices_by_mountain(
    trapezoids: list[Trapezoid],
) -> dict[Edge, dict[Vertex, Vertex]]:
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
    triangles: list[Triangle] = []

    for monotone_mountain in monotone_mountains:
        triangulate_monotone_mountain(monotone_mountain, triangles)

    return triangles


def triangulate_polygon_area(polygon_area: PolygonArea) -> list[Triangle]:
    search_tree = trapezoidation(polygon_area)

    all_trapezoids = search_tree.get_all_traps()

    inside_trapezoids = select_inside_trapezoids(all_trapezoids)

    monotone_mountains = make_monotone_mountains(inside_trapezoids)

    return make_triangles(monotone_mountains)
