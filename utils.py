from __future__ import annotations

import platform
import random
from tkinter import Tk
from typing import cast

from constants import Color


def replace(list_to_modify: list, to_replace, replace_by) -> None:
    for index in range(len(list_to_modify)):
        if list_to_modify[index] == to_replace:
            list_to_modify[index] = replace_by


def get_random_pastel_color() -> Color:
    return cast(Color, tuple([random.randint(100, 255) for _ in range(3)]))


def set_process_dpi() -> None:
    if platform.system() != "Windows":
        return

    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(2)

    except Exception:
        pass


def expand_app(root: Tk) -> None:
    if platform.system() != "Windows":
        return

    root.state("zoomed")
