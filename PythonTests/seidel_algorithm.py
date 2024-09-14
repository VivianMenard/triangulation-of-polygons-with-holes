import matplotlib.pyplot as plt
from enum import Enum
from random import shuffle

X_MIN, X_MAX = -10, 10
Y_MIN, Y_MAX = -10, 10



class Vertex:
    pass



class Vertex:
    def __init__(self, x:float, y:float) -> None:
        self.x = x
        self.y = y


    def __gt__(self, other:Vertex) -> bool:
        return (
            self.y > other.y or 
            (self.y == other.y and self.x > other.x)
        )



class Edge:
    def __init__(self, start:Vertex, end:Vertex) -> None:
        self.start = start
        self.end = end


    def display(self) -> None:
        x = [self.start.x, self.end.x]
        y = [self.start.y, self.end.y]

        plt.plot(x, y, color='blue')


    def get_x_by_y(self, y:float) -> float:
        start_x = self.start.x
        end_x = self.end.x
        start_y = self.start.y
        end_y = self.end.y

        if (
            y > max(start_y, end_y) or
            y < min(start_y, end_y)            
        ):
            raise ValueError("incorrect y")
        
        if (start_y == end_y):
            return (start_x + end_x)/2
        
        t = (y - start_y) / (end_y - start_y)
        return start_x + t * (end_x - start_x)
    

    def get_ordered_vertices(self) -> tuple[Vertex, Vertex]:
        if self.start > self.end:
            return self.end, self.start
        
        return self.start, self.end
    

    def is_vertex_at_the_right(self, vertex:Vertex) -> bool:
        x_edge = self.get_x_by_y(vertex.y)

        return vertex.x > x_edge



class Polygon:
    def __init__(self, vertices:list[Vertex]) -> None:
        self.vertices = vertices


    def get_edges(self) -> list[Edge]:
        return [
            Edge(self.vertices[i], self.vertices[(i+1)%len(self.vertices)]) 
            for i in range(len(self.vertices))
        ]
    

    def display(self) -> None:
        for edge in self.get_edges():
            edge.display()



class Trapezoid:
    pass



class NodeType(Enum):
    VERTEX = 0
    EDGE = 1
    TRAPEZOID = 2



class Node:
    pass



class Node:
    def __init__(
        self,
        node_type:NodeType,
        associated_obj:Vertex|Edge|Trapezoid,
        left_child:Node|None = None,
        right_child:Node|None = None,
        parent:Node|None = None
    ) -> None:
        self.node_type = node_type 
        self.associated_obj = associated_obj
        self.left_child = left_child
        self.right_child = right_child
        self.parent = parent


    def split_by_vertex(self, vertex:Vertex) -> None:
        assert(self.node_type == NodeType.TRAPEZOID)
        bottom_trapezoid, top_trapezoid = self.associated_obj.split_by_vertex(vertex)

        self.node_type = NodeType.VERTEX
        self.associated_obj = vertex

        self.left_child = Node(
            node_type=NodeType.TRAPEZOID,
            associated_obj=bottom_trapezoid,
            parent=self
        )
        self.right_child = Node(
            node_type=NodeType.TRAPEZOID,
            associated_obj=top_trapezoid,
            parent=self
        )


    def get_or_insert_vertex(self, vertex:Vertex) -> Node:
        if self.node_type == NodeType.TRAPEZOID:
            self.split_by_vertex(vertex)

        if self.node_type == NodeType.VERTEX and self.associated_obj == vertex: 
            return self
            
        if (
            (
                self.node_type == NodeType.VERTEX 
                and vertex > self.associated_obj
            ) or (
                self.node_type == NodeType.EDGE 
                and self.associated_obj.is_vertex_at_the_right(vertex)
            )
        ):
            return self.right_child.get_or_insert_vertex(vertex)
            
        return self.left_child.get_or_insert_vertex(vertex)     


    def display(self) -> None:
        if self.node_type == NodeType.TRAPEZOID:
            self.associated_obj.display()
            return

        self.left_child.display()
        self.right_child.display()
        


class Trapezoid:
    def __init__(
            self, 
            top_vertex:Vertex|None = None, 
            bottom_vertex:Vertex|None = None, 
            trapezoids_above:list[Trapezoid]|None = None, 
            trapezoids_below:list[Trapezoid]|None = None,
            left_edge:Edge|None = None, 
            right_edge:Edge|None = None,
            # tree_position:Node|None = None
        ) -> None:
        self.high = top_vertex
        self.low = bottom_vertex
        self.trapezoids_above = [] if trapezoids_above is None else trapezoids_above
        self.trapezoids_below = [] if trapezoids_below is None else trapezoids_below
        self.left_edge = left_edge
        self.right_edge = right_edge
        # self.tree_position = tree_position
        self.inside = False

    
    def duplicate(self) -> Trapezoid:
        return Trapezoid(
            top_vertex=self.high,
            bottom_vertex = self.low,
            left_edge=self.left_edge,
            right_edge=self.right_edge
        )


    def display(self) -> None:
        y_max = Y_MAX if self.high is None else self.high.y
        y_min = Y_MIN if self.low is None else self.low.y
        x_min_high, x_min_low = X_MIN, X_MIN
        x_max_high, x_max_low = X_MAX, X_MAX

        if self.left_edge is not None:
            x_min_high = self.left_edge.get_x_by_y(y_max)
            x_min_low = self.left_edge.get_x_by_y(y_min)
            plt.plot([x_min_low, x_min_high], [y_min, y_max], color='green')

        if self.right_edge is not None:
            x_max_high = self.right_edge.get_x_by_y(y_max)
            x_max_low = self.right_edge.get_x_by_y(y_min)
            plt.plot([x_max_low, x_max_high], [y_min, y_max], color='green')

        if self.high is not None:
            plt.plot([x_min_high, x_max_high], [y_max, y_max], color='green')

        if self.low is not None:
            plt.plot([x_min_low, x_max_low], [y_min, y_min], color='green')


    def split_by_vertex(self, vertex:Vertex) -> tuple[Trapezoid, Trapezoid]:
        top_trapezoid = self
        bottom_trapezoid = self.duplicate()

        top_trapezoid.low = vertex
        bottom_trapezoid.high = vertex

        top_trapezoid.trapezoids_below = [bottom_trapezoid]
        bottom_trapezoid.trapezoids_above = [top_trapezoid]

        return (bottom_trapezoid, top_trapezoid)



def seidel(polygon:Polygon) -> None:
    edges:list[Edge] = polygon.get_edges()
    shuffle(edges)

    search_tree = Node(
        node_type=NodeType.TRAPEZOID,
        associated_obj=Trapezoid()
    )    

    for edge in edges:
        low_vertex, high_vertex = edge.get_ordered_vertices()
        high_node = search_tree.get_or_insert_vertex(high_vertex)
        low_node = search_tree.get_or_insert_vertex(low_vertex)

    search_tree.display()



def main():
    contour = [
        Vertex(-5.14,4.73),
        Vertex(-5.68,2.31),
        Vertex(-7.42,3.65),
        Vertex(-8.82,1.59),
        Vertex(-5.58,-1.99),
        Vertex(-1.62,-0.65),
        Vertex(-3.26,0.45),
        Vertex(-0.1,3.31)
    ]

    polygon = Polygon(contour)
    polygon.display()
    seidel(polygon)

    plt.axis('equal')
    plt.show()


if __name__ == "__main__":
    main()
    