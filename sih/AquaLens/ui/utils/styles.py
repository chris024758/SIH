"""Theme and style utilities for AquaLens UI."""

from __future__ import annotations

from typing import Dict

import customtkinter as ctk


def apply_theme(ui_settings: Dict) -> Dict:
    """Merge default theme with overrides."""
    defaults = {
        "appearance_mode": "dark",
        "color_theme": "dark-blue",
        "primary_color": "#0FA3B1",
        "accent_color": "#1BA1E2",
        "surface": "#0E1F30",
        "panel": "#102A43",
        "background": "#091726",
        "text": "#E8F1F2",
        "muted": "#A6B8CC",
        "font_family": "Calibri",
        "mono_font": "Consolas",
        "default_size": "1200x800",
        "sidebar_width": 200,
    }
    merged = {**defaults, **(ui_settings or {})}
    ctk.set_default_color_theme(merged["color_theme"])
    return merged


def style_button(button: ctk.CTkButton, primary: bool = True) -> None:
    """Apply button styling."""
    if primary:
        button.configure(
            fg_color="#0FA3B1",
            hover_color="#1397A1",
            text_color="white",
            corner_radius=12,
            font=("Calibri", 13, "bold"),
        )
    else:
        button.configure(
            fg_color="#102A43",
            hover_color="#163659",
            text_color="#E8F1F2",
            corner_radius=10,
            font=("Calibri", 12),
        )


def style_card(frame: ctk.CTkFrame) -> None:
    """Apply card-like styling to frames."""
    frame.configure(
        corner_radius=14,
        fg_color="#102A43",
        border_width=1,
        border_color="#164769",
    )


def badge(widget, text: str, fg_color: str = "#1BA1E2") -> None:
    """Decorate a label-like widget as a pill badge."""
    widget.configure(
        text=text,
        fg_color=fg_color,
        corner_radius=999,
        padx=10,
        pady=4,
        font=("Calibri", 11, "bold"),
    )


def style_kpi_card(frame: ctk.CTkFrame) -> None:
    """Apply KPI card styling."""
    frame.configure(
        corner_radius=12,
        fg_color="#102A43",
        border_width=1,
        border_color="#164769",
        height=100,
    )


def style_summary_card(frame: ctk.CTkFrame) -> None:
    """Apply summary card styling."""
    frame.configure(
        corner_radius=12,
        fg_color="#0F2435",
        border_width=1,
        border_color="#164769",
    )
