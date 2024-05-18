import asyncio

import pytest

from storage.auxiliary import hasher
from storage.auxiliary.filetools import join_paths
from storage.implementations.binary_storage import BinaryPwnedStorage
from storage.implementations.mocked_requester import MockedPwnedRequester
from storage.models.abstract import PwnedRangeProvider, PwnedStorage, UpdateResult
from storage.models.pwned import PWNED_PREFIX_CAPACITY
from storage.models.revision import RevisionStatus
from storage.models.settings import (
    BinaryPwnedStorageSettings,
    NumericType,
    StorageFileQuantity,
)
from tests.shared import temp_dir

NUMERIC_TYPE = NumericType.BYTE


class RangeRequestCounter(PwnedRangeProvider):
    RANGE = f"{'0' * 35}:1"

    def __init__(self):
        self.prefix_request_counts = dict()

    async def get_range(self, prefix):
        await asyncio.sleep(0)
        self.prefix_request_counts[prefix] = 1 + self.prefix_request_counts.get(
            prefix, 0
        )
        return self.RANGE


def create_range_provider() -> PwnedRangeProvider:
    return MockedPwnedRequester("pwned-checker-tests")


def create_storage(temp_dir: str, range_provider: PwnedRangeProvider) -> PwnedStorage:
    resource_dir = join_paths(temp_dir, "storage")
    settings = BinaryPwnedStorageSettings(
        StorageFileQuantity.N_256,
        NUMERIC_TYPE,
    )
    coroutines = 3
    return BinaryPwnedStorage(resource_dir, range_provider, coroutines, settings)


@pytest.fixture(scope="session")
def range_provider() -> PwnedRangeProvider:
    return create_range_provider()


@pytest.fixture(scope="session")
def storage(temp_dir: str, range_provider: PwnedRangeProvider) -> PwnedStorage:
    return create_storage(temp_dir, range_provider)


@pytest.fixture(scope="session")
def updated_storage(storage: PwnedStorage) -> PwnedStorage:
    asyncio.run(storage.update())
    assert storage.revision.status == RevisionStatus.COMPLETED
    return storage


@pytest.mark.asyncio
async def test_ranges(
    updated_storage: PwnedStorage, range_provider: PwnedRangeProvider
):
    prefixes_to_check = ["FADED", "Faded", "F" * 5]
    for prefix in prefixes_to_check:
        found_range = await updated_storage.get_range(prefix)
        requested_range = await range_provider.get_range(prefix)
        assert found_range == requested_range
    found_range = await updated_storage.get_range("0" * 5)
    requested_range = await range_provider.get_range("0" * 5)
    assert len(found_range) == len(requested_range)
    assert found_range.count("\n") == requested_range.count("\n")
    assert found_range[:100] == requested_range[:100]
    assert (
        found_range[len(found_range) // 2 : len(found_range) // 2 + 100]
        == requested_range[len(found_range) // 2 : len(found_range) // 2 + 100]
    )
    assert found_range[-100:] == requested_range[-100:]


@pytest.mark.asyncio
async def test_leak_check(updated_storage: PwnedStorage):
    for password in ["hello", "hello12345"]:
        password_hash = hasher.sha1(password)
        records1 = await updated_storage.get_range(password_hash[:5])
        records2 = await updated_storage.get_range(password_hash[:6])
        expected_line = password_hash[5:] + ":"
        assert expected_line in records1
        assert expected_line in records2
    for password in ["1233492830984234230984", "123_56789"]:
        password += "_"
        password_hash = hasher.sha1(password)
        records1 = await updated_storage.get_range(password_hash[:5])
        records2 = await updated_storage.get_range(password_hash[:6])
        not_expected_suffix = password_hash[5:]
        assert not_expected_suffix not in records1
        assert not_expected_suffix not in records2


@pytest.mark.asyncio
async def test_revision_info(
    updated_storage: PwnedStorage, temp_dir: str, range_provider: PwnedRangeProvider
):
    revision = updated_storage.revision
    assert revision.status == RevisionStatus.COMPLETED
    assert revision.start_ts is not None
    assert revision.end_ts is not None
    assert revision.error_message is None
    assert revision.progress is None
    new_revision = create_storage(temp_dir, range_provider).revision
    assert new_revision.status == revision.status
    assert new_revision.start_ts == revision.start_ts
    assert new_revision.end_ts == revision.end_ts
    assert new_revision.error_message == revision.error_message
    assert new_revision.progress == revision.progress


@pytest.mark.asyncio
async def test_update_pause(temp_dir: str):
    request_counter = RangeRequestCounter()
    storage = create_storage(temp_dir, request_counter)

    async def __wait_for_progress(initial_progress):
        while storage.revision.status != RevisionStatus.PREPARATION:
            await asyncio.sleep(0)
        while storage.revision.progress == initial_progress:
            await asyncio.sleep(0)
        assert len(request_counter.prefix_request_counts) > 0

    async def __wait_for_stoppage():
        while storage.revision.status != RevisionStatus.STOPPED:
            assert storage.revision.status == RevisionStatus.STOPPAGE
            await asyncio.sleep(0)

    def __assert_all_prefixes_requested_once():
        assert all(
            count == 1 for count in request_counter.prefix_request_counts.values()
        )

    storage.request_update()
    await __wait_for_progress(0)
    storage.request_update_pause()
    await __wait_for_stoppage()
    __assert_all_prefixes_requested_once()
    start_ts = storage.revision.start_ts

    intermediate_progress = storage.revision.progress
    storage = create_storage(temp_dir, request_counter)
    storage.request_update()
    await __wait_for_progress(intermediate_progress)
    storage.request_update_pause()
    await __wait_for_stoppage()
    __assert_all_prefixes_requested_once()
    assert storage.revision.start_ts == start_ts

    assert await storage.update() == UpdateResult.DONE
    assert storage.revision.status == RevisionStatus.COMPLETED
    assert storage.revision.start_ts == start_ts

    assert len(request_counter.prefix_request_counts) == PWNED_PREFIX_CAPACITY
    __assert_all_prefixes_requested_once()

    found_range = await storage.get_range("00001")
    assert found_range == request_counter.RANGE
