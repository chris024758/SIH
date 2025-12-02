"""SQLite wrapper utilities for AquaLens."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from PIL import Image


class Database:
    """Lightweight SQLite helper for AquaLens data."""

    def __init__(self, db_path: Path):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_path = Path(db_path)
        self.schema_path = Path(__file__).resolve().parent / "schema.sql"
        self._ensure_database()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_database(self) -> None:
        """Initialize database from schema if empty."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn, self.schema_path.open("r", encoding="utf-8") as schema_file:
            conn.executescript(schema_file.read())
            conn.commit()
        self.logger.info("Database ready at %s", self.db_path)

    def insert_sample(self, metadata: Dict[str, Any]) -> int:
        """Insert a sample record and return its ID."""
        query = """
            INSERT INTO samples (timestamp, magnification, depth, operator, location, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (
            metadata.get("timestamp", datetime.utcnow().isoformat()),
            metadata.get("magnification"),
            metadata.get("depth"),
            metadata.get("operator"),
            metadata.get("location"),
            metadata.get("notes"),
        )
        with self._connect() as conn:
            cur = conn.execute(query, values)
            conn.commit()
            sample_id = cur.lastrowid
        self.logger.debug("Inserted sample %s", sample_id)
        return sample_id

    def insert_image(self, sample_id: int, image: Image.Image, filename: Optional[str] = None) -> int:
        """Insert an image blob tied to a sample."""
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
        filename = filename or f"sample_{sample_id}_{int(datetime.utcnow().timestamp())}.jpg"
        query = """
            INSERT INTO images (sample_id, data, filename, captured_at)
            VALUES (?, ?, ?, ?)
        """
        values = (sample_id, sqlite3.Binary(image_bytes), filename, datetime.utcnow().isoformat())
        with self._connect() as conn:
            cur = conn.execute(query, values)
            conn.commit()
            image_id = cur.lastrowid
        self.logger.debug("Inserted image %s for sample %s", image_id, sample_id)
        return image_id

    def insert_detection(self, sample_id: int, image_id: Optional[int], detection: Dict[str, Any]) -> int:
        """Insert detection metadata."""
        query = """
            INSERT INTO detections (sample_id, image_id, species, confidence, bbox)
            VALUES (?, ?, ?, ?, ?)
        """
        values = (
            sample_id,
            image_id,
            detection.get("species"),
            detection.get("confidence"),
            json.dumps(detection.get("bbox")),
        )
        with self._connect() as conn:
            cur = conn.execute(query, values)
            conn.commit()
            detection_id = cur.lastrowid
        self.logger.debug("Inserted detection %s for sample %s", detection_id, sample_id)
        return detection_id

    def get_sample_results(self, sample_id: int) -> Dict[str, Any]:
        """Fetch sample, images, and detections in a structured format."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            sample = conn.execute("SELECT * FROM samples WHERE id = ?", (sample_id,)).fetchone()
            images = conn.execute("SELECT id, filename, captured_at FROM images WHERE sample_id = ?", (sample_id,)).fetchall()
            detections = conn.execute("SELECT * FROM detections WHERE sample_id = ?", (sample_id,)).fetchall()

        return {
            "sample": dict(sample) if sample else None,
            "images": [dict(row) for row in images] if images else [],
            "detections": [dict(row) for row in detections] if detections else [],
        }
