from __future__ import annotations

import matplotlib.pyplot as plt
from typing import ClassVar

from objects import Vertex, Edge

from utils import replace
from constants import X_MIN, X_MAX, Y_MIN, Y_MAX



class Trapezoid:
    next_id:ClassVar[int] = 0

    top_vertex:Vertex|None
    bottom_vertex:Vertex|None
    trapezoids_above:list["Trapezoid"] # up to 2 trap above, if 2 the first is the one at the left
    trapezoids_below:list["Trapezoid"] # up to 2 trap below, if 2 the first is the one at the left
    left_edge:Edge|None
    right_edge:Edge|None
    associated_node:"Node"|None
    inside:bool
     
     
    def __init__(
            self, 
            top_vertex:Vertex|None = None, 
            bottom_vertex:Vertex|None = None, 
            trapezoids_above:list["Trapezoid"]|None = None, 
            trapezoids_below:list["Trapezoid"]|None = None,
            left_edge:Edge|None = None, 
            right_edge:Edge|None = None
        ) -> None:
        self.id = Trapezoid.next_id
        Trapezoid.next_id+=1

        self.top_vertex = top_vertex
        self.bottom_vertex = bottom_vertex
        self.trapezoids_above = [] if trapezoids_above is None else trapezoids_above
        self.trapezoids_below = [] if trapezoids_below is None else trapezoids_below
        self.left_edge = left_edge
        self.right_edge = right_edge
        self.associated_node = None
        self.inside = False

    
    @classmethod
    def merge(cls, top_trap:"Trapezoid", bottom_trap:"Trapezoid") -> None:
        assert(
            top_trap in bottom_trap.trapezoids_above
            and bottom_trap in top_trap.trapezoids_below
        )
        assert(top_trap.left_edge == bottom_trap.left_edge)
        assert(top_trap.right_edge == bottom_trap.right_edge)

        top_trap.bottom_vertex = bottom_trap.bottom_vertex
        top_trap.trapezoids_below = bottom_trap.trapezoids_below.copy() # I don't know if copy in necessary here

        for trap in bottom_trap.trapezoids_below:
            replace(trap.trapezoids_above, bottom_trap, top_trap)

        bottom_trap.associated_node.replace_by_another_node_in_tree(top_trap.associated_node)

    
    def duplicate(self) -> "Trapezoid":
        return Trapezoid(
            top_vertex=self.top_vertex,
            bottom_vertex = self.bottom_vertex,
            left_edge=self.left_edge,
            right_edge=self.right_edge
        )


    def display(self, color:str="green", debug:bool=False) -> None:
        y_max = Y_MAX if self.top_vertex is None else self.top_vertex.y
        y_min = Y_MIN if self.bottom_vertex is None else self.bottom_vertex.y
        x_min_top, x_min_bottom = X_MIN, X_MIN
        x_max_top, x_max_bottom = X_MAX, X_MAX

        if self.left_edge is not None:
            x_min_top = self.left_edge.get_x_by_y(y_max)
            x_min_bottom = self.left_edge.get_x_by_y(y_min)
            plt.plot([x_min_bottom, x_min_top], [y_min, y_max], color=color)

        if self.right_edge is not None:
            x_max_top = self.right_edge.get_x_by_y(y_max)
            x_max_bottom = self.right_edge.get_x_by_y(y_min)
            plt.plot([x_max_bottom, x_max_top], [y_min, y_max], color=color)

        if self.top_vertex is not None:
            plt.plot([x_min_top, x_max_top], [y_max, y_max], color=color)

        if self.bottom_vertex is not None:
            plt.plot([x_min_bottom, x_max_bottom], [y_min, y_min], color=color)

        if debug:
            y_average = (y_min + y_max) / 2
            x_average = (x_min_bottom + x_min_top + x_max_bottom + x_max_top) / 4
            
            above_str = ', '.join([str(trap.id) for trap in self.trapezoids_above])
            below_str = ', '.join([str(trap.id) for trap in self.trapezoids_below])
            infos = f"{self.id}\nab: [{above_str}], be: [{below_str}]"

            plt.text(x_average, y_average, infos, ha='center', va='center', fontsize=8, color="black")


    def split_by_vertex(self, vertex:Vertex) -> tuple["Trapezoid", "Trapezoid"]:
        top_trapezoid = self
        bottom_trapezoid = self.duplicate()

        top_trapezoid.bottom_vertex = vertex
        bottom_trapezoid.top_vertex = vertex

        # top_trapezoid = self -> no need to change trapezoids_above
        bottom_trapezoid.trapezoids_above = [top_trapezoid]
        bottom_trapezoid.trapezoids_below = self.trapezoids_below.copy()
        for trap in self.trapezoids_below:
            replace(trap.trapezoids_above, self, bottom_trapezoid)
        top_trapezoid.trapezoids_below = [bottom_trapezoid]

        return (bottom_trapezoid, top_trapezoid)
    

    def split_by_edge(self, edge:Edge) -> tuple["Trapezoid", "Trapezoid"]:
        right_trapezoid = self
        left_trapezoid = self.duplicate()

        left_trapezoid.right_edge = edge
        right_trapezoid.left_edge = edge

        return (left_trapezoid, right_trapezoid)


    def get_extreme_point(self, top:bool, right:bool) -> Vertex:
        relevant_vertex = self.top_vertex if top else self.bottom_vertex
        relevant_edge = self.right_edge if right else self.left_edge

        extreme_y = relevant_vertex.y if relevant_vertex else (Y_MAX if top else Y_MIN)
        extreme_x = relevant_edge.get_x_by_y(extreme_y) if relevant_edge else (X_MAX if right else X_MIN)

        return Vertex(extreme_x, extreme_y)


    def check_neighbors(self) -> bool:
        for trap in self.trapezoids_below:
            if self not in trap.trapezoids_above:
                return False

        for trap in self.trapezoids_above:
            if self not in trap.trapezoids_below:
                return False

        return True
