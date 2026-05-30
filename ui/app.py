"""Main application window — sidebar navigation and page container."""

import customtkinter as ctk
from typing import Optional


PAGES = [
    ("📊", "总览", 0),
    ("➕", "记账", 1),
    ("📋", "账单", 2),
    ("📈", "统计", 3),
    ("💰", "预算", 4),
    ("⚙️", "设置", 5),
]


class App(ctk.CTk):
    """Main application window with sidebar navigation."""

    def __init__(self):
        super().__init__()
        self.title("📒 个人记账本")
        self.geometry("1000x700")
        self.resizable(False, False)

        # Initialize database
        from database.connection import init_db
        try:
            init_db()
        except Exception:
            from database.connection import backup_and_rebuild
            backup_and_rebuild()

        self._conn = None
        self._current_page_index = -1
        self._pages: list[Optional[ctk.CTkFrame]] = [None] * len(PAGES)
        self._nav_buttons: list[ctk.CTkButton] = []

        self._build_sidebar()
        self._build_main_area()

        # Show default page (overview)
        self.show_page(0)

    @property
    def conn(self):
        """Lazy database connection."""
        if self._conn is None:
            from database.connection import get_connection
            self._conn = get_connection()
        return self._conn

    def _build_sidebar(self):
        """Build the left-side icon navigation bar."""
        self.sidebar = ctk.CTkFrame(self, width=70, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        for icon, label, idx in PAGES:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}\n{label}",
                width=60,
                height=60,
                corner_radius=8,
                fg_color="transparent",
                text_color=("gray40", "gray60"),
                hover_color=("gray85", "gray25"),
                font=ctk.CTkFont(size=11),
                command=lambda i=idx: self.show_page(i),
            )
            btn.pack(pady=4, padx=5)
            self._nav_buttons.append(btn)

    def _build_main_area(self):
        """Build the main content container."""
        self.main_container = ctk.CTkFrame(self, corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)

    def show_page(self, index: int):
        """Switch to the page at the given index."""
        if index == self._current_page_index:
            return

        # Update nav button highlight
        for i, btn in enumerate(self._nav_buttons):
            if i == index:
                btn.configure(fg_color=("gray75", "gray30"), text_color=("black", "white"))
            else:
                btn.configure(fg_color="transparent", text_color=("gray40", "gray60"))

        # Hide current page
        if self._current_page_index >= 0 and self._pages[self._current_page_index] is not None:
            self._pages[self._current_page_index].pack_forget()

        # Show (or lazy-load) new page
        if self._pages[index] is None:
            self._pages[index] = self._create_page(index)

        self._pages[index].pack(fill="both", expand=True)
        self._current_page_index = index

        # Refresh page data
        self._pages[index].refresh()

    def _create_page(self, index: int) -> ctk.CTkFrame:
        """Factory method — create a page by index."""
        from ui.pages.overview_page import OverviewPage
        from ui.pages.add_page import AddPage
        from ui.pages.bills_page import BillsPage
        from ui.pages.stats_page import StatsPage
        from ui.pages.budget_page import BudgetPage
        from ui.pages.settings_page import SettingsPage

        creators = [
            lambda: OverviewPage(self.main_container, self),
            lambda: AddPage(self.main_container, self),
            lambda: BillsPage(self.main_container, self),
            lambda: StatsPage(self.main_container, self),
            lambda: BudgetPage(self.main_container, self),
            lambda: SettingsPage(self.main_container, self),
        ]
        return creators[index]()
