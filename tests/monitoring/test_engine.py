from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.monitoring.simulator.engine import MonitoringEngine


class MonitoringEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="modelsentinel-engine-"))
        self.original_model_dir = os.environ.get("MODELSENTINEL_MODEL_DIR")
        os.environ["MODELSENTINEL_MODEL_DIR"] = str(self.temp_dir / "models")

    def tearDown(self) -> None:
        if self.original_model_dir is None:
            os.environ.pop("MODELSENTINEL_MODEL_DIR", None)
        else:
            os.environ["MODELSENTINEL_MODEL_DIR"] = self.original_model_dir
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_snapshot_contains_real_drift_and_model_health(self) -> None:
        engine = MonitoringEngine()
        snapshot = engine.snapshot

        self.assertIn("baseline_accuracy", snapshot)
        self.assertIn("current_accuracy", snapshot)
        self.assertGreater(snapshot["baseline_accuracy"], snapshot["current_accuracy"])
        self.assertTrue(any(feature["status"] == "critical" for feature in snapshot["features"]))

    def test_retraining_improves_snapshot(self) -> None:
        engine = MonitoringEngine()
        before = engine.snapshot
        after = engine.run_retraining()

        self.assertNotEqual(before["model_name"], after["model_name"])
        self.assertGreater(after["health_percent"], before["health_percent"])
        self.assertTrue(all(feature["status"] == "stable" for feature in after["features"]))


if __name__ == "__main__":
    unittest.main()
