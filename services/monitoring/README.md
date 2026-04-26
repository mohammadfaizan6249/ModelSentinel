# Monitoring Service

This service owns the production-drift simulation and metric generation.

Implemented modules:

- `simulator/synthetic_data.py` for synthetic credit-risk populations with configurable production drift
- `simulator/engine.py` for the end-to-end monitoring state machine used by the API
- `drift/metrics.py` for PSI, KS, and histogram comparison logic
- `jobs/drift_snapshot.py` for a local snapshot CLI entrypoint

Current behavior:

- baseline and production batches are generated from different population parameters
- drift metrics are computed from raw batch values rather than seeded UI constants
- retraining updates the reference window, model version, and dashboard snapshot
