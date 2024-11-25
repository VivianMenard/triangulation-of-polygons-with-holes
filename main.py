import tkinter as tk

from polygon_drawer import PolygonDrawer
from utils import set_process_dpi


def main():
    set_process_dpi()

    root = tk.Tk()
    PolygonDrawer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
