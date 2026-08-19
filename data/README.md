# data/

## ⚠️ DEMO / SYNTHETIC DATA

`data/sample/` contains a small, **deterministic, synthetically generated**
"before"/"after" coastal scene (128×128 pixels), created by
`data-processing/sample_data.py`. **It is not real satellite imagery.**
It exists so the entire pipeline, frontend, and test suite can run
instantly, offline, and reproducibly (fixed random seed) with no
downloads required.

```
data/
├── sample/
│   ├── before/
│   │   ├── green.png   # synthetic "Green band"
│   │   └── nir.png     # synthetic "NIR band"
│   └── after/
│       ├── green.png
│       └── nir.png
├── primary/    # placeholder for the real primary AOI dataset
└── backup/     # placeholder for a second/backup AOI dataset
```

Regenerate the sample data at any time with:

```bash
python data-processing/sample_data.py
```

## `primary/` and `backup/`

These directories are currently **empty placeholders**. They exist so the
team can drop in real satellite data later without restructuring the
project:

- `data/primary/` — the main AOI used for the live demo.
- `data/backup/` — a second AOI kept only as a fallback in case the
  primary dataset or imagery has a problem before presenting. It does not
  need a polished, separate UI — just a second copy of Green/NIR bands (or
  raw satellite files) the pipeline can be pointed at.

## Replacing sample data with real satellite imagery

1. Obtain Green and NIR bands for your AOI (e.g. Sentinel-2 bands B03 and
   B08) for two dates.
2. Either export them as single-channel PNGs matching the shape expected
   by `mask_generation.load_bands`, **or** extend
   `mask_generation.load_bands` to read the real raster format directly
   (e.g. with `rasterio`), keeping the same `(green_array, nir_array)`
   return signature.
3. Update `data-processing/utils.PipelineConfig` with the real AOI name,
   dates, and pixel resolution (derive `pixel_resolution_m` from the
   raster's geotransform where possible, instead of the hard-coded demo
   value).
4. Point `pipeline.run_pipeline()` at the new band paths instead of
   `data/sample/...`.

No changes are needed to `ndwi.py`, `change_detection.py`,
`area_calculation.py`, or `risk_classifier.py` — they are already
satellite-agnostic.
