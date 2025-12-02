"""Reusable dialog helpers for AquaLens."""

from __future__ import annotations

import customtkinter as ctk


def info(message: str, title: str = "Info") -> None:
    """Show an informational modal."""
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    ctk.CTkLabel(dialog, text=message, wraplength=400).pack(padx=20, pady=20)
    ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)


def error(message: str, title: str = "Error") -> None:
    """Show an error modal."""
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    ctk.CTkLabel(dialog, text=message, wraplength=400, text_color="red").pack(
        padx=20, pady=20
    )
    ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(pady=10)


def confirm(message: str, title: str = "Confirm") -> bool:
    """Display confirmation dialog; return True when accepted."""
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    response = {"confirmed": False}

    def on_confirm():
        response["confirmed"] = True
        dialog.destroy()

    ctk.CTkLabel(dialog, text=message, wraplength=400).pack(padx=20, pady=20)
    button_frame = ctk.CTkFrame(dialog)
    button_frame.pack(pady=10)
    ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy).pack(
        side="left", padx=5
    )
    ctk.CTkButton(button_frame, text="Confirm", command=on_confirm).pack(
        side="left", padx=5
    )
    dialog.wait_window()
    return response["confirmed"]
