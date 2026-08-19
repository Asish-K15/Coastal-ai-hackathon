import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data-processing"))

from utils import OUTPUTS_DIR  # noqa: E402
from pipeline import run_pipeline  # noqa: E402

REQUIRED_FIELDS = {
    "aoi_name": str,
    "date_before": str,
    "date_after": str,
    "area_eroded_sqm": (int, float),
    "area_accreted_sqm": (int, float),
    "net_change_sqm": (int, float),
    "percent_change": (int, float),
    "risk_tag": str,
}


class TestSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure stats.json exists / is fresh before validating.
        run_pipeline()
        stats_path = os.path.join(OUTPUTS_DIR, "stats.json")
        with open(stats_path) as f:
            cls.stats = json.load(f)

    def test_all_required_fields_present(self):
        for field in REQUIRED_FIELDS:
            self.assertIn(field, self.stats, f"Missing required field: {field}")

    def test_field_types(self):
        for field, expected_type in REQUIRED_FIELDS.items():
            self.assertIsInstance(
                self.stats[field], expected_type, f"Wrong type for {field}"
            )

    def test_risk_tag_is_valid_value(self):
        self.assertIn(self.stats["risk_tag"], {"Low", "Medium", "High"})

    def test_net_change_consistent_with_areas(self):
        expected_net = self.stats["area_accreted_sqm"] - self.stats["area_eroded_sqm"]
        self.assertAlmostEqual(self.stats["net_change_sqm"], expected_net, places=2)

    def test_no_extra_top_level_keys_missing_from_schema(self):
        # stats.json should contain exactly the contractual fields
        # (supplementary data belongs in meta.json, not here).
        self.assertEqual(set(self.stats.keys()), set(REQUIRED_FIELDS.keys()))


if __name__ == "__main__":
    unittest.main()
