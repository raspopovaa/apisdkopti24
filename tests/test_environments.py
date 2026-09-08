from apisdkopti24.environments import (
    DEMO_REQUESTS_PER_SECOND,
    PRODUCTION_REQUESTS_PER_SECOND,
    resolve_rate_limit_policy,
)
from apisdkopti24.policies import RateLimitPolicy


def test_environment_rate_limit_defaults_are_resolved_outside_transport() -> None:
    demo = resolve_rate_limit_policy(
        "https://api-demo.opti-24.ru/vip/",
        RateLimitPolicy(),
    )
    production = resolve_rate_limit_policy(
        "https://api.opti-24.ru/vip/",
        RateLimitPolicy(),
    )

    assert demo.requests_per_second == DEMO_REQUESTS_PER_SECOND
    assert production.requests_per_second == PRODUCTION_REQUESTS_PER_SECOND


def test_explicit_rate_limit_is_not_overridden_by_environment_default() -> None:
    configured = RateLimitPolicy(requests_per_second=1.5)

    assert resolve_rate_limit_policy("https://api-demo.opti-24.ru/vip/", configured) is configured
