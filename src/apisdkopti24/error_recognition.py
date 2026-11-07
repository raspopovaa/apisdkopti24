"""Сборка исключения по ответу API и таблица ответов, у которых код не называет причину."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .errors import (
    _ERROR_TYPE_CLASSES,
    ERROR_HINTS,
    MAX_SERVER_MESSAGES,
    AccessDeniedError,
    APIError,
    DuplicateConflictError,
    DuplicateLoginError,
    InviteNotReadyError,
    NotAuthenticatedError,
    NotFoundError,
    ObjectNotAccessibleError,
    PlanNotPaidError,
    ProcessingRefusalError,
    RateLimitError,
    ReportFailedError,
    ServerError,
    ValidationError,
    WafBlockedError,
    api_error_message,
    normalize_error_type,
)
from .http_status import RATE_LIMIT_STATUS_CODES, RETRYABLE_STATUS_CODES

# Спецификация QR 1.0.4 описывает message элемента ошибки как string[]; для остальных
# методов сервер присылает строку, и массив там не принимается до ответа разработчиков.
QR_OPERATIONS = frozenset(
    {
        "get_mpc_qr_list",
        "generate_payment_qr",
        "init_mpc",
        "confirm_mpc",
        "update_mpc",
        "delete_mpc",
        "reset_mpc",
    }
)


def _error_item_messages(item: object, *, allow_array: bool) -> list[str]:
    if not isinstance(item, dict):
        return []
    message = item.get("message")
    if isinstance(message, str):
        return [message]
    if allow_array and isinstance(message, list):
        return [part for part in message if isinstance(part, str)]
    return []


_STATUS_CLASSES: dict[int, type[APIError]] = {
    400: ValidationError,
    401: NotAuthenticatedError,
    403: AccessDeniedError,
    404: NotFoundError,
    409: DuplicateConflictError,
    **dict.fromkeys(RATE_LIMIT_STATUS_CODES, RateLimitError),
}


def _error_class_for_status(status_code: int) -> type[APIError]:
    if status_code in _STATUS_CLASSES:
        return _STATUS_CLASSES[status_code]
    return ServerError if status_code >= 500 else APIError


def _status_code_value(raw_code: object) -> int | None:
    """Код статуса в тех же формах, что принимает модель ответа; bool кодом не является."""
    if type(raw_code) is int:
        return raw_code
    if isinstance(raw_code, float) and raw_code.is_integer():
        return int(raw_code)
    if isinstance(raw_code, str) and raw_code.strip().isascii() and raw_code.strip().isdigit():
        return int(raw_code.strip())
    return None


def api_status_code(body: Any) -> int | None:
    """Код ``status.code`` из тела ответа; ``None``, если кода нет."""
    status = body.get("status") if isinstance(body, dict) else None
    return _status_code_value(status.get("code")) if isinstance(status, dict) else None


def _parse_error_status(
    body: Any, method_name: str | None
) -> tuple[int | None, str | None, list[str]]:
    """Код API, тип первой ошибки и сообщения сервера из ``status`` тела ответа."""
    status = body.get("status") if isinstance(body, dict) else None
    if not isinstance(status, dict):
        return None, None, []
    code = _status_code_value(status.get("code"))
    errors = status.get("errors")
    if not isinstance(errors, list):
        return code, None, []
    error_type = (
        normalize_error_type(errors[0].get("type"))
        if errors and isinstance(errors[0], dict)
        else None
    )
    allow_array = method_name in QR_OPERATIONS
    server_messages = [
        message
        for item in errors[:MAX_SERVER_MESSAGES]
        for message in _error_item_messages(item, allow_array=allow_array)
    ][:MAX_SERVER_MESSAGES]
    return code, error_type, server_messages


def _effective_status_code(
    status_code: int, http_status_code: int, api_status_code: int | None
) -> int:
    """Неуспешный HTTP-код важнее кода API, неуспешный код API важнее исходного."""
    if not 200 <= http_status_code < 300:
        return http_status_code
    if api_status_code is not None and not 200 <= api_status_code < 300:
        return api_status_code
    return status_code


_PROCESSING_CODE_RE = re.compile(r"\[код ошибки:\s*(\d{1,4})\]", re.IGNORECASE)


def _normalize_text(text: str) -> str:
    return text.casefold().replace("ё", "е")


@dataclass(frozen=True, slots=True)
class _KnownResponse:
    """Строка таблицы известных ответов API, у которых HTTP-код не называет причину.

    Правило срабатывает, если класс по коду равен ``base_class``, метод входит в
    ``methods`` и действующий код в ``status_codes`` (когда они заданы), и текст сервера содержит ``fragment`` или
    совпадает с ``pattern``. Новый случай добавляется строкой и тестом на реальном
    обезличенном ответе.
    """

    reason: str
    base_class: type[APIError]
    error_class: type[APIError]
    hint: str
    fragment: str | None = None
    pattern: re.Pattern[str] | None = None
    methods: frozenset[str] | None = None
    status_codes: frozenset[int] | None = None

    def _applies_to(
        self, exc_type: type[APIError], method_name: str | None, status_code: int | None
    ) -> bool:
        return (
            exc_type is self.base_class
            and (self.methods is None or method_name in self.methods)
            and (self.status_codes is None or status_code in self.status_codes)
        )

    def matches(
        self,
        exc_type: type[APIError],
        method_name: str | None,
        server_messages: list[str],
        http_status_code: int | None = None,
    ) -> bool:
        if not self._applies_to(exc_type, method_name, http_status_code):
            return False
        for message in server_messages:
            if self.pattern is not None and self.pattern.search(message):
                return True
            if self.fragment is not None and self.fragment in _normalize_text(message):
                return True
        return False


# Порядок важен: срабатывает первая подходящая строка.
_KNOWN_RESPONSES: tuple[_KnownResponse, ...] = (
    _KnownResponse(
        reason="processing_refused",
        base_class=AccessDeniedError,
        error_class=ProcessingRefusalError,
        pattern=_PROCESSING_CODE_RE,
        hint="Отказ процессинга по карте: код отказа в processing_code, "
        "его значение смотрите в таблице кодов ответа договора.",
    ),
    _KnownResponse(
        reason="plan_not_paid",
        base_class=AccessDeniedError,
        error_class=PlanNotPaidError,
        fragment="оплатить api vip",
        hint="Метод закрыт тарифом: проверьте оплату пакета API в личном кабинете.",
    ),
    _KnownResponse(
        reason="object_not_accessible",
        base_class=AccessDeniedError,
        error_class=ObjectNotAccessibleError,
        fragment="не найден контракт, карта или группа",
        hint="Объект не найден или относится к другому договору: API отвечает так на оба "
        "случая. Проверьте ID карты, группы или договора и выбранный договор. Если ID точно "
        "верный, повторите вызов через несколько секунд: сразу после входа API изредка "
        "отвечает так же.",
    ),
    _KnownResponse(
        reason="duplicate_login",
        base_class=AccessDeniedError,
        error_class=DuplicateLoginError,
        fragment="логин пользователя уже существует",
        hint="Пользователь с таким логином уже существует: найдите его, а не создавайте заново.",
    ),
    _KnownResponse(
        reason="invite_not_ready",
        base_class=ServerError,
        error_class=InviteNotReadyError,
        fragment="приглашение не готово к отправке",
        hint="Приглашение не готово: добавьте карты или шаблон виртуальной карты. "
        "Повтор того же запроса не поможет.",
    ),
    _KnownResponse(
        reason="report_failed",
        base_class=ServerError,
        error_class=ReportFailedError,
        fragment="отчет не будет сформирован",
        hint="Формирование отчёта завершилось неудачей: закажите отчёт заново. "
        "Повтор скачивания не поможет.",
    ),
    _KnownResponse(
        reason="transfer_failed",
        base_class=ServerError,
        error_class=ServerError,
        fragment="технические проблемы",
        methods=frozenset({"move_to_card"}),
        hint="Перевод не выполнен: так API отвечает и на нехватку средств на договоре. "
        "Проверьте остаток договора и кошелька карты, прежде чем повторять перевод.",
    ),
    _KnownResponse(
        reason="group_removal_unknown",
        base_class=ServerError,
        error_class=ServerError,
        fragment="технические проблемы",
        methods=frozenset({"remove_card_group"}),
        status_codes=frozenset({500}),
        hint="Удаление группы не подтверждено: так API отвечает и на повтор после ответа "
        "шлюза, и на удаление сразу после открепления карты. Перечитайте список групп; "
        "если группа на месте, повторите удаление через 30–60 секунд.",
    ),
    _KnownResponse(
        reason="region_limit_point_id",
        base_class=ServerError,
        error_class=ServerError,
        fragment="технические проблемы",
        methods=frozenset({"set_region_limit"}),
        status_codes=frozenset({500}),
        hint="Региональный лимит не создан. Частая причина: id точки вида `-1-…`, такой API "
        "не принимает. Возьмите числовой id точки из get_azs_list_v2 и проверьте список правил "
        "перед повтором.",
    ),
    _KnownResponse(
        reason="contract_data_missing",
        base_class=ServerError,
        error_class=ServerError,
        fragment="не хватает данных по контракту",
        methods=frozenset({"create_invite"}),
        hint="Приглашение не создано: API не хватает данных по договору для этой роли. "
        "Повтор того же запроса не поможет; уточните у оператора, какие данные нужны.",
    ),
)


# Шлюз оператора отвечает 502/503/504, не дождавшись сервера, а сервер продолжает
# изменение: setRegionLimit создаёт лимит, removeCardGroup удаляет группу. Для
# изменений исход такого ответа неизвестен, и повтор может создать дубликат.
GATEWAY_STATUS_CODES = frozenset({502, 503, 504})
# Эти операции не повторяются (retry_class = never), но ничего не меняют: они только
# считают цену или проверяют покупку. Ответ шлюза для них — обычный временный сбой.
NON_MUTATING_OPERATIONS = frozenset({"get_final_prices", "check_purchase"})
_OUTCOME_UNKNOWN = _KnownResponse(
    reason="outcome_unknown",
    base_class=ServerError,
    error_class=ServerError,
    hint="Шлюз API не дождался ответа сервера: изменение могло выполниться. Проверьте "
    "состояние чтением, прежде чем повторять; повтор создающих методов даёт дубликаты.",
)

# WAF отвечает HTML-страницей, а не JSON API: сообщений сервера в ней нет.
_WAF_BLOCKED = _KnownResponse(
    reason="waf_blocked",
    base_class=AccessDeniedError,
    error_class=WafBlockedError,
    hint="Запрос остановил WAF оператора, а не API. Проверьте, что base_url оканчивается "
    "на /vip/ и путь метода верный, не меняйте User-Agent SDK; после серии входов "
    "подождите несколько минут.",
)

KNOWN_ERROR_REASONS = frozenset(
    {rule.reason for rule in _KNOWN_RESPONSES} | {_OUTCOME_UNKNOWN.reason, _WAF_BLOCKED.reason}
)


def _is_html_page(body: Any) -> bool:
    return isinstance(body, str) and "<html" in body[:2000].casefold()


def _processing_code(server_messages: list[str]) -> int | None:
    for message in server_messages:
        match = _PROCESSING_CODE_RE.search(message)
        if match:
            return int(match.group(1))
    return None


def _recognize_server_message(
    exc_type: type[APIError],
    method_name: str | None,
    server_messages: list[str],
    http_status_code: int | None = None,
) -> _KnownResponse | None:
    """Найти известный ответ сервера, если HTTP-код причину не называет."""
    return next(
        (
            rule
            for rule in _KNOWN_RESPONSES
            if rule.matches(exc_type, method_name, server_messages, http_status_code)
        ),
        None,
    )


def _recognize_response(
    exc_type: type[APIError],
    method_name: str | None,
    server_messages: list[str],
    *,
    body: Any,
    mutation: bool,
    http_status_code: int,
    status_code: int | None = None,
) -> _KnownResponse | None:
    """Правило из таблицы известных ответов, страница WAF, а для изменения — ответ шлюза."""
    if exc_type is AccessDeniedError and _is_html_page(body):
        return _WAF_BLOCKED
    # Правила сверяют действующий код (из тела при HTTP 2xx), шлюз — только HTTP-код.
    rule_status = http_status_code if status_code is None else status_code
    recognized = _recognize_server_message(exc_type, method_name, server_messages, rule_status)
    changes_state = mutation and method_name not in NON_MUTATING_OPERATIONS
    if recognized is None and changes_state and http_status_code in GATEWAY_STATUS_CODES:
        return _OUTCOME_UNKNOWN
    return recognized


def build_api_error(
    *,
    status_code: int,
    body: Any,
    endpoint: str | None,
    method_name: str | None = None,
    http_status_code: int | None = None,
    mutation: bool = False,
) -> APIError:
    """Собрать исключение по ответу API.

    ``mutation=True`` означает изменение, которое SDK не повторяет: ответ шлюза
    502/503/504 для него помечается ``context.reason == "outcome_unknown"``.
    """
    api_status_code, error_type, server_messages = _parse_error_status(body, method_name)
    resolved_http_status_code = http_status_code if http_status_code is not None else status_code
    http_failed = not 200 <= resolved_http_status_code < 300
    effective_status_code = _effective_status_code(
        status_code, resolved_http_status_code, api_status_code
    )
    hint = ERROR_HINTS.get(
        effective_status_code,
        ERROR_HINTS.get(500) if effective_status_code >= 500 else None,
    )
    transient = effective_status_code in RETRYABLE_STATUS_CODES

    # HTTP-ошибка важнее типа из тела: 2xx-тело не может смягчить неуспешный ответ.
    typed_error = None if http_failed or error_type is None else _ERROR_TYPE_CLASSES[error_type]
    exc_type = typed_error or _error_class_for_status(effective_status_code)
    status_class = _error_class_for_status(effective_status_code)
    recognized = None
    # Тип из тела может расходиться с кодом (403 с ``internalError``): правило
    # проверяется и по классу из тела, и по классу из кода.
    for candidate in dict.fromkeys((exc_type, status_class)):
        recognized = _recognize_response(
            candidate,
            method_name,
            server_messages,
            body=body,
            mutation=mutation,
            http_status_code=resolved_http_status_code,
            status_code=effective_status_code,
        )
        if recognized is not None:
            break
    reason: str | None = None
    if recognized is not None:
        exc_type = recognized.error_class
        hint = recognized.hint
        # Известный ответ означает конкретную причину, а не временный сбой.
        transient = False
        reason = recognized.reason

    error = exc_type(
        status_code=effective_status_code,
        message=api_error_message(effective_status_code),
        body=body,
        endpoint=endpoint,
        http_status_code=resolved_http_status_code,
        api_status_code=api_status_code,
        error_type=error_type,
        messages=(api_error_message(effective_status_code),),
        method_name=method_name,
        hint=hint,
        transient=transient,
        server_messages=tuple(server_messages),
        reason=reason,
    )
    if isinstance(error, ProcessingRefusalError):
        error.processing_code = _processing_code(server_messages)
    return error
