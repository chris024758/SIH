"""Utilities to convert images between PIL, numpy, and Tk formats."""

from __future__ import annotations

from typing import Optional

import customtkinter as ctk
from PIL import Image, ImageTk

try:
    import numpy as np
except ImportError:
    np = None


def numpy_to_pil(array) -> Optional[Image.Image]:
    """Convert a numpy array to PIL Image if numpy is available."""
    if np is None:
        return None
    return Image.fromarray(array)


def pil_to_imagetk(image: Image.Image) -> ctk.CTkImage:
    """Wrap PIL Image for display in CustomTkinter."""
    return ctk.CTkImage(light_image=image, dark_image=image, size=image.size)


def resize_for_preview(image: Image.Image, max_size=(640, 480)) -> Image.Image:
    """Resize keeping aspect ratio for preview panels."""
    image.thumbnail(max_size)
    return image
