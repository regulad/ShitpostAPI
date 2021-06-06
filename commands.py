from utils import command
from io import FileIO


commands = command.CommandList()


@commands.command()
def top_text(fp: FileIO, text: str):
    """Appends text to the top of an image."""

    pass

