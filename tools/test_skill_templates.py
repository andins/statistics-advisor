"""Run the reference templates' own regression tests so they can't silently rot.

Only the meta-analysis template has standalone tests here (it has no course page running its
code, unlike the other templates, which notebooks/how-to guides in the companion course exercise).

Skipped automatically when the scientific-Python stack (numpy, pandas, scipy, statsmodels,
scikit-learn, matplotlib, seaborn) isn't installed.
"""

import importlib.util
import sys
import unittest

import package_skill

REQUIRED = ["numpy", "pandas", "scipy", "statsmodels", "sklearn", "matplotlib", "seaborn"]
MISSING = [name for name in REQUIRED if importlib.util.find_spec(name) is None]


@unittest.skipIf(MISSING, f"missing packages: {MISSING}")
class MetaAnalysisTemplateTests(unittest.TestCase):
    """The meta-analysis template is a script, not a course page; keep it from rotting here."""

    @classmethod
    def setUpClass(cls):
        path = package_skill.SKILL_ROOT / "scripts" / "meta_analysis_template.py"
        spec = importlib.util.spec_from_file_location("meta_analysis_template", path)
        cls.template = importlib.util.module_from_spec(spec)
        previous, sys.dont_write_bytecode = sys.dont_write_bytecode, True   # keep __pycache__ out of the skill folder
        try:
            spec.loader.exec_module(cls.template)
        finally:
            sys.dont_write_bytecode = previous
        cls.data = cls.template.load_study_data()

    def test_pooling_is_the_precision_weighted_average_with_a_wider_prediction_interval(self):
        pooled = self.template.pool_random_effects(self.data)
        weights = 1 / (self.data["se"] ** 2 + pooled["tau2"])
        self.assertAlmostEqual(pooled["estimate"], (weights * self.data["effect"]).sum() / weights.sum(), places=8)
        self.assertAlmostEqual(pooled["estimate"], pooled["result"].mean_effect_re, places=6)
        low, high = pooled["prediction_interval"]
        self.assertLess(low, pooled["ci"][0])
        self.assertGreater(high, pooled["ci"][1])
        self.assertGreaterEqual(pooled["i2"], 0)
        self.assertIn("prediction interval", self.template.summarize(pooled))

    def test_hartung_knapp_is_never_narrower_and_two_studies_have_no_prediction_interval(self):
        usual = self.template.pool_random_effects(self.data)
        adjusted = self.template.pool_random_effects(self.data, hksj=True)
        self.assertGreaterEqual(adjusted["ci"][1] - adjusted["ci"][0], usual["ci"][1] - usual["ci"][0])
        self.assertIsNone(self.template.pool_random_effects(self.data.head(2))["prediction_interval"])
        with self.assertRaises(ValueError):
            self.template.pool_random_effects(self.data.head(1))

    def test_leave_one_out_bias_check_and_conversions(self):
        loo = self.template.leave_one_out(self.data)
        self.assertEqual(len(loo), len(self.data))
        self.assertEqual(self.template.egger_test(self.data.head(8))["low_power"], True)
        summaries = fixture_summaries()
        diff = self.template.effect_sizes_from_summaries(summaries, "mean_difference")
        self.assertAlmostEqual(diff["effect"][0], 2.1)
        for kind in ("smd", "log_odds_ratio", "log_risk_ratio"):
            converted = self.template.effect_sizes_from_summaries(summaries, kind)
            self.assertTrue((converted["se"] > 0).all(), kind)
        with self.assertRaises(ValueError):
            self.template.effect_sizes_from_summaries(summaries, "nonsense")


def fixture_summaries():
    import pandas as pd

    return pd.DataFrame({
        "mean_t": [24.1, 22.8, 25.0], "sd_t": [3.2, 2.9, 3.6], "n_t": [30, 45, 28],
        "mean_c": [22.0, 22.1, 22.7], "sd_c": [3.0, 3.1, 3.3], "n_c": [30, 44, 29],
        "events_t": [12, 9, 20], "events_c": [20, 15, 24],
    })


if __name__ == "__main__":
    unittest.main()
