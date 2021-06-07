"""
Regulad's ShitpostAPI
https://github.com/regulad/ShitpostAPI

If you want to run the webserver with an external provisioning/management system like Gunicorn,
run the awaitable create_app.
"""

from os import environ
from collections import deque

from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient

from edits import commands
from routes import routes
from utils.files import FileCache
from utils.middlewares import *
from utils.signals import set_ratelimit_headers


async def create_app():
    """Create an app and configure it."""

    # Create the app
    app = web.Application(middlewares=[real_ip_behind_proxy, get_document, rate_limiter])

    # Config
    app["database_connection"] = AsyncIOMotorClient(environ.setdefault("SHITPOST_API_URI", "mongodb://localhost:27107"))
    app["database"] = app["database_connection"][environ.setdefault("SHITPOST_API_DB", "shitposts")]
    app["editing_commands"] = commands
    app["file_cache"] = FileCache(environ.setdefault("SHITPOST_API_CACHE", "downloads/"))
    app["document_cache"] = deque(maxlen=300)

    # Routes
    app.add_routes(routes)

    # Signals
    app.on_response_prepare.append(set_ratelimit_headers)

    # Off we go!
    return app


if __name__ == "__main__":
    port = int(environ.setdefault("SHITPOST_API_PORT", "8081"))
    host = environ.setdefault("SHITPOST_API_HOST", "0.0.0.0")

    web.run_app(create_app(), host=host, port=port)
