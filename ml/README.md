# ML Workspace

This folder should contain the model lifecycle pieces that make the project credible in interviews:

- feature preparation
- training pipeline
- evaluation reports
- versioned model outputs

Implemented for Phases 3 and 4:

- `features/credit_risk.py` defines the monitored feature schema and default-risk function
- `models/logistic_regression.py` contains a pure-Python logistic regression trainer and scorer
- `evaluation/metrics.py` computes evaluation metrics used by the monitoring engine
- `pipelines/retrain.py` runs training, validation, 3-fold CV, and writes versioned artifacts
- `models/model_registry.json` tracks trained model versions and metrics

The implementation is intentionally lightweight and dependency-friendly, but it now represents a real train/evaluate/retrain loop rather than a scripted UI reset.
