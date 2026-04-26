# ModelSentinel

<p align="center">
  <strong>Detect drift. Measure impact. Retrain with confidence.</strong>
</p>

<p align="center">
  ModelSentinel is a full-stack MLOps portfolio project for monitoring production model drift,
  analyzing degradation, and recovering with retraining.
</p>

<p align="center">
  <img alt="Frontend" src="https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-2563eb">
  <img alt="Backend" src="https://img.shields.io/badge/Backend-FastAPI-059669">
  <img alt="Monitoring" src="https://img.shields.io/badge/Monitoring-PSI%20%2B%20KS-f97316">
  <img alt="ML" src="https://img.shields.io/badge/ML-Logistic%20Regression-7c3aed">
</p>

---

## Why This Project Stands Out

Most ML portfolio projects stop at training a notebook model. ModelSentinel focuses on what happens after deployment:

- feature drift detection with real PSI and KS metrics
- production vs baseline distribution monitoring
- model health tracking through accuracy degradation
- AI-style root-cause analysis for operators
- retraining workflow with versioned model artifacts
- recovery validation after redeployment

This makes the project feel like a real production ML system instead of just a model demo.

## Product View

### What the dashboard shows

| View | What it tells you |
| --- | --- |
| `Feature Drift Table` | Which features drifted, by how much, and whether they are stable, warning, or critical |
| `Distribution Comparison` | Baseline vs production histograms for the selected feature |
| `PSI Trend Chart` | How drift evolved over the last 24 monitoring windows |
| `Alert Log` | Human-readable explanations of what changed and why it matters |
| `AI Analysis` | Root cause, business impact, immediate actions, and long-term fixes |
| `Retraining Workflow` | Recovery path from degraded `CreditRisk_v2.1` to improved `CreditRisk_v2.2` |

### What happens end to end
## Poster

<p align="center">
  <img src="./docs/assets/sentinel_project.jpg" alt="ModelSentinel Poster" width="100%">
</p>

<p align="center">
  <a href="./sentinel_project.pdf">Open PDF version</a>
</p>

## Demo Snapshot

When the app starts in the drifted state, you usually see:

- `credit_score` PSI around `0.32`
- `income` PSI around `0.27`
- `debt_ratio` PSI around `0.39`
- baseline accuracy around `0.84`
- current production accuracy around `0.75`

After retraining:

- the model upgrades from `CreditRisk_v2.1` to `CreditRisk_v2.2`
- alerts clear
- PSI values drop near zero
- model health recovers toward the baseline

## Tech Stack

| Layer | Tools |
| --- | --- |
| Frontend | React, TypeScript, Vite, Chart.js |
| Backend | FastAPI, Pydantic |
| Monitoring | synthetic production simulator, PSI, KS |
| ML | pure-Python logistic regression training and evaluation |
| Verification | `unittest`, lint, production build, CI |

## Repository Layout

```text
modelsentinel/
├── apps/web/                  # React dashboard
├── services/api/              # FastAPI backend
├── services/monitoring/       # Drift metrics, simulator, snapshot job
├── ml/                        # Features, model training, evaluation, artifacts
├── tests/                     # API + monitoring test coverage
├── docs/                      # Architecture, deployment, demo notes
├── scripts/                   # Repo-level helpers
└── .github/workflows/ci.yml   # CI checks
```

## Quick Start

### 1. Install dependencies

```bash
cd /Users/faizan/Desktop/projects/modelsentinel
npm install
python3 -m venv .venv
./.venv/bin/pip install ./services/api
```

### 2. Run the API

```bash
cd /Users/faizan/Desktop/projects/modelsentinel
make run-api
```

### 3. Run the frontend

In a second terminal:

```bash
cd /Users/faizan/Desktop/projects/modelsentinel
npm run dev:web
```

Open:

- frontend: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Verification

Run the full project check:

```bash
cd /Users/faizan/Desktop/projects/modelsentinel
./scripts/check_all.sh
```

That runs:

- backend unit tests
- frontend lint
- frontend production build
- monitoring snapshot CLI smoke test

## Useful Commands

```bash
cd /Users/faizan/Desktop/projects/modelsentinel
make run-api
npm run dev:web
make run-monitor
make test
./scripts/check_all.sh
```

## API Surface

- `GET /health`
- `GET /dashboard`
- `POST /dashboard/refresh`
- `POST /dashboard/live-tick`
- `GET /features`
- `GET /alerts`
- `GET /features/{feature_name}/distribution`
- `GET /features/{feature_name}/trend`
- `POST /analysis`
- `POST /retraining`
- `GET /retraining/{job_id}`

## Best Files To Showcase

- [dashboard_state.py](/Users/faizan/Desktop/projects/modelsentinel/services/api/app/services/dashboard_state.py)
- [engine.py](/Users/faizan/Desktop/projects/modelsentinel/services/monitoring/simulator/engine.py)
- [metrics.py](/Users/faizan/Desktop/projects/modelsentinel/services/monitoring/drift/metrics.py)
- [retrain.py](/Users/faizan/Desktop/projects/modelsentinel/ml/pipelines/retrain.py)
- [model_registry.json](/Users/faizan/Desktop/projects/modelsentinel/ml/models/model_registry.json)
- [deployment.md](/Users/faizan/Desktop/projects/modelsentinel/docs/deployment.md)
- [demo-script.md](/Users/faizan/Desktop/projects/modelsentinel/docs/demo-script.md)

## Resume Positioning

- Built an end-to-end ML monitoring platform that computes production drift with PSI and KS across six deployed credit-risk features.
- Developed a React dashboard and FastAPI backend for live model-health tracking, alert triage, feature-distribution inspection, and retraining workflows.
- Implemented a synthetic production simulator and retraining pipeline with versioned model artifacts to demonstrate full production ML lifecycle ownership.

## Docs

- [Project Analysis](/Users/faizan/Desktop/projects/modelsentinel/docs/project-analysis.md)
- [Architecture](/Users/faizan/Desktop/projects/modelsentinel/docs/architecture.md)
- [Roadmap](/Users/faizan/Desktop/projects/modelsentinel/docs/roadmap.md)
- [Deployment Notes](/Users/faizan/Desktop/projects/modelsentinel/docs/deployment.md)
- [Demo Script](/Users/faizan/Desktop/projects/modelsentinel/docs/demo-script.md)
