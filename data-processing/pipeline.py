"""
pipeline.py
-----------
Real Sentinel-2 coastal change-detection pipeline.

Data:
    BEFORE: 2020-12-28
    AFTER : 2025-01-16

Bands:
    B03 = Green
    B08 = NIR

Pipeline:
    Sentinel-2 B03/B08
        ↓
    NDWI
        ↓
    Water masks
        ↓
    Change detection
        ↓
    Erosion / accretion
        ↓
    Area calculation
        ↓
    Risk classification
        ↓
    outputs/
"""

from __future__ import annotations

import os
import sys

import numpy as np

# Allow imports when running:
# python data-processing/pipeline.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    DEFAULT_CONFIG,
    OUTPUTS_DIR,
    PRIMARY_DIR,
    ensure_dir,
    write_json,
    save_binary_mask_png,
    save_rgb_png,
)

from mask_generation import generate_mask_from_bands, load_bands
from change_detection import (
    detect_change,
    split_change_masks,
    change_map_to_rgb,
)
from area_calculation import calculate_areas
from risk_classifier import classify_risk


def _make_visualization_panel(
    before_mask: np.ndarray,
    after_mask: np.ndarray,
    change_rgb: np.ndarray,
) -> np.ndarray:
    """Create before / after / change visualization."""

    h, w = before_mask.shape
    gap = 6

    def mask_to_rgb(mask):
        rgb = np.zeros((h, w, 3), dtype=np.uint8)

        # Water
        rgb[mask == 1] = [40, 110, 200]

        # Land
        rgb[mask == 0] = [225, 215, 180]

        return rgb

    panel = np.full(
        (h, w * 3 + gap * 2, 3),
        255,
        dtype=np.uint8,
    )

    panel[:, 0:w] = mask_to_rgb(before_mask)

    panel[
        :,
        w + gap : 2 * w + gap
    ] = mask_to_rgb(after_mask)

    panel[
        :,
        2 * w + 2 * gap : 3 * w + 2 * gap
    ] = change_rgb

    return panel


