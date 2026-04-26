bootstrap:
	chmod +x scripts/bootstrap.sh && ./scripts/bootstrap.sh

run-api:
	cd services/api && ../../.venv/bin/python -m uvicorn app.main:app --reload

run-monitor:
	PYTHONPATH=$(PWD) ./.venv/bin/python -B services/monitoring/jobs/drift_snapshot.py

run-web:
	npm run dev:web

test:
	./scripts/check_all.sh
