import rasterio
import numpy as np

def check_ndwi(label, b03_path, b08_path):
    with rasterio.open(b03_path) as src:
        green = src.read(1).astype(np.float32)

    with rasterio.open(b08_path) as src:
        nir = src.read(1).astype(np.float32)

    ndwi = (green - nir) / (green + nir + 1e-10)

    print(f"\n{label}")
    print("-" * 30)
    print(f"NDWI min  : {np.nanmin(ndwi):.6f}")
    print(f"NDWI max  : {np.nanmax(ndwi):.6f}")
    print(f"NDWI mean : {np.nanmean(ndwi):.6f}")

    for threshold in [0.00, 0.05, 0.10, 0.15, 0.20]:
        water_pixels = np.count_nonzero(ndwi > threshold)
        total_pixels = ndwi.size
        percentage = (water_pixels / total_pixels) * 100

        print(
            f"Threshold {threshold:.2f} -> "
            f"{water_pixels} water pixels "
            f"({percentage:.2f}%)"
        )


check_ndwi(
    "BEFORE — 2020-12-28",
    "data/primary/before/B03.tif",
    "data/primary/before/B08.tif",
)

check_ndwi(
    "AFTER — 2025-01-16",
    "data/primary/after/B03.tif",
    "data/primary/after/B08.tif",
)