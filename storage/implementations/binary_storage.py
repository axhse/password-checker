from typing import Dict

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
        :param range_provider: The instance of the Pwned range provider.
        :param revision_coroutine_quantity: The number of coroutines to be used for requesting hashes during revision.
        :param settings: The settings for the binary storage.
        """
        self.__settings: BinaryPwnedStorageSettings = settings
        super().__init__(resource_dir, range_provider, revision_coroutine_quantity)
        self.__pwned_converter: PwnedRecordConverter = PwnedRecordConverter(
            settings.file_code_length,
            settings.occasion_numeric_type,
        )
        self.__record_search: PwnedRecordSearch = PwnedRecordSearch(
            self.__pwned_converter
        )

    def _get_setting_dict(self) -> Dict:
        return self.__settings.to_dict()

    def _get_range(self, prefix) -> str:
        return self.__record_search.get_range(prefix, self._active_dataset_dir)

    async def _prepare_batch(self, dataset: DatasetID, batch_index: int) -> None:
        dataset_dir = self._get_dataset_dir(dataset)
        file_quantity = self.__settings.file_quantity
        prefix_group_size = PWNED_PREFIX_CAPACITY // file_quantity
        coroutine_quantity = self._revision_coroutine_quantity
        preparation_offset = self._revision.get_batch_preparation_offset(batch_index)
        first_batch_file_index = file_quantity * batch_index // coroutine_quantity
        file_offset = preparation_offset // prefix_group_size
        first_prefix_index = (
            first_batch_file_index * prefix_group_size + preparation_offset
        )
        for file_index in range(
            first_batch_file_index + file_offset,
            file_quantity * (batch_index + 1) // coroutine_quantity,
        ):
            file_path = join_paths(
                dataset_dir, f"{number_to_hex_code(file_index, file_quantity)}.dat"
            )
            with open(file_path, "ab") as data_file:
                for prefix_index in range(
                    max(file_index * prefix_group_size, first_prefix_index),
                    (file_index + 1) * prefix_group_size,
                ):
                    if (
                        self._revision.is_cancelling
                        or self._revision.is_stopping
                        or self._revision.is_failed
                    ):
                        return
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
                    self._revision.count_prepared_prefix(batch_index)
