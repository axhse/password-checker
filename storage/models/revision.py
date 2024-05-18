from enum import Enum
from typing import Dict, Optional


class RevisionStatus(Enum):
    """Update status."""

    NEW = "new"
    """No update has been performed."""

    PREPARATION = "preparation"
    """New data is preparing."""

    TRANSITION = "transition"
    """Transition to new data is performing."""

    PURGE = "purge"
    """Removal of old data is performing."""

    STOPPAGE = "stoppage"
    """Preparation of new data is stopping."""

    CANCELLATION = "cancellation"
    """Preparation of new data is cancelling."""

    COMPLETED = "completed"
    """Update has completed successfully."""

    FAILED = "failed"
    """Update has failed."""

    STOPPED = "stopped"
    """Preparation of new data has stopped."""

    CANCELLED = "cancelled"
    """Preparation of new data has cancelled."""

    @property
    def is_idle(self) -> bool:
        """
        Check if the revision status is one of the idle statuses.
        :return: True if the status is idle, False otherwise.
        """
        return self in [
            RevisionStatus.NEW,
            RevisionStatus.COMPLETED,
            RevisionStatus.FAILED,
            RevisionStatus.STOPPED,
            RevisionStatus.CANCELLED,
        ]


class Revision:
    """Update-related information."""

    def __init__(
        self,
        status: RevisionStatus = RevisionStatus.NEW,
        progress: Optional[int] = None,
        start_ts: Optional[int] = None,
        end_ts: Optional[int] = None,
        error_message: Optional[str] = None,
    ):
        """
        Initialize a new Revision instance.

        :param status: The status of the update.
        :param progress: The progress percentage of the update.
        :param start_ts: The start timestamp of the update.
        :param end_ts: The end timestamp of the update.
        :param error_message: The error message associated with the update.
        """
        self._status: RevisionStatus = status
        self._progress: Optional[int] = progress
        self._start_ts: Optional[int] = start_ts
        self._end_ts: Optional[int] = end_ts
        self._error_message: Optional[str] = error_message

    @staticmethod
    def from_json(json: Dict):
        status_value = json.get("status")
        progress = json.get("progress")
        start_ts = json.get("start_ts")
        end_ts = json.get("end_ts")
        error_message = json.get("error_message")
        status = None
        for revision_status in RevisionStatus:
            if revision_status.value == status_value:
                status = revision_status
        return (
            Revision(status, progress, start_ts, end_ts, error_message)
            if (
                status is not None
                and (progress is None or type(progress) == int)
                and (start_ts is None or type(start_ts) == int)
                and (end_ts is None or type(end_ts) == int)
                and (error_message is None or type(error_message) == str)
            )
            else None
        )

    @property
    def status(self) -> RevisionStatus:
        """
        Get the status of the update.
        :return: The status of the update.
        """
        return self._status

    @property
    def progress(self) -> Optional[int]:
        """
        Get the progress percentage of the update.
        :return: The progress percentage of the update.
        """
        return self._progress

    @property
    def start_ts(self) -> Optional[int]:
        """
        Get the start timestamp of the update.
        :return: The start timestamp of the update.
        """
        return self._start_ts

    @property
    def end_ts(self) -> Optional[int]:
        """
        Get the end timestamp of the update.
        :return: The end timestamp of the update.
        """
        return self._end_ts

    @property
    def error_message(self) -> Optional[Exception]:
        """
        Get the error message associated with the update.
        :return: The error message associated with the update.
        """
        return self._error_message

    def to_json(self) -> Dict:
        return {
            "status": self._status.value,
            "progress": self._progress,
            "start_ts": self._start_ts,
            "end_ts": self._end_ts,
            "error_message": self._error_message,
        }
