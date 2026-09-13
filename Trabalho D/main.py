"""Compatibility ASGI entrypoint. Business logic lives under app/."""

from app.main import app

__all__ = ["app"]
