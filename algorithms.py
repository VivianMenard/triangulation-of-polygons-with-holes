from __future__ import annotations

from collections import defaultdict
from random import shuffle
from typing import TYPE_CHECKING, cast

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
from utils import counter_clockwise

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


def make_monotone_mountains(
    trapezoids: list[Trapezoid],
) -> list[MonotoneMountain]:
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
    mountain: MonotoneMountain, triangles: list[Triangle]
) -> None:
    if mountain.is_degenerated:
        return

    first_non_base_vertex: MonotoneVertex = mountain.bottom_vertex.above

    convex_order: bool = counter_clockwise(
        mountain.base.top_vertex,
        mountain.base.bottom_vertex,
        first_non_base_vertex.vertex,
    )

    current_vertex: MonotoneVertex = first_non_base_vertex

    while not current_vertex.is_base_vertex:
        below = current_vertex.below
        above = current_vertex.above
        is_current_vertex_convex = (
            counter_clockwise(below.vertex, current_vertex.vertex, above.vertex)
            == convex_order
        )

        if is_current_vertex_convex:
            vertices_counter_clockwise = (
                (below.vertex, current_vertex.vertex, above.vertex)
                if convex_order
                else (below.vertex, above.vertex, current_vertex.vertex)
            )
            triangles.append(Triangle(vertices_counter_clockwise))
            below.above = above
            above.below = below
            current_vertex = above if below.is_base_vertex else below

        else:
            current_vertex = above


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
