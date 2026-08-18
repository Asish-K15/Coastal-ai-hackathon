def calculate_statistics(
    erosion_pixels,
    accretion_pixels,
    pixel_area_sqm,
    original_water_area_sqm
):
    """
    Calculate erosion/accretion statistics.

    Parameters:
        erosion_pixels: Number of pixels changed from land to water.
        accretion_pixels: Number of pixels changed from water to land.
        pixel_area_sqm: Area represented by one pixel in square meters.
        original_water_area_sqm: Water area in the BEFORE image.

    Returns:
        Dictionary containing calculated statistics.
    """

    # Calculate areas
    area_eroded_sqm = erosion_pixels * pixel_area_sqm
    area_accreted_sqm = accretion_pixels * pixel_area_sqm

    # Net change:
    # Accretion is positive, erosion is negative
    net_change_sqm = area_accreted_sqm - area_eroded_sqm

    # Calculate percentage change relative to original water area
    if original_water_area_sqm > 0:
        percent_change = (
            net_change_sqm / original_water_area_sqm
        ) * 100
    else:
        percent_change = 0.0

    return {
        "area_eroded_sqm": round(area_eroded_sqm, 2),
        "area_accreted_sqm": round(area_accreted_sqm, 2),
        "net_change_sqm": round(net_change_sqm, 2),
        "percent_change": round(percent_change, 2)
    }


if __name__ == "__main__":

    # Temporary dummy values for testing

    erosion_pixels = 4
    accretion_pixels = 2

    # Example:
    # 10m × 10m pixel = 100 square meters
    pixel_area_sqm = 100

    # Temporary BEFORE water area
    original_water_area_sqm = 10000

    statistics = calculate_statistics(
        erosion_pixels,
        accretion_pixels,
        pixel_area_sqm,
        original_water_area_sqm
    )

    print("Statistics:")
    print("Area eroded:", statistics["area_eroded_sqm"], "sqm")
    print("Area accreted:", statistics["area_accreted_sqm"], "sqm")
    print("Net change:", statistics["net_change_sqm"], "sqm")
    print("Percentage change:", statistics["percent_change"], "%")