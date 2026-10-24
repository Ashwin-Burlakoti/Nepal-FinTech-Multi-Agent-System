"""UI navigation helper across Flet versions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import flet as ft


def navigate_to(page: ft.Page, route: str) -> None:
    """Navigate to a route compatible with Flet 1.0+ (page.navigate) and Flet 0.x (page.go)."""
    if hasattr(page, "navigate"):
        page.navigate(route)
    elif hasattr(page, "go"):
        getattr(page, "go")(route)  # noqa: B009
    else:
        page.route = route
        page.update()
