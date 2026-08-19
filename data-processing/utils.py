"""
utils.py
--------
Shared configuration, path helpers, and small IO utilities used across the
CoastalVision AI data-processing pipeline.

Nothing in this file is satellite-specific: it should keep working
unchanged once real Sentinel-2 (or other) imagery replaces the synthetic
sample data.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
SAMPLE_DIR = os.path.join(DATA_DIR, "sample")
PRIMARY_DIR = os.path.join(DATA_DIR, "primary")
BACKUP_DIR = os.path.join(DATA_DIR, "backup")
OUTPUTS_DIR = os.path.join(REPO_ROOT, "outputs")
INTEGRATION_DIR = os.path.join(REPO_ROOT, "integration")


def ensure_dir(path: str) -> str:
    """Create ``path`` (and parents) if it does not exist. Returns path."""
    os.makedirs(path, exist_ok=True)
    return path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# All "magic numbers" for the demo live here so they are easy to find and
# change instead of being buried inside pipeline logic.


@dataclass
class PipelineConfig:
    # --- AOI / dataset metadata (demo values — replace with real values) ---
    aoi_name: str = "Primary Coastal AOI"
    date_before: str = "2020-12-28"
    date_after: str = "2025-01-16"
    data_source: str = "Copernicus Sentinel-2 L2A"

    # --- NDWI ---
    ndwi_threshold: float = 0.0  # pixels with NDWI > threshold => water

    # --- Geometry ---
    # For the synthetic demo we assume a fixed pixel resolution.
    # For real satellite data this should be derived from raster metadata
    # (see mask_generation.load_bands / rasterio transform) instead of
    # being hard-coded.
    pixel_resolution_m: float = 10.0  # metres per pixel edge

    @property
    def pixel_area_sqm(self) -> float:
        return self.pixel_resolution_m ** 2

    # --- Risk classification thresholds ---
    # abs(percent_change) <= low_max_pct        -> Low
    # low_max_pct < abs(percent_change) <= medium_max_pct -> Medium
    # abs(percent_change) > medium_max_pct       -> High
    risk_low_max_pct: float = 2.0
    risk_medium_max_pct: float = 6.0

    def as_dict(self) -> dict:
        d = asdict(self)
        d["pixel_area_sqm"] = self.pixel_area_sqm
        return d


DEFAULT_CONFIG = PipelineConfig()


# ---------------------------------------------------------------------------
# Small IO helpers
# ---------------------------------------------------------------------------


def save_binary_mask_png(mask: np.ndarray, path: str) -> None:
    """Save a 0/1 (or bool) array as a black/white PNG."""
    arr = (mask.astype(np.uint8) * 255)
    Image.fromarray(arr, mode="L").save(path)


def save_rgb_png(rgb: np.ndarray, path: str) -> None:
    """Save an (H, W, 3) uint8 array as an RGB PNG."""
    Image.fromarray(rgb.astype(np.uint8), mode="RGB").save(path)


def write_json(data: dict, path: str) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def read_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def load_band_png(path: str) -> np.ndarray:
    """Load a single-channel band image (PNG/etc.) as a float64 array."""
    img = Image.open(path).convert("L")
    return np.asarray(img, dtype=np.float64)
