from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.monitoring.drift.metrics import compare_feature, ks_statistic, psi


class DriftMetricsTest(unittest.TestCase):
    def test_psi_is_zero_for_identical_distributions(self) -> None:
        distribution = [0.1, 0.2, 0.3, 0.4]
        self.assertEqual(psi(distribution, distribution), 0.0)

    def test_ks_and_psi_detect_shift(self) -> None:
        reference_values = [610, 620, 640, 660, 680, 700, 720, 740]
        current_values = [540, 550, 560, 580, 590, 610, 620, 630]

        _, _, psi_value, ks_value = compare_feature(reference_values, current_values, 300, 850)

        self.assertGreater(psi_value, 0.1)
        self.assertGreater(ks_value, 0.2)

    def test_ks_statistic_bounds(self) -> None:
        reference_values = [1, 2, 3, 4, 5]
        current_values = [1, 2, 3, 4, 5]
        self.assertGreaterEqual(ks_statistic(reference_values, current_values), 0.0)
        self.assertLessEqual(ks_statistic(reference_values, current_values), 1.0)


if __name__ == "__main__":
    unittest.main()
