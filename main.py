import tkinter as tk

from polygon_area_drawer import PolygonAreaDrawer
from utils import expand_app, set_process_dpi


def main():
    set_process_dpi()

    root = tk.Tk()
    expand_app(root)
    PolygonAreaDrawer(root)

    root.mainloop()


if __name__ == "__main__":
    main()
