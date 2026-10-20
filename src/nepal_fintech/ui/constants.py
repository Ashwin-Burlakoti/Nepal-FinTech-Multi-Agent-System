"""Constants and shared configuration for the Flet UI."""

from __future__ import annotations

from nepal_fintech.config import settings

# Determine the API base URL from settings (allowing override in dev/prod)
API_BASE: str = (
    f"http://{settings.app_host}:{settings.app_port}/api"
    if settings.app_host != "0.0.0.0"
    else f"http://127.0.0.1:{settings.app_port}/api"
)
