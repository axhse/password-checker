import argparse
import asyncio

from devops.auxiliary import programs
from devops.common.utils import (
    NUMERIC_TYPE_INT_OPTIONS,
    STORAGE_FILE_QUANTITY_INT_OPTIONS,
    get_numeric_type,
    get_storage_file_quantity,
)
from storage.implementations.storage_base import PwnedStorageBase
from storage.models.settings import BinaryPwnedStorageSettings

if __name__ == "__main__":
    default_revision_coroutine_quantity = (
        PwnedStorageBase.DEFAULT_REVISION_COROUTINE_QUANTITY
    )
    default_file_quantity = BinaryPwnedStorageSettings.DEFAULT_FILE_QUANTITY.value
    default_occasion_byte_number = (
        BinaryPwnedStorageSettings.DEFAULT_OCCASION_NUMERIC_TYPE.value
    )

    parser = argparse.ArgumentParser(
        description="Update the Pwned leak record storage."
    )
    parser.add_argument(
        "resource_dir",
        type=str,
        help="The directory to store data (recommended to be empty).",
    )
    parser.add_argument(
        "user_agent",
        type=str,
        help="The user agent header value to be sent to the Pwned API. "
        "For more details, see: https://haveibeenpwned.com/API/v2#UserAgent",
    )
    parser.add_argument(
        "-c",
        "--revision-coroutines",
        type=int,
        choices=range(1, 1024 + 1),
        metavar="NUMBER",
        default=default_revision_coroutine_quantity,
        help="The number of coroutines for requesting hashes during revision."
        f" Default: {default_revision_coroutine_quantity}.",
    )
    parser.add_argument(
        "-m",
        "--mocked",
        action="store_true",
        help="Whether to use a mocked Pwned requester.",
    )
    parser.add_argument(
        "-t",
        "--text-implementation",
        action="store_true",
        help="Whether to use a text implementation of the storage. The binary implementation is used by default.",
    )
    parser.add_argument(
        "-f",
        "--files",
        type=int,
        choices=STORAGE_FILE_QUANTITY_INT_OPTIONS,
        default=default_file_quantity,
        help="The number of files (batches) to store data (for binary implementation)."
        f" Default: {default_file_quantity}.",
    )
    parser.add_argument(
        "-b",
        "--occasion-bytes",
        type=int,
        choices=NUMERIC_TYPE_INT_OPTIONS,
        default=default_occasion_byte_number,
        help="The size of the stored leak occasion unsigned number in bytes (for binary implementation)."
        f" Default: {default_occasion_byte_number}.",
    )

    args = parser.parse_args()
    asyncio.run(
        programs.update_storage(
            args.resource_dir,
            args.user_agent,
            args.revision_coroutines,
            args.mocked,
            args.text_implementation,
            get_storage_file_quantity(args.files),
            get_numeric_type(args.occasion_bytes),
        )
    )
