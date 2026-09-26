import asyncio
import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_generator():
    path = PROJECT_ROOT / "scripts" / "generate_method_examples.py"
    spec = importlib.util.spec_from_file_location("generate_method_examples", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_committed_examples_and_pages_match_the_generator() -> None:
    generator = _load_generator()

    outputs = asyncio.run(generator.build_all())

    stale = [
        path.relative_to(PROJECT_ROOT).as_posix()
        for path, content in outputs.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]
    assert stale == [], "запустите python scripts/generate_method_examples.py"


def test_every_tutorial_page_shows_request_response_and_errors() -> None:
    pages = sorted((PROJECT_ROOT / "docs" / "examples" / "cards").glob("*.md"))
    method_pages = [page for page in pages if page.name != "index.md"]

    assert len(method_pages) == 9
    for page in method_pages:
        content = page.read_text(encoding="utf-8")
        for section in ("## Пример", "## Что отправляет SDK", "## Что возвращает API", "## Ошибки"):
            assert section in content, f"{page.name}: нет раздела {section}"
        assert "api_key: ***" in content
        assert "demo-api-key" not in content


def test_mutating_examples_ask_for_confirmation() -> None:
    generator = _load_generator()
    for name in ("block_card", "set_card_comment", "verify_pin", "reset_pin"):
        source = (PROJECT_ROOT / "examples" / "methods" / "cards" / f"{name}.py").read_text(
            encoding="utf-8"
        )
        assert "Продолжить? [yes/no]" in source
    source = (PROJECT_ROOT / "examples" / "methods" / "cards" / "get_cards_v2.py").read_text(
        encoding="utf-8"
    )
    assert "Продолжить?" not in source
    assert generator.is_read_only(generator.REGISTRY.get("get_cards_v2"))
