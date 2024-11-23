import tkinter as tk

from polygon_drawer import PolygonDrawer


def main():
    root = tk.Tk()
    PolygonDrawer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
