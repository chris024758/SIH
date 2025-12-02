# AquaLens

AquaLens is an embedded marine microscopy interface designed for Raspberry Pi–based imaging systems.  
It provides a CustomTkinter GUI for capturing, annotating, and storing plankton images, with a modular pipeline for preprocessing, inference, and postprocessing.

> Note: All ML components are currently **placeholders**. Hooks are in place for future detection, classification, and counting models.

---

## Features

- **Embedded GUI** using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Camera capture** via Picamera2 or OpenCV (with a graceful fallback placeholder)
- **Modular pipeline**: capture → preprocessing → inference → postprocessing
- **Results screens** for annotated image viewing and basic analytics UI
- **SQLite database** for samples, images, and detections
- **Config-driven** behavior via YAML & JSON
- **Logging** to a rotating log file
- Designed to be **Raspberry Pi friendly** (no heavy desktop frameworks)

---

## Project Structure

```text
AquaLens/
  app.py                # Main entrypoint

  core/
    capture.py          # CameraManager (Picamera2/OpenCV placeholder)
    preprocessing.py    # Preprocessor placeholder
    inference.py        # InferenceEngine placeholder
    postprocessing.py   # NMS / merging / counting placeholders
    manager.py          # PipelineManager (capture→pre→inference→post→DB)

  ui/
    main_window.py          # Main CustomTkinter window, navigation, status bars
    navigation_sidebar.py   # Sidebar navigation
    dashboard_screen.py     # Overview & KPI dashboard
    capture_screen.py       # Live preview, metadata, presets, capture controls
    results_screen.py       # Annotated image, species table, summary metrics
    settings_screen.py      # Camera/model/preprocessing/db settings tabs
    database_screen.py      # Sample browser, filters, details
    utils/
      styles.py             # Theme colors, button/card styles, badges
      image_utils.py        # PIL / numpy / ImageTk helpers
      dialogs.py            # Simple modal dialogs

  database/
    db.py               # SQLite wrapper (samples/images/detections)
    schema.sql          # DB schema

  config/
    settings.yaml       # Camera, preprocessing, inference, UI, DB settings
    species_mapping.json# Placeholder species list

  data/
    images_raw/         # Raw captured imagery
    images_annotated/   # Future annotated exports
    exports/            # CSV/JSON exports

  logs/
    aqulens.log         # Application log (created at runtime)
