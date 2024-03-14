from abc import ABC, abstractmethod
from enum import Enum

from storage.models.revision import Revision


class UpdateResult(Enum):
    """Possible result of an update."""

    DONE = "done"
    CANCELLED = "cancelled"
    FAILED = "failed"
    BUSY = "busy"


class UpdateResponse(Enum):
    """Possible response status when requesting an update."""

    STARTED = "started"
    BUSY = "busy"


class UpdateCancellationResponse(Enum):
    """Possible response status when requesting an update cancellation."""

    ACCEPTED = "accepted"
    IRRELEVANT = "irrelevant"


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
