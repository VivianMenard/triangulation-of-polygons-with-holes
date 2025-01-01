from __future__ import annotations

import platform
import random
from tkinter import Tk
from typing import cast

from constants import Color


def replace(list_to_modify: list, to_replace, replace_by) -> None:
    """
    Replaces all occurrences of a specified value in a list with a new value.

    Args:
        list_to_modify (list): The list in which values will be replaced.
        to_replace: The value to be replaced.
        replace_by: The value to replace the target with.
    """
    for index in range(len(list_to_modify)):
        if list_to_modify[index] == to_replace:
            list_to_modify[index] = replace_by


def get_random_pastel_color() -> Color:
    """
    Generates a random pastel color.

    Returns:
        Color: A tuple representing a pastel color in RGB format (r, g, b),
        where each component is an integer between 100 and 255.
    """
    return cast(Color, tuple([random.randint(100, 255) for _ in range(3)]))


def set_process_dpi() -> None:
    """
    Configures the process DPI awareness on Windows for improved display scaling.

    Notes:
        - This function has no effect on non-Windows platforms.
        - On Windows, it attempts to set the DPI awareness using the `SetProcessDpiAwareness`
          function from `ctypes.windll.shcore`.
    """
    if platform.system() != "Windows":
        return

    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(2)

    except Exception:
        pass


def expand_app(root: Tk) -> None:
    """
    Maximizes the application window on Windows platforms.

    Args:
        root (Tk): The root Tkinter window to be maximized.

    Notes:
        - This function has no effect on non-Windows platforms.
        - On Windows, it sets the application window state to "zoomed".
    """
    if platform.system() != "Windows":
        return

    root.state("zoomed")
