"""Transaction list widget — shows grouped transactions with date headers."""

import customtkinter as ctk
from typing import Optional, Callable, List
from models.transaction import get_transactions
from utils.helpers import format_currency


class TransactionList(ctk.CTkScrollableFrame):
    """Scrollable list of transactions grouped by date."""

    def __init__(self, parent, limit: int = 20, on_edit: Optional[Callable] = None, show_header: bool = True, **kwargs):
        super().__init__(parent, **kwargs)
        self.limit = limit
        self.on_edit = on_edit
        self.show_header = show_header
        self._offset = 0
        self._all_loaded = False
        self._item_frames: List[ctk.CTkFrame] = []

    def load(self, conn, typ=None, category_id=None, start_date=None, end_date=None, search=None, reset=True):
        if reset:
            self._offset = 0
            self._all_loaded = False
            self._clear_items()

        txs = get_transactions(
            conn, typ=typ, category_id=category_id,
            start_date=start_date, end_date=end_date,
            search=search, limit=self.limit + 1, offset=self._offset,
        )

        if len(txs) <= self.limit:
            self._all_loaded = True
        else:
            txs = txs[:self.limit]

        self._render_transactions(conn, txs)
        self._offset += self.limit

    def _clear_items(self):
        for f in self._item_frames:
            f.destroy()
        self._item_frames = []

    def _render_transactions(self, conn, txs):
        if not txs:
            empty = ctk.CTkLabel(self, text="暂无账单记录", font=ctk.CTkFont(size=13), text_color="gray")
            empty.pack(pady=40)
            self._item_frames.append(empty)
            return

        current_date = None
        for t in txs:
            if t["date"] != current_date:
                current_date = t["date"]
                date_label = ctk.CTkLabel(
                    self, text=f"  {current_date}",
                    font=ctk.CTkFont(size=12, weight="bold"), anchor="w",
                )
                date_label.pack(fill="x", pady=(8, 2), padx=4)
                self._item_frames.append(date_label)

            item = self._render_item(t)
            item.pack(fill="x", padx=4, pady=1)
            self._item_frames.append(item)

        if not self._all_loaded:
            more_btn = ctk.CTkButton(
                self, text="加载更多...", height=32,
                fg_color="transparent", text_color=("gray30", "gray70"),
                hover_color=("gray85", "gray25"),
                command=lambda: self.load(conn, reset=False),
            )
            more_btn.pack(pady=8)
            self._item_frames.append(more_btn)

    def _render_item(self, t) -> ctk.CTkFrame:
        icon = t["category_icon"] if t["category_icon"] else "🔄"
        cat_name = t["category_name"] if t["category_name"] else "转账"
        note = t["note"] if t["note"] else ""

        if t["type"] == "income":
            amount_color = "#1a8a3f"
            sign = "+"
        elif t["type"] == "expense":
            amount_color = "#c62828"
            sign = "-"
        else:
            amount_color = "#1565c0"
            sign = "→"

        amount_text = f"{sign} ¥{t['amount']:,.2f}"
        if t["type"] == "transfer":
            account_text = f"{t['account_name']} → {t['to_account_name'] or '?'}"
        else:
            account_text = t["account_name"] or ""

        frame = ctk.CTkFrame(self, fg_color=("white", "gray20"), corner_radius=8, height=44)
        frame.pack_propagate(False)

        if self.on_edit:
            frame.bind("<Button-1>", lambda e, tid=t["id"]: self.on_edit(tid))

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=6)

        ctk.CTkLabel(inner, text=f"{icon}  {cat_name}", font=ctk.CTkFont(size=13), width=120, anchor="w").pack(side="left")
        ctk.CTkLabel(inner, text=note, font=ctk.CTkFont(size=12), text_color="gray", width=200, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(inner, text=account_text, font=ctk.CTkFont(size=11), text_color="gray", width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(inner, text=amount_text, font=ctk.CTkFont(size=14, weight="bold"), text_color=amount_color).pack(side="right")

        return frame
