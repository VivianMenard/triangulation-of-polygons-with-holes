import tkinter as tk
from tkinter import Canvas

from objects import Vertex


class PolygonDrawer:
    def __init__(self, root:tk.Tk) -> None:
        self.canvas = Canvas(
            root, 
            width=1000, 
            height=600, 
            bg="white"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.add_vertex)
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

        self.vertex_color = "red"
        self.line_color = "black"
        self.vertex_radius = 2

        self.contours:list[list[Vertex]] = []
        self.objects_ids_by_contours:list[list[int]] = []
        self.in_progress:bool = False
        

    def add_vertex(self, event:tk.Event) -> None:
        if not self.in_progress:
            self.contours.append([])
            self.objects_ids_by_contours.append([])
            self.in_progress = True

            self.update_buttons()

        vertex = Vertex(event.x, event.y)

        contour = self.contours[-1]
        contour.append(vertex)
        self.draw_vertex(vertex)

        if len(contour) > 1:
            self.draw_line(contour[-2], contour[-1])


    def close_polygon(self, event:tk.Event) -> None:
        contour = self.contours[-1]

        if len(contour) > 2:
            self.draw_line(contour[-1], contour[0])
            self.in_progress = False
    

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

        self.update_button_state(
            self.clear_button, 
            clear_buttons_enabled
        )
        self.update_button_state(
            self.clear_last_button, 
            clear_buttons_enabled
        )


    def update_button_state(self, button:tk.Button, enabled:bool) -> None:
        state = "normal" if enabled else "disabled"
        button.config(state=state)


    def draw_vertex(self, vertex:Vertex) -> None:
        vertex_id = self.canvas.create_oval(
            vertex.x - self.vertex_radius, 
            vertex.y - self.vertex_radius, 
            vertex.x + self.vertex_radius, 
            vertex.y + self.vertex_radius, 
            fill=self.vertex_color
        )
        self.objects_ids_by_contours[-1].append(vertex_id)

    def draw_line(self, vertex_1:Vertex, vertex_2:Vertex) -> None:
        line_id = self.canvas.create_line(
            (vertex_1.x, vertex_1.y), 
            (vertex_2.x, vertex_2.y), 
            fill=self.line_color
        )
        self.objects_ids_by_contours[-1].append(line_id)


root = tk.Tk()
app = PolygonDrawer(root)
root.mainloop()
