"""Capture screen with live preview and metadata entry."""

from __future__ import annotations

import datetime
import logging

import customtkinter as ctk

from ui.utils import image_utils, styles


class CaptureScreen(ctk.CTkFrame):
    """Live capture interface."""

    def __init__(self, master, pipeline_manager, host=None, **kwargs):
        super().__init__(master, **kwargs)
        self.pipeline_manager = pipeline_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        self.host = host
        self.preview_image = None
        self.auto_save = ctk.BooleanVar(value=True)
        self.overlay_label = None
        self.toast_label = None
        self.preset_state = ctk.StringVar(value="Preset: Surface")
        self._build_layout()

    def _build_layout(self) -> None:
        header = ctk.CTkFrame(self, fg_color="#0F2435", corner_radius=12)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 2))
        ctk.CTkLabel(
            header,
            text="Capture & Annotate",
            font=("Calibri", 18, "bold"),
        ).pack(side="left", padx=12, pady=10)
        pulse = ctk.CTkLabel(header)
        pulse.pack(side="left", padx=6)
        styles.badge(pulse, "Live", fg_color="#0FA3B1")
        autosave_badge = ctk.CTkLabel(header)
        autosave_badge.pack(side="left", padx=6)
        styles.badge(autosave_badge, "Auto-save ON" if self.auto_save.get() else "Auto-save OFF", fg_color="#163659")

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)

        # Preview area
        preview_frame = ctk.CTkFrame(self)
        styles.style_card(preview_frame)
        preview_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(preview_frame, text="Live Preview", font=("Calibri", 16, "bold")).pack(
            anchor="w", padx=10, pady=6
        )
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="No feed",
            width=640,
            height=420,
            corner_radius=12,
            fg_color="#0B1826",
        )
        self.preview_label.pack(padx=10, pady=10)
        self.overlay_label = ctk.CTkLabel(
            preview_frame,
            text="Context: —",
            fg_color="#0F2435",
            corner_radius=8,
            padx=8,
            pady=4,
        )
        self.overlay_label.place(relx=0.02, rely=0.9)

        capture_btn = ctk.CTkButton(preview_frame, text="Capture Image", command=self.capture_image)
        styles.style_button(capture_btn, primary=True)
        capture_btn.pack(pady=10)

        # Metadata + controls
        side_panel = ctk.CTkFrame(self)
        styles.style_card(side_panel)
        side_panel.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(side_panel, text="Capture Metadata", font=("Calibri", 15, "bold")).pack(
            anchor="w", padx=10, pady=6
        )

        self.magnification = ctk.StringVar()
        self.depth = ctk.StringVar()
        self.operator = ctk.StringVar()
        self.location = ctk.StringVar()

        grid = ctk.CTkFrame(side_panel, fg_color="transparent")
        grid.pack(fill="x", padx=6, pady=4)
        entries = [
            ("Magnification", self.magnification),
            ("Depth", self.depth),
            ("Operator", self.operator),
            ("Location", self.location),
        ]
        for idx, (label, var) in enumerate(entries):
            col = idx % 2
            row = idx // 2
            cell = ctk.CTkFrame(grid, fg_color="transparent")
            cell.grid(column=col, row=row, padx=6, pady=6, sticky="ew")
            ctk.CTkLabel(cell, text=label).pack(anchor="w")
            ctk.CTkEntry(cell, textvariable=var).pack(fill="x")
            grid.columnconfigure(col, weight=1)

        toggle = ctk.CTkCheckBox(side_panel, text="Auto-save to database", variable=self.auto_save)
        toggle.pack(anchor="w", padx=10, pady=5)

        preset_frame = ctk.CTkFrame(side_panel, fg_color="transparent")
        preset_frame.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(preset_frame, text="Presets").pack(anchor="w")
        buttons = ctk.CTkFrame(preset_frame, fg_color="transparent")
        buttons.pack(fill="x", pady=4)
        for preset in ["Surface", "Mid-depth", "Deep"]:
            btn = ctk.CTkButton(buttons, text=preset, width=90, command=lambda p=preset: self._set_preset(p))
            styles.style_button(btn, primary=False)
            btn.pack(side="left", padx=4)
        ctk.CTkLabel(preset_frame, textvariable=self.preset_state, text_color="#9FB3C8").pack(
            anchor="w", pady=4
        )

        stats_frame = ctk.CTkFrame(side_panel, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(stats_frame, text="Camera FPS: ~30 (placeholder)").pack(anchor="w")
        ctk.CTkLabel(stats_frame, text="Storage: OK").pack(anchor="w")

        quality_frame = ctk.CTkFrame(side_panel, fg_color="transparent")
        quality_frame.pack(fill="x", padx=10, pady=6)
        ctk.CTkLabel(quality_frame, text="Capture Quality", font=("Calibri", 13, "bold")).pack(anchor="w")
        self.exposure_label = ctk.CTkLabel(quality_frame, text="Exposure: — ms")  # TODO wire to camera stats
        self.gain_label = ctk.CTkLabel(quality_frame, text="Gain: —")  # TODO wire to camera stats
        self.sharpness_label = ctk.CTkLabel(quality_frame, text="Sharpness: —")  # TODO compute focus metric
        self.brightness_label = ctk.CTkLabel(quality_frame, text="Brightness: [■■■■■■■■■■]")  # TODO real indicator
        for widget in [self.exposure_label, self.gain_label, self.sharpness_label, self.brightness_label]:
            widget.pack(anchor="w")

    def capture_image(self) -> None:
        """Capture via pipeline manager and update preview."""
        result = self.pipeline_manager.capture_and_process()
        image = result.get("image")
        if image:
            preview = image_utils.resize_for_preview(image.copy())
            self.preview_image = image_utils.pil_to_imagetk(preview)
            self.preview_label.configure(image=self.preview_image, text="")
            self._update_overlay()
            self._show_toast("Captured sample")
            if self.host:
                self.host.set_status("Captured frame")
        else:
            self.preview_label.configure(text="Capture failed")
            if self.host:
                self.host.set_status("Capture failed")
            return

        if self.auto_save.get():
            metadata = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "magnification": self.magnification.get(),
                "depth": self.depth.get(),
                "operator": self.operator.get(),
                "location": self.location.get(),
            }
            self.pipeline_manager.save_results(metadata, result)
            self.logger.info("Capture saved with metadata %s", metadata)
            if self.host:
                self.host.set_status("Captured frame and saved sample")
                self.host.set_sample_context(f"Sample: {metadata.get('location') or 'N/A'} @ {metadata.get('magnification') or '—'}")

    def _set_preset(self, preset: str) -> None:
        """Update preset state; TODO: wire to camera settings."""
        self.preset_state.set(f"Preset: {preset}")
        # TODO: apply actual camera parameters for presets

    def _update_overlay(self) -> None:
        """Update overlay label with context."""
        text = f"{self.magnification.get() or '—'} | {self.location.get() or '—'} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        if self.overlay_label:
            self.overlay_label.configure(text=text)

    def _show_toast(self, message: str) -> None:
        """Display a brief toast in the preview area."""
        if self.toast_label is None:
            self.toast_label = ctk.CTkLabel(
                self.preview_label.master,
                fg_color="#0FA3B1",
                text_color="white",
                corner_radius=8,
                padx=10,
                pady=6,
            )
        self.toast_label.configure(text=message)
        self.toast_label.place(relx=0.7, rely=0.08)
        self.after(1500, lambda: self.toast_label.place_forget())
