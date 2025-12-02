"""Navigation sidebar for screen selection."""

from __future__ import annotations

from typing import Callable, Dict

import customtkinter as ctk

from ui.utils import styles


class NavigationSidebar(ctk.CTkFrame):
    """Vertical navigation sidebar."""

    def __init__(self, master, on_nav: Callable[[str], None], theme: Dict):
        super().__init__(master, fg_color=theme.get("background"))
        self.on_nav = on_nav
        self.theme = theme
        self.buttons = {}
        self._build()

    def _build(self) -> None:
        header = ctk.CTkFrame(self, fg_color=self.theme.get("surface"))
        header.pack(fill="x", padx=10, pady=(12, 6))
        logo = ctk.CTkLabel(
            header,
            text="🌊 AquaLens",
            font=(self.theme.get("font_family", "Calibri"), 18, "bold"),
            text_color=self.theme.get("text"),
        )
        logo.pack(anchor="w", padx=6, pady=4)
        version = ctk.CTkLabel(header, text="Microscopy UI", fg_color="#163659")
        version.pack(anchor="w", padx=6, pady=(0, 6))
        styles.badge(version, "Beta")

        sections = [
            ("Dashboard", "dashboard"),
            ("Capture", "capture"),
            ("Results", "results"),
            ("Settings", "settings"),
            ("Database", "database"),
        ]
        for label, key in sections:
            btn = ctk.CTkButton(
                self,
                text=label,
                command=lambda k=key: self.navigate(k),
                anchor="w",
                height=40,
            )
            styles.style_button(btn, primary=False)
            btn.pack(fill="x", padx=10, pady=5)
            self.buttons[key] = btn

    def navigate(self, key: str) -> None:
        """Trigger navigation and update active state."""
        for name, btn in self.buttons.items():
            if name == key:
                btn.configure(fg_color=self.theme.get("primary_color"))
            else:
                styles.style_button(btn, primary=False)
        self.on_nav(key)
