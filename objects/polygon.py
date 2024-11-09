import matplotlib.pyplot as plt

from objects import Vertex, Edge



class Polygon:
    vertices:list[Vertex]


    def __init__(self, contours:list[list[Vertex]]) -> None:
        self.contours = contours


    def get_edges(self) -> list[Edge]:
        return [
            Edge(contour[i], contour[(i+1)%len(contour)]) 
            for contour in self.contours for i in range(len(contour)) 
        ]
    

    def display(self) -> None:
        for edge in self.get_edges():
            edge.display()
            