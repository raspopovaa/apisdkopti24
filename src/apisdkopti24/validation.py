"""Проверка параметров публичных методов до отправки запроса.

Каждая функция либо возвращает нормализованное значение (обычно с обрезанными
пробелами), либо поднимает :class:`~apisdkopti24.errors.RequestValidationError`
с понятным текстом. Ошибка до сети не тратит запросы из пакета договора.
"""

from __future__ import annotations

import calendar
import re
from collections.abc import Collection, Sequence
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import TypeVar

from .errors import RequestValidationError

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DocumentFormatT = TypeVar("DocumentFormatT", bound=str)
ModelT = TypeVar("ModelT")


def _require_str(value: object, field_name: str) -> str:
    """Убедиться, что значение — строка.

    Защищает от ``None`` или числа там, где тип в аннотации не проверяется во время
    выполнения.

    :param value: Значение из аргумента метода.
    :param field_name: Имя параметра для текста ошибки.
    :return: То же значение.
    :raises RequestValidationError: Значение не строка.
    """
    if not isinstance(value, str):
        raise RequestValidationError(f"{field_name}: ожидается строка")
    return value


def validate_non_empty_value(value: str, field_name: str) -> str:
    """Проверить, что строка непустая после обрезки пробелов.

    :param value: Значение из аргумента метода.
    :param field_name: Имя параметра для текста ошибки.
    :return: Строка без пробелов по краям.
    :raises RequestValidationError: Не строка или пустая строка.
    """
    normalized = _require_str(value, field_name).strip()
    if not normalized:
        raise RequestValidationError(f"{field_name}: значение не может быть пустым")
    return normalized


def require_identifier(value: str, field_name: str) -> str:
    """Проверить идентификатор (карты, группы, договора и т. п.).

    Сейчас правило то же, что у :func:`validate_non_empty_value`; отдельное имя
    оставлено, чтобы в методах было видно, что проверяется именно идентификатор.

    :param value: Идентификатор из аргумента метода.
    :param field_name: Имя параметра для текста ошибки.
    :return: Идентификатор без пробелов по краям.
    :raises RequestValidationError: Не строка или пустая строка.
    """
    return validate_non_empty_value(value, field_name)


def validate_identifier_list(values: Sequence[str], field_name: str) -> list[str]:
    """Проверить непустой список идентификаторов.

    Отдельно отклоняет одну строку: ``str`` тоже последовательность, и без этой
    проверки ``"card-1"`` ушёл бы на сервер шестью «идентификаторами».

    :param values: Список идентификаторов.
    :param field_name: Имя параметра для текста ошибки.
    :return: Новый список идентификаторов без пробелов по краям.
    :raises RequestValidationError: Передана строка, список пуст или элемент пустой.
    """
    # str тоже является Sequence[str]: без проверки "card-1" ушёл бы списком из шести символов.
    if isinstance(values, str):
        raise RequestValidationError(f"{field_name}: ожидается список идентификаторов, а не строка")
    if not values:
        raise RequestValidationError(f"{field_name}: необходим хотя бы один элемент")
    return [require_identifier(value, field_name) for value in values]


def validate_model_sequence(
    values: Sequence[object],
    model_type: type[ModelT],
    field_name: str,
) -> list[ModelT]:
    """Проверить непустой список моделей запроса одного типа.

    :param values: Элементы пакета (например, лимиты для установки).
    :param model_type: Ожидаемый класс модели.
    :param field_name: Имя параметра для текста ошибки.
    :return: Новый список тех же объектов.
    :raises RequestValidationError: Список пуст или элемент другого типа (в тексте его индекс).
    """
    if not values:
        raise RequestValidationError(f"{field_name}: необходим хотя бы один элемент")
    validated: list[ModelT] = []
    for index, value in enumerate(values):
        if not isinstance(value, model_type):
            raise RequestValidationError(
                f"{field_name}[{index}] должен быть экземпляром {model_type.__name__}"
            )
        validated.append(value)
    return validated


