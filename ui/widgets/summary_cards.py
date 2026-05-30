"""Summary cards widget — income, expense, balance display cards."""

import customtkinter as ctk


class SummaryCards(ctk.CTkFrame):
    """Three-column card display for income, expense, and balance."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.income_card = self._make_card(0, "💰 总收入", "¥0.00", "#1a8a3f", "#e8f5e9")
        self.expense_card = self._make_card(1, "💸 总支出", "¥0.00", "#c62828", "#fce4ec")
        self.balance_card = self._make_card(2, "📊 结余", "¥0.00", "#1565c0", "#e3f2fd")

    def _make_card(self, col, title, value, value_color, bg_color):
        card = ctk.CTkFrame(self, fg_color=bg_color, corner_radius=12, height=100)
        card.grid(row=0, column=col, padx=6, pady=8, sticky="nsew")
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13), text_color=("gray30", "gray70")).pack(pady=(14, 2))
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color=value_color)
        value_label.pack()

        card._value_label = value_label
        return card

    def update_data(self, income: float, expense: float, balance: float):
        """Update all three cards with new values."""
        self.income_card._value_label.configure(text=f"¥{income:,.2f}")
        self.expense_card._value_label.configure(text=f"¥{expense:,.2f}")

        balance_color = "#1a8a3f" if balance >= 0 else "#c62828"
        self.balance_card._value_label.configure(text=f"¥{balance:,.2f}", text_color=balance_color)
