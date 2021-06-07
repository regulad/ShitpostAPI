from aiohttp import web


async def set_ratelimit_headers(request: web.Request, response: web.Response) -> None:
    """Set the rate-limit headers into the response field."""

    response.headers["X-RateLimit-Limit"] = str(request.get("X-RateLimit-Limit"))
    response.headers["X-RateLimit-Remaining"] = str(request.get("X-RateLimit-Remaining"))
    response.headers["X-RateLimit-Reset"] = str(request.get("X-RateLimit-Reset"))


__all__ = ["set_ratelimit_headers"]
