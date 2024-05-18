from typing import Dict

from storage.auxiliary.filetools import join_paths, read, write
from storage.auxiliary.models.state import DatasetID
from storage.auxiliary.numeration import number_to_hex_code
from storage.implementations.storage_base import PwnedStorageBase
from storage.models.pwned import PWNED_PREFIX_CAPACITY


class TextPwnedStorage(PwnedStorageBase):
    """Stores Pwned password leak records in separate files in text format."""

    @staticmethod
    def _validate_prefix(prefix: str) -> str:
        if not isinstance(prefix, str):
            raise ValueError("The hash prefix must be a string.")
        prefix = prefix.upper()
        if not all([symbol.isdigit() or symbol in "ABCDEF" for symbol in prefix]):
            raise ValueError("The hash prefix must be a hex string.")
        if len(prefix) != 5:
            raise ValueError("The hash prefix must have a length of 5 symbols.")
        return prefix

    def _get_setting_dict(self) -> Dict:
        return dict()

    def _get_range(self, prefix) -> str:
        return read(join_paths(self._active_dataset_dir, f"{prefix}.txt"))

    async def _prepare_batch(self, dataset: DatasetID, batch_index: int) -> None:
        dataset_dir = self._get_dataset_dir(dataset)
        for prefix_index in range(
            batch_index * PWNED_PREFIX_CAPACITY // self._revision_coroutine_quantity
            + self._revision.get_batch_preparation_offset(batch_index),
            (batch_index + 1)
            * PWNED_PREFIX_CAPACITY
            // self._revision_coroutine_quantity,
        ):
            if (
                self._revision.is_cancelling
                or self._revision.is_stopping
                or self._revision.is_failed
            ):
                return
            hash_prefix = number_to_hex_code(prefix_index, PWNED_PREFIX_CAPACITY)
            file_path = join_paths(dataset_dir, f"{hash_prefix}.txt")
            write(file_path, await self._range_provider.get_range(hash_prefix))
            self._revision.count_prepared_prefix(batch_index)
