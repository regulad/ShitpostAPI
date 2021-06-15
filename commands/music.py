from io import FileIO, BytesIO
from os.path import splitext
from base64 import b64decode

import ffmpeg
from aiohttp.web import Request

from utils.command import CommandList

commands = CommandList()


@commands.command()
async def mute(request: Request):
    """Removes the audio from a video."""

    media_cache: FileIO = request["media_cache"]

    with request.app["file_cache"].create_file(splitext(media_cache.name)[1].strip(".")) as output_cache:
        output_cache: FileIO

        media_stream: ffmpeg.Stream = ffmpeg.input(media_cache.name)

        media_audio: ffmpeg.Stream = media_stream.audio
        media_video: ffmpeg.Stream = media_stream.video

        media_audio: ffmpeg.Stream = ffmpeg.filter(media_audio, "volume", 0)

        output_stream: ffmpeg.Stream = ffmpeg.output(media_audio, media_video, output_cache.name)

        await ffmpeg.run_asyncio(output_stream, overwrite_output=True)

        output_cache.seek(0)
        return output_cache.read()


@commands.command()
async def volume(request: Request, volume_value: float):
    """Changes the volume of audio in a video."""

    media_cache: FileIO = request["media_cache"]

    with request.app["file_cache"].create_file(splitext(media_cache.name)[1].strip(".")) as output_cache:
        output_cache: FileIO

        media_stream: ffmpeg.Stream = ffmpeg.input(media_cache.name)

        media_audio: ffmpeg.Stream = media_stream.audio
        media_video: ffmpeg.Stream = media_stream.video

        media_audio: ffmpeg.Stream = ffmpeg.filter(media_audio, "volume", volume_value)

        output_stream: ffmpeg.Stream = ffmpeg.output(media_audio, media_video, output_cache.name)

        await ffmpeg.run_asyncio(output_stream, overwrite_output=True)

        output_cache.seek(0)
        return output_cache.read()


@commands.command()
async def music(request: Request, music_b64: str):
    """Adds music over the top of a video. The string passed into the music argument must be base64 encoded MP3."""

    media_cache: FileIO = request["media_cache"]

    with request.app["file_cache"].create_file("mp3", b64decode(music_b64)) as music_cache, \
            request.app["file_cache"].create_file(splitext(media_cache.name)[1].strip(".")) as output_cache:
        music_cache: FileIO
        output_cache: FileIO

        media_stream: ffmpeg.Stream = ffmpeg.input(media_cache.name)
        music_stream: ffmpeg.Stream = ffmpeg.input(music_cache.name)

        media_audio: ffmpeg.Stream = media_stream.audio
        media_video: ffmpeg.Stream = media_stream.video

        overlayed_audio: ffmpeg.Stream = ffmpeg.filter([media_audio, music_stream], "amix", duration="first")

        output_stream: ffmpeg.Stream = ffmpeg.output(overlayed_audio, media_video, output_cache.name)

        await ffmpeg.run_asyncio(output_stream, overwrite_output=True)

        output_cache.seek(0)
        return output_cache.read()


__all__ = ["commands"]
