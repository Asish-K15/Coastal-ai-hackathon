import numpy as np


def detect_changes(before_mask, after_mask):
    """
    Compare two binary land/water masks.

    Mask convention:
        0 = Land
        1 = Water

    Land -> Water = Erosion
    Water -> Land = Accretion

    Returns:
        erosion_mask
        accretion_mask
        erosion_pixels
        accretion_pixels
    """

    # Check that both masks have the same dimensions
    if before_mask.shape != after_mask.shape:
        raise ValueError("Before and after masks must have the same shape.")

    # Detect erosion: Land -> Water
    erosion_mask = (before_mask == 0) & (after_mask == 1)

    # Detect accretion: Water -> Land
    accretion_mask = (before_mask == 1) & (after_mask == 0)

    # Count changed pixels
    erosion_pixels = int(np.sum(erosion_mask))
    accretion_pixels = int(np.sum(accretion_mask))

    return (
        erosion_mask,
        accretion_mask,
        erosion_pixels,
        accretion_pixels
    )


if __name__ == "__main__":

    # Temporary dummy masks for testing.
    # These will later be replaced by Member 1's real masks.

    before_mask = np.array([
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0]
    ])

    after_mask = np.array([
    [0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0],
    [0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0]
   ])

    (
        erosion_mask,
        accretion_mask,
        erosion_pixels,
        accretion_pixels
    ) = detect_changes(before_mask, after_mask)

    print("Before mask:")
    print(before_mask)

    print("\nAfter mask:")
    print(after_mask)

    print("\nErosion mask:")
    print(erosion_mask.astype(int))

    print("\nAccretion mask:")
    print(accretion_mask.astype(int))

    print("\nErosion pixels:", erosion_pixels)
    print("Accretion pixels:", accretion_pixels)