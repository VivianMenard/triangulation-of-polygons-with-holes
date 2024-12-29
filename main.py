import tkinter as tk

from polygonal_area_drawer import PolygonalAreaDrawer
from utils import expand_app, set_process_dpi


def main():
    set_process_dpi()

    root = tk.Tk()
    expand_app(root)
    PolygonalAreaDrawer(root)

    root.mainloop()


if __name__ == "__main__":
    main()
