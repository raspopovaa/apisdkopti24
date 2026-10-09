---
description: Контрольный список проверки, сборки и публикации новой версии apisdkopti24.
---

# Выпуск версии

## Перед началом

- Выпускать из ветки `main` с чистым рабочим деревом: workflow публикации запускается только из
  `main`. Не включать посторонние изменения.
- Определить SemVer: patch — совместимое исправление, minor — совместимая возможность, major — несовместимый API.
- Убедиться, что версия одинакова в `pyproject.toml`, `apisdkopti24.__version__`, документации и теге.
- Для изменений контрактов указать версии основной и QR-спецификаций.

## Обязательные проверки

```bash
uv sync --extra dev
uv run pytest --cov=apisdkopti24 --cov-branch --cov-report=term-missing
uv run ruff check src tests scripts tools
uv run black --check src tests scripts tools
uv run mypy src/apisdkopti24 typecheck examples/methods
uv run python scripts/verify_external_contract.py specifications/api-methods.yaml
uv run python scripts/verify_api_contract.py specifications/api-contract-v1.1.60.yaml
uv run python scripts/audit_spec_contract.py --mode verified
uv run python scripts/generate_request_metadata.py --check
uv run python scripts/generate_docs.py
uv run python scripts/generate_method_examples.py
uv run python scripts/export_request_models.py --check
uv run python scripts/export_request_matrix.py --check
uv run python scripts/export_model_matrix.py --check
uv run mkdocs build --strict
git status --short
uv build
```

После `generate_docs.py` и `generate_method_examples.py` команда `git status --short`
не должна показывать изменений: сгенерированные страницы, примеры и экспорты
(`request-models`, `request-matrix`, `model-matrix`) должны быть закоммичены в
актуальном виде.

Проверить wheel/sdist в новой виртуальной среде: установка, импорт, `__version__` и минимальный пример без реального сетевого запроса.

## Документация

Обновить `README.md`, `PROJECT.md`, `CHANGELOG.md`, заметки о совместимости при breaking changes, каталог методов и типы данных. Сверить, что QR-статус не описан как реализованный без тестируемого кода.

## Публикация

1. Вручную запустить `Publish TestPyPI and PyPI` (`workflow_dispatch`) для
   проверенного commit SHA из защищённой ветки `main`. Workflow отклоняет запуск
   с другой ветки; pull request не должен публиковать пакет.
2. Workflow один раз собирает artifact и публикует его в TestPyPI.
3. Отдельный job устанавливает точную версию из TestPyPI и выполняет smoke test
   без production credentials.
4. После подтверждения environment `pypi` тот же artifact без пересборки
   публикуется в PyPI через OIDC. Это происходит в том же запуске, если
   включён флаг `publish_pypi`.

   Чтобы опубликовать в PyPI позже, повторно запустите workflow с полем
   `promote_run_id` — номером запуска, который опубликовал пакет в TestPyPI.
   Workflow проверяет, что тот запуск был из `main` и его smoke-тест прошёл,
   скачивает его artifact (GitHub хранит его по умолчанию до 90 дней) и публикует его в PyPI без
   пересборки. Сборка, TestPyPI и smoke-тест в таком запуске пропускаются.
5. После успешной публикации создать подписанный/аннотированный tag и GitHub Release.

Токены не передавать в командной строке и не сохранять в `.env`, логах или workflow. При утечке токен отозвать.

## Откат

Опубликованный файл версии не перезаписывать. При дефекте остановить продвижение, пометить релиз, выпустить исправленную следующую версию и документировать влияние. Компрометированный секрет отозвать независимо от удаления файла из Git.