def run_pipeline(
    config=DEFAULT_CONFIG,
    out_dir: str = OUTPUTS_DIR,
) -> dict:
    """
    Run the real Sentinel-2 pipeline.
    """

    ensure_dir(out_dir)

    # ---------------------------------------------------------
    # 1. REAL SENTINEL-2 DATA
    # ---------------------------------------------------------

    before_b03 = os.path.join(
        PRIMARY_DIR,
        "before",
        "B03.tif",
    )

    before_b08 = os.path.join(
        PRIMARY_DIR,
        "before",
        "B08.tif",
    )

    after_b03 = os.path.join(
        PRIMARY_DIR,
        "after",
        "B03.tif",
    )

    after_b08 = os.path.join(
        PRIMARY_DIR,
        "after",
        "B08.tif",
    )

    required_files = [
        before_b03,
        before_b08,
        after_b03,
        after_b08,
    ]

    for path in required_files:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Required Sentinel-2 file not found:\n{path}"
            )

    print("\n--- LOADING REAL SENTINEL-2 DATA ---")

    print(f"BEFORE B03: {before_b03}")
    print(f"BEFORE B08: {before_b08}")
    print(f"AFTER  B03: {after_b03}")
    print(f"AFTER  B08: {after_b08}")

    before_green, before_nir = load_bands(
        before_b03,
        before_b08,
    )

    after_green, after_nir = load_bands(
        after_b03,
        after_b08,
    )

    print("\nData loaded successfully.")
    print(
        f"Before shape: {before_green.shape}"
    )
    print(
        f"After shape : {after_green.shape}"
    )

    # ---------------------------------------------------------
    # 2. NDWI + WATER MASKS
    # ---------------------------------------------------------

    # Start with 0.05.
    # We will validate this threshold using the generated masks.
    ndwi_threshold = 0.05

    print(
        f"\n--- NDWI THRESHOLD: {ndwi_threshold} ---"
    )

    before_ndwi, before_mask = generate_mask_from_bands(
        before_green,
        before_nir,
        threshold=ndwi_threshold,
    )

    after_ndwi, after_mask = generate_mask_from_bands(
        after_green,
        after_nir,
        threshold=ndwi_threshold,
    )

    print(
        f"Before water pixels: "
        f"{np.count_nonzero(before_mask)}"
    )

    print(
        f"After water pixels : "
        f"{np.count_nonzero(after_mask)}"
    )

    # ---------------------------------------------------------
    # 3. CHANGE DETECTION
    # ---------------------------------------------------------

    change_map = detect_change(
        before_mask,
        after_mask,
    )

    erosion_mask, accretion_mask = split_change_masks(
        change_map
    )

    change_rgb = change_map_to_rgb(
        change_map
    )

    print("\n--- CHANGE DETECTION ---")

    print(
        f"Erosion pixels  : "
        f"{np.count_nonzero(erosion_mask)}"
    )

    print(
        f"Accretion pixels: "
        f"{np.count_nonzero(accretion_mask)}"
    )

    # ---------------------------------------------------------
    # 4. AREA CALCULATION
    # ---------------------------------------------------------

    area_stats = calculate_areas(
        change_map,
        before_mask,
        pixel_area_sqm=config.pixel_area_sqm,
    )

    print("\n--- AREA RESULTS ---")

    print(
        f"Eroded area   : "
        f"{area_stats.area_eroded_sqm} m²"
    )

    print(
        f"Accreted area : "
        f"{area_stats.area_accreted_sqm} m²"
    )

    print(
        f"Net change    : "
        f"{area_stats.net_change_sqm} m²"
    )

    print(
        f"Percent change: "
        f"{area_stats.percent_change}%"
    )

    # ---------------------------------------------------------
    # 5. RISK CLASSIFICATION
    # ---------------------------------------------------------

    risk_tag = classify_risk(
        area_stats.percent_change,
        low_max_pct=config.risk_low_max_pct,
        medium_max_pct=config.risk_medium_max_pct,
    )

    print(
        f"Risk tag      : {risk_tag}"
    )

    # ---------------------------------------------------------
    # 6. STATS.JSON
    # ---------------------------------------------------------

    stats = {
        "aoi_name": config.aoi_name,
        "date_before": config.date_before,
        "date_after": config.date_after,
        "area_eroded_sqm": area_stats.area_eroded_sqm,
        "area_accreted_sqm": area_stats.area_accreted_sqm,
        "net_change_sqm": area_stats.net_change_sqm,
        "percent_change": area_stats.percent_change,
        "risk_tag": risk_tag,
    }

    write_json(
        stats,
        os.path.join(
            out_dir,
            "stats.json",
        ),
    )

    # ---------------------------------------------------------
    # 7. METADATA
    # ---------------------------------------------------------

    meta = {
        "pixel_area_sqm": config.pixel_area_sqm,
        "pixel_resolution_m": config.pixel_resolution_m,
        "image_width": int(before_mask.shape[1]),
        "image_height": int(before_mask.shape[0]),
        "ndwi_threshold": ndwi_threshold,
        "bands": {
            "green": "B03",
            "nir": "B08",
        },
        "data_source": config.data_source,
        "date_before": config.date_before,
        "date_after": config.date_after,
        "change_encoding": {
            "0": "no_change",
            "1": "erosion",
            "2": "accretion",
        },
        "risk_thresholds": {
            "low_max_pct": config.risk_low_max_pct,
            "medium_max_pct": config.risk_medium_max_pct,
        },
    }

    write_json(
        meta,
        os.path.join(
            out_dir,
            "meta.json",
        ),
    )

    # ---------------------------------------------------------
    # 8. SAVE OUTPUT MASKS
    # ---------------------------------------------------------

    save_binary_mask_png(
        before_mask,
        os.path.join(
            out_dir,
            "before_mask.png",
        ),
    )

    save_binary_mask_png(
        after_mask,
        os.path.join(
            out_dir,
            "after_mask.png",
        ),
    )

    save_binary_mask_png(
        erosion_mask,
        os.path.join(
            out_dir,
            "erosion_mask.png",
        ),
    )

    save_binary_mask_png(
        accretion_mask,
        os.path.join(
            out_dir,
            "accretion_mask.png",
        ),
    )

    save_rgb_png(
        change_rgb,
        os.path.join(
            out_dir,
            "change_map.png",
        ),
    )

    # ---------------------------------------------------------
    # 9. COMBINED VISUALIZATION
    # ---------------------------------------------------------

    visualization = _make_visualization_panel(
        before_mask,
        after_mask,
        change_rgb,
    )

    save_rgb_png(
        visualization,
        os.path.join(
            out_dir,
            "visualization.png",
        ),
    )

    return stats


if __name__ == "__main__":

    result = run_pipeline()

    print("\n========================================")
    print("REAL SENTINEL-2 PIPELINE COMPLETE")
    print("========================================")

    for key, value in result.items():
        print(f"{key}: {value}")