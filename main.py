"""Personal Accounting — Entry Point.

A lightweight desktop personal accounting tool built with
CustomTkinter, SQLite, and Matplotlib.
"""

from ui.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
