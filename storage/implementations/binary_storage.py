from storage.auxiliary.filetools import join_paths
from storage.auxiliary.implementations.record_converter import PwnedRecordConverter
from storage.auxiliary.implementations.record_search import PwnedRecordSearch
from storage.auxiliary.models.state import DatasetID
from storage.auxiliary.numeration import number_to_hex_code
from storage.implementations.storage_base import PwnedStorageBase
from storage.models.abstract import PwnedRangeProvider
from storage.models.pwned import PWNED_PREFIX_CAPACITY
from storage.models.settings import BinaryPwnedStorageSettings


class BinaryPwnedStorage(PwnedStorageBase):
    """Stores Pwned password leak records in files in memory-effective binary format."""

    def __init__(
        self,
        resource_dir: str,
        range_provider: PwnedRangeProvider,
        revision_coroutine_quantity: int = PwnedStorageBase.DEFAULT_REVISION_COROUTINE_QUANTITY,
        settings: BinaryPwnedStorageSettings = BinaryPwnedStorageSettings(),
    ):
        """
        Initialize a new BinaryPwnedStorage instance.

        :param resource_dir: The directory path for storing resources.
        :param range_provider: The instance of Pwned range provider.
        :param revision_coroutine_quantity: The number of coroutines to be used for requesting hashed during revision.
        :param settings: The settings for the binary storage.
        """
        super().__init__(resource_dir, range_provider, revision_coroutine_quantity)
        self.__settings: BinaryPwnedStorageSettings = settings
        self.__pwned_converter: PwnedRecordConverter = PwnedRecordConverter(
            settings.file_code_length,
            settings.occasion_numeric_type,
        )
        self.__record_search: PwnedRecordSearch = PwnedRecordSearch(
            self.__pwned_converter
        )

    def _get_range(self, prefix) -> str:
        return self.__record_search.get_range(prefix, self._active_dataset_dir)

    async def _prepare_batch(self, dataset: DatasetID, batch_index: int) -> None:
        dataset_dir = self._get_dataset_dir(dataset)
        file_quantity = self.__settings.file_quantity
        prefix_group_size = PWNED_PREFIX_CAPACITY // file_quantity
        coroutine_quantity = self._revision_coroutine_quantity
        for file_index in range(
            file_quantity * batch_index // coroutine_quantity,
            file_quantity * (batch_index + 1) // coroutine_quantity,
        ):
            if self._revision.is_cancelling or self._revision.is_failed:
                return
            file_path = join_paths(
                dataset_dir, f"{number_to_hex_code(file_index, file_quantity)}.dat"
            )
            with open(file_path, "wb") as data_file:
                for prefix_index in range(
                    file_index * prefix_group_size, (file_index + 1) * prefix_group_size
                ):
                    hash_prefix = number_to_hex_code(
                        prefix_index, PWNED_PREFIX_CAPACITY
                    )
                    records = await self._range_provider.get_range(hash_prefix)
                    data_file.write(
                        b"".join(
                            self.__pwned_converter.record_to_bytes(record, hash_prefix)
                            for record in records.split()
                        )
                    )
                    self._revision.count_prepared_prefix()
