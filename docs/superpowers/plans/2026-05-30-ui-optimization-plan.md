# 界面交互优化 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix window to fixed size (no drag-resize), eliminate unnecessary scrolling in pages, and add success/error toast notifications across the app.

**Architecture:** Fix window in `app.py` → create reusable Toast widget → remove `CTkScrollableFrame` from Add page → restructure Settings page → wire toasts into all save/delete operations.

**Tech Stack:** Python 3.10+, CustomTkinter

---

### Task 1: Fix window to fixed size (no resizing)

**Files:**
- Modify: `ui/app.py:22-25`

- [ ] **Step 1: Change window configuration**

Current code (lines 23-25):
```python
self.geometry("1000x700")
self.minsize(900, 600)
self.resizable(True, True)
```

Change to:
```python
self.geometry("1000x700")
self.resizable(False, False)
```

Remove `self.minsize()` and set `resizable(False, False)` so the window can't be dragged to resize.

- [ ] **Step 2: Run tests to confirm no regressions**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
uv run python -m pytest tests/ -v
```

Expected: 34 passed

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "fix: lock window to fixed size, disable resize dragging"
```

---

### Task 2: Create toast notification widget

**Files:**
- Create: `ui/widgets/toast.py`

- [ ] **Step 1: Write toast.py**

```python
"""Toast notification widget — auto-dismissing overlay messages."""

import customtkinter as ctk
from typing import Optional


class Toast:
    """A brief notification that appears at the top of the window and auto-disappears."""

    _instance: Optional[ctk.CTkLabel] = None
    _timer_id: Optional[str] = None

    @classmethod
    def show(cls, parent: ctk.CTk, message: str, duration: int = 2000, success: bool = True):
        """Show a toast notification at the top-center of the parent window."""
        cls.dismiss()  # remove any existing toast first

        bg_color = "#1a8a3f" if success else "#c62828"
        icon = "✅" if success else "⚠️"

        toast = ctk.CTkLabel(
            parent,
            text=f"  {icon} {message}  ",
            fg_color=bg_color,
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8,
            padx=16,
            pady=8,
        )
        toast.place(relx=0.5, rely=0.08, anchor="center")
        toast.lift()
        cls._instance = toast

        cls._timer_id = parent.after(duration, cls.dismiss)

    @classmethod
    def dismiss(cls):
        """Remove the current toast if visible."""
        if cls._instance:
            try:
                cls._instance.place_forget()
                cls._instance.destroy()
            except Exception:
                pass
            cls._instance = None
        if cls._timer_id:
            try:
                cls._instance.master.after_cancel(cls._timer_id)  # type: ignore
            except Exception:
                pass
            cls._timer_id = None
```

- [ ] **Step 2: Verify import**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
uv run python -c "from ui.widgets.toast import Toast; print('OK')"
```

Expected: OK

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: add toast notification widget"
```

---

### Task 3: Remove scrolling from Add Transaction page

**Files:**
- Modify: `ui/pages/add_page.py`

The Add page wraps the form in a `CTkScrollableFrame`. We need to remove it and make the form fit in the fixed window.

Current code (lines 10-15):
```python
def build(self):
    ctk.CTkLabel(self, text="➕ 记账", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=(16, 8))
    scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=20, pady=8)
    self.form = TransactionForm(scroll, self.app, on_save=self._on_saved)
    self.form.pack(fill="x", pady=8)
```

Replace with:
```python
def build(self):
    ctk.CTkLabel(self, text="➕ 记账", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=(16, 8))
    self.form = TransactionForm(self, self.app, on_save=self._on_saved)
    self.form.pack(fill="x", padx=20, pady=8)
```

Also need to make the category grid in `transaction_form.py` compact enough to fit without scrolling. The main issue is the category grid has 11 buttons × ~50px = potentially 3 rows. The buttons are 100×50. Reduce to 80×40 and arrange in a tighter grid.

- [ ] **Step 1: Modify add_page.py — remove CTkScrollableFrame**

Replace the build method in `ui/pages/add_page.py` to remove the scroll wrapper.

- [ ] **Step 2: Modify transaction_form.py — make category grid more compact**

In the `_populate_categories` method, change the category buttons to be more compact:

Change:
```python
btn = ctk.CTkButton(
    self.category_frame,
    text=f"{cat['icon']} {cat['name']}",
    width=100, height=50,
    ...
)
```
To:
```python
btn = ctk.CTkButton(
    self.category_frame,
    text=f"{cat['icon']} {cat['name']}",
    width=90, height=38,
    font=ctk.CTkFont(size=12),
    ...
)
```

Also reduce the grid padding from `padx=4, pady=4` to `padx=3, pady=3`.

