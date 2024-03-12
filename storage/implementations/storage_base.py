import asyncio
import json
from abc import abstractmethod
from json import JSONDecodeError
from typing import Dict

from storage.auxiliary.filetools import (
    is_file,
    join_paths,
    make_dir_if_not_exists,
    make_empty_dir,
    read,
    remove_dir,
    remove_file,
    write,
)
from storage.auxiliary.models.functional_revision import FunctionalRevision
from storage.auxiliary.models.state import DatasetID, PwnedStorageState, StoredStateKeys
from storage.models.abstract import (
    PwnedRangeProvider,
    PwnedStorage,
    UpdateCancellationResponse,
    UpdateResponse,
    UpdateResult,
)
from storage.models.revision import Revision


class PwnedStorageBase(PwnedStorage):
    """The base for Pwned storage."""

    DEFAULT_REVISION_COROUTINE_QUANTITY: int = 64
    """Default quantity of coroutines to be used during update."""

    STATE_WAIT_TIME_SECONDS: float = 0.5
    """Wait time in seconds between state checks."""

    STATE_FILE: str = "state.json"
    """The filename for storing state information."""

    IMPLEMENTATION_FILE: str = "implementation.json"
    """The filename for storing implementation information."""

    IMPLEMENTATION_NAME_KEY: str = "name"
    """The key in the implementation information JSON file to identify the implementation name."""

    DEFAULT_DATASET: DatasetID = DatasetID.A
    """The default dataset to be used."""

    def __init__(
        self,
        resource_dir: str,
        range_provider: PwnedRangeProvider,
        revision_coroutine_quantity: int = DEFAULT_REVISION_COROUTINE_QUANTITY,
    ):
        """
        Initialize the Pwned storage base.

        :param resource_dir: The directory path for storing resources.
        :param range_provider: The instance of the Pwned range provider.
        :param revision_coroutine_quantity: The number of coroutines to be used for requesting hashed during revision.
        """
        self.__resource_dir: str = resource_dir
        self.__state_file_path: str = join_paths(resource_dir, self.STATE_FILE)
        self.__implementation_file_path: str = join_paths(
            resource_dir, self.IMPLEMENTATION_FILE
        )
        self._range_provider: PwnedRangeProvider = range_provider
        self._revision: FunctionalRevision = FunctionalRevision()
        self._revision_coroutine_quantity: int = revision_coroutine_quantity
        self.__state: PwnedStorageState = PwnedStorageState()
        self.__initialize()

    @property
    def revision(self) -> Revision:
        return self._revision.to_dto()

    async def get_range(self, prefix: str) -> str:
        prefix = self._validate_prefix(prefix)
        while self._revision.is_transiting:
            await self.__wait_a_little()
        self.__state.count_started_request()
        try:
            return self._get_range(prefix)
        finally:
            self.__state.count_finished_request()

    async def update(self) -> UpdateResult:
        """
        Request an update of all Pwned password leak records.
        :return: The update response status.
        """
        if not self._revision.is_idle:
            return UpdateResult.BUSY
        self._revision.indicate_started()
        await self.__update_safely()
        if self._revision.is_failed:
            return UpdateResult.FAILED
        if self._revision.is_cancelled:
            return UpdateResult.CANCELLED
        return UpdateResult.DONE

    def request_update(self) -> UpdateResponse:
        """
        Request an update of all Pwned password leak records.
        :return: The update response status.
        """
        if not self._revision.is_idle:
            return UpdateResponse.BUSY
        self._revision.indicate_started()
        asyncio.create_task(self.__update_safely())
        return UpdateResponse.STARTED

    def request_update_cancellation(self) -> UpdateCancellationResponse:
        """
        Request an update cancellation.
        :return: The update cancellation response status.
        """
        if not self._revision.is_preparing:
            return UpdateCancellationResponse.IRRELEVANT
        self._revision.indicate_cancellation()
        return UpdateCancellationResponse.ACCEPTED

    @staticmethod
    def _validate_prefix(prefix: str) -> str:
        if not isinstance(prefix, str):
            raise ValueError("The hash prefix must be a string.")
        prefix = prefix.upper()
        if not all([symbol.isdigit() or symbol in "ABCDEF" for symbol in prefix]):
            raise ValueError("The hash prefix must be a hex string.")
        if len(prefix) < 5 or 6 < len(prefix):
            raise ValueError("The hash prefix must have a length of 5 or 6 symbols.")
        return prefix

    @staticmethod
    async def __wait_a_little() -> None:
        await asyncio.sleep(PwnedStorageBase.STATE_WAIT_TIME_SECONDS)

    @abstractmethod
    def _get_setting_dict(self) -> Dict:
        pass

    @abstractmethod
    def _get_range(self, prefix) -> str:
        pass

    @abstractmethod
    async def _prepare_batch(self, dataset: DatasetID, batch_index: int) -> None:
        pass

    @property
    def __class_name(self) -> str:
        return self.__class__.__name__

    @property
    def _active_dataset_dir(self) -> str:
        if self.__state.active_dataset is None:
            raise RuntimeError("The storage has no active dataset.")
        return self._get_dataset_dir(self.__state.active_dataset)

    def _get_dataset_dir(self, dataset: DatasetID) -> str:
        return join_paths(self.__resource_dir, dataset.dir_name)

    async def __update_safely(self) -> None:
        new_dataset = (self.__state.active_dataset or self.DEFAULT_DATASET.other).other
        try:
            await self.__update(new_dataset)
        except Exception as error:
            self._revision.indicate_failed(error)
        if self._revision.is_cancelled or self._revision.is_failed:
            await self.__try_remove_dataset(new_dataset)
        if self._revision.is_completed:
            await self.__try_remove_dataset(new_dataset.other)

    async def __update(self, new_dataset: DatasetID) -> None:
        await self.__prepare_new_dataset(new_dataset)
        if self._revision.is_cancelling:
            self._revision.indicate_cancelled()
            await self.__try_remove_dataset(new_dataset)
            return
        self._revision.indicate_prepared()
        while self.__state.has_active_requests:
            await self.__wait_a_little()
        self.__state.mark_to_be_ignored()
        self.__dump_state()
        self.__state.active_dataset = new_dataset
        self.__state.mark_not_to_be_ignored()
        self.__dump_state()
        self._revision.indicate_transited()
        await self.__try_remove_dataset(new_dataset.other)
        self._revision.indicate_completed()

    async def __prepare_new_dataset(self, dataset: DatasetID) -> None:
        dataset_dir = self._get_dataset_dir(dataset)
        await asyncio.to_thread(lambda: make_empty_dir(dataset_dir))
        await asyncio.gather(
            *[
                self._prepare_batch(dataset, batch_index)
                for batch_index in range(self._revision_coroutine_quantity)
            ]
        )

    async def __try_remove_dataset(self, dataset: DatasetID) -> None:
        try:
            await asyncio.to_thread(lambda: remove_dir(self._get_dataset_dir(dataset)))
        except Exception as error:
            # TODO: Log error.
            pass

    def __dump_state(self) -> None:
        state = dict()
        if self.__state.active_dataset is not None:
            state[StoredStateKeys.ACTIVE_DATASET] = self.__state.active_dataset.value
        if self.__state.is_to_be_ignored:
            state[StoredStateKeys.IGNORE_STATE_IN_FILE] = self.__state.is_to_be_ignored
        write(self.__state_file_path, json.dumps(state), overwrite=True)

    def __dump_implementation_info(self) -> None:
        info = self._get_setting_dict()
        info[self.IMPLEMENTATION_NAME_KEY] = self.__class_name
        write(self.__implementation_file_path, json.dumps(info), overwrite=True)

    def __remove_state_file_if_is_not_relevant(self) -> None:
        if not is_file(self.__implementation_file_path):
            self.__dump_implementation_info()
            return
        try:
            implementation_info = json.loads(read(self.__implementation_file_path))
        except JSONDecodeError:
            return
        if not isinstance(implementation_info, dict):
            return
        if implementation_info.get(
            self.IMPLEMENTATION_NAME_KEY
        ) == self.__class_name and all(
            implementation_info.get(key) == value
            for key, value in self._get_setting_dict().items()
        ):
            return
        remove_file(self.__state_file_path)
        self.__dump_implementation_info()

    def __import_state_from_file(self) -> None:
        if not is_file(self.__state_file_path):
            return
        try:
            state = json.loads(read(self.__state_file_path))
        except JSONDecodeError:
            return
        if not isinstance(state, dict):
            return
        if (
            StoredStateKeys.IGNORE_STATE_IN_FILE in state
            and state[StoredStateKeys.IGNORE_STATE_IN_FILE]
        ):
            return
        if StoredStateKeys.ACTIVE_DATASET in state:
            for dataset in DatasetID:
                if dataset.value == state[StoredStateKeys.ACTIVE_DATASET]:
                    self.__state.active_dataset = dataset

    def __initialize(self) -> None:
        make_dir_if_not_exists(self.__resource_dir)
        self.__remove_state_file_if_is_not_relevant()
        self.__import_state_from_file()
