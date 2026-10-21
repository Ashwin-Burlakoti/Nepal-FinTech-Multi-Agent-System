"""Onboarding view — income sources and portfolio split form."""

from __future__ import annotations

import flet as ft
import httpx

from nepal_fintech.ui.constants import API_BASE


class IncomeRowControls:
    """Controls for a single income source entry."""

    def __init__(self, on_remove: callable | None = None) -> None:
        self.income_type = ft.Dropdown(
            label="Type",
            width=160,
            options=[
                ft.dropdown.Option("salary"),
                ft.dropdown.Option("business"),
                ft.dropdown.Option("rental"),
                ft.dropdown.Option("capital_gains"),
                ft.dropdown.Option("other"),
            ],
            value="salary",
        )
        self.income_amount = ft.TextField(
            label="Annual NPR", width=160, keyboard_type=ft.KeyboardType.NUMBER
        )
        self.income_desc = ft.TextField(label="Description", width=330)
        self.on_remove = on_remove

    def build(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row([self.income_type, self.income_amount], spacing=10),
                    self.income_desc,
                ],
                spacing=6,
            ),
            padding=6,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
        )


class OnboardingView:
    """Onboarding form: name, email, income sources, portfolio split, risk."""

    def __init__(self, page: ft.Page, state: dict) -> None:
        self.page = page
        self.state = state
        self.income_items: list[IncomeRowControls] = []
        self.income_container = ft.Column(spacing=8)
        self._init_controls()

    def _init_controls(self) -> None:
        self.name_field = ft.TextField(label="Full Name", width=360)
        self.email_field = ft.TextField(label="Email", width=360)
        self._add_income_item()

        self.land_slider = ft.Slider(
            min=0, max=100, value=50, divisions=20, label="Land {value}%", width=340
        )
        self.shares_slider = ft.Slider(
            min=0, max=100, value=30, divisions=20, label="Shares {value}%", width=340
        )
        self.cash_slider = ft.Slider(
            min=0, max=100, value=20, divisions=20, label="Cash {value}%", width=340
        )
        self.risk_dropdown = ft.Dropdown(
            label="Risk Profile",
            width=360,
            options=[
                ft.dropdown.Option("conservative"),
                ft.dropdown.Option("moderate"),
                ft.dropdown.Option("aggressive"),
            ],
            value="moderate",
        )
        self.status_text = ft.Text("", color=ft.Colors.RED)

    def _add_income_item(self, e: ft.ControlEvent | None = None) -> None:
        if len(self.income_items) >= 5:
            return
        item = IncomeRowControls()
        self.income_items.append(item)
        self.income_container.controls.append(item.build())
        if e is not None:
            self.page.update()

    def _submit(self, e: ft.ControlEvent) -> None:
        """Validate and submit onboarding data to the API."""
        land = self.land_slider.value or 0
        shares = self.shares_slider.value or 0
        cash = self.cash_slider.value or 0
        if abs(land + shares + cash - 100) > 1:
            self.status_text.value = f"Portfolio must sum to 100% (got {land+shares+cash}%)"
            self.page.update()
            return

        incomes = []
        for item in self.income_items:
            amt_str = (item.income_amount.value or "0").strip()
            amt = float(amt_str) if amt_str else 0.0
            if amt > 0:
                incomes.append({
                    "source_type": item.income_type.value,
                    "annual_amount_npr": amt,
                    "description": item.income_desc.value or f"{item.income_type.value} income",
                })

        if not incomes:
            self.status_text.value = "Please enter at least one income source with amount > 0"
            self.page.update()
            return

        payload = {
            "name": self.name_field.value or "Investor",
            "email": self.email_field.value or "user@example.com",
            "income_sources": incomes,
            "portfolio_split": {
                "land_pct": land,
                "shares_pct": shares,
                "cash_pct": cash,
            },
            "risk_profile": self.risk_dropdown.value,
        }
        try:
            resp = httpx.post(f"{API_BASE}/users/onboard", json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self.state["user_id"] = data["user_id"]
            self.page.go("/dashboard")
        except Exception as exc:
            self.status_text.value = f"Error: {exc}"
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
                        ft.Text("Portfolio Split (must total 100%)", size=16),
                        ft.Text("Land %"),
                        self.land_slider,
                        ft.Text("Shares %"),
                        self.shares_slider,
                        ft.Text("Cash %"),
                        self.cash_slider,
                        ft.Divider(),
                        self.risk_dropdown,
                        self.status_text,
                        ft.FilledButton(
                            "Start Advisory →",
                            on_click=self._submit,
                            width=360,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
        )
