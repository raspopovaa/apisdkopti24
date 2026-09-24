from pathlib import Path
from typing import NoReturn

import pytest

from apisdkopti24.errors import FileWriteError
from apisdkopti24.file_io import AtomicFileWriter


@pytest.mark.asyncio
async def test_atomic_writer_does_not_reopen_replaceable_temporary_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "report.bin"
    protected_file = tmp_path / "protected.bin"
    protected_file.write_bytes(b"protected")
    attacker_link = tmp_path / ".report.bin.attacker.part"
    attacker_link.symlink_to(protected_file)

    monkeypatch.setattr(
        AtomicFileWriter,
        "_temporary_path",
        staticmethod(lambda _destination: attacker_link),
        raising=False,
    )

    writer = AtomicFileWriter()
    await writer.write_bytes(destination, b"download")

    assert protected_file.read_bytes() == b"protected"
    assert destination.read_bytes() == b"download"


@pytest.mark.asyncio
async def test_atomic_writer_wraps_os_error_without_exposing_destination(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "private-contract-report.bin"

    def fail_to_create(_destination: Path) -> NoReturn:
        raise PermissionError(str(destination))

    monkeypatch.setattr(
        AtomicFileWriter,
        "_temporary_file",
        staticmethod(fail_to_create),
    )

    with pytest.raises(FileWriteError) as captured:
        await AtomicFileWriter().write_bytes(destination, b"payload")

    assert str(destination) not in str(captured.value)
