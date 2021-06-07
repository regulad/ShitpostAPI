import datetime

from aiohttp import web

from utils.database import Document


@web.middleware
async def database_middleware(request: web.Request, handler):
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
    if document.setdefault("period_start", time_now.timestamp()) <= time_now.timestamp():
        time_later = time_now + datetime.timedelta(hours=1)
        await document.update_db({"$set": {"period_start": time_later.timestamp(), "requests_this_period": 0}})
    else:
        time_later = datetime.datetime.fromtimestamp(document["period_start"], datetime.timezone.utc)
    await document.update_db({"$inc": {"requests_this_period": 1}})

    # The maximum amount of requests a user can make per-hour.
    request["X-RateLimit-Limit"] = request["document"].setdefault("requests_per_period", 90)

    # The amount of rate-limits remaining.
    request["X-RateLimit-Remaining"] = document.setdefault("requests_per_period", 90) \
                                       - document.setdefault("requests_this_period", 0)

    # When the next period comes.
    request["X-RateLimit-Reset"] = (time_later - time_now).total_seconds()

    if document.setdefault("requests_this_period", 0) > document.setdefault("requests_per_period", 90):
        raise web.HTTPTooManyRequests
    elif len(await request.read()) > document.setdefault("max_size", 20000000):  # Maybe can be manipulated?
        raise web.HTTPRequestEntityTooLarge(
            actual_size=len(await request.read()),
            max_size=document.setdefault("max_size", 20000000),
        )
    else:
        return await handler(request)


__all__ = ["database_middleware", "rate_limiter"]
