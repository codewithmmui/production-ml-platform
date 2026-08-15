PYTHON ?= python3
.PHONY: install lint format typecheck test coverage generate-data train serve docker-up docker-down smoke-test
install:
	$(PYTHON) -m pip install -e '.[dev]'
lint:
	ruff check .
format:
	ruff format .
typecheck:
	mypy src
test:
	pytest
coverage:
	pytest --cov=ml_platform --cov-report=term-missing
generate-data:
	$(PYTHON) -m ml_platform.data.generate --rows 10000 --seed 42 --output data/raw/customers.csv
train:
	$(PYTHON) -m ml_platform.training.train --data data/raw/customers.csv --output artifacts
serve:
	uvicorn ml_platform.api.main:app --host 0.0.0.0 --port 8000
docker-up:
	docker compose up --build
docker-down:
	docker compose down
smoke-test:
	./scripts/smoke_test.sh
