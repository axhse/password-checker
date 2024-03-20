import os
from enum import Enum, auto
from typing import Type, Union


class EnvKey(Enum):
    """Environment variable name."""

    HTTPS_ONLY = auto()

    ADMIN_PASSWORD = auto()
    ADMIN_SESSION_LIFETIME_IN_MINUTES = auto()

    STORAGE_RESOURCE_DIR = auto()
    STORAGE_USER_AGENT = auto()
    STORAGE_COROUTINES = auto()
    STORAGE_FILES = auto()
    STORAGE_NUMERIC_BYTES = auto()
    IS_STORAGE_MOCKED = auto()
    IS_STORAGE_TEXT = auto()


def get_env_value(
    key: EnvKey,
    value_type: Union[Type[str], Type[int], Type[bool]],
    default: Union[None, str, int, bool] = None,
    nullable: bool = False,
) -> Union[None, str, int, bool]:
    """
    Get the value of environment variable.

    :param key: The environment variable key.
    :param value_type: The type of the environment variable value.
    :param default: The default value to replace None values.
    :param nullable: Whether the None value is allowed. Default: False.
    :return: The value.
    """
    optional_str_value: str = os.environ.get(key.name)
    if not nullable and optional_str_value is None and default is None:
        raise ValueError(f"The required value '{key.name}' is actually 'None'.")
    if value_type == int:
        return default if optional_str_value is None else int(optional_str_value)
    if value_type == bool:
        return (
            default
            if optional_str_value is None
            else optional_str_value.lower() not in ["false", "0"]
        )
    return default if optional_str_value is None else optional_str_value
