from typing import List

from storage.models.settings import NumericType, StorageFileQuantity

STORAGE_FILE_QUANTITY_INT_OPTIONS: List[int] = [
    quantity.value for quantity in StorageFileQuantity
]
"""All possible options for storage file quantity."""

NUMERIC_TYPE_INT_OPTIONS: List[int] = [
    numeric_type.value for numeric_type in NumericType
]
"""All possible options for numeric type."""


def get_storage_file_quantity(file_quantity_number: int) -> StorageFileQuantity:
    """
    Retrieve the StorageFileQuantity value for a given file quantity number.

    :param file_quantity_number: The file quantity number.
    :return: The corresponding StorageFileQuantity value.
    """
    for quantity in StorageFileQuantity:
        if quantity.value == file_quantity_number:
            return quantity

    raise ValueError(
        f"No matching StorageFileQuantity for file quantity number: {file_quantity_number}"
    )


def get_numeric_type(number_of_bytes: int) -> NumericType:
    """
    Retrieve the NumericType value for a given number of bytes.

    :param number_of_bytes: The number of bytes.
    :return: The corresponding NumericType value.
    """
    for numeric_type in NumericType:
        if numeric_type.value == number_of_bytes:
            return numeric_type

    raise ValueError(f"No matching NumericType for number of bytes: {number_of_bytes}")
