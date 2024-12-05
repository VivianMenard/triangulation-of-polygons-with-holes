from tkinter import BOTH, LEFT, Button, Canvas, Event, Tk

from algorithms import (
    make_monotone_mountains,
    make_triangles,
    select_inside_trapezoids,
    trapezoidation,
)
from objects import Polygon, PolygonArea, Triangle, Vertex
from utils import get_random_pastel_color, segment_intersect


class PolygonAreaDrawer:
    canvas: Canvas
    clear_button: Button
    clear_last_button: Button
    point_color: str
    line_color: str
    point_radius: int
    polygons: list[Polygon]
    objects_ids_by_polygon: list[list[int]]
    triangles_ids: list[int]
    in_progress: bool
    triangles_colors: dict[tuple[int, int, int], str]

    def __init__(self, root: Tk) -> None:
        self.canvas = Canvas(root, bg="white")
        self.canvas.pack(fill=BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<Button-3>", self.close_polygon)

        self.clear_button = Button(
            root, text="Clear", command=self.clear, state="disabled"
        )
        self.clear_button.pack(side=LEFT, padx=(20, 5), pady=10)

        self.clear_last_button = Button(
            root,
            text="Clear last polygon",
            command=self.clear_last_polygon,
            state="disabled",
        )
        self.clear_last_button.pack(side=LEFT, padx=(5, 5), pady=10)

        self.point_color = "brown"
        self.line_color = "grey"
        self.point_radius = 2

        self.polygons = []
        self.objects_ids_by_polygon = []
        self.triangles_ids = []
        self.in_progress = False
        self.triangles_colors = {}

    def add_point(self, event: Event) -> None:
        new_point = Vertex(event.x, event.y)

        if self.in_progress and self.intersect_already_drawn_lines(new_point):
            return

        if not self.in_progress:
            self.polygons.append([])
            self.objects_ids_by_polygon.append([])
            self.in_progress = True

            self.update_buttons()

        polygon = self.polygons[-1]
        polygon.append(new_point)
        self.draw_point(new_point)

        if len(polygon) > 1:
            self.draw_line(polygon[-2], polygon[-1])

    def close_polygon(self, _: Event) -> None:
        polygon = self.polygons[-1]

        if len(polygon) < 3 or self.intersect_already_drawn_lines():
            return

        self.draw_line(polygon[-1], polygon[0])
        self.in_progress = False
        self.triangulate()

    def clear(self) -> None:
        self.canvas.delete("all")
        self.polygons = []
        self.triangles_colors = {}
        self.in_progress = False

        self.update_buttons()

    def clear_last_polygon(self) -> None:
        if not self.polygons:
            return

        del self.polygons[-1]
        self.in_progress = False

        for line_id in self.objects_ids_by_polygon[-1]:
            self.canvas.delete(line_id)

        del self.objects_ids_by_polygon[-1]

        self.update_buttons()
        self.triangulate()

    def update_buttons(self) -> None:
        clear_buttons_enabled = bool(self.polygons)

        self.update_button_state(self.clear_button, clear_buttons_enabled)
        self.update_button_state(self.clear_last_button, clear_buttons_enabled)

    def update_button_state(self, button: Button, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        button.config(state=state)

    def draw_point(self, point: Vertex) -> None:
        pt_id = self.canvas.create_oval(
            point.x - self.point_radius,
            point.y - self.point_radius,
            point.x + self.point_radius,
            point.y + self.point_radius,
            fill=self.point_color,
        )
        self.objects_ids_by_polygon[-1].append(pt_id)

    def draw_line(self, ptA: Vertex, ptB: Vertex) -> None:
        line_id = self.canvas.create_line(
            (ptA.x, ptA.y), (ptB.x, ptB.y), fill=self.line_color
        )
        self.objects_ids_by_polygon[-1].append(line_id)

    def intersect_already_drawn_lines(self, new_pt: Vertex | None = None) -> bool:
        """
        If you specify a new_pt it tests if adding the new pt to the polygon will make intersecting edges,
        otherwise it tests if closing the polygon will do so.
        """
        closing = new_pt is None
        beg_new_line = self.polygons[-1][-1]

        if closing:
            new_pt = self.polygons[-1][0]

        for polygon_index, polygon in enumerate(self.polygons):
            is_last_polygon = polygon_index == len(self.polygons) - 1
            beg = 1 if is_last_polygon and closing else 0
            end_offset = 2 if is_last_polygon else 0

            for pt_index in range(beg, len(polygon) - end_offset):
                ptA = polygon[pt_index]
                ptB = polygon[(pt_index + 1) % len(polygon)]

                if segment_intersect(ptA, ptB, beg_new_line, new_pt):
                    return True

        return False

    def get_triangle_color(self, triangle: Triangle) -> str:
        triangle_key: tuple[int, int, int] = triangle.get_hashable_key()

        if triangle_key not in self.triangles_colors:
            self.triangles_colors[triangle_key] = get_random_pastel_color()

        return self.triangles_colors[triangle_key]

    def draw_triangle(self, triangle: Triangle) -> None:
        pt1, pt2, pt3 = triangle.vertices

        color = self.get_triangle_color(triangle)

        triangle_id = self.canvas.create_polygon(
            pt1.x, pt1.y, pt2.x, pt2.y, pt3.x, pt3.y, fill=color, outline=color, width=1
        )
        self.canvas.tag_lower(triangle_id)

        self.triangles_ids.append(triangle_id)

    def clear_triangulation(self) -> None:
        for triangle_id in self.triangles_ids:
            self.canvas.delete(triangle_id)

    def triangulate(self) -> None:
        self.clear_triangulation()

        polygon_area = PolygonArea(self.polygons)

        search_tree = trapezoidation(polygon_area)

        all_trapezoids = search_tree.get_all_traps()

        inside_trapezoids = select_inside_trapezoids(all_trapezoids)

        monotone_mountains = make_monotone_mountains(inside_trapezoids)

        triangles = make_triangles(monotone_mountains)

        for triangle in triangles:
            self.draw_triangle(triangle)
