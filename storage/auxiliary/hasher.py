import hashlib


def sha1(text: str) -> str:
    """
    Calculate the SHA-1 hash value of the input text.

    :param text: The text to be hashed.
    :return: The hexadecimal representation of the SHA-1 hash value in uppercase.
    """
    return hashlib.sha1(text.encode(encoding="ascii")).hexdigest().upper()
