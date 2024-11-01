import matplotlib.pyplot as plt
from enum import Enum
from random import shuffle
from utils import replace
from typing import ClassVar

X_MIN, X_MAX = -10, 10
Y_MIN, Y_MAX = -10, 10



class Vertex:
    pass



class Vertex:
    x:float
    y:float

    def __init__(self, x:float, y:float) -> None:
        self.x = x
        self.y = y


    def __gt__(self, other:Vertex) -> bool:
        return (
            self.y > other.y or 
            (self.y == other.y and self.x > other.x)
        )



class Edge:
    start:Vertex
    end:Vertex
    bottom_vertex:Vertex
    top_vertex:Vertex

    def __init__(self, start:Vertex, end:Vertex) -> None:
        self.start = start
        self.end = end
        self.bottom_vertex, self.top_vertex = self.__get_ordered_vertices()


    def display(self, color:str="blue") -> None:
        x = [self.start.x, self.end.x]
        y = [self.start.y, self.end.y]

        plt.plot(x, y, color=color)


    def get_x_by_y(self, y:float) -> float:
        start_x = self.start.x
        end_x = self.end.x
        start_y = self.start.y
        end_y = self.end.y

        if (start_y == end_y):
            return (start_x + end_x)/2
        
        t = (y - start_y) / (end_y - start_y)
        return start_x + t * (end_x - start_x)
    

    def __get_ordered_vertices(self) -> tuple[Vertex, Vertex]:
        if self.start > self.end:
            return self.end, self.start
        
        return self.start, self.end
    

    def is_vertex_at_the_right(self, vertex:Vertex) -> bool:
        x_edge = self.get_x_by_y(vertex.y)

        return vertex.x > x_edge



