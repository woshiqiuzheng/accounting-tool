"""Add transaction page."""

import customtkinter as ctk
from ui.base_page import BasePage
from ui.widgets.transaction_form import TransactionForm


class AddPage(BasePage):

    def build(self):
        ctk.CTkLabel(self, text="➕ 记账", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=(16, 8))
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=8)
        self.form = TransactionForm(scroll, self.app, on_save=self._on_saved)
        self.form.pack(fill="x", pady=8)

    def refresh(self):
        if not self._built:
            self.build()
            self._built = True
        self.form.refresh_accounts()

    def _on_saved(self):
        self.form.clear()
        self.form.refresh_accounts()
