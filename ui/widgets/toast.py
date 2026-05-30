"""Toast notification widget — auto-dismissing overlay messages."""

import customtkinter as ctk
from typing import Optional


class Toast:
    """A brief notification that appears at the top of the window and auto-disappears."""

    _instance: Optional[ctk.CTkLabel] = None
    _timer_id: Optional[str] = None

    @classmethod
    def show(cls, parent: ctk.CTk, message: str, duration: int = 2000, success: bool = True):
        """Show a toast notification at the top-center of the parent window."""
        cls.dismiss()  # remove any existing toast first

        bg_color = "#1a8a3f" if success else "#c62828"
        icon = "✅" if success else "⚠️"

        toast = ctk.CTkLabel(
            parent,
            text=f"  {icon} {message}  ",
            fg_color=bg_color,
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8,
            padx=16,
            pady=8,
        )
        toast.place(relx=0.5, rely=0.08, anchor="center")
        toast.lift()
        cls._instance = toast

        cls._timer_id = parent.after(duration, cls.dismiss)

    @classmethod
    def dismiss(cls):
        """Remove the current toast if visible."""
        if cls._instance:
            try:
                cls._instance.place_forget()
                cls._instance.destroy()
            except Exception:
                pass
            cls._instance = None
        if cls._timer_id:
            try:
                cls._instance.master.after_cancel(cls._timer_id)  # type: ignore
            except Exception:
                pass
            cls._timer_id = None
