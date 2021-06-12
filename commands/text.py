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

    overlay_bytes: bytes = await get_event_loop().run_in_executor(
        None, lambda: caption_executor(width, height, top, bottom)
    )

    with request.app["file_cache"].create_file("png", overlay_bytes) as overlay, \
            request.app["file_cache"].create_file(splitext(media_cache.name)[1].strip(".")) as out_media:
        overlay: FileIO
        out_media: FileIO

        media_stream: ffmpeg.Stream = ffmpeg.input(media_cache.name)
        overlay_stream: ffmpeg.Stream = ffmpeg.input(overlay.name)

        media_audio: ffmpeg.Stream = media_stream.audio
        media_video: ffmpeg.Stream = media_stream.video

        media_video: ffmpeg.Stream = ffmpeg.overlay(media_video, overlay_stream)

        media_stream: ffmpeg.Stream = ffmpeg.output(media_audio, media_video, out_media.name)

        await ffmpeg.run_asyncio(media_stream, overwrite_output=True)

        out_media.seek(0)
        return out_media.read()


def header_executor(width: int, height: int, top: str) -> bytes:
    image = Image.new("RGB", (width, round(height * 1.15)), (255, 255, 255))
    idraw = ImageDraw.Draw(image)

    top_height = round(height * 1.25 - height)

    idraw.text(
        (width / 2, top_height / 2),
        top,
        font=IMPACT_FONT,
        fill=(0, 0, 0),
        anchor="mm",
    )

    buffer = BytesIO()
    image.save(buffer, "PNG")
    buffer.seek(0)
    return buffer.read()


@commands.command()
async def header(request: Request, top: str):
    """Extends the top of an image and adds text."""

    media_cache: FileIO = request["media_cache"]

    probe_result: dict = await ffmpeg.probe_asyncio(media_cache.name)

    width: int = probe_result["streams"][0]["width"]
    height: int = probe_result["streams"][0]["height"]

    underlay_bytes: bytes = await get_event_loop().run_in_executor(None, lambda: header_executor(width, height, top))

    with request.app["file_cache"].create_file("png", underlay_bytes) as underlay_cache, \
            request.app["file_cache"].create_file(splitext(media_cache.name)[1].strip(".")) as output_cache:
        underlay_cache: FileIO
        output_cache: FileIO

        media_stream: ffmpeg.Stream = ffmpeg.input(media_cache.name)
        underlay_stream: ffmpeg.Stream = ffmpeg.input(underlay_cache.name)

        media_audio: ffmpeg.Stream = media_stream.audio
        media_video: ffmpeg.Stream = media_stream.video

        overlayed_video: ffmpeg.Stream = ffmpeg.overlay(
            underlay_stream, media_video, x=0, y=round(height * 1.25) - height
        )

        output_stream: ffmpeg.Stream = ffmpeg.output(media_audio, overlayed_video, output_cache.name)

        await ffmpeg.run_asyncio(output_stream, overwrite_output=True)

        output_cache.seek(0)
        return output_cache.read()
