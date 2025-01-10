import math
from tkinter import BOTH, LEFT, Button, Canvas, Event, Tk

from algorithms import triangulate_polygonal_area
from objects import Polygon, PolygonalArea, Triangle, Vertex


class PolygonalAreaDrawer:
    """
    A graphical interface for drawing polygonal areas and viewing the resulting triangulation.

    This class provides an interactive canvas where users can draw polygons by clicking
    to add vertices, close polygons, and visualize their triangulation. It also includes
    buttons for clearing all polygons or the last drawn polygon.
    """

    __canvas: Canvas
    """The drawing canvas."""
    __clear_button: Button
    """Button to clear all polygons."""
    __clear_last_button: Button
    """Button to clear the last drawn polygon."""
    __point_color: str
    """The color used to draw vertices."""
    __line_color: str
    """The color used to draw polygon edges."""
    __point_radius: int
    """The radius of points (vertices) on the canvas."""
    __polygons: list[Polygon]
    """The list of polygons drawn on the canvas."""
    __objects_ids_by_polygon: list[list[int]]
    """Canvas object IDs for each polygon."""
    __triangles_ids: list[int]
    """Canvas object IDs for drawn triangles."""
    __in_progress: bool
    """Whether a polygon is currently being drawn."""

    def __init__(self, root: Tk) -> None:
        """
        Initializes the PolygonalAreaDrawer.

        Args:
            root (Tk): The root Tkinter window.
        """
        self.__canvas = Canvas(root, bg="white")
        self.__canvas.pack(fill=BOTH, expand=True)

        self.__canvas.bind("<Button-1>", self.__add_point)
        self.__canvas.bind("<Button-3>", self.__close_polygon)

        self.__clear_button = Button(
            root, text="Clear", command=self.__clear, state="disabled"
        )
        self.__clear_button.pack(side=LEFT, padx=(20, 5), pady=10)

        self.__clear_last_button = Button(
            root,
            text="Clear last polygon",
            command=self.__clear_last_polygon,
            state="disabled",
        )
        self.__clear_last_button.pack(side=LEFT, padx=(5, 5), pady=10)

        self.__point_color = "brown"
        self.__line_color = "grey"
        self.__point_radius = 2

        self.__polygons = []
        self.__objects_ids_by_polygon = []
        self.__triangles_ids = []
        self.__in_progress = False

    def __add_point(self, event: Event) -> None:
        """
        Adds a vertex to the current polygon.

        This method handles left mouse clicks on the canvas to add a vertex
        to the current polygon (provided that it does not form intersecting edges).
        If no polygon is currently being drawn, a new one is started.

        Args:
            event (Event): The mouse click event containing the click position.
        """
        new_point = Vertex(event.x, event.y)

        if self.__is_same_as_another_point(
            new_point
        ) or self.__draws_intersecting_lines(new_point):
            return

        if not self.__in_progress:
            self.__polygons.append([])
            self.__objects_ids_by_polygon.append([])
            self.__in_progress = True

            self.__update_buttons()

        polygon = self.__polygons[-1]
        polygon.append(new_point)
        self.__draw_point(new_point)

        if len(polygon) > 1:
            self.__draw_line(polygon[-2], polygon[-1])

    def __close_polygon(self, _: Event) -> None:
        """
        Closes the current polygon.

        This method handles right mouse clicks on the canvas to close the current polygon,
        provided it forms a valid shape (at least 3 vertices and no intersecting edges).

        Args:
            _: Ignored event argument.
        """
        polygon = self.__polygons[-1]

        if len(polygon) < 3 or self.__draws_intersecting_lines():
            return

        self.__draw_line(polygon[-1], polygon[0])
        self.__in_progress = False
        self.__triangulate()

    def __clear(self) -> None:
        """
        Clears all polygons and their associated drawings from the canvas.
        """
        self.__canvas.delete("all")
        self.__polygons = []
        self.triangles_colors = {}
        self.__in_progress = False

        self.__update_buttons()

    def __clear_last_polygon(self) -> None:
        """
        Clears the last drawn polygons and its associated drawing from the canvas.
        """
        if not self.__polygons:
            return

        del self.__polygons[-1]
        self.__in_progress = False

        for line_id in self.__objects_ids_by_polygon[-1]:
            self.__canvas.delete(line_id)

        del self.__objects_ids_by_polygon[-1]

        self.__update_buttons()
        self.__triangulate()

    def __update_buttons(self) -> None:
        """
        Updates the state of the buttons based on the current state of the polygons.

        Enables or disables the 'Clear' and 'Clear last polygon' buttons depending on whether
        any polygons have been drawn.
        """
        clear_buttons_enabled = bool(self.__polygons)

        self.__update_button_state(self.__clear_button, clear_buttons_enabled)
        self.__update_button_state(self.__clear_last_button, clear_buttons_enabled)

    def __update_button_state(self, button: Button, enabled: bool) -> None:
        """
        Updates the enabled state of a given button.

        This method sets the button to 'normal' if enabled is True, or 'disabled' if enabled is False.

        Args:
            button (Button): The button to update.
            enabled (bool): Whether to enable or disable the button.
        """
        state = "normal" if enabled else "disabled"
        button.config(state=state)

    def __draw_point(self, point: Vertex) -> None:
        """
        Draws a vertex on the canvas.

        This method creates a small circle representing a vertex at the given point location.

        Args:
            point (Vertex): The vertex to be drawn.
        """
        pt_id = self.__canvas.create_oval(
            point.x - self.__point_radius,
            point.y - self.__point_radius,
            point.x + self.__point_radius,
            point.y + self.__point_radius,
            fill=self.__point_color,
        )
        self.__objects_ids_by_polygon[-1].append(pt_id)

    def __draw_line(self, pt_a: Vertex, pt_b: Vertex) -> None:
        """
        Draws a line between two vertices.

        This method creates a line connecting two given vertices on the canvas.

        Args:
            pt_a (Vertex): The starting point of the line.
            pt_b (Vertex): The ending point of the line.
        """
        line_id = self.__canvas.create_line(
            (pt_a.x, pt_a.y), (pt_b.x, pt_b.y), fill=self.__line_color
        )
        self.__objects_ids_by_polygon[-1].append(line_id)

    def __draws_intersecting_lines(self, new_pt: Vertex | None = None) -> bool:
        """
        Checks if adding a new point to the polygon will result in intersecting edges,
        or if closing the polygon will cause intersections.

        This method checks whether the addition of a new vertex or the closing of the current
        polygon will result in lines that intersect with any other lines from the current
        or previously drawn polygons. If an intersection is detected, it returns True, indicating
        that the polygon cannot be formed without self-intersections. Otherwise, it returns False.

        Args:
            new_pt (Vertex | None, optional): The new vertex to be added to the polygon.
                If None, it checks if closing the polygon creates intersections.

        Returns:
            bool: True if the new point or closing the polygon results in intersecting lines, otherwise False.
        """
        if not self.__in_progress:
            return False

        closing = new_pt is None
        beg_new_line = self.__polygons[-1][-1]

        if closing:
            new_pt = self.__polygons[-1][0]

        for polygon_index, polygon in enumerate(self.__polygons):
            is_last_polygon = polygon_index == len(self.__polygons) - 1
            beg = 1 if is_last_polygon and closing else 0
            end_offset = 2 if is_last_polygon else 0

            for pt_index in range(beg, len(polygon) - end_offset):
                pt_a = polygon[pt_index]
                pt_b = polygon[(pt_index + 1) % len(polygon)]

                if Vertex.segment_intersect(pt_a, pt_b, beg_new_line, new_pt):
                    return True

        return False

    def __is_same_as_another_point(self, new_point: Vertex) -> bool:
        """
        Checks if a given point is the same as any existing point.

        This method compares the new point with all the vertices in the current polygons to
        check if the new point already exists.

        Args:
            new_point (Vertex): The point to check for duplicates.

        Returns:
            bool: True if the point is the same as an existing one, otherwise False.
        """
        for polygon in self.__polygons:
            for point in polygon:
                if math.isclose(new_point.x, point.x) and math.isclose(
                    new_point.y, point.y
                ):
                    return True

        return False

    def __draw_triangle(self, triangle: Triangle) -> None:
        """
        Draws a triangle on the canvas.

        This method creates a filled polygon representing a triangle with the specified vertices.

        Args:
            triangle (Triangle): The triangle to be drawn.
        """
        pt1, pt2, pt3 = triangle.vertices

        color = triangle.color_str

        triangle_id = self.__canvas.create_polygon(
            pt1.x, pt1.y, pt2.x, pt2.y, pt3.x, pt3.y, fill=color, outline=color, width=1
        )
        self.__canvas.tag_lower(triangle_id)

        self.__triangles_ids.append(triangle_id)

    def __clear_triangulation(self) -> None:
        """
        Clears all drawn triangles from the canvas.

        This method deletes all the triangles that have been previously drawn to represent the triangulation.
        """
        for triangle_id in self.__triangles_ids:
            self.__canvas.delete(triangle_id)

    def __triangulate(self) -> None:
        """
        Performs triangulation on the drawn polygons.

        This method clears any existing triangulation, constructs a polygonal area
        from the drawn polygons, computes the triangulation and draws the resulting triangles.
        """
        self.__clear_triangulation()

        polygonal_area = PolygonalArea(self.__polygons)
        triangles = triangulate_polygonal_area(polygonal_area)

        for triangle in triangles:
            self.__draw_triangle(triangle)
