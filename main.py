import customtkinter as ctk


def main() -> None:
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.title("Personal Accounting Tool")
    root.geometry("1024x768")
    root.minsize(800, 600)

    root.mainloop()


if __name__ == "__main__":
    main()
