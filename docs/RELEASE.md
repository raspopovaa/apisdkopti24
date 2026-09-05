# Выпуск версии

## Перед началом

- Работать из чистой release-ветки; не включать посторонние изменения.
- Определить SemVer: patch — совместимое исправление, minor — совместимая возможность, major — несовместимый API.
- Убедиться, что версия одинакова в `pyproject.toml`, `api_client_opti24.__version__`, документации и теге.
- Для изменений контрактов указать версии основной и QR-спецификаций.

## Обязательные проверки

```bash
uv sync --extra dev
uv run pytest --cov=api_client_opti24 --cov-branch --cov-report=term-missing
uv run ruff check src tests scripts tools
uv run black --check src tests scripts tools
uv run mypy src/api_client_opti24
uv run python scripts/verify_external_contract.py specifications/api-methods.yaml
uv run python scripts/verify_api_contract.py specifications/api-contract-v1.1.60.yaml
uv run python scripts/audit_spec_contract.py --mode verified
uv build
```

Проверить wheel/sdist в новой виртуальной среде: установка, импорт, `__version__` и минимальный пример без реального сетевого запроса.

## Документация

Обновить `README.md`, `PROJECT.md`, `CHANGELOG.md`, migration guide при breaking changes, каталог методов и типы данных. Сверить, что QR-статус не описан как реализованный без тестируемого кода.

## Публикация

1. Опубликовать в TestPyPI только из утверждённого CI/workflow.
2. Установить точную версию из TestPyPI с зависимостями из основного PyPI.
3. Выполнить smoke test без production credentials.
4. После одобрения создать подписанный/аннотированный tag и GitHub Release.
5. Публикация в PyPI или production выполняется только по отдельному подтверждению.

Токены не передавать в командной строке и не сохранять в `.env`, логах или workflow. При утечке токен отозвать.

## Откат

Опубликованный файл версии не перезаписывать. При дефекте остановить продвижение, пометить релиз, выпустить исправленную следующую версию и документировать влияние. Компрометированный секрет отозвать независимо от удаления файла из Git.
