import time
from typing import Optional

from storage.models.pwned import PWNED_PREFIX_CAPACITY
from storage.models.revision import Revision, RevisionStatus


class FunctionalRevision(Revision):
    """Extended Revision class with auxiliary behavior."""

    def __init__(self, revision: Revision = Revision()):
        """
        Initialize a new FunctionalRevision instance.
        :param revision: Initial revision.
        """
        super().__init__(
            revision.status,
            revision.progress,
            revision.start_ts,
            revision.end_ts,
            revision.error_message,
        )
        self.__prepared_prefix_quantity: Optional[int] = None

    @property
    def progress(self) -> Optional[int]:
        if not self.is_preparing:
            return None
        return 100 * self.__prepared_prefix_quantity // PWNED_PREFIX_CAPACITY

    @property
    def is_idle(self) -> bool:
        """
        Check if the revision is in an idle state.
        :return: True if the revision is idle, False otherwise.
        """
        return self._status.is_idle

    @property
    def is_preparing(self) -> bool:
        """
        Check if the revision is in the preparation state.
        :return: True if the revision is preparing, False otherwise.
        """
        return self._status == RevisionStatus.PREPARATION

    @property
    def is_transiting(self) -> bool:
        """
        Check if the revision is in the transition state.
        :return: True if the revision is transiting, False otherwise.
        """
        return self._status == RevisionStatus.TRANSITION

    @property
    def is_cancelling(self) -> bool:
        """
        Check if the revision is in the cancellation state.
        :return: True if the revision is cancelling, False otherwise.
        """
        return self._status == RevisionStatus.CANCELLATION

    @property
    def is_completed(self) -> bool:
        """
        Check if the revision is successfully completed.
        :return: True if the revision is successfully completed, False otherwise.
        """
        return self._status == RevisionStatus.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        """
        Check if the revision is cancelled.
        :return: True if the revision is cancelled, False otherwise.
        """
        return self._status == RevisionStatus.CANCELLED

    @property
    def is_failed(self) -> bool:
        """
        Check if the revision is failed.
        :return: True if the revision is failed, False otherwise.
        """
        return self._status == RevisionStatus.FAILED

    def indicate_started(self) -> None:
        """Indicate that the preparation has started."""
        self._start_ts = int(time.time())
        self._end_ts = None
        self._error_message = None
        self.__prepared_prefix_quantity = 0
        self._status = RevisionStatus.PREPARATION

    def indicate_prepared(self) -> None:
        """Indicate that the preparation has completed."""
        self._status = RevisionStatus.TRANSITION

    def indicate_transited(self) -> None:
        """Indicate that the transition has completed."""
        self._status = RevisionStatus.PURGE

    def indicate_cancellation(self) -> None:
        """Indicate that the cancellation has started."""
        self._status = RevisionStatus.CANCELLATION

    def indicate_completed(self) -> None:
        """Indicate that the revision has completed successfully."""
        self.__set_end_ts()
        self._status = RevisionStatus.COMPLETED

    def indicate_cancelled(self) -> None:
        """Indicate that the revision has been cancelled."""
        self.__set_end_ts()
        self._status = RevisionStatus.CANCELLED

    def indicate_failed(self, error: Exception) -> None:
        """
        Indicate that the revision has failed with the given error.
        :param error: The error associated with the failure.
        """
        self.__set_end_ts()
        self._error_message = str(error)
        self._status = RevisionStatus.FAILED

    def count_prepared_prefix(self) -> None:
        """Increment the count of prepared prefixes."""
        self.__prepared_prefix_quantity += 1

    def to_dto(self) -> Revision:
        """
        Convert the FunctionalRevision to a pure Revision instance.
        :return: A Revision instance representing the current state of the revision.
        """
        return Revision(
            self.status,
            self.progress,
            self.start_ts,
            self.end_ts,
            self.error_message,
        )

    def __set_end_ts(self) -> None:
        self._end_ts = int(time.time())