class Polygon:
    vertices:list[Vertex]

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
    node_type:NodeType
    associated_obj:Trapezoid|Edge|Vertex
    left_child:Node|None
    right_child:Node|None
    parent:Node|None

    def __init__(
        self,
        trapezoid:Trapezoid,
        parent:Node|None = None
    ) -> None:
        # At the time of its creation a Node is always a leaf, ie a Trapezoid node
        self.node_type = NodeType.TRAPEZOID
        self.associated_obj = trapezoid
        trapezoid.associated_node = self
        self.left_child = None
        self.right_child = None
        self.parent = parent


    def split_by_vertex(self, vertex:Vertex) -> None:
        assert(self.node_type == NodeType.TRAPEZOID)
        bottom_trapezoid, top_trapezoid = self.associated_obj.split_by_vertex(vertex)

        self.node_type = NodeType.VERTEX
        self.associated_obj = vertex

        self.left_child = Node(
            trapezoid=bottom_trapezoid,
            parent=self
        )
        self.right_child = Node(
            trapezoid=top_trapezoid,
            parent=self
        )

    def split_by_edge(self, edge:Edge, created_trap_couples:list[tuple[Trapezoid, Trapezoid]]) -> None:
        assert(self.node_type == NodeType.TRAPEZOID)
        left_trapezoid, right_trapezoid = self.associated_obj.split_by_edge(edge)

        created_trap_couples.append((left_trapezoid, right_trapezoid))

        self.node_type = NodeType.EDGE
        self.associated_obj = edge

        self.left_child = Node(
            trapezoid=left_trapezoid,
            parent=self
        )
        self.right_child = Node(
            trapezoid=right_trapezoid,
            parent=self
        )


    def get_or_insert_vertex(self, vertex:Vertex) -> tuple[Node, bool]:
        """
        Returns a tuple (node associated with the vertex, is the vertex just inserted).
        """
        if self.node_type == NodeType.TRAPEZOID:
            self.split_by_vertex(vertex)
            return self, True

        if self.node_type == NodeType.VERTEX and self.associated_obj == vertex: 
            return self, False
            
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


    def display(self, debug:bool=False) -> None:
        if self.node_type == NodeType.TRAPEZOID:
            self.associated_obj.display(debug=debug)
            return

        self.left_child.display(debug)
        self.right_child.display(debug)


    def find_start_node(self, edge:Edge) -> Node:
        """
        Finds the node corresponding to the first trapezoid (the highest one) to cut to insert the edge.
        Needs to be called on the node representing the top vertex of the edge to insert.
        """
        assert(self.node_type == NodeType.VERTEX)
        assert(self.associated_obj == edge.top_vertex)

        return self.left_child.search_start_node(edge.bottom_vertex)


    def search_start_node(self, bottom_vertex:Vertex) -> Node:
        match self.node_type:
            case NodeType.TRAPEZOID:
                return self
            case NodeType.VERTEX:
                return self.right_child.search_start_node(bottom_vertex)
            case NodeType.EDGE: # is that correct ?
                return (
                    self.right_child if self.associated_obj.is_vertex_at_the_right(bottom_vertex) 
                    else self.left_child
                ).search_start_node(bottom_vertex)

    
    def insert_edge(self, edge:Edge, top_vertex_just_inserted:bool, bottom_vertex_just_inserted:bool) -> None:
        assert(self.node_type == NodeType.TRAPEZOID)
        assert(self.associated_obj.top_vertex == edge.top_vertex)

        nodes_to_split:list[Node] = [self]
        current_trap:Trapezoid = self.associated_obj

        while current_trap.bottom_vertex != edge.bottom_vertex:
            match len(current_trap.trapezoids_below):
                case 1:
                    current_trap = current_trap.trapezoids_below[0]

                case 2:
                    left_trap_below = current_trap.trapezoids_below[0]
                    left_trap_top_rightmost_pt = left_trap_below.get_extreme_point(top=True, right=True)
                    trap_index = 0 if edge.is_vertex_at_the_right(left_trap_top_rightmost_pt) else 1
                    current_trap = current_trap.trapezoids_below[trap_index]

                case _:
                    raise ValueError("Very strange...") # error ??? (avec 0 comme len)

            nodes_to_split.append(current_trap.associated_node)

        created_trap_couples:list[tuple[Trapezoid, Trapezoid]] = []
        for node_to_split in nodes_to_split:
            node_to_split.split_by_edge(edge, created_trap_couples)

        self.manage_adjacents_trap_after_edge_split(edge, created_trap_couples, top_vertex_just_inserted, bottom_vertex_just_inserted)

        # merge trap on top of each other with same left and right edges


    def manage_adjacents_trap_after_edge_split(
        self, 
        edge:Edge,
        created_trap_couples:list[tuple[Trapezoid, Trapezoid]], 
        top_vertex_just_inserted:bool, 
        bottom_vertex_just_inserted:bool
    ) -> None:
        first_trap_left, first_trap_right = created_trap_couples[0]
        if top_vertex_just_inserted:
            # only 1 trap above and it needs to be above for both
            # but already above for right
            assert(len(first_trap_right.trapezoids_above) == 1)
            first_trap_left.trapezoids_above = first_trap_right.trapezoids_above.copy()
            trap_above = first_trap_right.trapezoids_above[0]
            trap_above.trapezoids_below = [first_trap_left, first_trap_right]

        else:
            if getattr(first_trap_left.left_edge, "top_vertex", None) == edge.top_vertex: # left upward peak with an old edge
                assert(len(first_trap_right.trapezoids_above) == 1)
                # nothing to do

            elif getattr(first_trap_right.right_edge, "top_vertex", None) == edge.top_vertex: # right upward peak with an old edge
                assert(len(first_trap_right.trapezoids_above) == 1)
                first_trap_left.trapezoids_above = first_trap_right.trapezoids_above.copy()
                first_trap_right.trapezoids_above = []
                replace(first_trap_left.trapezoids_above[0].trapezoids_below, first_trap_right, first_trap_left)

            else: # the new edge just extend an old edge above
                assert(len(first_trap_right.trapezoids_above) == 2) # error ??? avec 1 mais pas tout le temps
                left_above, right_above = first_trap_right.trapezoids_above
                first_trap_left.trapezoids_above = [left_above]
                first_trap_right.trapezoids_above = [right_above]
                replace(left_above.trapezoids_below, first_trap_right, first_trap_left)



        last_trap_left, last_trap_right = created_trap_couples[-1]
        if bottom_vertex_just_inserted:
            # only 1 trap below and it needs to be below for both
            # but already below for right
            assert(len(last_trap_right.trapezoids_below) == 1)
            last_trap_left.trapezoids_below = last_trap_right.trapezoids_below.copy()
            trap_below = last_trap_right.trapezoids_below[0]
            trap_below.trapezoids_above = [last_trap_left, last_trap_right]

        else:
            if getattr(last_trap_left.left_edge, "bottom_vertex", None) == edge.bottom_vertex: # left downward peak with an old edge
                assert(len(last_trap_right.trapezoids_below) == 1)
                # nothing to do

            elif getattr(last_trap_right.right_edge, "bottom_vertex", None) == edge.bottom_vertex: # right downward peak with an old edge
                assert(len(last_trap_right.trapezoids_below) == 1)
                last_trap_left.trapezoids_below = last_trap_right.trapezoids_below.copy()
                last_trap_right.trapezoids_below = []
                replace(last_trap_left.trapezoids_below[0].trapezoids_above, last_trap_right, last_trap_left)

            else: # the new edge just extend an old edge below
                assert(len(last_trap_right.trapezoids_below) == 2) # error ??? avec 1 mais pas tout le temps
                left_below, right_below = last_trap_right.trapezoids_below
                last_trap_left.trapezoids_below = [left_below]
                last_trap_right.trapezoids_below = [right_below]
                replace(left_below.trapezoids_above, last_trap_right, last_trap_left)


        for i in range(len(created_trap_couples) - 1): # iterates on the borders between splited trapezoids
            top_left_trap, top_right_trap = created_trap_couples[i]
            bottom_left_trap, bottom_right_trap = created_trap_couples[i + 1]

            if len(top_right_trap.trapezoids_below) == 2: # downward branch
                assert(len(bottom_right_trap.trapezoids_above) == 1)

                branch_point = top_right_trap.trapezoids_below[0].get_extreme_point(top=True, right=True)
                if edge.is_vertex_at_the_right(branch_point):
                    top_left_trap.trapezoids_below = [bottom_left_trap]
                    bottom_left_trap.trapezoids_above = [top_left_trap]

                else:
                    additional_bottom_left_trap = top_right_trap.trapezoids_below[0]

                    top_right_trap.trapezoids_below = [bottom_right_trap]
                    bottom_right_trap.trapezoids_above = [top_right_trap]

                    top_left_trap.trapezoids_below = [additional_bottom_left_trap, bottom_left_trap]
                    bottom_left_trap.trapezoids_above = [top_left_trap]
                    additional_bottom_left_trap.trapezoids_above = [top_left_trap]

            else:
                if len(bottom_right_trap.trapezoids_above) == 2: # upward branch
                    assert(len(top_right_trap.trapezoids_below) == 1)

                    branch_point = bottom_right_trap.trapezoids_above[0].get_extreme_point(top=False, right=True)
                    if edge.is_vertex_at_the_right(branch_point):
                        top_left_trap.trapezoids_below = [bottom_left_trap]
                        bottom_left_trap.trapezoids_above = [top_left_trap]

                    else:
                        additional_top_left_trap = bottom_right_trap.trapezoids_above[0]

                        top_right_trap.trapezoids_below = [bottom_right_trap]
                        bottom_right_trap.trapezoids_above = [top_right_trap]

                        bottom_left_trap.trapezoids_above = [additional_top_left_trap, top_left_trap]
                        top_left_trap.trapezoids_below = [bottom_left_trap]
                        additional_top_left_trap.trapezoids_below = [bottom_left_trap]

                else: # no branch -> after merge addition it's not supposed to happened
                    assert(len(top_right_trap.trapezoids_below) == 1)
                    assert(len(bottom_right_trap.trapezoids_above) == 1)

                    top_left_trap.trapezoids_below = [bottom_left_trap]
                    bottom_left_trap.trapezoids_above = [top_left_trap]
        


