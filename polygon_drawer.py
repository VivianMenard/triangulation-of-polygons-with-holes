import tkinter as tk
from tkinter import Canvas

from objects import Vertex, Polygon
from algorithms import trapezoidation



def counter_clockwise(ptA:Vertex, ptB:Vertex, ptC:Vertex) -> bool:
    return (ptC.y - ptA.y) * (ptB.x - ptA.x) > (ptB.y-ptA.y) * (ptC.x - ptA.x)


def segment_intersect(ptA:Vertex, ptB:Vertex, ptC:Vertex, ptD:Vertex) -> bool:
    return (
        counter_clockwise(ptA, ptB, ptC) != counter_clockwise(ptA, ptB, ptD) and
        counter_clockwise(ptC, ptD, ptA) != counter_clockwise(ptC, ptD, ptB)
    )



class PolygonDrawer:
    def __init__(self, root:tk.Tk) -> None:
        self.canvas = Canvas(
            root, 
            width=1000, 
            height=600, 
            bg="white"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<Button-3>", self.close_polygon)

        self.clear_button = tk.Button(
            root, 
            text="Clear", 
            command=self.clear,
            state="disabled"
        )
        self.clear_button.pack(
            side=tk.LEFT, 
            padx=(20, 5), 
            pady=10
        )

        self.clear_last_button = tk.Button(
            root, 
            text="Clear last contour", 
            command=self.clear_last_contour,
            state="disabled"
        )
        self.clear_last_button.pack(
            side=tk.LEFT, 
            padx=(5,5), 
            pady=10
        )

        self.make_monotone_polygons = tk.Button(
            root, 
            text="Transform into monotone polygons", 
            command=self.make_monotone_polygons,
            state="disabled"
        )
        self.make_monotone_polygons.pack(
            side=tk.LEFT, 
            padx=(5,5), 
            pady=10
        )

        self.point_color = "red"
        self.line_color = "black"
        self.point_radius = 2

        self.contours:list[list[Vertex]] = []
        self.objects_ids_by_contours:list[list[int]] = []
        self.in_progress:bool = False
        

    def add_point(self, event:tk.Event) -> None:
        new_point = Vertex(event.x, event.y)

        if self.in_progress and self.intersect_already_drawn_lines(new_point):
            return

        if not self.in_progress:
            self.contours.append([])
            self.objects_ids_by_contours.append([])
            self.in_progress = True

            self.update_buttons()

        contour = self.contours[-1]
        contour.append(new_point)
        self.draw_point(new_point)

        if len(contour) > 1:
            self.draw_line(contour[-2], contour[-1])


    def close_polygon(self, event:tk.Event) -> None:
        contour = self.contours[-1]

        if len(contour) > 2 and not self.intersect_already_drawn_lines():
            self.draw_line(contour[-1], contour[0])
            self.in_progress = False
            self.update_buttons()
    

    def clear(self) -> None:
        self.canvas.delete("all")
        self.contours = []
        self.in_progress = False

        self.update_buttons()


    def clear_last_contour(self) -> None:
        if not self.contours:
            return

        del self.contours[-1]
        self.in_progress = False

        for line_id in self.objects_ids_by_contours[-1]:
            self.canvas.delete(line_id)

        del self.objects_ids_by_contours[-1]

        self.update_buttons()

    
    def update_buttons(self) -> None:
        clear_buttons_enabled = bool(self.contours)
        make_monotone_polygons_button_enabled = bool(self.contours) and not self.in_progress

        self.update_button_state(
            self.clear_button, 
            clear_buttons_enabled
        )
        self.update_button_state(
            self.clear_last_button, 
            clear_buttons_enabled
        )
        self.update_button_state(
            self.make_monotone_polygons,
            make_monotone_polygons_button_enabled
        )


    def update_button_state(self, button:tk.Button, enabled:bool) -> None:
        state = "normal" if enabled else "disabled"
        button.config(state=state)


    def draw_point(self, point:Vertex) -> None:
        pt_id = self.canvas.create_oval(
            point.x - self.point_radius, 
            point.y - self.point_radius, 
            point.x + self.point_radius, 
            point.y + self.point_radius, 
            fill=self.point_color
        )
        self.objects_ids_by_contours[-1].append(pt_id)


    def draw_line(self, ptA:Vertex, ptB:Vertex) -> None:
        line_id = self.canvas.create_line(
            (ptA.x, ptA.y), 
            (ptB.x, ptB.y), 
            fill=self.line_color
        )
        self.objects_ids_by_contours[-1].append(line_id)


    def intersect_already_drawn_lines(self, new_pt:Vertex|None=None) -> bool:
        """
        If you specify a new_pt it tests if adding the new pt to the polygon will make intersecting edges,
        otherwise it tests if closing the polygon will do so.
        """
        closing = new_pt is None
        beg_new_line = self.contours[-1][-1]

        if closing:
            new_pt = self.contours[-1][0]

        for contour_index, contour in enumerate(self.contours):
            is_last_contour = contour_index == len(self.contours) - 1
            beg = 1 if is_last_contour and closing else 0
            end_offset = 2 if is_last_contour else 0

            for pt_index in range(beg, len(contour) - end_offset):
                ptA = contour[pt_index]
                ptB = contour[(pt_index + 1) % len(contour)]

                if segment_intersect(ptA, ptB, beg_new_line, new_pt):
                    return True

        return False


    def make_monotone_polygons(self) -> None:
        polygon = Polygon(self.contours)

        search_tree = trapezoidation(polygon)

        for trap in search_tree.get_all_traps():
            if trap.is_inside:
                if (
                    (trap.bottom_vertex == trap.left_edge.bottom_vertex and trap.top_vertex == trap.left_edge.top_vertex) or 
                    (trap.bottom_vertex == trap.right_edge.bottom_vertex and trap.top_vertex == trap.right_edge.top_vertex)
                ): # the edge between bottom vertex and top vertex of a trap is its left/right edge -> already drawn
                    continue

                self.draw_line(trap.bottom_vertex, trap.top_vertex)



root = tk.Tk()
app = PolygonDrawer(root)
root.mainloop()
