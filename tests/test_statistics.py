import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data-processing"))

from change_detection import EROSION, ACCRETION, NO_CHANGE  # noqa: E402
from area_calculation import calculate_areas  # noqa: E402


class TestAreaCalculation(unittest.TestCase):
    def test_correct_area_counts(self):
        # 2 erosion pixels, 1 accretion pixel, 1 no-change pixel
        change_map = np.array([[EROSION, EROSION], [ACCRETION, NO_CHANGE]])
        before_mask = np.array([[0, 0], [1, 0]])  # 3 land pixels before
        stats = calculate_areas(change_map, before_mask, pixel_area_sqm=10.0)

        self.assertAlmostEqual(stats.area_eroded_sqm, 20.0)
        self.assertAlmostEqual(stats.area_accreted_sqm, 10.0)

    def test_net_change_is_accretion_minus_erosion(self):
        change_map = np.array([[EROSION, ACCRETION]])
        before_mask = np.array([[0, 1]])
        stats = calculate_areas(change_map, before_mask, pixel_area_sqm=5.0)
        # net = accreted - eroded = 5 - 5 = 0
        self.assertAlmostEqual(stats.net_change_sqm, 0.0)

    def test_percent_change_relative_to_before_land_area(self):
        # before_mask: 4 land pixels total
        before_mask = np.zeros((2, 2))
        # 1 pixel erodes (land->water)
        change_map = np.array([[EROSION, NO_CHANGE], [NO_CHANGE, NO_CHANGE]])
        stats = calculate_areas(change_map, before_mask, pixel_area_sqm=25.0)
        # before land area = 4 * 25 = 100 sqm; net change = -25 sqm
        # percent change = -25/100 * 100 = -25.0
        self.assertAlmostEqual(stats.percent_change, -25.0)

    def test_zero_pixel_area_raises(self):
        with self.assertRaises(ValueError):
            calculate_areas(np.zeros((2, 2)), np.zeros((2, 2)), pixel_area_sqm=0)

    def test_no_land_before_gives_zero_percent(self):
        before_mask = np.ones((2, 2))  # all water, no land
        change_map = np.zeros((2, 2))
        stats = calculate_areas(change_map, before_mask, pixel_area_sqm=10.0)
        self.assertEqual(stats.percent_change, 0.0)


if __name__ == "__main__":
    unittest.main()
