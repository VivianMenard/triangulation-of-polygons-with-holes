import tkinter as tk

from polygonal_area_drawer import PolygonalAreaDrawer
from utils import expand_app, set_process_dpi


def main():
    """
    The main entry point of the application.

    This function sets up the graphical environment, initializes the main drawing Tkinter interface for the
    polygonal area, and starts the main event loop.
    """
    set_process_dpi()

    root = tk.Tk()
    expand_app(root)
    PolygonalAreaDrawer(root)

    root.mainloop()


if __name__ == "__main__":
    main()
