import os
import shutil
from enum import Enum
from typing import List, Optional, Union


class Encoding(Enum):
    """Commonly used encodings."""

    UTF_8: str = "utf-8"
    ASCII: str = "ascii"


def join_paths(*paths: str) -> str:
    """
    Join multiple path components into a single path.

    :param paths: Path components.
    :return: The joined path.
    """
    return os.path.join(*paths)


def is_file(path: str) -> bool:
    """
    Check if a file exists.

    :param path: The path to the file.
    :return: True if the file exists, False otherwise.
    """
    return os.path.exists(path) and os.path.isfile(path)


def is_dir(path: str) -> bool:
    """
    Check if a directory exists.

    :param path: The path to the directory.
    :return: True if the directory exists, False otherwise.
    """
    return os.path.exists(path) and os.path.isdir(path)


def make_dir_if_not_exists(path: str) -> None:
    """
    Create a directory if it does not exist.
    :param path: The directory path.
    """
    if not is_dir(path):
        os.mkdir(path)


def remove_dir(path: str) -> None:
    """
    Remove a directory and its contents.
    :param path: The directory path.
    """
    if os.path.isdir(path):
        shutil.rmtree(path)


def make_empty_dir(path: str) -> None:
    """
    Create an empty directory or clear the existing one.
    :param path: The directory path.
    """
    remove_dir(path)
    make_dir_if_not_exists(path)


def remove_file(path: str) -> None:
    """
    Remove a file if it exists.
    :param path: The file path.
    """
    if os.path.exists(path) and not os.path.isdir(path):
        os.remove(path)


def read(path: str, binary=False, encoding: Optional[Encoding] = None) -> str:
    """
    Read the contents of a file.

    :param path: The file path.
    :param binary: Whether to open the file in binary mode.
    :param encoding: The file encoding.
    :return: The contents of the file.
    """
    mode = "rb" if binary else "r"
    encoding = encoding and encoding.value
    with open(path, mode, encoding=encoding) as file:
        return file.read()


def write(
    path: str,
    lines: Union[str, List[str]],
    overwrite=False,
    encoding: Encoding = Encoding.ASCII,
) -> None:
    """
    Write lines to a file.

    :param path: The file path.
    :param lines: The lines to write (either a string or a list of strings).
    :param overwrite: Whether to overwrite the file (default is False).
    :param encoding: The file encoding.
    """
    mode = "w" if overwrite else "a"
    with open(path, mode, encoding=encoding.value) as file:
        if isinstance(lines, str):
            file.write(lines)
        else:
            file.writelines(lines)
