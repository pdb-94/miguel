"""Minimal Report implementation for MiGUEL

This lightweight stub provides a small Report class so the rest of the
project can import `report.report.Report` without requiring the full
reporting dependencies while we get the project back to a runnable state.
"""
from typing import Any


class Report:
    """Simple Report placeholder used by the codebase.

    The real project provides many features (PDF, TXT, plots). This stub
    supplies the basic interface used elsewhere so imports succeed.
    """

    def __init__(self, env: Any = None):
        self.env = env

    def create_pdf(self, *args, **kwargs):
        """Placeholder for PDF generation."""
        return None

    def create_txt(self, *args, **kwargs):
        """Placeholder for TXT export."""
        return None

    def create_map(self, *args, **kwargs):
        """Placeholder for map generation."""
        return None

    def create_plot(self, *args, **kwargs):
        """Placeholder for plotting."""
        return None

    def summary(self) -> str:
        """Return a short summary string for quick inspection."""
        return f"Report(env={type(self.env).__name__})"
