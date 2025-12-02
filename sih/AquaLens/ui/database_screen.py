"""Database browser screen."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import ttk

from ui.utils import styles


class DatabaseScreen(ctk.CTkFrame):
    """Browse, export, and delete stored samples."""

    def __init__(self, master, database, host=None, **kwargs):
        super().__init__(master, **kwargs)
        self.database = database
        self.host = host
        self.samples_table = None
        self.details_box = None
        self.filter_from = ctk.StringVar()
        self.filter_to = ctk.StringVar()
        self.filter_operator = ctk.StringVar()
        self.filter_has_detections = ctk.BooleanVar(value=False)
        self._build()
        self.load_samples()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        sidebar = ctk.CTkFrame(self)
        styles.style_card(sidebar)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        sidebar.columnconfigure(0, weight=1)

        ctk.CTkLabel(sidebar, text="Filters", font=("Calibri", 15, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 4)
        )
        filters = ctk.CTkFrame(sidebar, fg_color="transparent")
        filters.grid(row=1, column=0, sticky="ew", padx=8)
        ctk.CTkLabel(filters, text="From (YYYY-MM-DD)").grid(row=0, column=0, sticky="w")
        ctk.CTkEntry(filters, textvariable=self.filter_from).grid(row=1, column=0, sticky="ew", pady=2)
        ctk.CTkLabel(filters, text="To (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ctk.CTkEntry(filters, textvariable=self.filter_to).grid(row=3, column=0, sticky="ew", pady=2)
        ctk.CTkLabel(filters, text="Operator").grid(row=4, column=0, sticky="w", pady=(6, 0))
        ctk.CTkEntry(filters, textvariable=self.filter_operator).grid(row=5, column=0, sticky="ew", pady=2)
        ctk.CTkCheckBox(filters, text="Has detections", variable=self.filter_has_detections).grid(
            row=6, column=0, sticky="w", pady=6
        )
        apply_btn = ctk.CTkButton(filters, text="Apply filters", command=self.load_samples)
        styles.style_button(apply_btn, primary=False)
        apply_btn.grid(row=7, column=0, pady=(4, 10), sticky="ew")
        filters.columnconfigure(0, weight=1)

        ctk.CTkLabel(sidebar, text="Samples", font=("Calibri", 15, "bold")).grid(
            row=2, column=0, sticky="w", padx=10, pady=6
        )
        self.samples_table = ttk.Treeview(
            sidebar,
            columns=("id", "date", "location", "operator", "images", "qc"),
            show="headings",
            height=12,
        )
        for col, text in [
            ("id", "Sample ID"),
            ("date", "Date"),
            ("location", "Location"),
            ("operator", "Operator"),
            ("images", "Images"),
            ("qc", "QC"),
        ]:
            self.samples_table.heading(col, text=text)
        self.samples_table.column("id", width=70, anchor="center")
        self.samples_table.column("date", width=100, anchor="center")
        self.samples_table.column("location", width=100, anchor="w")
        self.samples_table.column("operator", width=90, anchor="w")
        self.samples_table.column("images", width=60, anchor="center")
        self.samples_table.column("qc", width=60, anchor="center")
        self.samples_table.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.samples_table.bind("<<TreeviewSelect>>", self._on_select_sample)
        sidebar.rowconfigure(3, weight=1)

        content = ctk.CTkFrame(self)
        styles.style_card(content)
        content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(content, text="Details", font=("Calibri", 15, "bold")).pack(
            anchor="w", padx=10, pady=6
        )
        self.details_box = ctk.CTkTextbox(content, height=320)
        self.details_box.insert("end", "Select a sample to view details.")
        self.details_box.configure(state="disabled")
        self.details_box.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)
        for text in ["Delete sample", "Export sample", "Refresh"]:
            btn = ctk.CTkButton(btn_frame, text=text)
            styles.style_button(btn, primary=False)
            btn.pack(side="left", padx=5)

    def load_samples(self) -> None:
        """Populate sample list; TODO: fetch real filters from database."""
        # TODO: replace with real query using filters and SQLite
        placeholder_rows = [
            (1, "2025-12-02", "N/A", "N/A", 1, "OK"),
            (2, "2025-12-02", "Bay", "Op1", 2, "Review"),
        ]
        for row in self.samples_table.get_children():
            self.samples_table.delete(row)
        for row in placeholder_rows:
            self.samples_table.insert("", "end", values=row)

    def _on_select_sample(self, event) -> None:
        """Handle sample selection."""
        selection = self.samples_table.selection()
        if not selection:
            return
        values = self.samples_table.item(selection[0], "values")
        if not values:
            return
        sample_id = int(values[0])
        self.show_sample_details(sample_id)

    def show_sample_details(self, sample_id: int) -> None:
        """Fetch and display sample details."""
        details = self.database.get_sample_results(sample_id)
        self.details_box.configure(state="normal")
        self.details_box.delete("1.0", "end")
        self.details_box.insert("end", f"Sample metadata\n----------------\n{details.get('sample')}\n\n")
        self.details_box.insert("end", f"Images\n-------\n{details.get('images')}\n\n")
        self.details_box.insert("end", f"Detections summary\n-------------------\n{details.get('detections')}\n")
        self.details_box.configure(state="disabled")
        if self.host:
            self.host.set_status(f"Loaded sample {sample_id}")
