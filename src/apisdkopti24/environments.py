from __future__ import annotations

from urllib.parse import urlsplit

from .policies import RateLimitPolicy

DEMO_API_HOST = "api-demo.opti-24.ru"
DEMO_REQUESTS_PER_SECOND = 2.0
PRODUCTION_REQUESTS_PER_SECOND = 5.0


def resolve_rate_limit_policy(base_url: str, policy: RateLimitPolicy) -> RateLimitPolicy:
    """Resolve the documented default without coupling transport to environment names."""
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
