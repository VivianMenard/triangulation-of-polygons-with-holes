from __future__ import annotations

import platform
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from objects import Vertex


def replace(list_to_modify: list, to_replace, replace_by) -> None:
    for index in range(len(list_to_modify)):
        if list_to_modify[index] == to_replace:
            list_to_modify[index] = replace_by


def counter_clockwise(ptA: Vertex, ptB: Vertex, ptC: Vertex) -> bool:
    return (ptC.y - ptA.y) * (ptB.x - ptA.x) > (ptB.y - ptA.y) * (ptC.x - ptA.x)


def segment_intersect(ptA: Vertex, ptB: Vertex, ptC: Vertex, ptD: Vertex) -> bool:
    return counter_clockwise(ptA, ptB, ptC) != counter_clockwise(
        ptA, ptB, ptD
    ) and counter_clockwise(ptC, ptD, ptA) != counter_clockwise(ptC, ptD, ptB)


def get_random_pastel_color() -> str:
    return f"#{random.randint(100, 255):02x}{random.randint(100, 255):02x}{random.randint(100, 255):02x}"


def set_process_dpi() -> None:
    if platform.system() != "Windows":
        return

    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(2)

    except Exception:
        pass
