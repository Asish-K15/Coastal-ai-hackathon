import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data-processing"))

from change_detection import (  # noqa: E402
    detect_change,
    split_change_masks,
    change_map_to_rgb,
    NO_CHANGE,
    EROSION,
    ACCRETION,
)


class TestChangeDetection(unittest.TestCase):
    def test_land_to_water_is_erosion(self):
        before = np.array([[0]])  # land
        after = np.array([[1]])  # water
        result = detect_change(before, after)
        self.assertEqual(result[0, 0], EROSION)

    def test_water_to_land_is_accretion(self):
        before = np.array([[1]])  # water
        after = np.array([[0]])  # land
        result = detect_change(before, after)
        self.assertEqual(result[0, 0], ACCRETION)

    def test_land_to_land_no_change(self):
        before = np.array([[0]])
        after = np.array([[0]])
        result = detect_change(before, after)
        self.assertEqual(result[0, 0], NO_CHANGE)

    def test_water_to_water_no_change(self):
        before = np.array([[1]])
        after = np.array([[1]])
        result = detect_change(before, after)
        self.assertEqual(result[0, 0], NO_CHANGE)

    def test_combined_grid(self):
        before = np.array([[0, 1], [0, 1]])
        after = np.array([[1, 0], [0, 1]])
        result = detect_change(before, after)
        expected = np.array([[EROSION, ACCRETION], [NO_CHANGE, NO_CHANGE]])
        np.testing.assert_array_equal(result, expected)

    def test_shape_mismatch_raises(self):
        with self.assertRaises(ValueError):
            detect_change(np.zeros((2, 2)), np.zeros((3, 3)))

    def test_split_change_masks(self):
        change_map = np.array([[EROSION, ACCRETION, NO_CHANGE]])
        erosion_mask, accretion_mask = split_change_masks(change_map)
        np.testing.assert_array_equal(erosion_mask, np.array([[1, 0, 0]]))
        np.testing.assert_array_equal(accretion_mask, np.array([[0, 1, 0]]))

    def test_change_map_to_rgb_shape(self):
        change_map = np.array([[EROSION, ACCRETION], [NO_CHANGE, NO_CHANGE]])
        rgb = change_map_to_rgb(change_map)
        self.assertEqual(rgb.shape, (2, 2, 3))
        # erosion pixel should be reddish (R channel high, G channel low)
        self.assertGreater(rgb[0, 0, 0], rgb[0, 0, 1])
        # accretion pixel should be greenish (G channel high, R channel low)
        self.assertGreater(rgb[0, 1, 1], rgb[0, 1, 0])


if __name__ == "__main__":
    unittest.main()
