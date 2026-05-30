"""Budget progress widget — displays budget status bars."""

import customtkinter as ctk
from typing import List, Optional
from models.budget import get_budget_status, get_all_budgets_for_month
from utils.helpers import current_month_str


class BudgetProgress(ctk.CTkFrame):
    """Display budget progress bars for a given month."""

    def __init__(self, parent, month: Optional[str] = None, show_header: bool = True, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.month = month or current_month_str()
        self.show_header = show_header
        self._rows: List[ctk.CTkFrame] = []

    def refresh(self, conn):
        for row in self._rows:
            row.destroy()
        self._rows = []

        if self.show_header:
            header = ctk.CTkLabel(self, text=f"💰 预算概览 ({self.month})", font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
            header.pack(fill="x", pady=(0, 8))
            self._rows.append(header)

        budgets = get_all_budgets_for_month(conn, self.month)
        if not budgets:
            empty = ctk.CTkLabel(self, text="暂无预算设置", font=ctk.CTkFont(size=12), text_color="gray")
            empty.pack(pady=20)
            self._rows.append(empty)
            return

        status_list = get_budget_status(conn, self.month)
        for s in status_list:
            row = self._build_row(s)
            row.pack(fill="x", pady=4)
            self._rows.append(row)

    def _build_row(self, status: dict) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self, fg_color=("white", "gray20"), corner_radius=8)
        frame.pack_propagate(False)

        over_budget = status["percentage"] > 100
        bar_color = "#c62828" if over_budget else "#1a8a3f"

        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(label_frame, text=f"{status['category_icon']} {status['category_name']}", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        ctk.CTkLabel(label_frame, text=f"¥{status['spent']:,.0f} / ¥{status['amount']:,.0f}", font=ctk.CTkFont(size=12), text_color="gray").pack(side="right")

        progress_frame = ctk.CTkFrame(frame, height=20, fg_color=("gray85", "gray30"), corner_radius=10)
        progress_frame.pack(fill="x", padx=10, pady=(0, 8))
        progress_frame.pack_propagate(False)

        pct = min(status["percentage"], 100)
        fill_width = max(int(pct), 5)
        fill = ctk.CTkFrame(progress_frame, width=fill_width, height=20, fg_color=bar_color, corner_radius=10)
        fill.place(x=0, y=0)
        fill.pack_propagate(False)

        pct_label = ctk.CTkLabel(
            progress_frame,
            text=f"{status['percentage']:.0f}%" if not over_budget else f"{status['percentage']:.0f}% ⚠",
            font=ctk.CTkFont(size=11), text_color="white",
        )
        pct_label.place(relx=0.5, rely=0.5, anchor="center")

        return frame