class Trapezoid:
    next_id:ClassVar[int] = 0

    top_vertex:Vertex|None
    bottom_vertex:Vertex|None
    trapezoids_above:list[Trapezoid] # up to 2 trap above, if 2 the first is the one at the left
    trapezoids_below:list[Trapezoid] # up to 2 trap below, if 2 the first is the one at the left
    left_edge:Edge|None
    right_edge:Edge|None
    associated_node:Node|None
    inside:bool
     
    def __init__(
            self, 
            top_vertex:Vertex|None = None, 
            bottom_vertex:Vertex|None = None, 
            trapezoids_above:list[Trapezoid]|None = None, 
            trapezoids_below:list[Trapezoid]|None = None,
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

    
    def duplicate(self) -> Trapezoid:
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



    def split_by_vertex(self, vertex:Vertex) -> tuple[Trapezoid, Trapezoid]:
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
    
    def split_by_edge(self, edge:Edge) -> tuple[Trapezoid, Trapezoid]:
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



def seidel(polygon:Polygon, debug:bool=False) -> None:
    edges:list[Edge] = polygon.get_edges()
    shuffle(edges)

    search_tree = Node(
        trapezoid=Trapezoid()
    )    

    for edge in edges:
        top_vertex_node, top_vertex_just_inserted = search_tree.get_or_insert_vertex(edge.top_vertex)
        _, bottom_vertex_just_inserted = search_tree.get_or_insert_vertex(edge.bottom_vertex)

        start_node = top_vertex_node.find_start_node(edge)
        start_node.insert_edge(
            edge, top_vertex_just_inserted, bottom_vertex_just_inserted)

    search_tree.display(debug)



def main():
    debug = True

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
    seidel(polygon, debug)

    plt.axis('equal')
    plt.xlim(X_MIN, X_MAX)
    plt.ylim(Y_MIN, Y_MAX)
    plt.show()


if __name__ == "__main__":
    main()
    