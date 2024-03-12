from typing import List, Tuple

import pytest

from storage.auxiliary.implementations.record_converter import PwnedRecordConverter
from storage.models.settings import NumericType


def record_conversion_parameters() -> List[Tuple[int, NumericType]]:
    return [
        (dropped_prefix_length, numeric_type)
        for numeric_type in NumericType
        for dropped_prefix_length in [0, 1, 2, 3, 10, 11, 38, 39, 40]
    ]


def record_conversion_cases() -> List[Tuple[str, str]]:
    return [
        (f"{'0' * 35}:0", "0" * 5),
        (f"{'0' * 35}:0", "F" * 5),
        (f"{'F' * 35}:0", "0" * 5),
        (f"{'F' * 35}:0", "F" * 5),
        ("0123456789ABCDEF0123456789ABCDEF012:345", "01234"),
        ("08033582034850114353458373485345735:999999", "F" * 5),
    ]


@pytest.mark.parametrize(
    "dropped_prefix_length, numeric_type", record_conversion_parameters()
)
def test_record_conversion(dropped_prefix_length: int, numeric_type: NumericType):
    converter = PwnedRecordConverter(dropped_prefix_length, numeric_type)
    for record, prefix in record_conversion_cases():
        record_partition = record.partition(":")
        expected_result = (
            record_partition[0]
            + record_partition[1]
            + str(min(int(record_partition[2]), numeric_type.max_unsigned_value))
        )
        dropped_prefix = (prefix + record)[:dropped_prefix_length]
        record_bytes = converter.record_to_bytes(record, prefix)
        actual_result = converter.record_from_bytes(record_bytes, dropped_prefix)
        assert actual_result == expected_result
