def number_to_hex_code(number: int, capacity: int) -> str:
    """
    Convert a number to a hexadecimal string with a fixed length based on the specified hexadecimal value capacity.

    :param number: The number.
    :param capacity: The capacity.
    :return: A hexadecimal string.
    """
    if number < 0 or capacity <= number:
        raise ValueError("The number does not fit the capacity.")
    number_width = 0
    capacity -= 1
    while capacity > 0:
        number_width += 1
        capacity //= 16
    return hex(number)[2:].upper().rjust(number_width, "0")
