"""Main entry point for the AquaLens microscopy interface."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

import customtkinter as ctk

from core.manager import PipelineManager
from ui.main_window import MainWindow
from ui.utils import styles


BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "logs" / "aqulens.log"
SETTINGS_FILE = BASE_DIR / "config" / "settings.yaml"


def configure_logging() -> None:
    """Configure application-wide logging."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.info("Logging initialized")


def load_settings() -> Dict[str, Any]:
    """Load YAML settings with safe defaults when PyYAML is unavailable."""
    if not SETTINGS_FILE.exists() or yaml is None:
        logging.warning("Settings file missing or PyYAML unavailable; using defaults")
        return {}

    with SETTINGS_FILE.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
        logging.info("Settings loaded from %s", SETTINGS_FILE)
        return data


def global_exception_handler(exc_type, exc_value, exc_traceback) -> None:  # type: ignore
    """Log uncaught exceptions and exit gracefully."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.stderr.write("A fatal error occurred. See aqulens.log for details.\n")


def main() -> None:
    """Initialize CustomTkinter and start the main window."""
    configure_logging()
    sys.excepthook = global_exception_handler

    settings = load_settings()
    theme = styles.apply_theme(settings.get("ui", {}))

    ctk.set_appearance_mode(theme.get("appearance_mode", "system"))
    ctk.set_default_color_theme(theme.get("color_theme", "blue"))

    pipeline_manager = PipelineManager(settings=settings)

    app = MainWindow(
        pipeline_manager=pipeline_manager,
        settings=settings,
        theme=theme,
    )
    app.title("AquaLens Microscopy Interface")
    app.geometry(theme.get("default_size", "1200x800"))
    logging.info("Starting AquaLens UI")
    app.mainloop()


if __name__ == "__main__":
    main()
