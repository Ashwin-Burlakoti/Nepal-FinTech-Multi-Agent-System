"""Tests for Flet UI components and application runner."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from nepal_fintech.ui.app import main, start_ui
from nepal_fintech.ui.constants import API_BASE
from nepal_fintech.ui.navigation import navigate_to
from nepal_fintech.ui.onboarding import IncomeRowControls, OnboardingView


def test_ui_api_base_configured() -> None:
    assert API_BASE.startswith("http")
    assert "/api" in API_BASE


def test_income_row_controls_build() -> None:
    controls = IncomeRowControls()
    container = controls.build()
    assert container is not None
    assert controls.income_type.value == "salary"
    assert controls.remove_button.visible is False


def test_income_row_controls_with_on_remove() -> None:
    removed = False

    def on_rem() -> None:
        nonlocal removed
        removed = True

    controls = IncomeRowControls(on_remove=on_rem)
    controls.build()
    assert controls.remove_button.visible is True
    controls._handle_remove()
    assert removed is True


def test_onboarding_view_init_and_income_management() -> None:
    page = MagicMock()
    state: dict = {}
    view = OnboardingView(page, state)
    view.build()

    # Initially 1 income source, remove button should be hidden
    assert len(view.income_items) == 1
    assert view.income_items[0].remove_button.visible is False

    # Add 4 more sources -> total 5
    for _ in range(4):
        view._add_income_item(MagicMock())
    assert len(view.income_items) == 5
    # Remove buttons should now be visible on all items
    assert all(it.remove_button.visible for it in view.income_items)

    # Attempting to add a 6th source is capped
    view._add_income_item(MagicMock())
    assert len(view.income_items) == 5
    assert "Maximum" in view.status_text.value

    # Remove an item
    item_to_remove = view.income_items[2]
    view._remove_income_item(item_to_remove)
    assert len(view.income_items) == 4
    assert item_to_remove not in view.income_items


def test_onboarding_view_cannot_remove_last_income_item() -> None:
    page = MagicMock()
    view = OnboardingView(page, {})
    view.build()

    assert len(view.income_items) == 1
    view._remove_income_item(view.income_items[0])
    assert len(view.income_items) == 1
    assert "At least one income source is required" in view.status_text.value


def test_onboarding_slider_change_and_auto_balance() -> None:
    page = MagicMock()
    view = OnboardingView(page, {})
    view.build()

    # Move land slider to 60 (total 60 + 30 + 20 = 110)
    view.land_slider.value = 60.0
    view._on_slider_change()
    assert view.land_label.value == "Land: 60%"
    assert view.split_total_text.value == "Total: 110%"

    # Auto balance should bring it back to 100%
    view._auto_balance_split()
    total = (
        int(round(view.land_slider.value))
        + int(round(view.shares_slider.value))
        + int(round(view.cash_slider.value))
    )
    assert total == 100
    assert view.split_total_text.value == "Total: 100%"


def test_onboarding_validation_invalid_email() -> None:
    page = MagicMock()
    view = OnboardingView(page, {})
    view.build()

    view.email_field.value = "notanemail"
    view._submit(MagicMock())
    assert "valid email address" in view.status_text.value


def test_onboarding_validation_split_not_100() -> None:
    page = MagicMock()
    view = OnboardingView(page, {})
    view.build()

    view.land_slider.value = 70.0
    view._submit(MagicMock())
    assert "must sum exactly to 100%" in view.status_text.value


def test_onboarding_validation_invalid_amount() -> None:
    page = MagicMock()
    view = OnboardingView(page, {})
    view.build()

    view.income_items[0].income_amount.value = "invalid_number"
    view._submit(MagicMock())
    assert "not a valid number" in view.status_text.value


def test_onboarding_validation_no_incomes() -> None:
    page = MagicMock()
    view = OnboardingView(page, {})
    view.build()

    view.income_items[0].income_amount.value = ""
    view._submit(MagicMock())
    assert "Please enter at least one income source" in view.status_text.value


def test_onboarding_successful_submit(monkeypatch: pytest.MonkeyPatch) -> None:
    page = MagicMock()
    state: dict = {}
    view = OnboardingView(page, state)
    view.build()

    view.name_field.value = "Ashwin Burlakoti"
    view.email_field.value = "ashwin@example.com"
    view.income_items[0].income_amount.value = "1,200,000"
    view.income_items[0].income_desc.value = "Consulting"

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"user_id": 42, "message": "Success"}

    with patch("nepal_fintech.ui.onboarding.httpx.post", return_value=mock_resp):
        with patch("nepal_fintech.ui.onboarding.navigate_to") as mock_nav:
            view._submit(MagicMock())
            assert state.get("user_id") == 42
            mock_nav.assert_called_once_with(page, "/dashboard")


def test_start_ui_launches_flet_run(monkeypatch: pytest.MonkeyPatch) -> None:
    called_args: dict = {}

    def fake_run(target: callable, **kwargs) -> None:
        called_args["target"] = target
        called_args.update(kwargs)

    monkeypatch.setattr("nepal_fintech.ui.app.ft.run", fake_run)
    start_ui()

    assert called_args["target"] is main
    assert called_args.get("port") == 8550


def test_start_ui_fallback_to_callable_ft_app(monkeypatch: pytest.MonkeyPatch) -> None:
    called_args: dict = {}

    def fake_app(target: callable, **kwargs) -> None:
        called_args["target"] = target
        called_args.update(kwargs)

    monkeypatch.setattr("nepal_fintech.ui.app.ft.run", None)
    monkeypatch.setattr("nepal_fintech.ui.app.ft.app", fake_app)
    start_ui()

    assert called_args["target"] is main
    assert called_args.get("port") == 8550


def test_start_ui_raises_when_neither_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("nepal_fintech.ui.app.ft.run", None)
    monkeypatch.setattr("nepal_fintech.ui.app.ft.app", None)
    with patch("nepal_fintech.ui.app.getattr", return_value=None):
        with pytest.raises(RuntimeError, match="Flet application runner not found"):
            start_ui()


def test_navigate_to_uses_navigate() -> None:
    page = MagicMock(spec=["navigate"])
    navigate_to(page, "/dashboard")
    page.navigate.assert_called_once_with("/dashboard")


def test_navigate_to_falls_back_to_go() -> None:
    page = MagicMock(spec=["go"])
    navigate_to(page, "/dashboard")
    page.go.assert_called_once_with("/dashboard")


def test_navigate_to_falls_back_to_route_and_update() -> None:
    page = MagicMock(spec=["route", "update"])
    navigate_to(page, "/dashboard")
    assert page.route == "/dashboard"
    page.update.assert_called_once()


def test_app_main_bootstrap() -> None:
    page = MagicMock()
    page.route = "/"
    page.views = []
    main(page)
    assert page.title == "Nepal FinTech AI Advisory"
    assert page.on_route_change is not None
    assert page.on_view_pop is not None
