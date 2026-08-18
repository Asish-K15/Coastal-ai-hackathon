"""
sample_data.py
---------------
Generates a small, DETERMINISTIC, SYNTHETIC "before" / "after" coastal
scene so the entire pipeline can be demoed and tested without downloading
any real satellite imagery.

THIS IS NOT REAL SATELLITE DATA. It is a stand-in Green/NIR band pair
designed so that:
  * roughly the bottom portion of the "before" scene is water, the rest land
  * some land pixels flip to water in "after" (-> erosion)
  * some water pixels flip to land in "after" (-> accretion)

Running this script (or importing generate_sample_dataset) recreates the
files under data/sample/before and data/sample/after deterministically
(fixed seed) — safe to re-run any time.
"""

from __future__ import annotations

import os

import numpy as np
from PIL import Image

from utils import SAMPLE_DIR, ensure_dir

SIZE = 128  # 128x128 demo scene
SEED = 42


def _make_band_pair(is_water: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Given a boolean water/land array, synthesize plausible Green/NIR band
    values such that NDWI = (Green-NIR)/(Green+NIR) will threshold back
    into the same water/land pattern.

    Water pixels: high Green, low NIR (water absorbs NIR) -> NDWI > 0
    Land pixels: low-ish Green, high NIR (vegetation/soil) -> NDWI < 0
    """
    rng = np.random.default_rng(SEED)
    green = np.zeros(is_water.shape, dtype=np.float64)
    nir = np.zeros(is_water.shape, dtype=np.float64)

    # Water: Green high (~140-170), NIR low (~10-40)
    n_water = int(np.count_nonzero(is_water))
    green[is_water] = rng.integers(140, 170, size=n_water)
    nir[is_water] = rng.integers(10, 40, size=n_water)

    # Land: Green moderate (~70-110), NIR high (~150-200)
    land_mask = ~is_water
    n_land = int(np.count_nonzero(land_mask))
    green[land_mask] = rng.integers(70, 110, size=n_land)
    nir[land_mask] = rng.integers(150, 200, size=n_land)

    return green, nir


def _base_coastline(size: int) -> np.ndarray:
    """
    Deterministic base coastline: a gently sloped/curved line, water
    below it, land above it. Returns a boolean array (True = water).
    """
    y, x = np.mgrid[0:size, 0:size]
    # Coastline boundary follows a sine curve so change looks natural.
    boundary = size * 0.55 + 8 * np.sin(x / size * 3 * np.pi)
    is_water = y > boundary
    return is_water


def generate_sample_dataset(out_dir: str = SAMPLE_DIR, size: int = SIZE) -> dict:
    """
    Generate before/after Green + NIR band PNGs under out_dir/before and
    out_dir/after. Returns a dict of the file paths written.
    """
    before_dir = ensure_dir(os.path.join(out_dir, "before"))
    after_dir = ensure_dir(os.path.join(out_dir, "after"))

    before_water = _base_coastline(size)

    # "After" scene: erode a chunk of land into water on the left half,
    # and accrete a chunk of water into land on the right half, so the
    # demo clearly shows both erosion and accretion.
    after_water = before_water.copy()

    y, x = np.mgrid[0:size, 0:size]

    # Erosion patch: an area that was land in "before", becomes water.
    erosion_region = (
        (~before_water)
        & (x < size * 0.45)
        & (y > size * 0.30)
        & (y < size * 0.60)
    )
    after_water[erosion_region] = True

    # Accretion patch: an area that was water in "before", becomes land.
    accretion_region = (
        before_water
        & (x > size * 0.55)
        & (y > size * 0.55)
        & (y < size * 0.80)
    )
    after_water[accretion_region] = False

    before_green, before_nir = _make_band_pair(before_water)
    after_green, after_nir = _make_band_pair(after_water)

    paths = {
        "before_green": os.path.join(before_dir, "green.png"),
        "before_nir": os.path.join(before_dir, "nir.png"),
        "after_green": os.path.join(after_dir, "green.png"),
        "after_nir": os.path.join(after_dir, "nir.png"),
    }

    Image.fromarray(before_green.astype(np.uint8), mode="L").save(paths["before_green"])
    Image.fromarray(before_nir.astype(np.uint8), mode="L").save(paths["before_nir"])
    Image.fromarray(after_green.astype(np.uint8), mode="L").save(paths["after_green"])
    Image.fromarray(after_nir.astype(np.uint8), mode="L").save(paths["after_nir"])

    return paths


if __name__ == "__main__":
    written = generate_sample_dataset()
    print("DEMO / SYNTHETIC DATA generated:")
    for name, path in written.items():
        print(f"  {name}: {path}")
