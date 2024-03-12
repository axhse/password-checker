import asyncio

import pytest

from storage.auxiliary import hasher
from storage.auxiliary.filetools import join_paths, make_empty_dir
from storage.implementations.binary_storage import BinaryPwnedStorage
from storage.implementations.mocked_requester import MockedPwnedRequester
from storage.models.abstract import PwnedRangeProvider, PwnedStorage
from storage.models.revision import RevisionStatus
from storage.models.settings import (
    BinaryPwnedStorageSettings,
    NumericType,
    StorageFileQuantity,
)
from tests.shared import temp_dir

NUMERIC_TYPE = NumericType.BYTE


@pytest.fixture(scope="session")
def range_provider() -> PwnedRangeProvider:
    return MockedPwnedRequester("pwned-checker-tests")


@pytest.fixture(scope="session")
def storage(temp_dir: str, range_provider: PwnedRangeProvider) -> PwnedStorage:
    resource_dir = join_paths(temp_dir, "storage")
    make_empty_dir(resource_dir)
    settings = BinaryPwnedStorageSettings(
        StorageFileQuantity.N_256,
        NUMERIC_TYPE,
    )
    coroutines = max(16, 1 + len(MockedPwnedRequester.INCLUDED_PASSWORDS))
    return BinaryPwnedStorage(resource_dir, range_provider, coroutines, settings)


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