def validate_card_or_group_target(
    *,
    card_id: str | None,
    group_id: str | None,
    required: bool = False,
) -> tuple[str | None, str | None]:
    """Проверить цель правила: карта или группа, но не обе сразу.

    :param card_id: Идентификатор карты или ``None``.
    :param group_id: Идентификатор группы или ``None``.
    :param required: Нужна ли цель обязательно.
    :return: Пара ``(card_id, group_id)`` без пробелов по краям; одно из значений ``None``.
    :raises RequestValidationError: Заданы оба идентификатора, ни одного при ``required``
        или идентификатор пустой.
    """
    normalized_card = require_identifier(card_id, "card_id") if card_id is not None else None
    normalized_group = require_identifier(group_id, "group_id") if group_id is not None else None
    if normalized_card is not None and normalized_group is not None:
        raise RequestValidationError("card_id и group_id нельзя задавать одновременно")
    if required and normalized_card is None and normalized_group is None:
        raise RequestValidationError("Необходимо указать card_id или group_id")
    return normalized_card, normalized_group


def validate_date_range(
    date_start: str,
    date_end: str,
    *,
    start_name: str = "date_start",
    end_name: str = "date_end",
) -> tuple[str, str]:
    """Проверить формат ``YYYY-MM-DD`` и порядок двух дат.

    :param date_start: Дата начала.
    :param date_end: Дата конца; может совпадать с началом.
    :param start_name: Имя параметра начала для текста ошибки.
    :param end_name: Имя параметра конца для текста ошибки.
    :return: Исходные строки без изменений: на сервер уходит то, что передал пользователь.
    :raises RequestValidationError: Неверный формат, несуществующая дата или конец раньше начала.
    """
    start = parse_iso_date(date_start, start_name)
    end = parse_iso_date(date_end, end_name)
    if end < start:
        raise RequestValidationError(f"{end_name} не может предшествовать {start_name}")
    return date_start, date_end


