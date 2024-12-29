import math
from tkinter import BOTH, LEFT, Button, Canvas, Event, Tk

from algorithms import triangulate_polygonal_area
from objects import Polygon, PolygonalArea, Triangle, Vertex


class PolygonalAreaDrawer:
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

    def add_point(self, event: Event) -> None:
        new_point = Vertex(event.x, event.y)

        if self.is_same_as_another_point(new_point) or self.draws_intersecting_lines(
            new_point
        ):
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

        if len(polygon) < 3 or self.draws_intersecting_lines():
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

    def draw_line(self, pt_a: Vertex, pt_b: Vertex) -> None:
        line_id = self.canvas.create_line(
            (pt_a.x, pt_a.y), (pt_b.x, pt_b.y), fill=self.line_color
        )
        self.objects_ids_by_polygon[-1].append(line_id)

    def draws_intersecting_lines(self, new_pt: Vertex | None = None) -> bool:
        """
        If you specify a new_pt it tests if adding the new pt to the polygon will make intersecting edges,
        otherwise it tests if closing the polygon will do so.
        """
        if not self.in_progress:
            return False

        closing = new_pt is None
        beg_new_line = self.polygons[-1][-1]

        if closing:
            new_pt = self.polygons[-1][0]

        for polygon_index, polygon in enumerate(self.polygons):
            is_last_polygon = polygon_index == len(self.polygons) - 1
            beg = 1 if is_last_polygon and closing else 0
            end_offset = 2 if is_last_polygon else 0

            for pt_index in range(beg, len(polygon) - end_offset):
                pt_a = polygon[pt_index]
                pt_b = polygon[(pt_index + 1) % len(polygon)]

                if Vertex.segment_intersect(pt_a, pt_b, beg_new_line, new_pt):
                    return True

        return False

    def is_same_as_another_point(self, new_point: Vertex) -> bool:
        for polygon in self.polygons:
            for point in polygon:
                if math.isclose(new_point.x, point.x) and math.isclose(
                    new_point.y, point.y
                ):
                    return True

        return False

    def draw_triangle(self, triangle: Triangle) -> None:
        pt1, pt2, pt3 = triangle.vertices

        color = triangle.color_str

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

        polygonal_area = PolygonalArea(self.polygons)
        triangles = triangulate_polygonal_area(polygonal_area)

        for triangle in triangles:
            self.draw_triangle(triangle)
