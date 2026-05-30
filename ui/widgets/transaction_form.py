"""Transaction form widget — reusable for both add and edit modes."""

import customtkinter as ctk
from typing import Optional, Callable
from models.category import get_categories_by_type
from models.account import get_all_accounts
from utils.helpers import today_str


class TransactionForm(ctk.CTkFrame):
    """Reusable form for adding/editing transactions."""

    TRANSACTION_TYPES = [
        ("💸 支出", "expense"),
        ("💰 收入", "income"),
        ("🔄 转账", "transfer"),
    ]

    def __init__(self, parent, app, on_save: Optional[Callable] = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app
        self.on_save = on_save
        self._transaction_id: Optional[int] = None
        self._selected_category_id: Optional[int] = None

        self._build_type_selector()
        self._build_form_fields()
        self._build_category_grid()
        self._build_save_button()

    def _build_type_selector(self):
        ctk.CTkLabel(self, text="类型", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 4))
        self.type_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.type_frame.pack(fill="x", pady=(0, 12))

        self._type_btns = {}
        for i, (label, typ) in enumerate(self.TRANSACTION_TYPES):
            btn = ctk.CTkButton(
                self.type_frame,
                text=label,
                width=100,
                height=36,
                fg_color=("gray75", "gray30") if i == 0 else "transparent",
                text_color=("black", "white"),
                hover_color=("gray85", "gray25"),
                border_width=1,
                border_color=("gray60", "gray40"),
                command=lambda t=typ: self._select_type(t),
            )
            btn.grid(row=0, column=i, padx=4)
            self._type_btns[typ] = btn
        self._current_type = "expense"

    def _build_form_fields(self):
        ctk.CTkLabel(self, text="金额", font=ctk.CTkFont(size=13)).pack(anchor="w")
        self.amount_entry = ctk.CTkEntry(self, placeholder_text="0.00", height=36)
        self.amount_entry.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(self, text="日期", font=ctk.CTkFont(size=13)).pack(anchor="w")
        self.date_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD", height=36)
        self.date_entry.insert(0, today_str())
        self.date_entry.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(self, text="账户", font=ctk.CTkFont(size=13)).pack(anchor="w")
        self.account_var = ctk.StringVar()
        self.account_menu = ctk.CTkOptionMenu(self, variable=self.account_var, values=[], height=36)
        self.account_menu.pack(fill="x", pady=(2, 8))

        self.to_account_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.to_account_frame, text="目标账户", font=ctk.CTkFont(size=13)).pack(anchor="w")
        self.to_account_var = ctk.StringVar()
        self.to_account_menu = ctk.CTkOptionMenu(self.to_account_frame, variable=self.to_account_var, values=[], height=36)
        self.to_account_menu.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(self, text="备注", font=ctk.CTkFont(size=13)).pack(anchor="w")
        self.note_entry = ctk.CTkEntry(self, placeholder_text="可选备注", height=36)
        self.note_entry.pack(fill="x", pady=(2, 8))

        self.error_label = ctk.CTkLabel(self, text="", text_color="red", font=ctk.CTkFont(size=12))
        self.error_label.pack(anchor="w", pady=(4, 0))

    def _build_category_grid(self):
        ctk.CTkLabel(self, text="分类", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(8, 4))
        self.category_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.category_frame.pack(fill="x", pady=(0, 8))
        self._category_buttons = {}
        self._populate_categories("expense")

    def _build_save_button(self):
        self.save_btn = ctk.CTkButton(
            self, text="💾 保存", height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_save_click,
        )
        self.save_btn.pack(pady=(8, 4))

    def _select_type(self, typ: str):
        self._current_type = typ
        for t, btn in self._type_btns.items():
            btn.configure(fg_color=("gray75", "gray30") if t == typ else "transparent")
        self._populate_categories(typ if typ != "transfer" else "expense")
        if typ == "transfer":
            self.to_account_frame.pack(fill="x", pady=(0, 8))
        else:
            self.to_account_frame.pack_forget()
            self.error_label.configure(text="")

    def _populate_categories(self, typ: str):
        for widget in self.category_frame.winfo_children():
            widget.destroy()
        self._category_buttons = {}
        self._selected_category_id = None

        cats = get_categories_by_type(self.app.conn, typ)
        for i, cat in enumerate(cats):
            row = i // 4
            col = i % 4
            btn = ctk.CTkButton(
                self.category_frame,
                text=f"{cat['icon']} {cat['name']}",
                width=90, height=38,
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                text_color=("gray20", "gray80"),
                hover_color=("gray80", "gray30"),
                border_width=1,
                border_color=("gray65", "gray45"),
                command=lambda cid=cat["id"]: self._select_category(cid),
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="w")
            self._category_buttons[cat["id"]] = btn

    def _select_category(self, category_id: Optional[int]):
        self._selected_category_id = category_id
        for cid, btn in self._category_buttons.items():
            btn.configure(fg_color=("gray75", "gray30") if cid == category_id else "transparent")

    def refresh_accounts(self):
        accounts = get_all_accounts(self.app.conn)
        names = [f"{a['icon']} {a['name']}" for a in accounts]
        self.account_menu.configure(values=names)
        if names:
            self.account_var.set(names[0])
        self.to_account_menu.configure(values=names)
        if len(names) > 1:
            self.to_account_var.set(names[1])
        elif names:
            self.to_account_var.set(names[0])

    def _get_account_id_from_var(self, var) -> Optional[int]:
        accounts = get_all_accounts(self.app.conn)
        for a in accounts:
            if f"{a['icon']} {a['name']}" == var.get():
                return a["id"]
        return None

    def _validate(self) -> Optional[str]:
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                return "金额必须大于 0"
        except ValueError:
            return "请输入有效金额"
        if self._current_type != "transfer" and self._selected_category_id is None:
            return "请选择分类"
        if self._get_account_id_from_var(self.account_var) is None:
            return "请选择账户"
        if self._current_type == "transfer":
            src = self._get_account_id_from_var(self.account_var)
            dst = self._get_account_id_from_var(self.to_account_var)
            if src and dst and src == dst:
                return "转账源账户和目标账户不能相同"
        return None

    def _on_save_click(self):
        error = self._validate()
        if error:
            self.error_label.configure(text=f"⚠ {error}")
            return
        self.error_label.configure(text="")

        from models.transaction import add_transaction, update_transaction

        amount = float(self.amount_entry.get())
        account_id = self._get_account_id_from_var(self.account_var)
        to_account_id = self._get_account_id_from_var(self.to_account_var) if self._current_type == "transfer" else None
        category_id = self._selected_category_id if self._current_type != "transfer" else None
        date_val = self.date_entry.get() or today_str()
        note = self.note_entry.get()

        if self._transaction_id:
            update_transaction(
                self.app.conn, self._transaction_id,
                typ=self._current_type, amount=amount,
                category_id=category_id, account_id=account_id,
                to_account_id=to_account_id, note=note, date=date_val,
            )
        else:
            add_transaction(
                self.app.conn, self._current_type, amount,
                category_id=category_id, account_id=account_id,
                to_account_id=to_account_id, note=note, date=date_val,
            )

        if self._current_type == "expense" and category_id:
            from models.budget import get_budget_status
            status_list = get_budget_status(self.app.conn, date_val[:7])
            for s in status_list:
                if s["category_id"] == category_id and s["percentage"] > 100:
                    self._show_budget_alert(s)

        self.clear()
        if self.on_save:
            self.on_save()

    def _show_budget_alert(self, status: dict):
        import tkinter.messagebox as mb
        mb.showwarning(
            "预算超支提醒",
            f"⚠️ 本月 {status['category_icon']} {status['category_name']} "
            f"已支出 ¥{status['spent']:,.2f}\n"
            f"预算为 ¥{status['amount']:,.2f}，超支 ¥{abs(status['remaining']):,.2f}",
        )

    def load_transaction(self, transaction_id: int):
        from models.transaction import get_transaction_by_id
        t = get_transaction_by_id(self.app.conn, transaction_id)
        if not t:
            return
        self._transaction_id = transaction_id
        self._select_type(t["type"])
        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, str(t["amount"]))
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, t["date"])
        self.note_entry.delete(0, "end")
        self.note_entry.insert(0, t["note"] or "")
        accounts = get_all_accounts(self.app.conn)
        for a in accounts:
            if a["id"] == t["account_id"]:
                self.account_var.set(f"{a['icon']} {a['name']}")
                break
        if t["type"] == "transfer" and t["to_account_id"]:
            for a in accounts:
                if a["id"] == t["to_account_id"]:
                    self.to_account_var.set(f"{a['icon']} {a['name']}")
                    break
        if t["category_id"]:
            self._select_category(t["category_id"])
        self.save_btn.configure(text="💾 更新")

    def clear(self):
        self._transaction_id = None
        self._selected_category_id = None
        self.amount_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, today_str())
        self.note_entry.delete(0, "end")
        self._select_type("expense")
        self.save_btn.configure(text="💾 保存")
        self.error_label.configure(text="")
