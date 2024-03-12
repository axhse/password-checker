import asyncio

from devops.auxiliary.core import watch_and_print_revision
from storage.implementations.binary_storage import BinaryPwnedStorage
from storage.implementations.mocked_requester import MockedPwnedRequester
from storage.implementations.requester import PwnedRequester
from storage.implementations.text_storage import TextPwnedStorage
from storage.models.settings import (
    BinaryPwnedStorageSettings,
    NumericType,
    StorageFileQuantity,
)


async def update_storage(
    resource_dir: str,
    user_agent: str,
    revision_coroutine_quantity: int,
    is_mocked_requester: bool,
    is_text_implementation: bool,
    file_quantity: StorageFileQuantity,
    occasion_numeric_type: NumericType,
) -> None:
    """Update Pwned storage."""
    settings = BinaryPwnedStorageSettings(file_quantity, occasion_numeric_type)
    requester = (
        MockedPwnedRequester(user_agent)
        if is_mocked_requester
        else PwnedRequester(user_agent)
    )
    storage = (
        TextPwnedStorage(resource_dir, requester, revision_coroutine_quantity)
        if is_text_implementation
        else BinaryPwnedStorage(
            resource_dir, requester, revision_coroutine_quantity, settings
        )
    )
    await asyncio.gather(storage.update(), watch_and_print_revision(storage))
