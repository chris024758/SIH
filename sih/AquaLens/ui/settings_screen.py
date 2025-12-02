"""Settings screen with tabbed configuration panels."""

from __future__ import annotations

import customtkinter as ctk

from ui.utils import styles


class SettingsScreen(ctk.CTkFrame):
    """Tabbed interface for camera, model, preprocessing, and database tools."""

    def __init__(self, master, settings: dict | None = None, **kwargs):
        super().__init__(master, **kwargs)
        self.settings = settings or {}
        self._build()

    def _build(self) -> None:
        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)

        camera_tab = tabs.add("Camera Settings")
        model_tab = tabs.add("Model Settings")
        pre_tab = tabs.add("Preprocessing Options")
        db_tab = tabs.add("Database Tools")

        self._camera_tab(camera_tab)
        self._model_tab(model_tab)
        self._pre_tab(pre_tab)
        self._db_tab(db_tab)

    def _camera_tab(self, tab: ctk.CTkFrame) -> None:
        ctk.CTkLabel(tab, text="Resolution", font=("Calibri", 13, "bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkComboBox(tab, values=["640x480", "1280x720", "1920x1080"]).pack(
            anchor="w", padx=10
        )
        ctk.CTkLabel(tab, text="FPS", font=("Calibri", 13, "bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkSlider(tab, from_=5, to=60, number_of_steps=55).pack(fill="x", padx=10)
        ctk.CTkSwitch(tab, text="Auto Exposure", onvalue="auto", offvalue="manual").pack(
            anchor="w", padx=10, pady=5
        )

    def _model_tab(self, tab: ctk.CTkFrame) -> None:
        ctk.CTkLabel(tab, text="Model Path", font=("Calibri", 13, "bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkEntry(tab, placeholder_text="path/to/model.pt").pack(
            fill="x", padx=10, pady=5
        )
        ctk.CTkLabel(tab, text="Confidence Threshold", font=("Calibri", 13, "bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkSlider(tab, from_=0.1, to=0.99, number_of_steps=89).pack(
            fill="x", padx=10
        )
        ctk.CTkLabel(tab, text="NMS Threshold", font=("Calibri", 13, "bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkSlider(tab, from_=0.1, to=0.99, number_of_steps=89).pack(
            fill="x", padx=10
        )
        ctk.CTkLabel(tab, text="Model integration TODO", text_color="gray").pack(
            anchor="w", padx=10, pady=10
        )

    def _pre_tab(self, tab: ctk.CTkFrame) -> None:
        ctk.CTkSwitch(tab, text="Enable Denoise").pack(anchor="w", padx=10, pady=5)
        ctk.CTkSwitch(tab, text="Enable Normalization").pack(anchor="w", padx=10, pady=5)
        ctk.CTkSwitch(tab, text="Illumination Correction").pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(tab, text="Preprocessing placeholder; hooks pending integration").pack(
            anchor="w", padx=10, pady=10
        )

    def _db_tab(self, tab: ctk.CTkFrame) -> None:
        ctk.CTkLabel(tab, text="Backup Database").pack(anchor="w", padx=10, pady=5)
        backup_btn = ctk.CTkButton(tab, text="Export .db")
        styles.style_button(backup_btn, primary=False)
        backup_btn.pack(anchor="w", padx=10, pady=5)
        ctk.CTkButton(tab, text="Vacuum / Optimize").pack(anchor="w", padx=10, pady=5)
