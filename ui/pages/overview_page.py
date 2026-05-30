"""Overview page — monthly summary, recent transactions, budget overview."""

import customtkinter as ctk
from ui.base_page import BasePage
from ui.widgets.summary_cards import SummaryCards
from ui.widgets.transaction_list import TransactionList
from ui.widgets.budget_progress import BudgetProgress
from models.statistics import get_monthly_summary
from utils.helpers import current_month_str


class OverviewPage(BasePage):

    def build(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(header_frame, text="📊 总览", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")

        self.month_var = ctk.StringVar(value=current_month_str())
        self.month_menu = ctk.CTkOptionMenu(
            header_frame, variable=self.month_var, values=self._get_recent_months(),
            command=lambda _: self._refresh_data(), width=120,
        )
        self.month_menu.pack(side="right")

        self.summary_cards = SummaryCards(self)
        self.summary_cards.pack(fill="x", padx=20, pady=8)

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="both", expand=True, padx=20, pady=8)
        bottom.grid_columnconfigure(0, weight=3)
        bottom.grid_columnconfigure(1, weight=2)

        recent_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        recent_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        recent_header = ctk.CTkFrame(recent_frame, fg_color="transparent")
        recent_header.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(recent_header, text="最近账单", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        view_all_btn = ctk.CTkButton(
            recent_header, text="查看全部 →",
            width=80, height=24,
            fg_color="transparent", text_color=("blue", "lightblue"),
            hover_color=("gray85", "gray25"),
            font=ctk.CTkFont(size=11),
            command=lambda: self.app.show_page(2),
        )
        view_all_btn.pack(side="right")
        self.recent_list = TransactionList(recent_frame, limit=5, show_header=False)
        self.recent_list.pack(fill="both", expand=True)

        budget_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        budget_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.budget_preview = BudgetProgress(budget_frame, show_header=True)
        self.budget_preview.pack(fill="x")

    def _get_recent_months(self):
        import datetime
        months = []
        today = datetime.date.today()
        for i in range(12):
            m = today.month - i
            y = today.year
            while m < 1:
                m += 12
                y -= 1
            months.append(f"{y}-{m:02d}")
        return months

    def refresh(self):
        if not self._built:
            self.build()
            self._built = True
        self._refresh_data()

    def _refresh_data(self):
        month = self.month_var.get()
        parts = month.split("-")
        if len(parts) != 2:
            return
        summary = get_monthly_summary(self.app.conn, parts[0], parts[1])
        self.summary_cards.update_data(summary["income"], summary["expense"], summary["balance"])
        import calendar
        last_day = calendar.monthrange(int(parts[0]), int(parts[1]))[1]
        start = f"{parts[0]}-{parts[1]}-01"
        end = f"{parts[0]}-{parts[1]}-{last_day:02d}"
        self.recent_list.load(self.app.conn, start_date=start, end_date=end, reset=True)
        self.budget_preview.refresh(self.app.conn)
