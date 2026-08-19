"""
mask_generation.py
-------------------
Helpers for turning raw band arrays (or pre-made band PNGs) into the
before/after water masks used by the change-detection stage.

This module wraps ndwi.py with a small amount of file-IO convenience so
pipeline.py stays readable. It does not know anything about the *source*
of the bands (synthetic sample vs. real Sentinel-2 raster) — that
distinction lives in sample_data.py today, and would live in a future
`satellite_loader.py` for real imagery.
"""

from __future__ import annotations

import os
from typing import Tuple

import numpy as np
import rasterio

from ndwi import calculate_ndwi, create_water_mask
from utils import save_binary_mask_png


def generate_mask_from_bands(
    green_band: np.ndarray,
    nir_band: np.ndarray,
    threshold: float = 0.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Full Green/NIR -> (ndwi, water_mask) convenience wrapper.

    Returns
    -------
    (ndwi, water_mask) : tuple of np.ndarray
    """
    ndwi = calculate_ndwi(green_band, nir_band)
    water_mask = create_water_mask(ndwi, threshold=threshold)
    return ndwi, water_mask


def save_mask(mask: np.ndarray, out_path: str) -> str:
    """Save a binary mask as a PNG and return the path."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    save_binary_mask_png(mask, out_path)
    return out_path


def load_bands(green_path: str, nir_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load Sentinel-2 Green (B03) and NIR (B08) GeoTIFF bands.

    Both rasters must have the same shape and spatial grid.
    """
    with rasterio.open(green_path) as green_src:
        green = green_src.read(1).astype(np.float64)
        green_shape = green_src.shape
        green_transform = green_src.transform
        green_crs = green_src.crs

    with rasterio.open(nir_path) as nir_src:
        nir = nir_src.read(1).astype(np.float64)
        nir_shape = nir_src.shape
        nir_transform = nir_src.transform
        nir_crs = nir_src.crs

    if green_shape != nir_shape:
        raise ValueError(
            f"Green shape {green_shape} != NIR shape {nir_shape}"
        )

    if green_transform != nir_transform:
        raise ValueError("Green and NIR rasters have different spatial transforms")

    if green_crs != nir_crs:
        raise ValueError("Green and NIR rasters have different CRS")

    return green, nir