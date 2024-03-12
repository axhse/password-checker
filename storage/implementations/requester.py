import asyncio
import ssl
from typing import List

import aiohttp
import certifi
from aiohttp import ClientResponseError

from storage.models.abstract import PwnedRangeProvider


class PwnedRequester(PwnedRangeProvider):
    """Pwned API client."""

    PWNED_RANGE_API_BASE_URI: str = "https://api.pwnedpasswords.com/range/"
    """API base URI for the Pwned password leak range API"""

    RETRY_DELAYS: List[int] = [0, 30, 60, 120]
    """List of time delays (in seconds) for retry attempts."""

    def __init__(self, user_agent: str):
        """
        Initialize a new PwnedRequester instance.
        :param user_agent: The user agent header value to be used in HTTP requests.
                           More details: https://haveibeenpwned.com/API/v2#UserAgent
        """
        self.__user_agent: str = user_agent

    async def get_range_with_retries(self, hash_prefix: str) -> str:
        """
        Request the Pwned password leak record range for a hash prefix.
        Performs retries if necessary.

        :param hash_prefix: The hash prefix to query.
        :return: The range as plain text.
        """
        for delay_index in range(len(self.RETRY_DELAYS)):
            try:
                return await self.get_range(hash_prefix)
            except ClientResponseError:
                await self.__wait_for_delay(self.RETRY_DELAYS[delay_index])
        return await self.get_range(hash_prefix)

    async def get_range(self, hash_prefix: str) -> str:
        """
        Request the Pwned password leak record range for a hash prefix.

        :param hash_prefix: The hash prefix to query.
        :return: The range as plain text.
        """
        url = f"{self.PWNED_RANGE_API_BASE_URI}{hash_prefix}"
        headers = {"user-agent": self.__user_agent}
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        tcp_connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=tcp_connector) as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return (await response.text()).replace("\r\n", "\n")

    @staticmethod
    async def __wait_for_delay(delay: int) -> None:
        await asyncio.sleep(delay)
