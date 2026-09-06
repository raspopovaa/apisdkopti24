from apisdkopti24.execution_budget import OperationBudget
from apisdkopti24.requests import PreparedRequest
from apisdkopti24.session import RequestContext


def prepared_request(
    method: str,
    endpoint: str,
    *,
    api_version: str = "v1",
    timeout: float = 30.0,
    retry_class: str = "safe",
    idempotent: bool | None = None,
    budget: OperationBudget | None = None,
) -> PreparedRequest:
    return PreparedRequest(
        method=method,
        endpoint=endpoint,
        api_version=api_version,
        headers={},
        query={},
        form=None,
        json_body=None,
        timeout=timeout,
        method_name="test_operation",
        retry_class=retry_class,
        idempotent=(
            method.upper() in {"GET", "HEAD", "OPTIONS"} if idempotent is None else idempotent
        ),
        request_context=RequestContext(None, None, 0),
        operation_budget=budget or OperationBudget(deadline_at=float("inf"), max_attempts=10),
    )
