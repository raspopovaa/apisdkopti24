from __future__ import annotations

import inspect

import pytest

import apisdkopti24
from apisdkopti24 import Opti24Error

# Встроенные родители, на которые уже может опираться код приложений.
_BUILTIN_PARENTS = {
    "SDKConfigurationError": ValueError,
    "RequestValidationError": ValueError,
    "RequestPreparationError": ValueError,
    "ResponseTooLargeError": ValueError,
    "ResponseShapeError": TypeError,
    "ResponseValidationError": ValueError,
    "ContractSelectionError": ValueError,
    "PaginationLimitError": RuntimeError,
    "RetryBudgetExceededError": RuntimeError,
    "ReportWaitTimeoutError": TimeoutError,
    "OperationTimeoutError": TimeoutError,
    "FileWriteError": OSError,
}


def _exported_exceptions() -> list[type[BaseException]]:
    exported = (getattr(apisdkopti24, name) for name in apisdkopti24.__all__)
    return [
        value
        for value in exported
        if inspect.isclass(value) and issubclass(value, BaseException) and value is not Opti24Error
    ]


def test_every_exported_exception_shares_one_base() -> None:
    exceptions = _exported_exceptions()

    assert len(exceptions) >= 20
    assert [error.__name__ for error in exceptions if not issubclass(error, Opti24Error)] == []


@pytest.mark.parametrize(("name", "parent"), sorted(_BUILTIN_PARENTS.items()))
def test_exceptions_keep_builtin_parents(name: str, parent: type[BaseException]) -> None:
    assert issubclass(getattr(apisdkopti24, name), parent)


def test_network_errors_are_caught_by_common_base() -> None:
    with pytest.raises(Opti24Error):
        raise apisdkopti24.APIConnectionError("api.example.test")


def test_api_error_remains_separate_from_network_errors() -> None:
    assert not issubclass(apisdkopti24.APINetworkError, apisdkopti24.APIError)
