"""
change_detection.py
--------------------
Pixel-level comparison of the "before" and "after" water masks.

Encoding (see SCHEMA.md, kept in sync with this constant set):

    0 = no change   (Land->Land or Water->Water)
    1 = erosion     (Land->Water)
    2 = accretion   (Water->Land)

Mask convention (matches ndwi.create_water_mask): 1 = water, 0 = land.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

NO_CHANGE = 0
EROSION = 1
ACCRETION = 2


def detect_change(before_mask: np.ndarray, after_mask: np.ndarray) -> np.ndarray:
    """
    Compare two binary water masks (1=water, 0=land) and classify each
    pixel as no-change / erosion / accretion.

    Parameters
    ----------
    before_mask, after_mask : np.ndarray
        Binary (0/1) arrays of identical shape.

    Returns
    -------
    np.ndarray (same shape, dtype=uint8)
        0 = no change, 1 = erosion (land->water), 2 = accretion (water->land)
    """
    if before_mask.shape != after_mask.shape:
        raise ValueError(
            f"before_mask shape {before_mask.shape} != after_mask shape {after_mask.shape}"
        )

    before = before_mask.astype(bool)
    after = after_mask.astype(bool)

    change_map = np.full(before.shape, NO_CHANGE, dtype=np.uint8)

    # Land (False) -> Water (True) = erosion
    change_map[(~before) & after] = EROSION

    # Water (True) -> Land (False) = accretion
    change_map[before & (~after)] = ACCRETION

    # Land->Land and Water->Water pixels remain NO_CHANGE by construction.
    return change_map


def split_change_masks(change_map: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Split a combined change_map into separate erosion/accretion binary masks."""
    erosion_mask = (change_map == EROSION).astype(np.uint8)
    accretion_mask = (change_map == ACCRETION).astype(np.uint8)
    return erosion_mask, accretion_mask


def change_map_to_rgb(change_map: np.ndarray) -> np.ndarray:
    """
    Render the change_map as an RGB visualization.

    Red   = erosion
    Green = accretion
    Black = no change
    """
    h, w = change_map.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    rgb[change_map == EROSION] = [220, 40, 40]      # red
    rgb[change_map == ACCRETION] = [40, 180, 90]    # green
    return rgb
