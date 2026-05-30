"""Bills page — full transaction list with filters and edit/delete."""

import customtkinter as ctk
import tkinter.messagebox as mb
from ui.base_page import BasePage
from ui.widgets.transaction_list import TransactionList
from ui.widgets.transaction_form import TransactionForm
from models.category import get_all_categories
from models.transaction import delete_transaction


class BillsPage(BasePage):

    def build(self):
        ctk.CTkLabel(self, text="📋 账单", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=(16, 8))

        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(filter_frame, text="类型:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 4))
        self.type_var = ctk.StringVar(value="全部")
        type_menu = ctk.CTkOptionMenu(
            filter_frame, variable=self.type_var,
            values=["全部", "支出", "收入", "转账"], width=80,
            command=lambda _: self._apply_filters(),
        )
        type_menu.pack(side="left", padx=4)

        ctk.CTkLabel(filter_frame, text="分类:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(8, 4))
        self.cat_var = ctk.StringVar(value="全部")
        self.cat_menu = ctk.CTkOptionMenu(
            filter_frame, variable=self.cat_var,
            values=["全部"], width=100,
            command=lambda _: self._apply_filters(),
        )
        self.cat_menu.pack(side="left", padx=4)

        ctk.CTkLabel(filter_frame, text="从:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(8, 2))
        self.start_date_entry = ctk.CTkEntry(filter_frame, width=90, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.pack(side="left", padx=2)
        ctk.CTkLabel(filter_frame, text="到:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(4, 2))
        self.end_date_entry = ctk.CTkEntry(filter_frame, width=90, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.pack(side="left", padx=2)

        self.search_entry = ctk.CTkEntry(filter_frame, width=120, placeholder_text="🔍 搜索备注...")
        self.search_entry.pack(side="left", padx=8)
        ctk.CTkButton(filter_frame, text="筛选", width=60, command=self._apply_filters).pack(side="left", padx=4)
        ctk.CTkButton(filter_frame, text="重置", width=60, fg_color="transparent", border_width=1,
                      command=self._reset_filters).pack(side="left", padx=4)

        self.tx_list = TransactionList(self, limit=20, on_edit=self._edit_transaction)
        self.tx_list.pack(fill="both", expand=True, padx=20, pady=8)
        self._edit_dialog = None

    def refresh(self):
        if not self._built:
            self.build()
            self._built = True
        self._populate_category_filter()
        self._apply_filters()

    def _populate_category_filter(self):
        cats = get_all_categories(self.app.conn)
        values = ["全部"] + [f"{c['icon']} {c['name']}" for c in cats]
        self.cat_menu.configure(values=values)
        self.cat_var.set("全部")

    def _get_filter_params(self):
        type_map = {"支出": "expense", "收入": "income", "转账": "transfer"}
        typ = type_map.get(self.type_var.get(), None)
        category_id = None
        if self.cat_var.get() != "全部":
            cats = get_all_categories(self.app.conn)
            for c in cats:
                if f"{c['icon']} {c['name']}" == self.cat_var.get():
                    category_id = c["id"]
                    break
        start_date = self.start_date_entry.get() or None
        end_date = self.end_date_entry.get() or None
        search = self.search_entry.get() or None
        return typ, category_id, start_date, end_date, search

    def _apply_filters(self):
        typ, category_id, start_date, end_date, search = self._get_filter_params()
        self.tx_list.load(self.app.conn, typ=typ, category_id=category_id,
                          start_date=start_date, end_date=end_date, search=search, reset=True)

    def _reset_filters(self):
        self.type_var.set("全部")
        self.cat_var.set("全部")
        self.start_date_entry.delete(0, "end")
        self.end_date_entry.delete(0, "end")
        self.search_entry.delete(0, "end")
        self._apply_filters()

    def _edit_transaction(self, transaction_id: int):
        if self._edit_dialog is not None:
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title("编辑账单")
        dialog.geometry("500x650")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        form = TransactionForm(dialog, self.app, on_save=lambda: self._on_edit_saved(dialog))
        form.pack(fill="both", expand=True, padx=16, pady=16)
        form.refresh_accounts()
        form.load_transaction(transaction_id)

        from models.transaction import get_transaction_by_id
        t = get_transaction_by_id(self.app.conn, transaction_id)
        ctk.CTkButton(
            dialog, text="🗑 删除", fg_color="#c62828", hover_color="#b71c1c",
            command=lambda: self._delete_transaction(transaction_id, dialog),
        ).pack(pady=(0, 12))
        self._edit_dialog = dialog

    def _on_edit_saved(self, dialog):
        dialog.destroy()
        self._edit_dialog = None
        self._apply_filters()

    def _delete_transaction(self, transaction_id: int, dialog):
        if not mb.askyesno("确认删除", "确定要删除这条账单记录吗？"):
            return
        delete_transaction(self.app.conn, transaction_id)
        dialog.destroy()
        self._edit_dialog = None
        self._apply_filters()
