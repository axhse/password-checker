import time
from typing import List, Optional

from storage.models.pwned import PWNED_PREFIX_CAPACITY
from storage.models.revision import Revision, RevisionStatus


class FunctionalRevision(Revision):
    """Extended Revision class with auxiliary behavior."""

    def __init__(
        self,
        batch_quantity: int,
        revision: Revision = Revision(),
        batch_preparation_offsets: Optional[List[int]] = None,
    ):
        """
        Initialize a new FunctionalRevision instance.

        :param batch_quantity: Quantity of parallel preparation batches.
        :param batch_preparation_offsets: Quantities of processed prefixes for preparation batches.
        :param revision: Initial revision.
        """
        super().__init__(
            revision.status,
            revision.progress,
            revision.start_ts,
            revision.end_ts,
            revision.error_message,
        )
        self.__batch_preparation_offsets: List[int] = (
            batch_preparation_offsets or [0] * batch_quantity
        )
        self.__prepared_prefix_quantity: int = sum(self.__batch_preparation_offsets)

    @property
    def progress(self) -> Optional[int]:
        if (
            not self.is_preparing
            and not self.is_stopped
            and not self.has_preparation_failed
        ):
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
    def is_stopping(self) -> bool:
        """
        Check if the revision is in the stopping state.
        :return: True if the revision is stopping, False otherwise.
        """
        return self._status == RevisionStatus.STOPPAGE

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
    def is_stopped(self) -> bool:
        """
        Check if the revision is stopped.
        :return: True if the revision is stopped, False otherwise.
        """
        return self._status == RevisionStatus.STOPPED

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

    @property
    def has_preparation_failed(self) -> bool:
        """
        Check if preparation of new data has failed during revision.
        :return: True if preparation has failed, False otherwise.
        """
        return self._status == RevisionStatus.PREPARATION_FAILED

    def indicate_started(self) -> None:
        """Indicate that the preparation has started."""
        self._end_ts = None
        self._error_message = None
        if (
            self._status != RevisionStatus.STOPPED
            and self.status != RevisionStatus.PREPARATION_FAILED
        ):
            self._start_ts = int(time.time())
        self._status = RevisionStatus.PREPARATION

    def indicate_prepared(self) -> None:
        """Indicate that the preparation has completed."""
        self.__clear_progress()
        self._status = RevisionStatus.TRANSITION

    def indicate_transited(self) -> None:
        """Indicate that the transition has completed."""
        self._status = RevisionStatus.PURGE

    def indicate_stoppage(self) -> None:
        """Indicate that the stoppage has started."""
        self._status = RevisionStatus.STOPPAGE

    def indicate_cancellation(self) -> None:
        """Indicate that the cancellation has started."""
        self._status = RevisionStatus.CANCELLATION

    def indicate_completed(self) -> None:
        """Indicate that the revision has completed successfully."""
        self.__set_end_ts()
        self._status = RevisionStatus.COMPLETED

    def indicate_stopped(self) -> None:
        """Indicate that the revision has stopped."""
        self.__set_end_ts()
        self._status = RevisionStatus.STOPPED

    def indicate_cancelled(self) -> None:
        """Indicate that the revision has cancelled."""
        self.__clear_progress()
        self.__set_end_ts()
        self._status = RevisionStatus.CANCELLED

    def indicate_failed(self, error: Exception) -> None:
        """
        Indicate that the revision has failed with the given error.
        :param error: The error associated with the failure.
        """
        self.__clear_progress()
        self.__set_end_ts()
        self._error_message = str(error)
        self._status = RevisionStatus.FAILED

    def indicate_preparation_failed(self, error: Exception) -> None:
        """
        Indicate that preparation of new data has failed during revision with the given error.
        :param error: The error associated with the failure.
        """
        self.__set_end_ts()
        self._error_message = str(error)
        self._status = RevisionStatus.PREPARATION_FAILED

    def count_prepared_prefix(self, batch_index: int) -> None:
        """Increment the count of prepared prefixes."""
        self.__batch_preparation_offsets[batch_index] += 1
        self.__prepared_prefix_quantity += 1

    def get_batch_preparation_offset(self, batch_index: int) -> int:
        """
        Get quantity of processed prefixes for a specific preparation batch.

        :param batch_index: Batch index.
        :return: Processed quantity.
        """
        return self.__batch_preparation_offsets[batch_index]

    def has_progress(self) -> bool:
        """
        Check if the revision has progress.
        :return: True if the revision has progress, False otherwise.
        """
        return self.__prepared_prefix_quantity != 0

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

    def __clear_progress(self):
        self.__batch_preparation_offsets = [0] * len(self.__batch_preparation_offsets)
        self.__prepared_prefix_quantity = 0
