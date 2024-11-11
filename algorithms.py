from random import shuffle

from objects import Polygon, Trapezoid, Node



def trapezoidation(polygon:Polygon) -> Node:
    edges:list[Edge] = polygon.get_edges()
    shuffle(edges)

    search_tree = Node(
        trapezoid=Trapezoid()
    )
    already_inserted:set[Vertex] = set()

    for edge in edges:
        bottom_vertex, top_vertex = edge.get_ordered_vertices()
        
        if top_should_be_inserted := top_vertex not in already_inserted:
            search_tree.insert_vertex(top_vertex)
            already_inserted.add(top_vertex)

        if bottom_should_be_inserted := bottom_vertex not in already_inserted:
            search_tree.insert_vertex(bottom_vertex)
            already_inserted.add(bottom_vertex)

        start_node = search_tree.search_area_containing_vertex(edge.get_mid_point())

        start_node.insert_edge(
            edge, 
            top_should_be_inserted,
            bottom_should_be_inserted
        )

    return search_tree
