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
    :return: Joined path.
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

    :param path: Directory path.
    """
    if not is_dir(path):
        os.mkdir(path)


def remove_dir(path: str) -> None:
    """
    Remove a directory and its content.

    :param path: Directory path.
    """
    if os.path.isdir(path):
        shutil.rmtree(path)


def make_empty_dir(path: str) -> None:
    """
    Create an empty directory or clear the existing one.

    :param path: Directory path.
    """
    remove_dir(path)
    make_dir_if_not_exists(path)


def create_empty_file(path: str) -> None:
    """
    Create an empty file.

    :param path: File path.
    """
    with open(path, "w"):
        pass


def create_file_if_not_exists(path: str) -> None:
    """
    Create a file if it does not exist.

    :param path: File path.
    """
    if not is_file(path):
        create_empty_file(path)


def remove_file(path: str) -> None:
    """
    Remove a file if it exists.

    :param path: File path.
    """
    if os.path.exists(path) and not os.path.isdir(path):
        os.remove(path)


def remove_files(paths: List[str]) -> None:
    """
    Remove multiple files.

    :param paths: List of file paths.
    """
    for path in paths:
        remove_file(path)


def read(path: str, binary=False, encoding: Optional[Encoding] = None) -> str:
    """
    Read the contents of a file.

    :param path: File path.
    :param binary: Whether to open the file in binary mode.
    :param encoding: File encoding.
    :return: Contents of the file.
    """
    mode = "rb" if binary else "r"
    encoding = encoding and encoding.value
    with open(path, mode, encoding=encoding) as file:
        return file.read()


def read_lines(path: str, encoding: Encoding = Encoding.ASCII) -> List[str]:
    """
    Read the lines of a file and return them as a list.

    :param path: File path.
    :param encoding: File encoding.
    :return: List of lines.
    """
    with open(path, "r", encoding=encoding.value) as file:
        return file.readlines()


def write(
    path: str,
    lines: Union[str, List[str]],
    overwrite=False,
    encoding: Encoding = Encoding.ASCII,
) -> None:
    """
    Write lines to a file.

    :param path: File path.
    :param lines: Lines to write (either a string or a list of strings).
    :param overwrite: Whether to overwrite the file (default is False).
    :param encoding: File encoding.
    """
    mode = "w" if overwrite else "a"
    with open(path, mode, encoding=encoding.value) as file:
        if isinstance(lines, str):
            file.write(lines)
        else:
            file.writelines(lines)
