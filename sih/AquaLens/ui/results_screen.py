"""Results viewer screen."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import ttk

from ui.utils import styles


class ResultsScreen(ctk.CTkFrame):
    """Display annotated images and species statistics."""

    def __init__(self, master, host=None, **kwargs):
        super().__init__(master, **kwargs)
        self.host = host
        self.preview_image = None
        self.summary_labels = {}
        self.table = None
        self.bars_box = None
        self._build()
        self.update_summary({})

    def _build(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)

        image_frame = ctk.CTkFrame(self)
        styles.style_card(image_frame)
        image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(image_frame, text="Annotated Image", font=("Calibri", 16, "bold")).pack(
            anchor="w", padx=10, pady=6
        )
        self.image_label = ctk.CTkLabel(image_frame, text="No image loaded", width=640, height=480)
        self.image_label.pack(padx=10, pady=10)

        side_frame = ctk.CTkFrame(self, fg_color="transparent")
        side_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        side_frame.columnconfigure(0, weight=1)

        summary_frame = ctk.CTkFrame(side_frame)
        styles.style_summary_card(summary_frame)
        summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ctk.CTkLabel(summary_frame, text="Summary", font=("Calibri", 15, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=10, pady=6
        )
        metrics = ["Total detections", "Species detected", "Dominant species", "Mean confidence", "QC flag"]
        for idx, metric in enumerate(metrics, start=1):
            lbl_key = ctk.CTkLabel(summary_frame, text=metric, text_color="#9FB3C8")
            lbl_val = ctk.CTkLabel(summary_frame, text="—", font=("Calibri", 13, "bold"))
            lbl_key.grid(row=idx, column=0, sticky="w", padx=10, pady=2)
            lbl_val.grid(row=idx, column=1, sticky="e", padx=10, pady=2)
            self.summary_labels[metric] = lbl_val

        table_frame = ctk.CTkFrame(side_frame)
        styles.style_card(table_frame)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=4)
        ctk.CTkLabel(table_frame, text="Species Table", font=("Calibri", 15, "bold")).pack(
            anchor="w", padx=10, pady=6
        )
        self.table = ttk.Treeview(table_frame, columns=("species", "count", "relative", "confidence"), show="headings", height=6)
        self.table.heading("species", text="Species")
        self.table.heading("count", text="Count")
        self.table.heading("relative", text="Relative %")
        self.table.heading("confidence", text="Mean conf")
        self.table.column("species", width=120, anchor="w")
        self.table.column("count", width=60, anchor="center")
        self.table.column("relative", width=80, anchor="center")
        self.table.column("confidence", width=90, anchor="center")
        self.table.pack(fill="both", expand=True, padx=10, pady=6)

        bars_frame = ctk.CTkFrame(side_frame)
        styles.style_card(bars_frame)
        bars_frame.grid(row=2, column=0, sticky="nsew", pady=(4, 0))
        ctk.CTkLabel(bars_frame, text="Species Distribution", font=("Calibri", 15, "bold")).pack(
            anchor="w", padx=10, pady=6
        )
        self.bars_box = ctk.CTkTextbox(bars_frame, height=120)
        self.bars_box.insert("end", "No detections yet.")
        self.bars_box.configure(state="disabled")
        self.bars_box.pack(fill="both", expand=True, padx=10, pady=8)

        buttons_frame = ctk.CTkFrame(side_frame, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, sticky="ew", pady=6)
        for text in ["Export CSV", "Export JSON", "Save annotated image"]:
            btn = ctk.CTkButton(buttons_frame, text=text)
            styles.style_button(btn, primary=False)
            btn.pack(fill="x", pady=3)

    def update_summary(self, results: dict) -> None:
        """Update summary card with detection metrics."""
        detections = results.get("detections", []) or []
        counts = results.get("counts", {}) or {}
        total = len(detections)
        species_detected = len(counts.keys())
        dominant = max(counts, key=counts.get) if counts else "N/A"
        confidences = [d.get("confidence") for d in detections if d.get("confidence") is not None]
        mean_conf = sum(confidences) / len(confidences) if confidences else 0
        qc_flag = "OK" if total > 0 and mean_conf >= 0.5 else "Review"

        data = {
            "Total detections": total,
            "Species detected": species_detected,
            "Dominant species": dominant,
            "Mean confidence": f"{mean_conf:.2f}" if confidences else "N/A",
            "QC flag": qc_flag,
        }
        for key, label in self.summary_labels.items():
            label.configure(text=data.get(key, "—"))

    def update_species_table(self, counts: dict, confidences: dict | None = None) -> None:
        """Populate species table from counts/confidences."""
        if not self.table:
            return
        for row in self.table.get_children():
            self.table.delete(row)
        total = sum(counts.values()) if counts else 0
        for species, count in counts.items():
            rel = f"{(count / total * 100):.1f}%" if total else "0%"
            conf = confidences.get(species) if confidences else None
            conf_text = f"{conf:.2f}" if conf is not None else "N/A"
            self.table.insert("", "end", values=(species, count, rel, conf_text))

    def update_distribution_bars(self, counts: dict) -> None:
        """Render a text-based bar chart for species counts."""
        self.bars_box.configure(state="normal")
        self.bars_box.delete("1.0", "end")
        if not counts:
            self.bars_box.insert("end", "No detections yet.")
            self.bars_box.configure(state="disabled")
            return
        max_count = max(counts.values())
        for species, count in counts.items():
            bar_len = int((count / max_count) * 20) if max_count else 0
            bar = "█" * bar_len
            self.bars_box.insert("end", f"{species}: {bar} ({count})\n")
        self.bars_box.configure(state="disabled")
