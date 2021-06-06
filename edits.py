from typing import Optional
from io import FileIO

from utils import command


commands = command.CommandList()


@commands.command()
async def caption(fp: FileIO, top: Optional[str] = None, bottom: Optional[str] = None) -> None:
    """Appends text to the top of an image."""

    return 1
