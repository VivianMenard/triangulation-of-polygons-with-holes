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
            command=self.clear_canvas
        )
        self.clear_button.pack()

        self.vertex_color = "red"
        self.line_color = "black"
        self.vertex_radius = 2

        self.contours:list[list[Vertex]] = []
        self.in_progress:bool = False
        

    def add_vertex(self, event:tk.Event) -> None:
        if not self.in_progress:
            self.contours.append([])
            self.in_progress = True

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
    

    def clear_canvas(self) -> None:
        self.canvas.delete("all")
        self.contours = []
        self.in_progress = False


    def draw_vertex(self, vertex:Vertex) -> None:
        self.canvas.create_oval(
            vertex.x - self.vertex_radius, 
            vertex.y - self.vertex_radius, 
            vertex.x + self.vertex_radius, 
            vertex.y + self.vertex_radius, 
            fill=self.vertex_color
        )

    def draw_line(self, vertex_1:Vertex, vertex_2:Vertex) -> None:
        self.canvas.create_line(
            (vertex_1.x, vertex_1.y), 
            (vertex_2.x, vertex_2.y), 
            fill=self.line_color
        )


root = tk.Tk()
app = PolygonDrawer(root)
root.mainloop()
