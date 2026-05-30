"""Base page class — all pages inherit from this."""

import customtkinter as ctk


class BasePage(ctk.CTkFrame):
    """Base class for all pages. Subclasses must implement refresh()."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._built = False

    def refresh(self):
        """Called when the page becomes visible. Override to reload data."""
        if not self._built:
            self.build()
            self._built = True

    def build(self):
        """Build the UI once. Called on first show."""
        raise NotImplementedError
