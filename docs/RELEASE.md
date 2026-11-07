---
description: Контрольный список проверки, сборки и публикации новой версии apisdkopti24.
---

# Выпуск версии

## Перед началом

- Выпускать из ветки `main` с чистым рабочим деревом: workflow публикации запускается только из
  `main`. Не включать посторонние изменения.
- Определить номер версии по [политике совместимости](versioning.md#compatibility): до 1.0.0
  несовместимое изменение возможно в любом выпуске и отмечается в CHANGELOG разделом
  «Несовместимые изменения»; с 1.0.0 — SemVer.
- Убедиться, что версия одинакова в `pyproject.toml`, `apisdkopti24.__version__`, документации и теге.
- Для изменений контрактов указать версии основной и QR-спецификаций.

## Обязательные проверки

```bash
uv sync --extra dev
uv run pytest --cov=apisdkopti24 --cov-branch --cov-report=term-missing
uv run ruff check src tests scripts tools
uv run black --check src tests scripts tools
uv run mypy src/apisdkopti24 typecheck examples/methods
uv run pyright src/apisdkopti24
uv run pyright --verifytypes apisdkopti24 --ignoreexternal
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
   `promote_run_id`: номером запуска, который опубликовал пакет в TestPyPI.
   Workflow проверяет, что тот запуск был из `main` и его smoke-тест прошёл,
   скачивает его artifact (GitHub хранит его по умолчанию до 90 дней) и публикует его в PyPI без
   пересборки. Сборка, TestPyPI и smoke-тест в таком запуске пропускаются.
5. Сразу после успешной публикации создать аннотированный tag `vX.Y.Z` на том
   commit SHA, из которого workflow собрал пакет (он указан в запуске workflow и в
   подтверждении происхождения на PyPI), и GitHub Release с разделом версии из
   CHANGELOG:

   ```bash
   git tag -a vX.Y.Z <commit-sha> -m "apisdkopti24 X.Y.Z"
   git push origin vX.Y.Z
   gh release create vX.Y.Z --verify-tag --title "apisdkopti24 X.Y.Z" --notes-file notes.md
   ```

   Без тега пакет на PyPI нельзя сопоставить с исходным кодом в репозитории.

Токены не передавать в командной строке и не сохранять в `.env`, логах или workflow. При утечке токен отозвать.

## Проверка после публикации

В новой виртуальной среде установите точную версию с PyPI и проверьте импорт и
версию; затем выполните пример без тарифицируемых вызовов на DEMO:

```bash
python -m venv /tmp/sdk-check && /tmp/sdk-check/bin/pip install apisdkopti24==X.Y.Z
/tmp/sdk-check/bin/python -c "import apisdkopti24; print(apisdkopti24.__version__)"
```

Затем проверьте вход и чтение на DEMO. Проверка намеренно не запускает
`examples/non_billable_real_api.py`: в нём есть методы, недоступные на DEMO, и вызовы,
которые тарифицируются на рабочем API. Здесь только методы, у которых в каталоге
`demo_available: true` и `billable: false`: `auth_user`, `get_info`, `get_limits`, `logoff`.

Файл `.env` с настройками DEMO положите в текущий каталог. Команда `env -i` запускает
Python без переменных окружения шелла, поэтому `API_*` из вашей сессии (например,
настройки рабочего API) не попадут в проверку. Адрес проверяется до первого запроса.

```bash
cat > check_demo.py <<'PY'
import asyncio
from pathlib import Path

from apisdkopti24 import APIClient, ConnectionSettings, EnvironmentCredentialsProvider

ENV = Path(".env")
settings = ConnectionSettings.from_env(env_file=ENV)
assert "api-demo.opti-24.ru" in settings.base_url, settings.base_url


async def main() -> None:
    credentials = EnvironmentCredentialsProvider.from_env(env_file=ENV)
    async with APIClient(settings=settings, credentials_provider=credentials) as client:
        await client.auth.auth_user()
        await client.auth.get_info()
        await client.limits.get_limits()
        await client.auth.logoff()


asyncio.run(main())
PY
env -i HOME="$HOME" PATH="$PATH" /tmp/sdk-check/bin/python check_demo.py && echo "Проверка пройдена"
```

Если любой шаг падает, скрипт завершается с ошибкой и «Проверка пройдена» не печатается.
Если у договора несколько, `auth_user` вернёт ошибку выбора договора: тогда проверка
остановится, и это нужно учесть вручную.

## Откат

PyPI не позволяет перезаписать опубликованный файл, поэтому откат — это пометка
версии и следующий патч.

Когда откатывать:

- пакет не устанавливается или не импортируется;
- основной сценарий (вход, чтение договора, карт или операций) падает на DEMO;
- в пакет попал секрет или персональные данные.

Если в пакет попал секрет или персональные данные, сначала:

1. Отозвать секрет (ключ, пароль, токен) до любых действий с пакетом: пометка версии
   его не обезвреживает.
2. Удалить файлы версии, а не только пометить её: **Manage project → Releases →
   X.Y.Z → Options → Delete**. Yank здесь не подходит: отозванную версию по-прежнему
   можно установить с `==X.Y.Z`. Если копии могли разойтись по зеркалам, сообщить
   в службу безопасности PyPI (security@pypi.org).
3. Выпустить исправленную следующую версию.

В остальных случаях (дефект без утечки):

1. Пометить версию как отозванную (yank) на странице управления пакетом PyPI:
   **Manage project → Releases → X.Y.Z → Options → Yank**, указав причину.
   Закреплённые установки `==X.Y.Z` продолжат работать, новые установки без
   версии получат предыдущую.
2. В GitHub Release отметить проблему в описании; тег не удалять, чтобы версию
   можно было сопоставить с кодом.
3. Выпустить исправленную следующую версию и описать влияние в CHANGELOG.
