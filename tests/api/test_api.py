from __future__ import annotations

import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
API_ROOT = REPO_ROOT / "services" / "api"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

TEMP_DIR = Path(tempfile.mkdtemp(prefix="modelsentinel-api-"))
os.environ["MODELSENTINEL_MODEL_DIR"] = str(TEMP_DIR / "models")

from fastapi.testclient import TestClient

from app.main import app


class ApiSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_dashboard_endpoint_returns_computed_metrics(self) -> None:
        response = self.client.get("/dashboard")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("baselineAccuracy", payload)
        self.assertIn("currentAccuracy", payload)
        self.assertGreater(payload["baselineAccuracy"], payload["currentAccuracy"])
        self.assertGreaterEqual(len(payload["features"]), 6)

    def test_analysis_endpoint_returns_sections(self) -> None:
        response = self.client.post("/analysis")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload["sections"]), 4)

    def test_retraining_flow_completes(self) -> None:
        with patch("app.services.dashboard_state.STEP_DURATION_SECONDS", 0.001):
            start = self.client.post("/retraining")
            job_id = start.json()["jobId"]
            time.sleep(0.02)
            done = self.client.get(f"/retraining/{job_id}")
            payload = done.json()

        self.assertEqual(done.status_code, 200)
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["snapshot"]["modelName"], "CreditRisk_v2.2")
        self.assertTrue(all(feature["status"] == "stable" for feature in payload["snapshot"]["features"]))


if __name__ == "__main__":
    unittest.main()
