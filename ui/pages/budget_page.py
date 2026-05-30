"""Budget page — set and track monthly budgets."""

import customtkinter as ctk
from ui.base_page import BasePage
from ui.widgets.budget_progress import BudgetProgress
from ui.widgets.toast import Toast
from models.category import get_categories_by_type
from models.budget import set_budget, get_all_budgets_for_month
from utils.helpers import current_month_str


class BudgetPage(BasePage):

    def build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(header, text="💰 预算", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")

        self.month_var = ctk.StringVar(value=current_month_str())
        self.month_menu = ctk.CTkOptionMenu(
            header, variable=self.month_var,
            values=self._get_recent_months(), width=120,
            command=lambda _: self._refresh_data(),
        )
        self.month_menu.pack(side="right")
        ctk.CTkButton(header, text="+ 设置预算", width=100, command=self._add_budget_dialog).pack(side="right", padx=8)

        self.budget_progress = BudgetProgress(self, show_header=False)
        self.budget_progress.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(self, text="预算明细（点击金额可编辑）", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(12, 4))
        self.table_frame = ctk.CTkFrame(self, fg_color=("white", "gray20"), corner_radius=8)
        self.table_frame.pack(fill="x", padx=20, pady=(0, 8))

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
        self.budget_progress.month = month
        self.budget_progress.refresh(self.app.conn)
        self._populate_table(month)

    def _populate_table(self, month: str):
        for w in self.table_frame.winfo_children():
            w.destroy()
        budgets = get_all_budgets_for_month(self.app.conn, month)
        if not budgets:
            ctk.CTkLabel(self.table_frame, text="暂无预算，点击右上角「设置预算」开始", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=20)
            return
        hdr = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=8, pady=(8, 2))
        for i, text in enumerate(["分类", "预算金额"]):
            ctk.CTkLabel(hdr, text=text, font=ctk.CTkFont(size=12, weight="bold"), width=150).grid(row=0, column=i, padx=8)
        for b in budgets:
            row_f = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            row_f.pack(fill="x", padx=8, pady=2)
            ctk.CTkLabel(row_f, text=f"{b['category_icon']} {b['category_name']}", width=150, anchor="w").grid(row=0, column=0, padx=8)
            amount_label = ctk.CTkLabel(
                row_f, text=f"¥{b['amount']:,.2f}", width=150, anchor="w",
                font=ctk.CTkFont(size=13),
                text_color=("blue", "lightblue"), cursor="hand2",
            )
            amount_label.grid(row=0, column=1, padx=8)
            cid = b["category_id"]
            mid = month
            amount_label.bind("<Button-1>", lambda e, cat_id=cid, mon=mid: self._edit_budget_amount(cat_id, mon))

    def _add_budget_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("设置预算")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="选择分类", font=ctk.CTkFont(size=13)).pack(pady=(12, 4))
        cats = get_categories_by_type(self.app.conn, "expense")
        cat_names = [f"{c['icon']} {c['name']}" for c in cats]
        cat_var = ctk.StringVar(value=cat_names[0] if cat_names else "")
        cat_menu = ctk.CTkOptionMenu(dialog, variable=cat_var, values=cat_names, width=200)
        cat_menu.pack(pady=4)

        ctk.CTkLabel(dialog, text="每月预算金额 (¥)", font=ctk.CTkFont(size=13)).pack(pady=(12, 4))
        amount_entry = ctk.CTkEntry(dialog, placeholder_text="0.00", width=200)
        amount_entry.pack(pady=4)

        def save():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                ctk.CTkLabel(dialog, text="请输入有效金额", text_color="red").pack()
                return
            selected_cat = cat_var.get()
            for c in cats:
                if f"{c['icon']} {c['name']}" == selected_cat:
                    set_budget(self.app.conn, c["id"], self.month_var.get(), amount)
                    Toast.show(dialog.winfo_toplevel(), "预算已设置", success=True)
                    dialog.destroy()
                    self._refresh_data()
                    return
        ctk.CTkButton(dialog, text="保存", command=save).pack(pady=16)

    def _edit_budget_amount(self, category_id: int, month: str):
        from models.budget import get_budget
        budget = get_budget(self.app.conn, category_id, month)
        if not budget:
            return
        from tkinter.simpledialog import askfloat
        new_amount = askfloat(
            "修改预算",
            f"输入 {budget['category_icon']}{budget['category_name']} 的新预算金额:",
            initialvalue=budget["amount"], minvalue=0.01,
        )
        if new_amount is not None:
            set_budget(self.app.conn, category_id, month, new_amount)
            Toast.show(self.winfo_toplevel(), "预算已更新", success=True)
            self._refresh_data()
