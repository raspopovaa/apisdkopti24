import httpx

from apisdkopti24 import AsyncTransport


def inject_http_client() -> AsyncTransport:
    # Документированный способ: свой httpx.AsyncClient (прокси, CA, trust_env).
    return AsyncTransport("https://api.example.test", http_client=httpx.AsyncClient())
