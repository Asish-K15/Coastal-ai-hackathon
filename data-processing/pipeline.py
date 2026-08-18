"""
pipeline.py
-----------
End-to-end CoastalVision AI pipeline:

    bands -> NDWI -> water masks -> change detection -> areas
          -> risk classification -> stats.json + PNG outputs

Run directly:

    python pipeline.py

to regenerate the synthetic sample dataset (if missing) and produce all
files under outputs/. This is the same entry point run_demo.py calls.
"""

from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image

# Allow running this file directly (python pipeline.py) as well as via
# `python -m data_processing.pipeline`-style imports.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    DEFAULT_CONFIG,
    OUTPUTS_DIR,
    SAMPLE_DIR,
    ensure_dir,
    write_json,
    save_binary_mask_png,
    save_rgb_png,
)
from sample_data import generate_sample_dataset
from mask_generation import generate_mask_from_bands, load_bands
from change_detection import detect_change, split_change_masks, change_map_to_rgb
from area_calculation import calculate_areas
from risk_classifier import classify_risk


def _ensure_sample_data_exists() -> None:
    before_green = os.path.join(SAMPLE_DIR, "before", "green.png")
    after_green = os.path.join(SAMPLE_DIR, "after", "green.png")
    if not (os.path.exists(before_green) and os.path.exists(after_green)):
        generate_sample_dataset()


def _make_visualization_panel(
    before_mask: np.ndarray, after_mask: np.ndarray, change_rgb: np.ndarray
) -> np.ndarray:
    """Stitch before-mask / after-mask / change-map side by side for report.html."""
    h, w = before_mask.shape
    gap = 6

    def mask_to_rgb(mask):
        rgb = np.zeros((h, w, 3), dtype=np.uint8)
        rgb[mask == 1] = [40, 110, 200]   # water = blue
        rgb[mask == 0] = [225, 215, 180]  # land = sand
        return rgb

    panel = np.full((h, w * 3 + gap * 2, 3), 255, dtype=np.uint8)
    panel[:, 0:w] = mask_to_rgb(before_mask)
    panel[:, w + gap : 2 * w + gap] = mask_to_rgb(after_mask)
    panel[:, 2 * w + 2 * gap : 3 * w + 2 * gap] = change_rgb
    return panel


def run_pipeline(config=DEFAULT_CONFIG, out_dir: str = OUTPUTS_DIR) -> dict:
    """
    Run the full pipeline and write all output files.

    Returns the stats dict that was written to stats.json.
    """
    ensure_dir(out_dir)
    _ensure_sample_data_exists()

    # 1. Load bands (demo: synthetic PNG bands; real data: rasterio bands)
    before_green, before_nir = load_bands(
        os.path.join(SAMPLE_DIR, "before", "green.png"),
        os.path.join(SAMPLE_DIR, "before", "nir.png"),
    )
    after_green, after_nir = load_bands(
        os.path.join(SAMPLE_DIR, "after", "green.png"),
        os.path.join(SAMPLE_DIR, "after", "nir.png"),
    )

    # 2. NDWI + water/land masks
    _, before_mask = generate_mask_from_bands(
        before_green, before_nir, threshold=config.ndwi_threshold
    )
    _, after_mask = generate_mask_from_bands(
        after_green, after_nir, threshold=config.ndwi_threshold
    )

    # 3. Change detection
    change_map = detect_change(before_mask, after_mask)
    erosion_mask, accretion_mask = split_change_masks(change_map)
    change_rgb = change_map_to_rgb(change_map)

    # 4. Area calculation
    area_stats = calculate_areas(
        change_map, before_mask, pixel_area_sqm=config.pixel_area_sqm
    )

    # 5. Risk classification
    risk_tag = classify_risk(
        area_stats.percent_change,
        low_max_pct=config.risk_low_max_pct,
        medium_max_pct=config.risk_medium_max_pct,
    )

    # 6. Write stats.json (matches SCHEMA.md exactly — do not rename fields)
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
    write_json(stats, os.path.join(out_dir, "stats.json"))

    # 6b. Write supplementary (non-contractual) metadata
    meta = {
        "pixel_area_sqm": config.pixel_area_sqm,
        "image_width": int(before_mask.shape[1]),
        "image_height": int(before_mask.shape[0]),
        "change_encoding": {"0": "no_change", "1": "erosion", "2": "accretion"},
        "data_source": config.data_source,
        "risk_thresholds": {
            "low_max_pct": config.risk_low_max_pct,
            "medium_max_pct": config.risk_medium_max_pct,
        },
    }
    write_json(meta, os.path.join(out_dir, "meta.json"))

    # 7. Write PNG outputs
    save_binary_mask_png(before_mask, os.path.join(out_dir, "before_mask.png"))
    save_binary_mask_png(after_mask, os.path.join(out_dir, "after_mask.png"))
    save_binary_mask_png(erosion_mask, os.path.join(out_dir, "erosion_mask.png"))
    save_binary_mask_png(accretion_mask, os.path.join(out_dir, "accretion_mask.png"))
    save_rgb_png(change_rgb, os.path.join(out_dir, "change_map.png"))

    viz = _make_visualization_panel(before_mask, after_mask, change_rgb)
    save_rgb_png(viz, os.path.join(out_dir, "visualization.png"))

    return stats


if __name__ == "__main__":
    result = run_pipeline()
    print("Pipeline complete. stats.json:")
    for k, v in result.items():
        print(f"  {k}: {v}")
