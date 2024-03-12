import asyncio
import sys
import time
from enum import Enum
from typing import List, Union

from storage.models.abstract import PwnedStorage
from storage.models.revision import Revision, RevisionStatus

CONSOLE_UPDATE_INTERVAL: float = 1
"""The interval between console updates in seconds."""


class TextStyle(Enum):
    """Text styles for the console."""

    NONE = 0
    BOLD = 1
    ITALIC = 3
    BLACK = 30
    PALE_RED = 31
    PALE_GREEN = 32
    PALE_YELLOW = 33
    PALE_BLUE = 34
    PALE_PURPLE = 35
    PALE_CYAN = 36
    PALE_GRAY = 37
    GRAY = 90
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94
    PURPLE = 95
    CYAN = 96

    @property
    def pale(self):
        """
        Get a paler version of the text style.
        :return: A pale version of the text style.
        """
        if self.value < TextStyle.RED.value or TextStyle.CYAN.value < self.value:
            return self
        return TextStyle(self.value - TextStyle.RED.value + TextStyle.PALE_RED.value)

    @property
    def bright(self):
        """
        Get a brighter version of the text style.
        :return: A bright version of the text style.
        """
        if (
            self.value < TextStyle.PALE_RED.value
            or TextStyle.PALE_CYAN.value < self.value
        ):
            return self
        return TextStyle(self.value - TextStyle.PALE_RED.value + TextStyle.RED.value)


def stylize_text(text: str, styles: Union[TextStyle, List[TextStyle]]) -> str:
    """
    Apply the specified text styles to the given text.

    :param text: The text to stylize.
    :param styles: A single style or a list of styles to apply.
    :return: A stylized text.
    """
    if isinstance(styles, TextStyle):
        styles = [styles]
    return "".join([f"\x1B[{style.value}m" for style in styles]) + text + "\x1B[0m"


def write(text: str) -> None:
    """
    Write the provided text to standard output.
    :param text: The text to write.
    """
    sys.stdout.write(text)
    sys.stdout.flush()


def convert_seconds(seconds: int) -> str:
    """
    Convert the number of seconds to a formatted time string.

    :param seconds: An integer representing the number of seconds to convert.
    :return: A formatted time string.
    """
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    seconds = seconds % 60
    hour_string = f"" if hours == 0 else "{hours}:"
    minute_string = f"{minutes:0{0 if hours == 0 else 2}d}"
    return f"{hour_string}{minute_string}:{seconds:02d}"


def print_revision_information(
    revision: Revision, previous_status: RevisionStatus
) -> None:
    """
    Print information related to a revision.

    :param revision: A revision.
    :param previous_status: The previous status of the revision.
    """

    def __get_completion_style(completed: bool) -> TextStyle:
        return TextStyle.GREEN if completed else TextStyle.BLUE

    new_status = revision.status
    if new_status == RevisionStatus.NEW:
        return
    if new_status == RevisionStatus.FAILED:
        if previous_status != RevisionStatus.NEW:
            write("\n")
        write(
            stylize_text(f"[FAILED] {revision.error}", [TextStyle.BOLD, TextStyle.RED])
        )
        write("\n")
        return
    if new_status == RevisionStatus.CANCELLED:
        if previous_status != RevisionStatus.NEW:
            write("\n")
        write(stylize_text("[CANCELLED]", [TextStyle.BOLD, TextStyle.YELLOW]))
        write("\n")
        return
    console_status = previous_status
    if console_status in [RevisionStatus.NEW, RevisionStatus.PREPARATION]:
        if previous_status != RevisionStatus.NEW:
            write("\r")
        is_completed = new_status in [
            RevisionStatus.TRANSITION,
            RevisionStatus.PURGE,
            RevisionStatus.COMPLETED,
        ]
        elapsed_seconds = int(time.time()) - revision.start_ts
        style = __get_completion_style(is_completed)
        progress = 100 if is_completed else revision.progress or 0
        write(
            stylize_text(f"[{convert_seconds(elapsed_seconds)}]", TextStyle.PALE_GRAY)
        )
        write(stylize_text(" Prepare new data: ", style))
        write(stylize_text(f"{progress}%", [TextStyle.BOLD, style]))
        if is_completed:
            write("\n")
            console_status = RevisionStatus.TRANSITION
    if console_status == RevisionStatus.TRANSITION:
        if previous_status not in [RevisionStatus.NEW, RevisionStatus.PREPARATION]:
            write("\r")
        is_completed = new_status in [RevisionStatus.PURGE, RevisionStatus.COMPLETED]
        style = __get_completion_style(is_completed)
        write(stylize_text("Transit to new prepared data", style))
        if is_completed:
            write("\n")
            console_status = RevisionStatus.PURGE
    if console_status == RevisionStatus.PURGE:
        if previous_status not in [
            RevisionStatus.NEW,
            RevisionStatus.PREPARATION,
            RevisionStatus.TRANSITION,
        ]:
            write("\r")
        is_completed = new_status in [RevisionStatus.COMPLETED]
        style = __get_completion_style(is_completed)
        write(stylize_text("Purge old data", style))
        if is_completed:
            write("\n")


async def watch_and_print_revision(storage: PwnedStorage) -> None:
    """
    Watch storage revision and print its information.
    :param storage: A storage.
    """
    previous_status = RevisionStatus.NEW
    while True:
        revision = storage.revision
        print_revision_information(revision, previous_status)
        previous_status = revision.status
        if previous_status in [
            RevisionStatus.COMPLETED,
            RevisionStatus.CANCELLED,
            RevisionStatus.FAILED,
        ]:
            break
        await asyncio.sleep(CONSOLE_UPDATE_INTERVAL)