And reduce the type selector button width from 120 to 100.

- [ ] **Step 3: Verify imports still work**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
uv run python -c "from ui.pages.add_page import AddPage; print('OK')"
```

Expected: OK

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "fix: remove scrollable frame from add page, compact category grid"
```

---

### Task 4: Fix Settings page scrollable areas

**Files:**
- Modify: `ui/pages/settings_page.py`

The Settings page wraps category and account lists in `CTkScrollableFrame`. With the default 17 categories + 4 accounts, the content fits. Replace the scrollable frames with regular frames.

- [ ] **Step 1: Replace CTkScrollableFrame with CTkFrame in settings tab**

In `_build_category_tab`, change:
```python
scroll = ctk.CTkScrollableFrame(self.cat_tab, fg_color="transparent")
scroll.pack(fill="both", expand=True)
self.cat_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
self.cat_list_frame.pack(fill="x")
```
To:
```python
self.cat_list_frame = ctk.CTkFrame(self.cat_tab, fg_color="transparent")
self.cat_list_frame.pack(fill="both", expand=True)
```

In `_build_account_tab`, change:
```python
scroll = ctk.CTkScrollableFrame(self.acc_tab, fg_color="transparent")
scroll.pack(fill="both", expand=True)
self.acc_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
self.acc_list_frame.pack(fill="x")
```
To:
```python
self.acc_list_frame = ctk.CTkFrame(self.acc_tab, fg_color="transparent")
self.acc_list_frame.pack(fill="both", expand=True)
```

- [ ] **Step 2: Verify import**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
uv run python -c "from ui.pages.settings_page import SettingsPage; print('OK')"
```

Expected: OK

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "fix: remove scrollable frames from settings page"
```

---

### Task 5: Add toast notifications to save operations

**Files:**
- Modify: `ui/widgets/transaction_form.py`
- Modify: `ui/pages/add_page.py`
- Modify: `ui/pages/bills_page.py`
- Modify: `ui/pages/settings_page.py`
- Modify: `ui/pages/budget_page.py`

This task wires success/failure toasts into all user actions across the app.

- [ ] **Step 1: Add success toast to TransactionForm save**

In `ui/widgets/transaction_form.py`, modify `_on_save_click`. After the successful save (after `add_transaction`/`update_transaction` but before `self.clear()`), show a success toast:

```python
from ui.widgets.toast import Toast

# After add_transaction or update_transaction succeeds:
action = "更新" if self._transaction_id else "保存"
Toast.show(self.winfo_toplevel(), f"{action}成功", success=True)
```

Add this right before `self.clear()` (around line 211).

- [ ] **Step 2: Add success toast in bills_page.py for delete**

In `ui/pages/bills_page.py`, modify `_delete_transaction`. After `delete_transaction(...)` succeeds (line 127), add a toast before destroying the dialog:

```python
from ui.widgets.toast import Toast
# After delete_transaction:
Toast.show(dialog.winfo_toplevel(), "删除成功", success=True)
```

- [ ] **Step 3: Add toasts in settings_page.py**

In `ui/pages/settings_page.py`, add toasts after these operations:
- After `add_category` or `update_category` succeeds: `Toast.show(dialog.winfo_toplevel(), "分类已保存", success=True)`
- After `delete_category` succeeds: `Toast.show(self.winfo_toplevel(), "分类已删除", success=True)`
- After `reset_to_defaults` succeeds: `Toast.show(self.winfo_toplevel(), "已恢复默认分类", success=True)`
- After `add_account` or `update_account` succeeds: `Toast.show(dialog.winfo_toplevel(), "账户已保存", success=True)`
- After `update_balance` succeeds: `Toast.show(self.winfo_toplevel(), "余额已更新", success=True)`
- After `delete_account` succeeds: `Toast.show(self.winfo_toplevel(), "账户已删除", success=True)`
- After CSV export succeeds: `Toast.show(self.winfo_toplevel(), f"已导出 {len(txs)} 条记录", success=True)`

Import at top of file:
```python
from ui.widgets.toast import Toast
```

- [ ] **Step 4: Add toast in budget_page.py**

In `ui/pages/budget_page.py`, add toasts:
- In the save function of `_add_budget_dialog`, after `set_budget`: `Toast.show(dialog.winfo_toplevel(), "预算已设置", success=True)`
- In `_edit_budget_amount`, after `set_budget`: `Toast.show(self.winfo_toplevel(), "预算已更新", success=True)`

Import:
```python
from ui.widgets.toast import Toast
```

- [ ] **Step 5: Run all tests to verify no regressions**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
uv run python -m pytest tests/ -v
```

Expected: 34 passed

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: add success toast notifications to all save/edit/delete operations"
```
