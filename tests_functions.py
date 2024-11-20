from __future__ import annotations

from typing import TYPE_CHECKING

from algorithms import trapezoidation

if TYPE_CHECKING:
    from objects import Node, Polygon


def check_trapezoidation(search_tree: Node, print_result: bool = False) -> bool:
    all_traps = search_tree.get_all_traps()

    for trap in all_traps:
        if not trap.check_neighbors():
            if print_result:
                print("Trapezoidation: Incorrect")

            return False

    if print_result:
        print("Trapezoidation: Correct")

    return True


def check_tree_consistency(search_tree: Node, print_result: bool = False) -> bool:
    is_consistent = search_tree.check_consistency()

    if print_result:
        print(f"Tree consistency: {"Correct" if is_consistent else "Incorrect"}")

    return is_consistent


def test_trapezoidation_a_lot_of_times(polygon: Polygon, nb_iterations: int) -> None:
    nb_errors = 0
    nb_incorrect_trapezoidations = 0
    nb_incorrect_trees = 0

    for _ in range(nb_iterations):
        try:
            search_tree = trapezoidation(polygon=polygon, display=False)

            if not check_trapezoidation(search_tree):
                nb_incorrect_trapezoidations += 1

            if not check_tree_consistency(search_tree):
                nb_incorrect_trees += 1

        except:
            nb_errors += 1

    print(f"Nb errors: {nb_errors}")
    print(f"Nb incorrect trapezoidations: {nb_incorrect_trapezoidations}")
    print(f"Nb incorrect trees: {nb_incorrect_trees}")
