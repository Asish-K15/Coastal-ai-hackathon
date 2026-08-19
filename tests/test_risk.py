import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data-processing"))

from risk_classifier import classify_risk, LOW, MEDIUM, HIGH  # noqa: E402


class TestRiskClassifier(unittest.TestCase):
    def test_low_risk(self):
        self.assertEqual(classify_risk(0.0), LOW)
        self.assertEqual(classify_risk(2.0), LOW)  # boundary inclusive
        self.assertEqual(classify_risk(-1.5), LOW)

    def test_medium_risk(self):
        self.assertEqual(classify_risk(3.0), MEDIUM)
        self.assertEqual(classify_risk(6.0), MEDIUM)  # boundary inclusive
        self.assertEqual(classify_risk(-4.0), MEDIUM)

    def test_high_risk(self):
        self.assertEqual(classify_risk(6.1), HIGH)
        self.assertEqual(classify_risk(-10.0), HIGH)
        self.assertEqual(classify_risk(50.0), HIGH)

    def test_custom_thresholds(self):
        self.assertEqual(classify_risk(3.0, low_max_pct=5.0, medium_max_pct=10.0), LOW)
        self.assertEqual(classify_risk(15.0, low_max_pct=5.0, medium_max_pct=10.0), HIGH)

    def test_invalid_thresholds_raise(self):
        with self.assertRaises(ValueError):
            classify_risk(1.0, low_max_pct=10.0, medium_max_pct=5.0)
        with self.assertRaises(ValueError):
            classify_risk(1.0, low_max_pct=-1.0, medium_max_pct=5.0)


if __name__ == "__main__":
    unittest.main()
