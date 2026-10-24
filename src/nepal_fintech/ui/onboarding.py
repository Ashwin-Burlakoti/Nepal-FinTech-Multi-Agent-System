"""Onboarding view — income sources and portfolio split form."""

from __future__ import annotations

import re
from typing import Callable

import flet as ft
import httpx

from nepal_fintech.ui.constants import API_BASE
from nepal_fintech.ui.navigation import navigate_to

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class IncomeRowControls:
    """Controls for a single income source entry."""

    def __init__(self, on_remove: Callable[[], None] | None = None) -> None:
        self.on_remove = on_remove
        self.container: ft.Container | None = None

        self.income_type = ft.Dropdown(
            label="Type",
            width=140,
            options=[
                ft.DropdownOption("salary"),
                ft.DropdownOption("business"),
                ft.DropdownOption("rental"),
                ft.DropdownOption("capital_gains"),
                ft.DropdownOption("other"),
            ],
            value="salary",
        )
        self.income_amount = ft.TextField(
            label="Annual NPR",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="e.g. 500000",
        )
        self.remove_button = ft.IconButton(
            ft.Icons.DELETE_OUTLINE,
            tooltip="Remove Source",
            icon_color=ft.Colors.RED_400,
            on_click=self._handle_remove,
            visible=on_remove is not None,
        )
        self.income_desc = ft.TextField(
            label="Description",
            width=340,
            hint_text="e.g. Salary from employment",
        )

    def _handle_remove(self, e: ft.ControlEvent | None = None) -> None:
        if self.on_remove:
            self.on_remove()

    def build(self) -> ft.Container:
        self.container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [self.income_type, self.income_amount, self.remove_button],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self.income_desc,
                ],
                spacing=6,
            ),
            padding=8,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
            width=360,
        )
        return self.container


