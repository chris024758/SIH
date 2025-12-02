"""Camera capture utilities for AquaLens."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from picamera2 import Picamera2  # type: ignore
except ImportError:
    Picamera2 = None

from PIL import Image


class CameraManager:
    """Manage camera preview and capture."""

    def __init__(self, output_dir: Optional[Path] = None, resolution=(1280, 720)):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.output_dir = Path(output_dir) if output_dir else None
        self.resolution = resolution
        self._camera = None
        self._capture_device = None
        self.logger.info("CameraManager initialized with resolution %s", resolution)

    def _init_camera(self) -> None:
        """Initialize camera using available backend."""
        if Picamera2 is not None:
            self._camera = Picamera2()
            config = self._camera.create_preview_configuration(
                main={"size": self.resolution}
            )
            self._camera.configure(config)
            self.logger.info("Picamera2 initialized")
        elif cv2 is not None:
            self._capture_device = cv2.VideoCapture(0)
            if not self._capture_device.isOpened():
                self.logger.error("Unable to open CV2 capture device")
            else:
                self._capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                self._capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                self.logger.info("OpenCV capture initialized")
        else:
            self.logger.warning("No camera backend available; running in placeholder mode")

    def start_preview(self) -> None:
        """Start camera preview (placeholder hooks)."""
        if self._camera is None and self._capture_device is None:
            self._init_camera()
        if self._camera:
            self._camera.start()
        self.logger.debug("Preview started")

    def capture_image(self) -> Optional[Image.Image]:
        """Capture a single frame and return as PIL Image."""
        if self._camera is None and self._capture_device is None:
            self._init_camera()

        if self._camera:
            frame = self._camera.capture_array()
            if frame is None:
                self.logger.error("Picamera2 returned no frame")
                return None
            image = Image.fromarray(frame)
        elif self._capture_device and cv2 is not None:
            ret, frame = self._capture_device.read()
            if not ret:
                self.logger.error("OpenCV failed to read frame")
                return None
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb_frame)
        else:
            self.logger.info("Placeholder capture used (blank image)")
            image = Image.new("RGB", self.resolution, color=(0, 92, 128))

        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            file_path = self.output_dir / "capture_placeholder.jpg"
            image.save(file_path)
            self.logger.info("Captured image saved to %s", file_path)

        return image

    def stop_preview(self) -> None:
        """Stop camera preview and release resources."""
        if self._camera:
            self._camera.stop()
            self._camera.close()
            self._camera = None
        if self._capture_device and cv2 is not None:
            self._capture_device.release()
            self._capture_device = None
        self.logger.debug("Preview stopped and resources released")
