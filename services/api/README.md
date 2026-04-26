# API Service

The API should be the single source of truth for the dashboard.

Implemented Phase 2 endpoints:

- `GET /health`
- `GET /dashboard`
- `POST /dashboard/refresh`
- `POST /dashboard/live-tick`
- `GET /features`
- `GET /alerts`
- `GET /features/{name}/distribution`
- `GET /features/{name}/trend`
- `POST /analysis`
- `POST /retraining`
- `GET /retraining/{job_id}`

Notes:

- The current implementation uses in-memory state for fast local development.
- CORS is enabled for the Vite frontend on `localhost:5173`.
- Retraining is modeled as a pollable job so the UI can show progress updates without browser-side fake state.
