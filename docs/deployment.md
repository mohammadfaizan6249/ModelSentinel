# Deployment Notes

## Local Demo

The easiest deployment story for interviews is:

1. Run the FastAPI API locally from the project virtual environment.
2. Run the Vite frontend locally and point it at `http://127.0.0.1:8000`.
3. Demo live drift updates, feature inspection, and the retraining flow.

## Simple Hosting Split

- Frontend: Vercel or Netlify
- API: Render, Railway, or Fly.io

Recommended environment variable for the hosted frontend:

- `VITE_API_URL=https://your-api-host.example.com`

## What To Say In Interviews

- The frontend is a thin client; the backend owns drift state, analysis results, and retraining jobs.
- Drift metrics are computed from synthetic reference and production batches using PSI and KS.
- Retraining produces versioned model artifacts and updates the serving reference window.
