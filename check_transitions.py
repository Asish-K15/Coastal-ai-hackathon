import rasterio
import numpy as np

BASE = "data/primary"

with rasterio.open(f"{BASE}/before/B03.tif") as src:
    before_b03 = src.read(1).astype(np.float64)

with rasterio.open(f"{BASE}/before/B08.tif") as src:
    before_b08 = src.read(1).astype(np.float64)

with rasterio.open(f"{BASE}/after/B03.tif") as src:
    after_b03 = src.read(1).astype(np.float64)

with rasterio.open(f"{BASE}/after/B08.tif") as src:
    after_b08 = src.read(1).astype(np.float64)


# Calculate NDWI
before_ndwi = (before_b03 - before_b08) / (
    before_b03 + before_b08 + 1e-10
)

after_ndwi = (after_b03 - after_b08) / (
    after_b03 + after_b08 + 1e-10
)


# Use the current candidate threshold
threshold = 0.05

before_water = before_ndwi > threshold
after_water = after_ndwi > threshold


# Pixel transitions
land_to_water = (~before_water) & after_water
water_to_land = before_water & (~after_water)
unchanged = before_water == after_water


print("=" * 45)
print("DIRECT NDWI TRANSITION CHECK")
print("=" * 45)

print(f"Threshold: {threshold}")

print()
print("BEFORE WATER :", int(np.count_nonzero(before_water)))
print("AFTER WATER  :", int(np.count_nonzero(after_water)))

print()
print("LAND -> WATER :", int(np.count_nonzero(land_to_water)))
print("WATER -> LAND :", int(np.count_nonzero(water_to_land)))
print("UNCHANGED     :", int(np.count_nonzero(unchanged)))

print()
print("INTERPRETATION")
print("------------------------------")
print("LAND -> WATER = EROSION")
print("WATER -> LAND = ACCRETION")

print()
print("AREA")
print("------------------------------")
print(
    "Erosion area   :",
    int(np.count_nonzero(land_to_water)) * 100,
    "m²"
)

print(
    "Accretion area :",
    int(np.count_nonzero(water_to_land)) * 100,
    "m²"
)

net = (
    int(np.count_nonzero(water_to_land))
    - int(np.count_nonzero(land_to_water))
) * 100

print("Net change     :", net, "m²")
print("=" * 45)