"""Settings page — category/account management, CSV export."""

import customtkinter as ctk
import tkinter.messagebox as mb
import csv
from tkinter import filedialog
from ui.base_page import BasePage
from models.category import (
    get_categories_by_type, add_category, update_category,
    delete_category, get_category_usage_count, reset_to_defaults,
)
from models.account import (
    get_all_accounts, add_account, update_account,
    delete_account, update_balance, get_account_usage_count,
)
from models.transaction import get_transactions


class SettingsPage(BasePage):

    def build(self):
        ctk.CTkLabel(self, text="⚙️ 设置", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=(16, 8))

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=8)

        self.cat_tab = self.tab_view.add("📂 分类管理")
        self.acc_tab = self.tab_view.add("🏦 账户管理")
        self.export_tab = self.tab_view.add("📤 数据导出")

        self._build_category_tab()
        self._build_account_tab()
        self._build_export_tab()

    def refresh(self):
        if not self._built:
            self.build()
            self._built = True
        self._refresh_category_list()
        self._refresh_account_list()

    # --- Category Tab ---

    def _build_category_tab(self):
        ctk.CTkButton(self.cat_tab, text="+ 新增分类", width=100, command=self._add_category_dialog).pack(anchor="w", pady=(8, 4))
        ctk.CTkButton(self.cat_tab, text="🔄 重置为默认", width=120, fg_color="transparent", border_width=1,
                      command=self._reset_categories).pack(anchor="w", pady=(0, 8))
        self.cat_list_frame = ctk.CTkFrame(self.cat_tab, fg_color="transparent")
        self.cat_list_frame.pack(fill="both", expand=True)

    def _refresh_category_list(self):
        for w in self.cat_list_frame.winfo_children():
            w.destroy()
        for typ, title in [("expense", "💸 支出分类"), ("income", "💰 收入分类")]:
            ctk.CTkLabel(self.cat_list_frame, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(8, 4))
            cats = get_categories_by_type(self.app.conn, typ)
            for c in cats:
                self._build_category_row(c)

    def _build_category_row(self, cat):
        row = ctk.CTkFrame(self.cat_list_frame, fg_color=("white", "gray20"), corner_radius=6)
        row.pack(fill="x", pady=2, padx=4)
        ctk.CTkLabel(row, text=f"{cat['icon']} {cat['name']}", font=ctk.CTkFont(size=13), width=150, anchor="w").pack(side="left", padx=10, pady=6)

        def edit():
            dialog = ctk.CTkToplevel(self)
            dialog.title("编辑分类")
            dialog.geometry("300x200")
            dialog.transient(self)
            dialog.grab_set()
            ctk.CTkLabel(dialog, text="名称:").pack(pady=(12, 2))
            name_entry = ctk.CTkEntry(dialog, width=200)
            name_entry.insert(0, cat["name"])
            name_entry.pack(pady=4)
            ctk.CTkLabel(dialog, text="图标 (emoji):").pack(pady=(8, 2))
            icon_entry = ctk.CTkEntry(dialog, width=200)
            icon_entry.insert(0, cat["icon"])
            icon_entry.pack(pady=4)

            def save():
                update_category(self.app.conn, cat["id"], name_entry.get(), icon_entry.get(), cat["sort_order"])
                dialog.destroy()
                self._refresh_category_list()
            ctk.CTkButton(dialog, text="保存", command=save).pack(pady=12)

        ctk.CTkButton(row, text="✏️", width=30, command=edit).pack(side="right", padx=4)

        def delete():
            usage = get_category_usage_count(self.app.conn, cat["id"])
            if usage > 0:
                mb.showwarning("无法删除", f"该分类下有 {usage} 条账单记录，请先更换分类后再删除。")
                return
            if mb.askyesno("确认删除", f"确定要删除分类「{cat['name']}」吗？"):
                delete_category(self.app.conn, cat["id"])
                self._refresh_category_list()
        ctk.CTkButton(row, text="🗑", width=30, fg_color="transparent", text_color="#c62828", command=delete).pack(side="right", padx=4)

    def _add_category_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("新增分类")
        dialog.geometry("300x220")
        dialog.transient(self)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="类型:").pack(pady=(12, 2))
        type_var = ctk.StringVar(value="expense")
        type_menu = ctk.CTkOptionMenu(dialog, variable=type_var, values=["expense", "income"], width=200)
        type_menu.pack(pady=4)
        ctk.CTkLabel(dialog, text="名称:").pack(pady=(4, 2))
        name_entry = ctk.CTkEntry(dialog, width=200)
        name_entry.pack(pady=4)
        ctk.CTkLabel(dialog, text="图标 (emoji):").pack(pady=(4, 2))
        icon_entry = ctk.CTkEntry(dialog, width=200, placeholder_text="🍜")
        icon_entry.pack(pady=4)

        def save():
            if name_entry.get():
                add_category(self.app.conn, name_entry.get(), type_var.get(), icon_entry.get() or "❓")
                dialog.destroy()
                self._refresh_category_list()
        ctk.CTkButton(dialog, text="保存", command=save).pack(pady=12)

    def _reset_categories(self):
        if mb.askyesno("确认重置", "将恢复所有分类为默认设置，确定吗？"):
            reset_to_defaults(self.app.conn)
            self._refresh_category_list()

    # --- Account Tab ---

    def _build_account_tab(self):
        ctk.CTkButton(self.acc_tab, text="+ 新增账户", width=100, command=self._add_account_dialog).pack(anchor="w", pady=(8, 4))
        self.acc_list_frame = ctk.CTkFrame(self.acc_tab, fg_color="transparent")
        self.acc_list_frame.pack(fill="both", expand=True)

    def _refresh_account_list(self):
        for w in self.acc_list_frame.winfo_children():
            w.destroy()
        accounts = get_all_accounts(self.app.conn)
        for a in accounts:
            self._build_account_row(a)

    def _build_account_row(self, account):
        row = ctk.CTkFrame(self.acc_list_frame, fg_color=("white", "gray20"), corner_radius=6)
        row.pack(fill="x", pady=2, padx=4)
        ctk.CTkLabel(row, text=f"{account['icon']} {account['name']}", font=ctk.CTkFont(size=13), width=120, anchor="w").pack(side="left", padx=10, pady=6)
        ctk.CTkLabel(row, text=f"余额: ¥{account['balance']:,.2f}", font=ctk.CTkFont(size=12), width=120, anchor="e").pack(side="left", padx=10)

        def edit_balance():
            from tkinter.simpledialog import askfloat
            new_bal = askfloat("修改余额", f"输入 {account['name']} 的新余额:", initialvalue=account["balance"])
            if new_bal is not None:
                update_balance(self.app.conn, account["id"], new_bal)
                self._refresh_account_list()
        ctk.CTkButton(row, text="💰调余额", width=70, command=edit_balance).pack(side="right", padx=4)

        def edit():
            dialog = ctk.CTkToplevel(self)
            dialog.title("编辑账户")
            dialog.geometry("300x200")
            dialog.transient(self)
            dialog.grab_set()
            ctk.CTkLabel(dialog, text="名称:").pack(pady=(12, 2))
            name_entry = ctk.CTkEntry(dialog, width=200)
            name_entry.insert(0, account["name"])
            name_entry.pack(pady=4)
            ctk.CTkLabel(dialog, text="图标 (emoji):").pack(pady=(8, 2))
            icon_entry = ctk.CTkEntry(dialog, width=200)
            icon_entry.insert(0, account["icon"])
            icon_entry.pack(pady=4)

            def save():
                update_account(self.app.conn, account["id"], name_entry.get(), icon_entry.get(), account["sort_order"])
                dialog.destroy()
                self._refresh_account_list()
            ctk.CTkButton(dialog, text="保存", command=save).pack(pady=12)
        ctk.CTkButton(row, text="✏️", width=30, command=edit).pack(side="right", padx=4)

        def delete():
            usage = get_account_usage_count(self.app.conn, account["id"])
            if usage > 0:
                mb.showwarning("无法删除", f"该账户下有 {usage} 条账单记录，请先更换账户后再删除。")
                return
            if mb.askyesno("确认删除", f"确定要删除账户「{account['name']}」吗？"):
                delete_account(self.app.conn, account["id"])
                self._refresh_account_list()
        ctk.CTkButton(row, text="🗑", width=30, fg_color="transparent", text_color="#c62828", command=delete).pack(side="right", padx=4)

    def _add_account_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("新增账户")
        dialog.geometry("300x220")
        dialog.transient(self)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="名称:").pack(pady=(12, 2))
        name_entry = ctk.CTkEntry(dialog, width=200)
        name_entry.pack(pady=4)
        ctk.CTkLabel(dialog, text="图标 (emoji):").pack(pady=(8, 2))
        icon_entry = ctk.CTkEntry(dialog, width=200, placeholder_text="💳")
        icon_entry.pack(pady=4)
        ctk.CTkLabel(dialog, text="初始余额:").pack(pady=(8, 2))
        balance_entry = ctk.CTkEntry(dialog, width=200, placeholder_text="0.00")
        balance_entry.pack(pady=4)

        def save():
            if name_entry.get():
                try:
                    bal = float(balance_entry.get()) if balance_entry.get() else 0.0
                except ValueError:
                    bal = 0.0
                add_account(self.app.conn, name_entry.get(), bal, icon_entry.get() or "💳")
                dialog.destroy()
                self._refresh_account_list()
        ctk.CTkButton(dialog, text="保存", command=save).pack(pady=12)

    # --- Export Tab ---

    def _build_export_tab(self):
        ctk.CTkLabel(self.export_tab, text="导出账单数据为 CSV 文件", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(12, 8))
        ctk.CTkLabel(self.export_tab, text="时间范围（可选，留空为全部）:").pack(anchor="w")
        range_frame = ctk.CTkFrame(self.export_tab, fg_color="transparent")
        range_frame.pack(anchor="w", pady=4)
        ctk.CTkLabel(range_frame, text="从:").pack(side="left")
        self.export_start = ctk.CTkEntry(range_frame, width=100, placeholder_text="YYYY-MM-DD")
        self.export_start.pack(side="left", padx=4)
        ctk.CTkLabel(range_frame, text="到:").pack(side="left")
        self.export_end = ctk.CTkEntry(range_frame, width=100, placeholder_text="YYYY-MM-DD")
        self.export_end.pack(side="left", padx=4)
        ctk.CTkButton(self.export_tab, text="📤 导出 CSV", command=self._export_csv).pack(pady=16)

    def _export_csv(self):
        start = self.export_start.get() or None
        end = self.export_end.get() or None
        txs = get_transactions(self.app.conn, start_date=start, end_date=end)
        if not txs:
            mb.showinfo("无数据", "所选时间范围内没有账单记录。")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
            title="保存 CSV 文件",
        )
        if not file_path:
            return
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["日期", "类型", "分类", "金额", "账户", "目标账户", "备注"])
            for t in txs:
                type_cn = {"income": "收入", "expense": "支出", "transfer": "转账"}.get(t["type"], t["type"])
                writer.writerow([
                    t["date"], type_cn,
                    f"{t['category_icon'] or ''}{t['category_name'] or '转账'}",
                    t["amount"], t["account_name"],
                    t.get("to_account_name", ""), t["note"],
                ])
        mb.showinfo("导出成功", f"已导出 {len(txs)} 条记录到:\n{file_path}")
