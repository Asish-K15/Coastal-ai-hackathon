# data-processing/

Python backend for the CoastalVision AI pipeline. Pure NumPy/Pillow — no
heavy geospatial dependencies required for the demo (an optional
`rasterio` path is noted for real satellite data).

## Modules

| File                    | Responsibility                                                          |
|--------------------------|--------------------------------------------------------------------------|
| `utils.py`                | Paths, `PipelineConfig` (all thresholds/config in one place), IO helpers.|
| `ndwi.py`                  | `calculate_ndwi`, `create_water_mask`.                                   |
| `mask_generation.py`       | Band loading + NDWI→mask convenience wrappers, mask saving.              |
| `change_detection.py`      | `detect_change` (0/1/2 encoding), mask splitting, RGB visualization.     |
| `area_calculation.py`      | Pixel counts → real-world area, net change, percent change.              |
| `risk_classifier.py`       | Percentage-based Low/Medium/High risk tagging.                          |
| `sample_data.py`           | Generates the deterministic synthetic demo dataset.                     |
| `pipeline.py`              | Orchestrates all of the above; writes `outputs/`.                        |

## Running

```bash
# from the repo root
python data-processing/pipeline.py
```

This will (re)generate the synthetic sample dataset if missing, run the
full pipeline, and write `outputs/stats.json`, `outputs/meta.json`, and
all mask/visualization PNGs.

## Design notes

- **No hard-coded satellite assumptions.** `ndwi.py` and
  `change_detection.py` operate on plain arrays; nothing about Sentinel-2
  or any specific sensor is baked in.
- **No hard-coded pixel area.** `area_calculation.calculate_areas` takes
  `pixel_area_sqm` as an explicit argument (see `utils.PipelineConfig`).
- **Configurable thresholds.** NDWI threshold and risk thresholds live in
  `utils.PipelineConfig`, not scattered through the code.
- **JSON contract.** `pipeline.run_pipeline()` writes exactly the fields
  defined in `../SCHEMA.md` to `stats.json`; anything extra goes in the
  separate `meta.json`.

See `../data/README.md` for how to swap in real satellite imagery.
