import asyncio
from typing import List

from storage.auxiliary import hasher
from storage.implementations.requester import PwnedRequester
from storage.models.pwned import PWNED_PREFIX_LENGTH


class MockedPwnedRequester(PwnedRequester):
    """Mocked Pwned API client."""

    RECORD_QUANTITY: int = 1009
    """The quantity of fictive records to be generated."""

    INCLUDED_PASSWORDS: List[str] = [
        "hello",
        "hello12345",
        "123_56789",
    ]
    """List of passwords for which real data will be requested."""

    def __init__(self, user_agent: str):
        """
        Initialize a new MockedPwnedRequester instance.
        :param user_agent: The user agent value for the Pwned range API.
        """
        super().__init__(user_agent)
        self.__records: List[str] = [
            hasher.sha1(str(index * 397 + 124))[PWNED_PREFIX_LENGTH:]
            + f":{int(hasher.sha1(str(index * 82 + 59))[0], 16) + 1}"
            for index in range(self.RECORD_QUANTITY)
        ]
        self.__records.sort()
        self.__required_prefixes = set()
        self.__required_prefixes.add("00000")
        for password in self.INCLUDED_PASSWORDS:
            self.__required_prefixes.add(hasher.sha1(password)[:5])

    async def get_range(self, hash_prefix: str) -> str:
        hash_prefix = hash_prefix.upper()
        if hash_prefix in self.__required_prefixes:
            return await super().get_range(hash_prefix)
        await asyncio.sleep(0)
        num = int(hash_prefix, base=16)
        offset = (num + 3234) % 54347 % (self.RECORD_QUANTITY * 9 // 11 + 1) + 1
        amount = (num + 2832) % 71203 % 8235 % 4 + 1
        records = self.__records[offset : offset + amount]
        return "\n".join(records)
