# Единый список проверок: его запускают разработчик и CI.
# Все проверки: uv run make check. Отдельные группы: uv run make lint types.

CODE_PATHS := src tests scripts tools typecheck

.PHONY: check lint types tests contracts docs

check: lint types tests contracts docs

lint:
	ruff check $(CODE_PATHS)
	black --check $(CODE_PATHS)

types:
	mypy src/apisdkopti24 typecheck examples/methods
	mypy tests
	pyright src/apisdkopti24
	pyright --verifytypes apisdkopti24 --ignoreexternal

tests:
	pytest --cov=apisdkopti24 --cov-branch --cov-report=term-missing

contracts:
	python scripts/verify_external_contract.py specifications/api-methods.yaml
	python scripts/verify_api_contract.py specifications/api-contract-v1.1.60.yaml
	python scripts/audit_spec_contract.py --mode verified
	python scripts/generate_request_metadata.py --check
	python scripts/generate_method_examples.py --check
	python scripts/export_request_models.py --check
	python scripts/export_request_matrix.py --check
	python scripts/export_model_matrix.py --check

docs:
	python scripts/generate_docs.py
	mkdocs build --strict