# Строго YYYY-MM-DD ASCII-цифрами: date.fromisoformat в Python 3.11+ принимает и
# 20260901, и 2026-W36-1, а на сервер уходит исходная строка.
_ISO_DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def parse_iso_date(value: str, field_name: str) -> date:
    """Разобрать дату ``YYYY-MM-DD``; другие формы ISO 8601 не принимаются."""
    if not isinstance(value, str) or not _ISO_DATE_PATTERN.fullmatch(value):
        raise RequestValidationError(f"{field_name}: ожидается дата в формате YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RequestValidationError(f"{field_name}: такой даты не существует") from exc


def _add_months(value: date, months: int) -> date:
    """Прибавить календарные месяцы; день прижимается к концу месяца.

    31 января плюс 1 месяц даёт 28 (или 29) февраля, а не ошибку.

    :param value: Исходная дата.
    :param months: Число месяцев, не меньше нуля.
    :return: Дата через ``months`` месяцев.
    """
    month_index = value.month - 1 + months
    year, month = value.year + month_index // 12, month_index % 12 + 1
    return date(year, month, min(value.day, calendar.monthrange(year, month)[1]))


def validate_period_months(
    date_start: str,
    date_end: str,
    *,
    months: int,
    start_name: str,
    end_name: str,
) -> tuple[str, str]:
    """Проверить формат, порядок дат и длину периода в календарных месяцах.

    Конец периода может совпадать с той же датой через ``months`` месяцев: пример
    спецификации заказывает отчёт с 2022-11-01 по 2022-12-01. Длиннее сервер не
    отклоняет, а молча сокращает период.
    """
    validate_date_range(date_start, date_end, start_name=start_name, end_name=end_name)
    start, end = parse_iso_date(date_start, start_name), parse_iso_date(date_end, end_name)
    if end > _add_months(start, months):
        raise RequestValidationError(
            f"Период {start_name}–{end_name} длиннее {months} календарн"
            f"{'ого месяца' if months == 1 else 'ых месяцев'}"
        )
    return date_start, date_end


def validate_month_span(date_from: str, date_to: str) -> None:
    """Проверить порядок дат и предел интервала в днях.

    Предел равен числу дней в месяце date_from; конец интервала может
    находиться в следующем календарном месяце.
    """
    d_from = parse_iso_date(date_from, "date_from")
    d_to = parse_iso_date(date_to, "date_to")
    if d_to < d_from:
        raise RequestValidationError("date_to не может быть меньше date_from")

    days_in_month = calendar.monthrange(d_from.year, d_from.month)[1]
    if (d_to - d_from).days > days_in_month:
        raise RequestValidationError(f"Разница между датами превышает {days_in_month} дней")


def validate_choice(value: str | None, allowed: Collection[str], field_name: str) -> None:
    """Проверить, что значение входит в допустимый набор.

    :param value: Значение или ``None`` (тогда проверки нет).
    :param allowed: Допустимые значения.
    :param field_name: Имя параметра для текста ошибки.
    :raises RequestValidationError: Значение не из набора; в тексте перечислены допустимые.
    """
    if value is not None and value not in allowed:
        raise RequestValidationError(f"{field_name} должен быть одним из: {', '.join(allowed)}")


def validate_sort_fields(sort: str | None, allowed: Collection[str], owner: str) -> str | None:
    """Проверить строку ``sort`` вида ``field,-other`` по допустимым полям ответа."""
    if sort is None:
        return None
    fields = [part.strip() for part in _require_str(sort, "sort").split(",")]
    for field in fields:
        if field.removeprefix("-") not in allowed:
            raise RequestValidationError(
                f"sort: у {owner} нет поля {field.removeprefix('-')!r}; допустимые поля: "
                f"{', '.join(sorted(allowed))}; «-» перед полем: по убыванию"
            )
    return ",".join(fields)


# ASCII-цифры: \d пропускает и другие цифры Юникода, которые сервер отклонит.
_MOBILE_PATTERN = re.compile(r"[0-9]{11,13}")


def validate_mobile(value: str, field_name: str = "mobile") -> str:
    """Телефон-логин: только цифры, 11–13 знаков, без ``+``: иначе сервер отвечает 400."""
    normalized = _require_str(value, field_name).strip()
    if not _MOBILE_PATTERN.fullmatch(normalized):
        raise RequestValidationError(f"{field_name}: ожидается 11–13 цифр без «+» и пробелов")
    return normalized


def validate_email_list(values: Sequence[str], field_name: str) -> list[str]:
    """Проверить непустой список адресов почты.

    :param values: Адреса; одна строка вместо списка отклоняется.
    :param field_name: Имя параметра; в тексте ошибки к нему добавляется индекс адреса.
    :return: Адреса без пробелов по краям.
    :raises RequestValidationError: Строка вместо списка, пустой список или неверный адрес.
    """
    if isinstance(values, str) or not values:
        raise RequestValidationError(f"{field_name}: ожидается непустой список адресов")
    return [validate_email(value, f"{field_name}[{index}]") for index, value in enumerate(values)]


def validate_pagination(page: int, on_page: int) -> tuple[int, int]:
    """Проверить постраничный вывод ``page``/``on_page`` (нумерация с 1).

    :param page: Номер страницы, больше нуля.
    :param on_page: Размер страницы, больше нуля.
    :return: Пара ``(page, on_page)`` без изменений.
    :raises RequestValidationError: Номер или размер страницы не больше нуля.
    """
    if page <= 0:
        raise RequestValidationError("page должен быть больше нуля")
    if on_page <= 0:
        raise RequestValidationError("on_page должен быть больше нуля")
    return page, on_page


def validate_offset_pagination(limit: int, offset: int) -> tuple[int, int]:
    """Проверить вывод через ``limit``/``offset``.

    :param limit: Сколько записей вернуть, больше нуля.
    :param offset: Сколько записей пропустить, не меньше нуля.
    :return: Пара ``(limit, offset)`` без изменений.
    :raises RequestValidationError: ``limit`` не больше нуля или ``offset`` отрицательный.
    """
    if limit <= 0:
        raise RequestValidationError("limit должен быть больше нуля")
    if offset < 0:
        raise RequestValidationError("offset не может быть отрицательным")
    return limit, offset


def validate_positive_count(count: int) -> int:
    """Проверить положительное количество (например, карт в заказе).

    :param count: Количество.
    :return: То же количество.
    :raises RequestValidationError: Значение не больше нуля.
    """
    if count <= 0:
        raise RequestValidationError("count должен быть больше нуля")
    return count


def decimal_to_wire(value: Decimal, field_name: str = "amount") -> str:
    """Проверить денежную сумму и записать её строкой для запроса.

    Сумма должна быть конечной, больше нуля и не точнее копейки: ``10.500``
    допустимо, ``10.005`` нет, потому что доли копейки сервер мог бы округлить
    по-своему. Строка без экспоненты, чтобы ``1E+3`` не ушло на сервер.

    :param value: Сумма в рублях (``Decimal`` или то, что ``Decimal`` примет).
    :param field_name: Имя параметра для текста ошибки.
    :return: Сумма в десятичной записи, например ``"10.50"``.
    :raises RequestValidationError: Не число, не больше нуля, точнее копейки или слишком
        большое для точности ``Decimal``.
    """
    try:
        normalized = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RequestValidationError(
            f"{field_name}: ожидается корректное десятичное число"
        ) from exc
    if not normalized.is_finite() or normalized <= 0:
        raise RequestValidationError(f"{field_name}: значение должно быть больше нуля")
    # Денежные суммы задаются в рублях с копейками: доли копейки сервер мог бы округлить
    # или отбросить по-своему. 10.500 допустимо, 10.005: нет.
    try:
        in_kopecks = normalized.quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        # quantize не укладывается в точность контекста Decimal (28 значащих цифр).
        raise RequestValidationError(f"{field_name}: слишком большое значение") from exc
    if normalized != in_kopecks:
        raise RequestValidationError(f"{field_name}: не больше двух знаков после запятой (копейки)")
    return format(normalized, "f")


def validate_email(value: str, field_name: str = "email") -> str:
    """Проверить адрес почты простым шаблоном ``имя@домен.зона``.

    Это защита от опечаток, а не полная проверка RFC 5322: сервер может отклонить
    адрес, который здесь прошёл.

    :param value: Адрес.
    :param field_name: Имя параметра для текста ошибки.
    :return: Адрес без пробелов по краям.
    :raises RequestValidationError: Не строка или адрес не похож на почту.
    """
    normalized = _require_str(value, field_name).strip()
    if not _EMAIL_PATTERN.fullmatch(normalized):
        raise RequestValidationError(f"{field_name}: ожидается корректный адрес электронной почты")
    return normalized


def validate_document_order(
    document_ids: list[str],
    document_format: DocumentFormatT,
    emails: list[str],
) -> tuple[list[str], DocumentFormatT, list[str]]:
    """Проверить заказ закрывающих документов на почту.

    :param document_ids: Непустой список идентификаторов документов.
    :param document_format: ``"pdf"`` или ``"xlsx"``.
    :param emails: От 1 до 5 адресов.
    :return: Кортеж ``(идентификаторы, формат, адреса)`` после нормализации.
    :raises RequestValidationError: Пустой список документов, другой формат, 0 или больше
        5 адресов или неверный адрес.
    """
    normalized_ids = validate_identifier_list(document_ids, "Идентификаторы документов")
    if document_format not in {"pdf", "xlsx"}:
        raise RequestValidationError("fmt должен быть равен 'pdf' или 'xlsx'")
    if not emails or len(emails) > 5:
        raise RequestValidationError("emails должен содержать от 1 до 5 адресов")
    normalized_emails = [validate_email(value, "email") for value in emails]
    return normalized_ids, document_format, normalized_emails


__all__ = [
    "decimal_to_wire",
    "require_identifier",
    "validate_card_or_group_target",
    "validate_choice",
    "validate_date_range",
    "validate_document_order",
    "validate_email",
    "validate_email_list",
    "validate_identifier_list",
    "validate_mobile",
    "validate_model_sequence",
    "validate_non_empty_value",
    "validate_offset_pagination",
    "validate_pagination",
    "validate_period_months",
    "validate_positive_count",
    "parse_iso_date",
    "validate_sort_fields",
]
