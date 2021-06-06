from os import environ

from motor.motor_asyncio import AsyncIOMotorClient
from aiohttp import web

from commands import commands as editing_commands


app = web.Application()
routes = web.RouteTableDef()

app["database_connection"] = AsyncIOMotorClient(environ.setdefault("SHITPOST_API_URI", "mongodb://localhost:27107"))
app["database"] = app["database_connection"][environ.setdefault("SHITPOST_API_DB", "shitposts")]
app["editing_commands"] = editing_commands


@routes.post("/edit")
async def edit_video(request: web.Request):
    pass


app.add_routes(routes)


if __name__ == "__main__":
    from aiohttp import web

    port = int(environ.setdefault("SHITPOST_API_PORT", "8081"))
    host = environ.setdefault("SHITPOST_API_HOST", "0.0.0.0")

    web.run_app(app, host=host, port=port)
