from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from services.monitoring.simulator.engine import MonitoringEngine


def main() -> None:
    engine = MonitoringEngine()
    snapshot = engine.snapshot
    summary = {
        "model_name": snapshot["model_name"],
        "current_accuracy": snapshot["current_accuracy"],
        "baseline_accuracy": snapshot["baseline_accuracy"],
        "health_percent": snapshot["health_percent"],
        "top_features": [
            {"name": feature["name"], "psi": feature["psi"], "ks": feature["ks"]}
            for feature in snapshot["features"][:3]
        ],
    }
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
