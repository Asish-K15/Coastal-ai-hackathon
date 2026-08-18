"""
area_calculation.py
--------------------
Convert pixel counts from the change map into real-world areas and
percentage change.

Pixel area is NEVER assumed to be 1 sqm — it is passed in explicitly
(see utils.PipelineConfig.pixel_area_sqm), sourced today from a
documented demo value and, for real satellite data, intended to be
derived from raster metadata (resolution in the CRS transform).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from change_detection import EROSION, ACCRETION


@dataclass
class AreaStats:
    area_eroded_sqm: float
    area_accreted_sqm: float
    net_change_sqm: float
    percent_change: float


def calculate_areas(
    change_map: np.ndarray,
    before_mask: np.ndarray,
    pixel_area_sqm: float,
) -> AreaStats:
    """
    Compute erosion/accretion/net/percent statistics.

    Parameters
    ----------
    change_map : np.ndarray
        Output of change_detection.detect_change (0/1/2 encoding).
    before_mask : np.ndarray
        The "before" water mask (1=water, 0=land) — used to compute the
        baseline land area that percent_change is relative to.
    pixel_area_sqm : float
        Real-world area represented by a single pixel, in square metres.
        Must be > 0.

    Returns
    -------
    AreaStats
    """
    if pixel_area_sqm <= 0:
        raise ValueError("pixel_area_sqm must be > 0")

    eroded_pixels = int(np.count_nonzero(change_map == EROSION))
    accreted_pixels = int(np.count_nonzero(change_map == ACCRETION))

    area_eroded_sqm = eroded_pixels * pixel_area_sqm
    area_accreted_sqm = accreted_pixels * pixel_area_sqm
    net_change_sqm = area_accreted_sqm - area_eroded_sqm

    # Baseline: total LAND area at "before" date (land = mask value 0).
    before_land_pixels = int(np.count_nonzero(before_mask == 0))
    before_land_area_sqm = before_land_pixels * pixel_area_sqm

    if before_land_area_sqm > 0:
        percent_change = (net_change_sqm / before_land_area_sqm) * 100.0
    else:
        # Degenerate case (no land at all in the "before" scene).
        percent_change = 0.0

    return AreaStats(
        area_eroded_sqm=round(area_eroded_sqm, 2),
        area_accreted_sqm=round(area_accreted_sqm, 2),
        net_change_sqm=round(net_change_sqm, 2),
        percent_change=round(percent_change, 2),
    )
