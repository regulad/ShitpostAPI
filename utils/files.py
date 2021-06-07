import os
from io import FileIO
from random import choice
from string import ascii_letters
from typing import Optional


class CachedBinaryFile:
    """A cached binary file. It must be entered and exited."""

    def __init__(self, path: str, initial_bytes: Optional[bytes] = None) -> None:
        self._bytes = initial_bytes
        self._path = path
        self._file: Optional[FileIO] = None

    @property
    def path(self) -> str:
        return self._path

    def __enter__(self) -> FileIO:
        self._file = FileIO(self.path, "wb+")

        if self._bytes is not None:
            self._file.write(self._bytes)
            self._file.seek(0)

        return self._file

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._file.close()
        os.remove(self.path)


class FileCache:
    """Handles the caching of files."""

    def __init__(self, directory: str) -> None:
        self._directory = directory

        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

    @property
    def directory(self) -> str:
        return self._directory

    def create_file(self, file_extension: str, initial_bytes: Optional[bytes] = None) -> CachedBinaryFile:
        file_name = f"{self.directory}{''.join(choice(ascii_letters) for _ in range(15))}.{file_extension}"
        return CachedBinaryFile(file_name, initial_bytes)
