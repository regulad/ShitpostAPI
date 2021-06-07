from asyncio import get_event_loop
from io import FileIO, BytesIO
from os.path import splitext
from typing import Optional

import ffmpeg
from PIL import Image, ImageFont, ImageDraw
from aiohttp.web import Request

from utils.command import CommandList

IMPACT_FONT = ImageFont.truetype("resources/maximum-impact.ttf", 75)

commands = CommandList()


def caption_executor(
        width: int,
        height: int,
        top: Optional[str] = None,
        bottom: Optional[str] = None
) -> bytes:
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    idraw = ImageDraw.Draw(image)

    if top is not None:
        idraw.text(
            (width / 2, 25),
            top,
            font=IMPACT_FONT,
            fill=(255, 255, 255, 255),
            anchor="mt",
            stroke_width=5,
            stroke_fill=(0, 0, 0, 255),
        )

    if bottom is not None:
        idraw.text(
            (width / 2, height - 25),
            bottom,
            font=IMPACT_FONT,
            fill=(255, 255, 255, 255),
            anchor="ms",
            stroke_width=5,
            stroke_fill=(0, 0, 0, 255),
        )

    buffer = BytesIO()
    image.save(buffer, "PNG")
    buffer.seek(0)

    return buffer.read()


@commands.command()
async def caption(
        request: Request,
        top: Optional[str] = None,
        bottom: Optional[str] = None
) -> bytes:
    """Appends text to the top of an image. Multi-line text is not supported."""

    media_cache: FileIO = request["media_cache"]

    probe_result: dict = await ffmpeg.probe_asyncio(media_cache.name)

    width: int = probe_result["streams"][0]["width"]
    height: int = probe_result["streams"][0]["height"]

    overlay_bytes = await get_event_loop().run_in_executor(None, lambda: caption_executor(width, height, top, bottom))

    with request.app["file_cache"].create_file("png", overlay_bytes) as overlay:
        overlay: FileIO

        media_stream = ffmpeg.input(media_cache.name)
        overlay_stream = ffmpeg.input(overlay.name)

        media_audio = media_stream.audio
        media_video = media_stream.video

        media_video = ffmpeg.overlay(media_video, overlay_stream)

        with request.app["file_cache"].create_file(splitext(media_cache.name)[1].strip(".")) as out_media:
            out_media: FileIO

            media_stream = ffmpeg.output(media_audio, media_video, out_media.name)

            await ffmpeg.run_asyncio(media_stream, overwrite_output=True)

            out_media.seek(0)
            out_bytes = out_media.read()

        return out_bytes
