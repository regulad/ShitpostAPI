"""
Regulad's ShitpostAPI
https://github.com/regulad/ShitpostAPI

If you want to run the webserver with an external provisioning/management system like Gunicorn,
run the awaitable create_app.
"""

from os import environ

from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient

from edits import commands
from routes import routes
from utils.files import FileCache


async def create_app():
    """Create an app and configure it."""

    # Create the app
    app = web.Application()

    # Config
    app["database_connection"] = AsyncIOMotorClient(environ.setdefault("SHITPOST_API_URI", "mongodb://localhost:27107"))
    app["database"] = app["database_connection"][environ.setdefault("SHITPOST_API_DB", "shitposts")]
    app["editing_commands"] = commands
    app["file_cache"] = FileCache(environ.setdefault("SHITPOST_API_CACHE", "downloads/"))

    # Routes
    app.add_routes(routes)

    # Off we go!
    return app


if __name__ == "__main__":
    port = int(environ.setdefault("SHITPOST_API_PORT", "8081"))
    host = environ.setdefault("SHITPOST_API_HOST", "0.0.0.0")

    web.run_app(create_app(), host=host, port=port)
