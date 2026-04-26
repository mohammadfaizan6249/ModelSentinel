# ModelSentinel Architecture

## Core Flow

1. A simulator creates production-like batches with controlled feature drift.
2. The monitoring service compares current batches against a stored baseline.
3. Drift metrics are saved and exposed through the API.
4. The web dashboard fetches those metrics and renders alerts, charts, and model health.
5. A retraining job rebuilds the model and publishes a new version when triggered.

## Components

### `apps/web`

Owns the operator dashboard:

- feature drift table
- distribution comparison
- PSI trend chart
- retraining trigger modal
- AI incident analysis panel

### `services/api`

Owns application APIs:

- `GET /health`
- `GET /features`
- `GET /alerts`
- `GET /metrics/{feature_name}`
- `POST /retraining`
- `GET /retraining/{job_id}`

### `services/monitoring`

Owns background jobs:

- synthetic production stream generation
- PSI / KS calculation
- threshold evaluation
- alert snapshot creation

### `ml`

Owns offline ML logic:

- dataset preparation
- feature engineering
- model training
- evaluation reports
- model version metadata

## Data Contracts

Each feature metric should include:

- `name`
- `psi`
- `ks`
- `status`
- `trend`
- `baseline_distribution`
- `current_distribution`
- `trend_series`
- `last_updated_at`

## Technical Decisions

- Use Python for drift math and retraining because it aligns with ML workflows.
- Use React for the frontend because it is easier to present as a polished product.
- Keep the first version synchronous and local-first.
- Add persistence later if needed instead of starting with heavy infrastructure.
