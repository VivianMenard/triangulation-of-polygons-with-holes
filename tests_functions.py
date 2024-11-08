from objects import Trapezoid
from objects import Node
from objects import Polygon

from algorithms import trapezoidation



def check_trapezoidation(search_tree:Node, print_result:bool=False) -> bool:
    all_traps:list[Trapezoid] = []
    search_tree.get_all_traps(all_traps)

    for trap in all_traps:
        if not trap.check_neighbors():
            if print_result:
                print("Trapezoidation: Incorrect")

            return False

    if print_result:
        print("Trapezoidation: Correct")

    return True


def test_trapezoidation_a_lot_of_times(polygon:Polygon, nb_iterations:int) -> None:
    nb_errors = 0
    nb_incorrect_trapezoidation = 0

    for _ in range(nb_iterations):
        try:
            search_tree = trapezoidation(
                polygon=polygon, 
                display=False
            )

            if not check_trapezoidation(search_tree):
                nb_incorrect_trapezoidation += 1

        except:
            nb_errors += 1

    print(f"Nb errors: {nb_errors}")
    print(f"Nb incorrect trapezoidations: {nb_incorrect_trapezoidation}")