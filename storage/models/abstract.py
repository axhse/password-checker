from abc import ABC, abstractmethod
from enum import Enum

from storage.models.revision import Revision


class UpdateResult(Enum):
    """Possible result of an update."""

    DONE = "done"
    """The update has completed successfully."""

    CANCELLED = "cancelled"
    """The update has cancelled."""

    FAILED = "failed"
    """The update has failed."""

    BUSY = "busy"
    """There is already an ongoing update."""


class UpdateResponse(Enum):
    """Possible response when requesting an update."""

    STARTED = "started"
    """The update has started."""

    BUSY = "busy"
    """There is already an ongoing update."""


class UpdateCancellationResponse(Enum):
    """Possible response when requesting an update cancellation."""

    ACCEPTED = "accepted"
    """The cancellation has started."""

    IRRELEVANT = "irrelevant"
    """There is no ongoing data preparation."""


class UpdatePauseResponse(Enum):
    """Possible response when requesting an update pause."""

    ACCEPTED = "accepted"
    """The stoppage has started."""

    IRRELEVANT = "irrelevant"
    """There is no ongoing data preparation."""


class PwnedStorage(ABC):
    """Stores Pwned password leak records."""

    @property
    @abstractmethod
    def revision(self) -> Revision:
        """
        Get the information related to the most recent update.
        :return: The update-related information.
        """
        ...

    @abstractmethod
    async def get_range(self, prefix: str) -> str:
        """
        Get the Pwned password leak record range for a hash prefix.

        :param prefix: The hash prefix to query.
        :return: The range as plain text.
        """
        pass

    @abstractmethod
    async def update(self) -> UpdateResult:
        """
        Request an update of all Pwned password leak records.
        :return: The update response status.
        """
        pass

    @abstractmethod
    def request_update(self) -> UpdateResponse:
        """
        Request an update of all Pwned password leak records.
        :return: The update response status.
        """
        pass

    @abstractmethod
    def request_update_pause(self) -> UpdatePauseResponse:
        """
        Request an update pause.
        :return: The update pause response status.
        """
        pass

    @abstractmethod
    def request_update_cancellation(self) -> UpdateCancellationResponse:
        """
        Request an update cancellation.
        :return: The update cancellation response status.
        """
        pass


class PwnedRangeProvider(ABC):
    """Provides Pwned password leak record ranges"""

    @abstractmethod
    async def get_range(self, hash_prefix: str) -> str:
        """
        Gets the Pwned password leak record range for a hash prefix.

        :param hash_prefix: The hash prefix.
        :return: The range as plain text.
        """
        pass
