"""Preprocessing placeholders for AquaLens."""

from __future__ import annotations

from PIL import Image


class Preprocessor:
    """Placeholder preprocessing pipeline."""

    def __init__(self):
        pass

    def apply(self, image: Image.Image) -> Image.Image:
        """Placeholder for illumination correction, denoise, normalization."""
        # TODO: implement preprocessing steps (illumination correction, denoise, normalization)
        return image
