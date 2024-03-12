from enum import Enum
from typing import Dict


class StorageFileQuantity(Enum):
    """The number of files (batches) in which the storage stores its data."""

    N_1 = 1
    """A single file."""

    N_16 = 16
    """16 files."""

    N_256 = 16**2
    """256 files."""

    N_4096 = 16**3
    """4096 files."""

    N_65536 = 16**4
    """65536 files."""

    N_1048576 = 16**5
    """1048576 files."""


class NumericType(Enum):
    """Integer numeric types with specific byte size."""

    BYTE = 1
    """Single-byte type."""

    SHORT = 2
    """2-byte type."""

    INTEGER = 4
    """4-byte type."""

    @property
    def byte_length(self) -> int:
        """
        Get type length in bytes.
        :return: Type length in bytes.
        """
        return self.value

    @property
    def capacity(self) -> int:
        """
        Get type capacity.
        :return: Type capacity.
        """
        return 256**self.value

    @property
    def max_unsigned_value(self) -> int:
        """
        Get the maximal supported value of unsigned version of the type.
        :return: Maximal unsigned value.
        """
        return self.capacity - 1


class BinaryPwnedStorageSettings:
    """Settings for BinaryPwnedStorage."""

    DEFAULT_FILE_QUANTITY = StorageFileQuantity.N_65536
    """The default number of files to store data."""

    DEFAULT_OCCASION_NUMERIC_TYPE = NumericType.INTEGER
    """The default size of stored leak occasion unsigned number in bytes."""

    def __init__(
        self,
        file_quantity: StorageFileQuantity = DEFAULT_FILE_QUANTITY,
        occasion_numeric_type: NumericType = DEFAULT_OCCASION_NUMERIC_TYPE,
    ):
        """
        Initialize a new PwnedStorageSettings instance.

        :param file_quantity: The number of files (batches) in which the storage stores its data.
        :param occasion_numeric_type: The numeric type used for storing leak occasion values.
        """
        self.__file_quantity: int = file_quantity.value
        self.__occasion_numeric_type: NumericType = occasion_numeric_type
        self.__file_code_length: int = self.__calculate_file_code_length()

    @property
    def file_quantity(self) -> int:
        """
        Get the quantity of storage files.
        :return: The quantity of storage files.
        """
        return self.__file_quantity

    @property
    def occasion_numeric_type(self) -> NumericType:
        """
        Get the numeric type used for storing leak occasion values.
        :return: The numeric type.
        """
        return self.__occasion_numeric_type

    @property
    def file_code_length(self) -> int:
        """
        Get the length of data file codes.
        :return: The length of data file codes.
        """
        return self.__file_code_length

    def to_dict(self) -> Dict:
        """
        Convert settings to dictionary.
        :return: Settings as a dictionary.
        """
        return {
            "file_quantity": self.file_quantity,
            "numeric_bytes": self.occasion_numeric_type.byte_length,
        }

    def __calculate_file_code_length(self) -> int:
        code_length = 0
        file_quantity = self.file_quantity - 1
        while file_quantity > 0:
            file_quantity //= 16
            code_length += 1
        return code_length
