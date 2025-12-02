"""Coordinator for the AquaLens processing pipeline."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

from core.capture import CameraManager
from core.inference import InferenceEngine
from core.postprocessing import count_per_species, merge_bounding_boxes, non_max_suppression
from core.preprocessing import Preprocessor
from database.db import Database


class PipelineManager:
    """Coordinate image capture, preprocessing, inference, and result packaging."""

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = settings or {}
        data_dir = Path(self.settings.get("data_dir", Path(__file__).resolve().parent.parent / "data"))
        self.camera = CameraManager(output_dir=data_dir / "images_raw")
        self.preprocessor = Preprocessor()
        self.inference_engine = InferenceEngine(model_path=self.settings.get("inference", {}).get("model_path"))
        self.database = Database(db_path=Path(self.settings.get("database", {}).get("path", data_dir / "aqulens.db")))
        self.logger.info("PipelineManager initialized")

    def capture_and_process(self) -> Dict[str, Any]:
        """Capture image, preprocess, run inference, and postprocess results."""
        image = self.camera.capture_image()
        if image is None:
            self.logger.error("Capture failed; no image to process")
            return {}

        processed = self.preprocessor.apply(image)
        inference_output = self.inference_engine.run(processed)
        detections = inference_output.get("detections", [])

        detections = non_max_suppression(detections, threshold=self.settings.get("inference", {}).get("nms_threshold", 0.4))
        detections = merge_bounding_boxes(detections)
        counts = count_per_species(detections)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "detections": detections,
            "counts": counts,
            "image": processed,
        }
        self.logger.debug("Pipeline result: %s", result)
        return result

    def save_results(self, sample_metadata: Dict[str, Any], results: Dict[str, Any]) -> None:
        """Persist sample, image, and detection metadata to SQLite."""
        image: Optional[Image.Image] = results.get("image")
        sample_id = self.database.insert_sample(sample_metadata)
        image_id = None
        if image:
            image_id = self.database.insert_image(sample_id=sample_id, image=image)
        for detection in results.get("detections", []):
            self.database.insert_detection(sample_id=sample_id, image_id=image_id, detection=detection)
        self.logger.info("Results saved for sample %s", sample_id)
