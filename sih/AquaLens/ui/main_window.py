"""Main window for AquaLens."""

from __future__ import annotations

import datetime
import logging
from typing import Dict

import customtkinter as ctk

from ui.capture_screen import CaptureScreen
from ui.dashboard_screen import DashboardScreen
from ui.database_screen import DatabaseScreen
from ui.navigation_sidebar import NavigationSidebar
from ui.results_screen import ResultsScreen
from ui.settings_screen import SettingsScreen


class MainWindow(ctk.CTk):
    """Primary CustomTkinter application window."""

    def __init__(self, pipeline_manager, settings: Dict, theme: Dict):
        super().__init__()
        self.pipeline_manager = pipeline_manager
        self.settings = settings
        self.theme = theme
        self.logger = logging.getLogger(self.__class__.__name__)
        self.frames: Dict[str, ctk.CTkFrame] = {}
        self.status_bar_bottom = None
        self.camera_status = ctk.StringVar(value="Camera: Idle")
        self.time_var = ctk.StringVar(value="")
        self.status_message = ctk.StringVar(value="Ready")
        self.sample_context = ctk.StringVar(value="Sample: not set")
        self.step_labels: Dict[str, ctk.CTkLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        self.rowconfigure(2, weight=1)
        self.columnconfigure(1, weight=1)
        self.configure(fg_color=self.theme.get("background"))

        # Top status bar
        top_bar = ctk.CTkFrame(self, height=32, fg_color=self.theme.get("surface"))
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        ctk.CTkLabel(
            top_bar,
            text="AquaLens Marine Microscopy",
            font=(self.theme.get("font_family", "Calibri"), 16, "bold"),
        ).pack(side="left", padx=12, pady=6)
        status = ctk.CTkLabel(top_bar)
        status.pack(side="left", padx=8)
        status.configure(
            text="SYSTEM READY",
            fg_color=self.theme.get("primary_color"),
            corner_radius=999,
            padx=12,
            pady=4,
            font=(self.theme.get("font_family", "Calibri"), 11, "bold"),
        )
        ctk.CTkLabel(
            top_bar,
            textvariable=self.sample_context,
            text_color="#9FB3C8",
            font=(self.theme.get("font_family", "Calibri"), 11),
        ).pack(side="right", padx=12, pady=6)

        # Workflow stepper
        stepper = ctk.CTkFrame(self, fg_color=self.theme.get("background"))
        stepper.grid(row=1, column=0, columnspan=2, sticky="ew")
        steps = [
            ("setup", "1) Setup"),
            ("capture", "2) Capture"),
            ("review", "3) Review"),
            ("save", "4) Save / Export"),
        ]
        for idx, (key, label) in enumerate(steps):
            step_label = ctk.CTkLabel(
                stepper,
                text=label,
                padx=12,
                pady=6,
                font=(self.theme.get("font_family", "Calibri"), 12),
                fg_color=self.theme.get("surface"),
                corner_radius=8,
            )
            step_label.grid(row=0, column=idx, padx=4, pady=4, sticky="ew")
            stepper.columnconfigure(idx, weight=1)
            self.step_labels[key] = step_label

        # Sidebar
        sidebar = NavigationSidebar(self, on_nav=self.show_frame, theme=self.theme)
        sidebar.grid(row=2, column=0, sticky="ns")
        sidebar.configure(width=self.theme.get("sidebar_width", 200))

        # Content container
        container = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.theme.get("background"),
        )
        container.grid(row=2, column=1, sticky="nsew")

        # Screens
        self.frames["dashboard"] = DashboardScreen(container, host=self, fg_color=self.theme.get("background"))
        self.frames["capture"] = CaptureScreen(container, pipeline_manager=self.pipeline_manager, host=self, fg_color=self.theme.get("background"))
        self.frames["results"] = ResultsScreen(container, host=self, fg_color=self.theme.get("background"))
        self.frames["settings"] = SettingsScreen(container, settings=self.settings, fg_color=self.theme.get("background"))
        self.frames["database"] = DatabaseScreen(container, database=self.pipeline_manager.database, host=self, fg_color=self.theme.get("background"))

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("dashboard")

        # Bottom status bar
        bottom_bar = ctk.CTkFrame(self, height=28, fg_color=self.theme.get("surface"))
        bottom_bar.grid(row=3, column=0, columnspan=2, sticky="ew")
        ctk.CTkLabel(bottom_bar, textvariable=self.time_var).pack(
            side="left", padx=10, pady=2
        )
        ctk.CTkLabel(bottom_bar, textvariable=self.status_message).pack(
            side="left", padx=10, pady=2
        )
        ctk.CTkLabel(bottom_bar, textvariable=self.camera_status).pack(
            side="right", padx=10, pady=2
        )
        self._tick_clock()

    def _tick_clock(self) -> None:
        """Update timestamp in the status bar."""
        self.time_var.set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.after(1000, self._tick_clock)

    def show_frame(self, key: str) -> None:
        """Raise selected screen."""
        frame = self.frames.get(key)
        if not frame:
            self.logger.error("No frame registered for key %s", key)
            return
        frame.tkraise()
        self.logger.debug("Switched to frame %s", key)
        self._highlight_stepper(key)

    def _highlight_stepper(self, key: str) -> None:
        """Highlight workflow stepper based on active key."""
        mapping = {
            "dashboard": "setup",
            "settings": "setup",
            "capture": "capture",
            "results": "review",
            "database": "save",
        }
        active = mapping.get(key, "setup")
        for step_key, label in self.step_labels.items():
            if step_key == active:
                label.configure(fg_color=self.theme.get("primary_color"), corner_radius=8, text_color="white")
            else:
                label.configure(fg_color=self.theme.get("surface"), text_color=self.theme.get("text"))

    def set_sample_context(self, text: str) -> None:
        """Update sample context label."""
        self.sample_context.set(text)

    def set_status(self, message: str) -> None:
        """Update transient status message in the bottom bar."""
        self.status_message.set(message)
