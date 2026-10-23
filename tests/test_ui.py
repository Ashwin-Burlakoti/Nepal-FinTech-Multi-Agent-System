"""Tests for Flet UI components and application runner."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from nepal_fintech.ui.app import start_ui
from nepal_fintech.ui.constants import API_BASE
from nepal_fintech.ui.onboarding import IncomeRowControls


def test_ui_api_base_configured() -> None:
    assert API_BASE.startswith("http")
    assert "/api" in API_BASE


def test_income_row_controls_build() -> None:
    controls = IncomeRowControls()
    container = controls.build()
    assert container is not None
    assert controls.income_type.value == "salary"


def test_start_ui_uses_ft_run_when_available() -> None:
    mock_run = MagicMock()
    with patch("nepal_fintech.ui.app.ft.run", mock_run, create=True):
        with patch("nepal_fintech.ui.app.hasattr", side_effect=lambda obj, attr: attr == "run"):
            start_ui()
            mock_run.assert_called_once()


def test_start_ui_falls_back_to_ft_app() -> None:
    mock_app = MagicMock()
    with patch("nepal_fintech.ui.app.ft.app", mock_app, create=True):
        with patch("nepal_fintech.ui.app.hasattr", side_effect=lambda obj, attr: attr == "app"):
            start_ui()
            mock_app.assert_called_once()


def test_start_ui_raises_when_neither_available() -> None:
    with patch("nepal_fintech.ui.app.hasattr", return_value=False):
        with pytest.raises(RuntimeError, match="Flet application runner not found"):
            start_ui()
