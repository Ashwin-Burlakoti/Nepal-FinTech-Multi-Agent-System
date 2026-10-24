"""Flet app entry point — routing and bootstrap."""

from __future__ import annotations

import flet as ft

from nepal_fintech.ui.constants import API_BASE
from nepal_fintech.ui.dashboard import DashboardView
from nepal_fintech.ui.navigation import navigate_to
from nepal_fintech.ui.notifications import NotificationDrawer
from nepal_fintech.ui.onboarding import OnboardingView


def main(page: ft.Page) -> None:
    """Flet app main — configure page and set up routing."""
    page.title = "Nepal FinTech AI Advisory"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window.width = 420
    page.window.height = 780

    # Shared state
    state: dict = {"user_id": None, "api_base": API_BASE}

    # Notification drawer (shared across views)
    notif_drawer = NotificationDrawer(page, state)
    page.end_drawer = notif_drawer.drawer

    def route_change(e: ft.RouteChangeEvent | None = None) -> None:
        page.views.clear()
        if page.route == "/dashboard":
            page.views.append(DashboardView(page, state, notif_drawer).build())
        else:
            page.views.append(OnboardingView(page, state).build())
        page.update()

    def view_pop(e: ft.ViewPopEvent) -> None:
        page.views.pop()
        if page.views:
            top = page.views[-1]
            navigate_to(page, top.route)
        page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    navigate_to(page, page.route or "/")


def start_ui() -> None:
    """Launch the Flet app targeting web browser."""
    runner = getattr(ft, "run", None)
    if callable(runner):
        runner(main, view=ft.AppView.WEB_BROWSER, port=8550)
        return

    app_fn = getattr(ft, "app", None)
    if callable(app_fn):
        app_fn(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
        return

    import flet.app as ft_app

    if callable(getattr(ft_app, "run", None)):
        ft_app.run(main, view=ft.AppView.WEB_BROWSER, port=8550)
        return
    if callable(getattr(ft_app, "app", None)):
        ft_app.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
        return

    msg = "Flet application runner not found (neither ft.run nor ft.app is callable)"
    raise RuntimeError(msg)
