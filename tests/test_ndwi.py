import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data-processing"))

from ndwi import calculate_ndwi, create_water_mask  # noqa: E402


class TestNDWI(unittest.TestCase):
    def test_known_values(self):
        green = np.array([[100.0, 50.0]])
        nir = np.array([[50.0, 100.0]])
        ndwi = calculate_ndwi(green, nir)
        # (100-50)/(100+50) = 0.333..., (50-100)/(50+100) = -0.333...
        self.assertAlmostEqual(ndwi[0, 0], 1 / 3, places=5)
        self.assertAlmostEqual(ndwi[0, 1], -1 / 3, places=5)

    def test_zero_denominator_no_crash(self):
        green = np.array([[0.0, 5.0]])
        nir = np.array([[0.0, -5.0]])
        # green+nir = 0 for both columns
        ndwi = calculate_ndwi(green, nir)
        self.assertTrue(np.all(np.isfinite(ndwi)))
        self.assertEqual(ndwi[0, 0], 0.0)
        self.assertEqual(ndwi[0, 1], 0.0)

    def test_shape_mismatch_raises(self):
        with self.assertRaises(ValueError):
            calculate_ndwi(np.zeros((2, 2)), np.zeros((3, 3)))

    def test_water_mask_threshold(self):
        ndwi = np.array([[-0.5, 0.0, 0.1, 0.6]])
        mask = create_water_mask(ndwi, threshold=0.0)
        # only strictly > 0 counts as water
        np.testing.assert_array_equal(mask, np.array([[0, 0, 1, 1]], dtype=np.uint8))

    def test_water_mask_is_binary(self):
        ndwi = np.random.default_rng(0).uniform(-1, 1, size=(10, 10))
        mask = create_water_mask(ndwi, threshold=0.2)
        unique_vals = set(np.unique(mask).tolist())
        self.assertTrue(unique_vals.issubset({0, 1}))


if __name__ == "__main__":
    unittest.main()
