"""Statistics page — yearly summary table and category pie charts."""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.base_page import BasePage
from models.statistics import get_yearly_summary, get_category_summary
from utils.helpers import format_currency
import datetime


class StatsPage(BasePage):

    def build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(header, text="📈 统计", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")

        self.year_var = ctk.StringVar(value=str(datetime.date.today().year))
        self.year_menu = ctk.CTkOptionMenu(
            header, variable=self.year_var,
            values=[str(y) for y in range(2020, datetime.date.today().year + 1)],
            command=lambda _: self._refresh_data(), width=80,
        )
        self.year_menu.pack(side="right")

        ctk.CTkLabel(self, text="月度汇总", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(4, 4))
        self.table_frame = ctk.CTkFrame(self, fg_color=("white", "gray20"), corner_radius=8)
        self.table_frame.pack(fill="x", padx=20, pady=(0, 12))

        chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=8)
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(1, weight=1)

        expense_chart_container = ctk.CTkFrame(chart_frame, fg_color=("white", "gray20"), corner_radius=8)
        expense_chart_container.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(expense_chart_container, text="支出分类占比", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(8, 0))
        self.expense_figure = Figure(figsize=(3, 2.5), dpi=100)
        self.expense_canvas = FigureCanvasTkAgg(self.expense_figure, expense_chart_container)
        self.expense_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        income_chart_container = ctk.CTkFrame(chart_frame, fg_color=("white", "gray20"), corner_radius=8)
        income_chart_container.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(income_chart_container, text="收入分类占比", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(8, 0))
        self.income_figure = Figure(figsize=(3, 2.5), dpi=100)
        self.income_canvas = FigureCanvasTkAgg(self.income_figure, income_chart_container)
        self.income_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        chart_control = ctk.CTkFrame(self, fg_color="transparent")
        chart_control.pack(fill="x", padx=20, pady=(0, 8))
        ctk.CTkLabel(chart_control, text="图表月份:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.chart_month_var = ctk.StringVar(value=f"{datetime.date.today().year}-{datetime.date.today().month:02d}")
        self.chart_month_menu = ctk.CTkOptionMenu(
            chart_control, variable=self.chart_month_var, values=[], width=80,
            command=lambda _: self._update_charts(),
        )
        self.chart_month_menu.pack(side="left", padx=4)

    def refresh(self):
        if not self._built:
            self.build()
            self._built = True
        self._refresh_data()

    def _refresh_data(self):
        year = self.year_var.get()
        self._populate_month_menu(year)
        self._update_table(year)
        self._update_charts()

    def _populate_month_menu(self, year: str):
        months = [f"{year}-{m:02d}" for m in range(1, 13)]
        self.chart_month_menu.configure(values=months)
        current = self.chart_month_var.get()
        if current not in months:
            self.chart_month_var.set(months[0])

    def _update_table(self, year: str):
        for w in self.table_frame.winfo_children():
            w.destroy()
        data = get_yearly_summary(self.app.conn, year)
        if not data:
            ctk.CTkLabel(self.table_frame, text="该年度暂无数据", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=20)
            return
        hdr = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=8, pady=(8, 2))
        for i, text in enumerate(["月份", "收入", "支出", "结余"]):
            ctk.CTkLabel(hdr, text=text, font=ctk.CTkFont(size=12, weight="bold"), width=100).grid(row=0, column=i, padx=8)
        for d in data:
            row_f = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            row_f.pack(fill="x", padx=8, pady=1)
            balance_color = "#1a8a3f" if d["balance"] >= 0 else "#c62828"
            ctk.CTkLabel(row_f, text=f"{d['month']}月", width=100, anchor="w").grid(row=0, column=0, padx=8)
            ctk.CTkLabel(row_f, text=format_currency(d["income"]), width=100, anchor="e", text_color="#1a8a3f").grid(row=0, column=1, padx=8)
            ctk.CTkLabel(row_f, text=format_currency(d["expense"]), width=100, anchor="e", text_color="#c62828").grid(row=0, column=2, padx=8)
            ctk.CTkLabel(row_f, text=format_currency(d["balance"]), width=100, anchor="e", text_color=balance_color).grid(row=0, column=3, padx=8)

    def _update_charts(self):
        month = self.chart_month_var.get()
        self._draw_pie_chart(self.expense_figure, "expense", month, "支出分类")
        self.expense_canvas.draw()
        self._draw_pie_chart(self.income_figure, "income", month, "收入分类")
        self.income_canvas.draw()

    def _draw_pie_chart(self, figure: Figure, typ: str, month: str, title: str):
        figure.clear()
        ax = figure.add_subplot(111)
        data = get_category_summary(self.app.conn, typ, month)
        if not data:
            ax.text(0.5, 0.5, "暂无数据", ha="center", va="center", fontsize=12)
            ax.set_title(title, fontsize=10)
            return
        labels = [f"{d['icon']} {d['name']}" for d in data]
        sizes = [d["total"] for d in data]
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct="%1.1f%%",
            startangle=90, textprops={"fontsize": 8},
        )
        ax.set_title(title, fontsize=10)
