from io import FileIO
from json import load
from os.path import splitext
from typing import Optional

from aiohttp import web, BodyPartReader, hdrs
from jsonschema import validate, ValidationError

from utils.command import EditCommand

routes = web.RouteTableDef()

EDITS_SCHEMA = load(open("resources/edits_schema.json"))
FILE_TYPES = load(open("resources/types.json"))

README_FILE = []
for line in open("README.md").readlines():
    README_FILE.append(line.strip())


@routes.get("/")
async def get_docs(request: web.Request):
    return web.json_response({"lines": README_FILE})


@routes.get("/user")
async def get_user(request: web.Request):
    return web.json_response(request["document"])


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
                extension: str = splitext(part.filename)[1].strip(".")
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

    with request.app["file_cache"].create_file(extension, media_bytes) as request["media_cache"]:
        request["media_cache"]: FileIO

        for edit in edits_json["edits"]:
            edit: dict

            for edit_command in request.app["editing_commands"]:
                edit_command: EditCommand

                if edit_command.name == edit["name"]:
                    command = edit_command
                    break
            else:
                continue

            request["media_cache"].seek(0)

            out_bytes = await command.function(request, **edit["parameters"])
            request["media_cache"].truncate()
            request["media_cache"].write(out_bytes)

        request["media_cache"].seek(0)
        stream_response = web.StreamResponse()
        stream_response.content_type = content_type
        await stream_response.prepare(request)
        await stream_response.write(request["media_cache"].read())
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


@routes.get("/commands/{command_name}")
async def get_command(request: web.Request):
    """Returns info on a single command."""

    for command in request.app["editing_commands"]:
        if command.name == request.match_info["command_name"]:
            desired_command: EditCommand = command
            break
    else:
        raise web.HTTPBadRequest(reason="Command doesn't exist.")

    return web.json_response(desired_command.__dict__())
