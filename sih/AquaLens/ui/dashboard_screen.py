"""Dashboard placeholder screen."""

from __future__ import annotations

import customtkinter as ctk

from ui.utils import styles


class DashboardScreen(ctk.CTkFrame):
    """Simple dashboard summary panel."""

    def __init__(self, master, host=None, **kwargs):
        super().__init__(master, **kwargs)
        self.host = host
        self.kpi_labels = {}
        hero = ctk.CTkFrame(self, fg_color="#0F2435", corner_radius=14)
        hero.pack(fill="x", padx=14, pady=14)
        ctk.CTkLabel(hero, text="AquaLens Dashboard", font=("Calibri", 20, "bold")).pack(
            anchor="w", padx=12, pady=(12, 4)
        )
        ctk.CTkLabel(
            hero,
            text="System READY • Monitor captures, results, and database activity.",
            justify="left",
            text_color="#9FB3C8",
            font=("Calibri", 12),
        ).pack(anchor="w", padx=12, pady=(0, 12))

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=14, pady=6)
        for label in ["Captures today", "Samples stored", "Last capture", "Disk usage"]:
            card = ctk.CTkFrame(stats)
            styles.style_kpi_card(card)
            card.pack(side="left", expand=True, fill="both", padx=6)
            ctk.CTkLabel(card, text=label, text_color="#9FB3C8").pack(anchor="w", padx=12, pady=(10, 2))
            value_label = ctk.CTkLabel(card, text="—", font=("Calibri", 18, "bold"))
            value_label.pack(anchor="w", padx=12, pady=(0, 10))
            self.kpi_labels[label] = value_label

        activity = ctk.CTkFrame(self, fg_color="#0F2435", corner_radius=12)
        activity.pack(fill="x", padx=14, pady=10)
        ctk.CTkLabel(activity, text="Activity timeline (TODO)", text_color="#9FB3C8").pack(
            anchor="w", padx=12, pady=10
        )

        self.update_kpis(0, 0, "N/A", "N/A")

    def update_kpis(self, captures_today: int, samples_total: int, last_capture: str | None, disk_usage: str) -> None:
        """Refresh dashboard KPIs."""
        data = {
            "Captures today": captures_today,
            "Samples stored": samples_total,
            "Last capture": last_capture or "N/A",
            "Disk usage": disk_usage,
        }
        for key, label in self.kpi_labels.items():
            label.configure(text=str(data.get(key, "—")))
