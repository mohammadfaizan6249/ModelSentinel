# Demo Script

## 90-Second Walkthrough

1. Open the dashboard and explain that it monitors a deployed credit-risk model.
2. Click a drifted feature and show baseline vs production distribution shift.
3. Point out that PSI and KS are computed in the backend from synthetic production batches.
4. Turn on live mode and mention that each tick simulates fresh production drift.
5. Run AI analysis and explain that the UI reads a backend-generated incident summary.
6. Trigger retraining and show the version change from `CreditRisk_v2.1` to `CreditRisk_v2.2`.
7. End on the recovery story: drift falls, alerts clear, and health improves.

## Resume Bullets

- Built an end-to-end ML monitoring platform that computes production drift using PSI and KS across six credit-risk features.
- Developed a React dashboard and FastAPI backend for live model-health tracking, alerting, feature inspection, and retraining workflows.
- Implemented a synthetic production simulator and pure-Python retraining pipeline with versioned model artifacts to demonstrate full ML lifecycle ownership.
