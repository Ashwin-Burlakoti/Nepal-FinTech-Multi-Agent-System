"""Expandable notification drawer — shows agent outputs with full debate."""

from __future__ import annotations

import flet as ft
import httpx

from nepal_fintech.ui.constants import API_BASE


class NotificationDrawer:
    """Side drawer that lists notifications with expandable triad debates."""

    def __init__(self, page: ft.Page, state: dict) -> None:
        self.page = page
        self.state = state
        self.drawer = ft.NavigationDrawer(controls=[], position=ft.NavigationDrawerPosition.END)
        self._notif_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=4)

    def refresh(self) -> None:
        """Fetch notifications from API and rebuild the drawer."""
        user_id = self.state.get("user_id", 1)
        try:
            resp = httpx.get(
                f"{API_BASE}/notifications/",
                params={"user_id": user_id},
                timeout=10,
            )
            resp.raise_for_status()
            notifications = resp.json()
        except Exception:
            notifications = []

        self._notif_list.controls.clear()
        if not notifications:
            self._notif_list.controls.append(ft.Text("No notifications yet."))
        else:
            for n in notifications:
                self._notif_list.controls.append(self._build_tile(n))

        self.drawer.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Notifications",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    self._notif_list,
                ]),
                padding=16,
                width=380,
            ),
        ]

    def _build_tile(self, notif: dict) -> ft.ExpansionTile:
        """Build an expandable tile for a single notification."""
        agent = notif.get("agent_type", "unknown")
        title = notif.get("short_title", "Untitled")
        is_read = notif.get("is_read", False)
        notif_id = notif.get("id")

        # Thinker section
        thinker = notif.get("thinker_points", {})
        thinker_text = thinker.get("thesis", "N/A") if isinstance(thinker, dict) else str(thinker)
        thinker_points = thinker.get("key_points", []) if isinstance(thinker, dict) else []

        # Critique section
        critique = notif.get("critique_risks", {})
        objections = critique.get("objections", []) if isinstance(critique, dict) else []
        risk_flags = critique.get("risk_flags", []) if isinstance(critique, dict) else []

        # Judge section
        verdict = notif.get("judge_verdict", "N/A")
        citations = notif.get("citations", [])

        def mark_read(e: ft.ControlEvent) -> None:
            if notif_id and not is_read:
                try:
                    httpx.patch(
                        f"{API_BASE}/notifications/{notif_id}/read",
                        timeout=5,
                    )
                except Exception:
                    pass

        return ft.ExpansionTile(
            title=ft.Text(
                f"[{agent}] {title}",
                weight=ft.FontWeight.BOLD if not is_read else ft.FontWeight.NORMAL,
                size=14,
            ),
            subtitle=ft.Text(notif.get("action_summary", "")[:80], size=12),
            on_change=mark_read,
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text("🧠 Thinker", weight=ft.FontWeight.BOLD),
                        ft.Text(thinker_text, size=12),
                        *[ft.Text(f"  • {p}", size=11) for p in thinker_points[:5]],
                        ft.Divider(),
                        ft.Text("⚔️ Critique", weight=ft.FontWeight.BOLD),
                        *[ft.Text(f"  ⚠ {o}", size=11) for o in objections[:5]],
                        *[ft.Text(f"  🚩 {r}", size=11, color=ft.Colors.RED) for r in risk_flags[:3]],
                        ft.Divider(),
                        ft.Text("⚖️ Judge Verdict", weight=ft.FontWeight.BOLD),
                        ft.Text(verdict, size=12),
                        ft.Divider(),
                        ft.Text("📎 Citations", weight=ft.FontWeight.BOLD),
                        *[
                            ft.TextButton(c, url=c if c.startswith("http") else None)
                            for c in citations[:5]
                        ],
                    ]),
                    padding=ft.padding.only(left=16, right=8, bottom=8),
                ),
            ],
        )
