"""
ndwi.py
-------
NDWI (Normalized Difference Water Index) calculation and water-mask
generation.

    NDWI = (Green - NIR) / (Green + NIR)

This module is intentionally satellite-agnostic: it accepts plain
NumPy arrays for the Green and NIR bands. For the demo, those arrays
come from the synthetic sample dataset (see sample_data.py). For real
Sentinel-2 imagery later, the caller just needs to supply the Green
(B03) and NIR (B08) bands read via rasterio — nothing in this file
needs to change.
"""

from __future__ import annotations

import numpy as np


def calculate_ndwi(green_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
    """
    Compute the NDWI array from Green and NIR band arrays.

    Handles division-by-zero safely: pixels where (green + nir) == 0
    are assigned NDWI = 0 instead of raising or producing NaN/inf.

    Parameters
    ----------
    green_band, nir_band : np.ndarray
        Same-shape arrays of band reflectance/intensity values.

    Returns
    -------
    np.ndarray
        NDWI values in the range [-1, 1] (float64), same shape as input.
    """
    if green_band.shape != nir_band.shape:
        raise ValueError(
            f"green_band shape {green_band.shape} != nir_band shape {nir_band.shape}"
        )

    green = green_band.astype(np.float64)
    nir = nir_band.astype(np.float64)

    denominator = green + nir
    numerator = green - nir

    # Safe divide: where denominator is 0, result is 0 (no data / no signal)
    ndwi = np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator, dtype=np.float64),
        where=denominator != 0,
    )

    return ndwi


def create_water_mask(ndwi: np.ndarray, threshold: float = 0.0) -> np.ndarray:
    """
    Threshold an NDWI array into a binary water/land mask.

    Parameters
    ----------
    ndwi : np.ndarray
        NDWI array, as produced by ``calculate_ndwi``.
    threshold : float
        Pixels with NDWI > threshold are classified as water (1).
        Configurable because the "correct" threshold depends on the
        sensor/scene; 0.0 is a common default starting point.

    Returns
    -------
    np.ndarray
        Boolean/uint8-compatible mask, same shape as ``ndwi``.
        1 (True) = water, 0 (False) = land.
    """
    return (ndwi > threshold).astype(np.uint8)