class OnboardingView:
    """Onboarding form: name, email, income sources, portfolio split, risk."""

    def __init__(self, page: ft.Page, state: dict) -> None:
        self.page = page
        self.state = state
        self.income_items: list[IncomeRowControls] = []
        self.income_container = ft.Column(spacing=8)
        self._init_controls()

    def _init_controls(self) -> None:
        self.name_field = ft.TextField(
            label="Full Name",
            width=360,
            hint_text="e.g. Ashwin Burlakoti",
        )
        self.email_field = ft.TextField(
            label="Email",
            width=360,
            hint_text="e.g. user@example.com",
            keyboard_type=ft.KeyboardType.EMAIL,
        )

        self._add_income_item()

        # Portfolio split sliders & live labels
        self.land_label = ft.Text("Land: 50%", size=14, weight=ft.FontWeight.W_500)
        self.land_slider = ft.Slider(
            min=0,
            max=100,
            value=50,
            divisions=20,
            label="{value}%",
            width=360,
            on_change=self._on_slider_change,
        )

        self.shares_label = ft.Text("Shares: 30%", size=14, weight=ft.FontWeight.W_500)
        self.shares_slider = ft.Slider(
            min=0,
            max=100,
            value=30,
            divisions=20,
            label="{value}%",
            width=360,
            on_change=self._on_slider_change,
        )

        self.cash_label = ft.Text("Cash: 20%", size=14, weight=ft.FontWeight.W_500)
        self.cash_slider = ft.Slider(
            min=0,
            max=100,
            value=20,
            divisions=20,
            label="{value}%",
            width=360,
            on_change=self._on_slider_change,
        )

        self.split_total_text = ft.Text(
            "Total: 100%", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN
        )

        self.risk_dropdown = ft.Dropdown(
            label="Risk Profile",
            width=360,
            options=[
                ft.DropdownOption("conservative"),
                ft.DropdownOption("moderate"),
                ft.DropdownOption("aggressive"),
            ],
            value="moderate",
        )
        self.status_text = ft.Text("", color=ft.Colors.RED, size=13)
        self.submit_btn = ft.FilledButton(
            "Start Advisory →",
            on_click=self._submit,
            width=360,
        )

    def _on_slider_change(self, e: ft.ControlEvent | None = None) -> None:
        land = int(round(self.land_slider.value or 0))
        shares = int(round(self.shares_slider.value or 0))
        cash = int(round(self.cash_slider.value or 0))
        total = land + shares + cash

        self.land_label.value = f"Land: {land}%"
        self.shares_label.value = f"Shares: {shares}%"
        self.cash_label.value = f"Cash: {cash}%"
        self.split_total_text.value = f"Total: {total}%"

        if total == 100:
            self.split_total_text.color = ft.Colors.GREEN
        else:
            self.split_total_text.color = ft.Colors.RED_600

        if self.page:
            self.page.update()

    def _auto_balance_split(self, e: ft.ControlEvent | None = None) -> None:
        """Adjust cash to bring the portfolio allocation to exactly 100%."""
        land = int(round(self.land_slider.value or 0))
        shares = int(round(self.shares_slider.value or 0))
        if land + shares <= 100:
            cash = 100 - (land + shares)
        else:
            total = land + shares
            land = int(round((land / total) * 70))
            shares = int(round((shares / total) * 30))
            cash = 100 - (land + shares)

        self.land_slider.value = float(land)
        self.shares_slider.value = float(shares)
        self.cash_slider.value = float(cash)
        self._on_slider_change()

    def _update_remove_buttons(self) -> None:
        can_remove = len(self.income_items) > 1
        for item in self.income_items:
            item.remove_button.visible = can_remove

    def _add_income_item(self, e: ft.ControlEvent | None = None) -> None:
        if len(self.income_items) >= 5:
            self.status_text.value = "Maximum of 5 income sources allowed"
            if self.page:
                self.page.update()
            return

        item = IncomeRowControls()
        item.on_remove = lambda it=item: self._remove_income_item(it)
        self.income_items.append(item)
        self.income_container.controls.append(item.build())
        self._update_remove_buttons()

        if e is not None and self.page:
            self.page.update()

    def _remove_income_item(self, item: IncomeRowControls) -> None:
        if len(self.income_items) <= 1:
            self.status_text.value = "At least one income source is required."
            if self.page:
                self.page.update()
            return

        if item in self.income_items:
            self.income_items.remove(item)
            if item.container and item.container in self.income_container.controls:
                self.income_container.controls.remove(item.container)

        self._update_remove_buttons()
        self.status_text.value = ""
        if self.page:
            self.page.update()

    def _submit(self, e: ft.ControlEvent) -> None:
        """Validate and submit onboarding data to the API."""
        name = (self.name_field.value or "").strip()
        if not name:
            name = "Investor"

        email = (self.email_field.value or "").strip()
        if not email:
            email = "user@example.com"
        elif not EMAIL_REGEX.match(email):
            self.status_text.color = ft.Colors.RED
            self.status_text.value = "Please enter a valid email address (e.g. user@example.com)"
            self.page.update()
            return

        land = float(round(self.land_slider.value or 0))
        shares = float(round(self.shares_slider.value or 0))
        cash = float(round(self.cash_slider.value or 0))
        total_split = land + shares + cash

        if abs(total_split - 100.0) > 0.01:
            self.status_text.color = ft.Colors.RED
            self.status_text.value = (
                f"Portfolio split must sum exactly to 100% (currently {int(total_split)}%)"
            )
            self.page.update()
            return

        incomes: list[dict] = []
        for idx, item in enumerate(self.income_items, start=1):
            raw_amt = (item.income_amount.value or "").replace(",", "").strip()
            if not raw_amt:
                continue

            try:
                amt = float(raw_amt)
            except ValueError:
                self.status_text.color = ft.Colors.RED
                self.status_text.value = (
                    f"Invalid amount in source #{idx}: '{raw_amt}' is not a valid number"
                )
                self.page.update()
                return

            if amt <= 0:
                self.status_text.color = ft.Colors.RED
                self.status_text.value = f"Amount in source #{idx} must be greater than 0"
                self.page.update()
                return

            source_type = item.income_type.value or "salary"
            desc = (item.income_desc.value or "").strip() or f"{source_type} income"
            incomes.append({
                "source_type": source_type,
                "annual_amount_npr": amt,
                "description": desc,
            })

        if not incomes:
            self.status_text.color = ft.Colors.RED
            self.status_text.value = (
                "Please enter at least one income source with an amount > 0"
            )
            self.page.update()
            return

        risk = self.risk_dropdown.value or "moderate"
        payload = {
            "name": name,
            "email": email,
            "income_sources": incomes,
            "portfolio_split": {
                "land_pct": land,
                "shares_pct": shares,
                "cash_pct": cash,
            },
            "risk_profile": risk,
        }

        self.status_text.color = ft.Colors.BLUE
        self.status_text.value = "Setting up your advisory account..."
        self.submit_btn.disabled = True
        self.page.update()

        try:
            resp = httpx.post(f"{API_BASE}/users/onboard", json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            self.state["user_id"] = data["user_id"]
            navigate_to(self.page, "/dashboard")
        except httpx.ConnectError:
            self.status_text.color = ft.Colors.RED
            self.status_text.value = f"Could not connect to backend server at {API_BASE}."
        except httpx.HTTPStatusError as exc:
            self.status_text.color = ft.Colors.RED
            try:
                err_data = exc.response.json()
                detail = err_data.get("detail", str(exc))
                if isinstance(detail, list):
                    msgs = [d.get("msg", str(d)) for d in detail]
                    self.status_text.value = f"Validation Error: {'; '.join(msgs)}"
                else:
                    self.status_text.value = f"Submission Error: {detail}"
            except Exception:
                self.status_text.value = f"Server Error ({exc.response.status_code})"
        except Exception as exc:
            self.status_text.color = ft.Colors.RED
            self.status_text.value = f"Error: {exc}"
        finally:
            self.submit_btn.disabled = False
            self.page.update()

    def build(self) -> ft.View:
        return ft.View(
            route="/",
            controls=[
                ft.AppBar(title=ft.Text("Welcome — Nepal FinTech AI")),
                ft.Column(
                    [
                        ft.Text("Onboarding", size=24, weight=ft.FontWeight.BOLD),
                        self.name_field,
                        self.email_field,
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.Text("Income Sources", size=16, weight=ft.FontWeight.BOLD),
                                ft.TextButton("+ Add Source", on_click=self._add_income_item),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            width=360,
                        ),
                        self.income_container,
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.Text("Portfolio Split", size=16, weight=ft.FontWeight.BOLD),
                                self.split_total_text,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            width=360,
                        ),
                        ft.Row(
                            [self.land_label],
                            width=360,
                        ),
                        self.land_slider,
                        ft.Row(
                            [self.shares_label],
                            width=360,
                        ),
                        self.shares_slider,
                        ft.Row(
                            [self.cash_label],
                            width=360,
                        ),
                        self.cash_slider,
                        ft.Row(
                            [
                                ft.TextButton(
                                    "⚡ Auto-balance to 100%",
                                    on_click=self._auto_balance_split,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            width=360,
                        ),
                        ft.Divider(),
                        self.risk_dropdown,
                        self.status_text,
                        self.submit_btn,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
        )
