"""Uvicorn entrypoint. Application composition lives in application.py."""

try:
	from .application import app
except ImportError:
	import sys
	from pathlib import Path

	sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
	from app.application import app

__all__ = ["app"]
