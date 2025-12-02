"""Postprocessing placeholders for AquaLens."""

from __future__ import annotations

from typing import Any, Dict, List


def non_max_suppression(detections: List[Dict[str, Any]], threshold: float = 0.4):
    """Placeholder for NMS to reduce overlapping detections."""
    # TODO: implement NMS logic
    return detections


def merge_bounding_boxes(detections: List[Dict[str, Any]]):
    """Placeholder for merging overlapping bounding boxes."""
    # TODO: implement bounding box merging
    return detections


def count_per_species(detections: List[Dict[str, Any]]):
    """Placeholder for species counting aggregation."""
    # TODO: implement species-specific counting
    return {}
