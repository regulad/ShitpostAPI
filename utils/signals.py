from aiohttp import web


async def set_ratelimit_headers(request: web.Request, response: web.Response) -> None:
    """Set the rate-limit headers into the response field."""

    response.headers["X-RateLimit-Limit"] = str(request.get("X-RateLimit-Limit"))
    response.headers["X-RateLimit-Remaining"] = str(request.get("X-RateLimit-Remaining"))
    response.headers["X-RateLimit-Reset"] = str(request.get("X-RateLimit-Reset"))


ON_RESPONSE_PREPARE_SIGNALS: list = [set_ratelimit_headers]


__all__ = ["ON_RESPONSE_PREPARE_SIGNALS"]
