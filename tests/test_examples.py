from pathlib import Path


def test_async_demo_compiles() -> None:
    example_path = Path(__file__).resolve().parents[1] / "examples" / "demo_async.py"
    source = example_path.read_text(encoding="utf-8")

    compile(source, str(example_path), "exec")
