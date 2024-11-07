import matplotlib.pyplot as plt

from objects.vertex import Vertex
from objects.polygon import Polygon
from algorithms import trapezoidation, check_trapezoidation

from constants import X_MIN, X_MAX, Y_MIN, Y_MAX



def main():
    debug = True

    contours = [
        [
            Vertex(-5.14,4.73),
            Vertex(-5.68,2.31),
            Vertex(-7.42,3.65),
            Vertex(-8.82,1.59),
            Vertex(-5.58,-1.99),
            Vertex(-1.62,-0.65),
            Vertex(-3.26,0.45),
            Vertex(-0.1,3.31)
        ],
        [
            Vertex(-6,1),
            Vertex(-3.87,2.59),
            Vertex(-4.82,-0.51),
        ]
    ]

    polygon = Polygon(contours)
    # polygon.display()

    search_tree = trapezoidation(polygon, debug)
    
    if check_trapezoidation(search_tree):
        print("Trapezoidation: Correct")
    else:
        print("Error in Trapezoidation")

    plt.axis('equal')
    plt.xlim(X_MIN, X_MAX)
    plt.ylim(Y_MIN, Y_MAX)
    plt.show()


if __name__ == "__main__":
    main()
    