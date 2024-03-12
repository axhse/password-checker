from storage.models.pwned import PWNED_PREFIX_LENGTH, SHA1_HASH_LENGTH
from storage.models.settings import NumericType


class PwnedRecordConverter:
    """Pwned password leak record converter."""

    def __init__(self, dropped_prefix_length: int, numeric_type: NumericType):
        """
        Initialize a new PwnedRecordConverter instance.

        :param dropped_prefix_length: The length of the prefix to drop when converting string records to bytes.
        :param numeric_type: The numeric type used for storing integer values.
        """
        self.__dropped_prefix_length: int = dropped_prefix_length
        self.__has_stored_suffix_odd_length: bool = (
            SHA1_HASH_LENGTH - dropped_prefix_length
        ) % 2 != 0
        self.__numeric_byte_length: int = numeric_type.byte_length
        self.__max_numeric_value: int = numeric_type.max_unsigned_value
        self.__stored_suffix_size = (SHA1_HASH_LENGTH - dropped_prefix_length + 1) // 2
        self.__stored_record_size: int = (
            self.__stored_suffix_size + self.__numeric_byte_length
        )

    @property
    def dropped_prefix_length(self) -> int:
        """
        Get the length of the prefix that is dropped when converting string records to bytes.
        :return: The length of the dropped prefix.
        """
        return self.__dropped_prefix_length

    @property
    def record_size(self) -> int:
        """
        Get the size of the stored record in bytes.
        :return: The size of the record in bytes.
        """
        return self.__stored_record_size

    def record_to_bytes(self, record_row: str, record_prefix: str) -> bytes:
        """
        Convert a string Pwned password leak record to bytes.

        :param record_row: A string record.
        :param record_prefix: The prefix of the record.
        :return: The record converted to bytes.
        """
        hex_hash, _, occasions = record_row.partition(":")
        hex_hash = (record_prefix + hex_hash)[self.dropped_prefix_length :]
        if len(hex_hash) % 2 != 0:
            hex_hash = hex_hash + "0"
        occasions = min(int(occasions), self.__max_numeric_value)
        hash_bytes = bytes.fromhex(hex_hash)
        number_bytes = occasions.to_bytes(
            self.__numeric_byte_length, byteorder="big", signed=False
        )
        return hash_bytes + number_bytes

    def record_from_bytes(self, record_bytes: bytes, dropped_prefix: str) -> str:
        """
        Convert bytes back to a Pwned password leak string record.

        :param record_bytes: The bytes representing the record.
        :param dropped_prefix: The dropped prefix before conversion.
        :return: The reconstructed Pwned password leak string record.
        """
        hash_bytes = record_bytes[: self.__stored_suffix_size]
        number_bytes = record_bytes[self.__stored_suffix_size :]
        hex_hash = bytes.hex(hash_bytes)
        if self.__has_stored_suffix_odd_length:
            hex_hash = hex_hash[:-1]
        occasions = int.from_bytes(number_bytes, byteorder="big", signed=False)
        return f"{dropped_prefix}{hex_hash.upper()}:{occasions}"[PWNED_PREFIX_LENGTH:]

    def has_desired_stored_prefix_odd_length(self, full_desired_prefix: str) -> bool:
        """
        Check if the desired stored prefix has an odd length.

        :param full_desired_prefix: The full desired prefix to check.
        :return: True if the full desired stored prefix has an odd length, False otherwise.
        """
        return (len(full_desired_prefix) - self.__dropped_prefix_length) % 2 != 0

    def desired_stored_prefix_bytes(self, full_desired_prefix: str) -> bytes:
        """
        Get the desired stored prefix as bytes.

        :param full_desired_prefix: The full desired prefix.
        :return: The desired stored prefix as bytes.
        """
        desired_stored_prefix = full_desired_prefix[self.__dropped_prefix_length :]
        if len(desired_stored_prefix) % 2 != 0:
            desired_stored_prefix = desired_stored_prefix + "0"
        return bytes.fromhex(desired_stored_prefix)
