from os import environ
from typing import Optional
from json import load
from io import FileIO

from motor.motor_asyncio import AsyncIOMotorClient
from aiohttp import web, hdrs, BodyPartReader
from jsonschema import validate, ValidationError

from utils.files import FileCache
from utils.command import EditCommand
from edits import commands


app = web.Application()
routes = web.RouteTableDef()


app["database_connection"] = AsyncIOMotorClient(environ.setdefault("SHITPOST_API_URI", "mongodb://localhost:27107"))
app["database"] = app["database_connection"][environ.setdefault("SHITPOST_API_DB", "shitposts")]
app["editing_commands"] = commands
app["file_cache"] = FileCache(environ.setdefault("SHITPOST_API_CACHE", "downloads/"))


EDITS_SCHEMA: dict = load(open("resources/edits_schema.json"))


FILE_TYPES: dict = load(open("resources/types.json"))


@routes.post("/edit")
async def post_edit(request: web.Request):
    """Returns a stream of bytes from a multipart request to edit a video."""

    multipart = await request.multipart()

    media_bytes: Optional[bytes] = None
    edits_json: Optional[dict] = None
    content_type: Optional[str] = None
    extension: Optional[str] = None

    while True:
        part = await multipart.next()

        if not isinstance(part, BodyPartReader):
            break
        else:
            part: BodyPartReader

        if part.name == "Media":  # Not the cleanest. But it works.
            if part.headers.get(hdrs.CONTENT_TYPE) is not None:
                content_type: str = part.headers[hdrs.CONTENT_TYPE]
                extension: str = FILE_TYPES.get(content_type) or "mp4"
            elif part.filename is not None:
                extension: str = part.filename.strip().split(".")[-1]
                for key, value in FILE_TYPES.items():
                    if value == extension:
                        content_type: str = key
                        break
                else:
                    raise web.HTTPUnsupportedMediaType(reason="Media was not on type whitelist.")
            else:
                raise web.HTTPUnsupportedMediaType(
                    reason="Unable to find information the the media's type. Add a Content-Type header or filename."
                )

            media_bytes = await part.read()
        elif part.name == "Edits":
            edits_json: dict = await part.json()

    if media_bytes is None or edits_json is None:
        raise web.HTTPBadRequest(reason="Missing a required field.")

    try:
        validate(edits_json, EDITS_SCHEMA)
    except ValidationError:
        raise web.HTTPBadRequest(reason="Malformed edits field.")
    except Exception:
        raise

    with request.app["file_cache"].create_file(extension, media_bytes) as file:
        file: FileIO

        for edit in edits_json["edits"]:
            edit: dict

            for edit_command in request.app["editing_commands"]:
                edit_command: EditCommand

                if edit_command.name == edit["name"]:
                    command = edit_command
                    break
            else:
                continue

            file.seek(0)
            print(await command.function(file, **edit["parameters"]))

        file.seek(0)
        stream_response = web.StreamResponse()
        stream_response.content_type = content_type
        await stream_response.prepare(request)
        await stream_response.write(file.read())
        await stream_response.write_eof()
        return stream_response


@routes.get("/commands")
async def get_commands(request: web.Request):
    """Returns JSON data detailing available commands."""

    accessible_commands = []

    for command in request.app["editing_commands"]:
        accessible_commands.append(command.__dict__())

    return_json = {"commands": accessible_commands}

    return web.json_response(return_json)


app.add_routes(routes)


if __name__ == "__main__":
    from aiohttp import web

    port = int(environ.setdefault("SHITPOST_API_PORT", "8081"))
    host = environ.setdefault("SHITPOST_API_HOST", "0.0.0.0")

    web.run_app(app, host=host, port=port)
