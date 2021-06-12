import datetime

from aiohttp import web, hdrs

from utils.database import Document


@web.middleware
async def real_ip_behind_proxy(request: web.Request, handler):
    """Changes the remote attribute of the request to the X-Real-IP, if present"""

    if request.headers.get("X-Real-IP") is not None:
        request = request.clone(remote=request.headers.get("X-Real-IP"))

    return await handler(request)


@web.middleware
async def get_document(request: web.Request, handler):
    """Fetches the document for a user from their IP address."""

    request["document"] = await Document.get_from_id(
        request.app["database"]["users"],
        request.remote,
    )

    return await handler(request)


@web.middleware
async def rate_limiter(request: web.Request, handler):
    """Rate-limits a user, if necessary."""

    document: Document = request["document"]

    time_now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    # Update/get the retry-after
    if document.get("period_start", time_now.timestamp()) <= time_now.timestamp():
        time_later = time_now + datetime.timedelta(hours=1)
        await document.update_db({"$set": {"period_start": time_later.timestamp(), "requests_this_period": 0}})
    else:
        time_later = datetime.datetime.fromtimestamp(document["period_start"], datetime.timezone.utc)
    await document.update_db({"$inc": {"requests_this_period": 1}})

    # The maximum amount of requests a user can make per-hour.
    request["X-RateLimit-Limit"] = request["document"].get("requests_per_period", 90)

    # The amount of rate-limits remaining.
    request["X-RateLimit-Remaining"] = document.get("requests_per_period", 90) \
                                       - document.get("requests_this_period", 0)

    # When the next period comes.
    request["X-RateLimit-Reset"] = (time_later - time_now).total_seconds()

    if document.get("requests_this_period", 0) > document.get("requests_per_period", 90):
        raise web.HTTPTooManyRequests
    elif float(request.headers.get(hdrs.CONTENT_LENGTH, "0")) > document.get("max_size", 20000000):
        # TODO: Maybe can be manipulated? Not sure. I barely know HTTP.
        raise web.HTTPRequestEntityTooLarge(
            actual_size=float(request.headers.get(hdrs.CONTENT_LENGTH, "0")),
            max_size=document.setdefault("max_size", 20000000),
        )
    else:
        return await handler(request)


MIDDLEWARE_CHAIN: list = [real_ip_behind_proxy, get_document, rate_limiter]


__all__ = ["MIDDLEWARE_CHAIN"]
