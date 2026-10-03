from __future__ import annotations

from urllib.parse import urlsplit

from .policies import RateLimitPolicy

DEMO_API_HOST = "api-demo.opti-24.ru"
# Спецификация заявляет 2 и 5 запросов/с, но сервер отвечает 509 уже примерно на
# четверть запросов при 2 запросах/с; при 1 запросе/с ответов 509 не было.
DEMO_REQUESTS_PER_SECOND = 1.0
PRODUCTION_REQUESTS_PER_SECOND = 1.0


def resolve_rate_limit_policy(base_url: str, policy: RateLimitPolicy) -> RateLimitPolicy:
    """Выбрать стандартную частоту запросов для среды независимо от транспорта."""
    if policy.requests_per_second is not None:
        return policy
    hostname = urlsplit(base_url).hostname
    requests_per_second = (
        DEMO_REQUESTS_PER_SECOND if hostname == DEMO_API_HOST else PRODUCTION_REQUESTS_PER_SECOND
    )
    return RateLimitPolicy(requests_per_second=requests_per_second)


__all__ = [
    "DEMO_API_HOST",
    "DEMO_REQUESTS_PER_SECOND",
    "PRODUCTION_REQUESTS_PER_SECOND",
    "resolve_rate_limit_policy",
]
