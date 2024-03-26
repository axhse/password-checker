import os
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

TEnvVar = TypeVar("TEnvVar")


class GenericEnvVar(Generic[TEnvVar], ABC):
    """Generic environment variable."""

    def __init__(self, key: str):
        self.__key = key

    def get(self) -> TEnvVar:
        nullable_str_value = self.__get_nullable_str_value()
        if nullable_str_value is None:
            raise ValueError(f"Environment variable {self.__key} is not set.")
        return self._convert_value(nullable_str_value)

    def get_nullable(self) -> Optional[TEnvVar]:
        nullable_str_value = self.__get_nullable_str_value()
        if nullable_str_value is None:
            return None
        return self._convert_value(nullable_str_value)

    def get_or_default(self, default: TEnvVar) -> Optional[TEnvVar]:
        nullable_str_value = self.__get_nullable_str_value()
        if nullable_str_value is None:
            return default
        return self._convert_value(nullable_str_value)

    @property
    def _key(self) -> str:
        return self.__key

    @abstractmethod
    def _convert_value(self, str_value: str) -> TEnvVar:
        pass

    def __get_nullable_str_value(self) -> str:
        return os.environ.get(self.__key)


class StrEnvVar(GenericEnvVar[str]):
    """String environment variable."""

    def __init__(self, key: str):
        super().__init__(key)

    def _convert_value(self, str_value: str) -> str:
        return str_value


class IntEnvVar(GenericEnvVar[int]):
    """Integer environment variable."""

    def __init__(self, key: str):
        super().__init__(key)

    def _convert_value(self, str_value: str) -> int:
        return int(str_value)


class FloatEnvVar(GenericEnvVar[float]):
    """Float environment variable."""

    def __init__(self, key: str):
        super().__init__(key)

    def _convert_value(self, str_value: str) -> float:
        return float(str_value)


class BoolEnvVar(GenericEnvVar[bool]):
    """Boolean environment variable."""

    STR_VALUES_TRUE = ["TRUE", "True", "true"]
    STR_VALUES_FALSE = ["FALSE", "False", "false"]

    def __init__(self, key: str):
        super().__init__(key)

    def _convert_value(self, str_value: str) -> bool:
        if str_value in self.STR_VALUES_TRUE:
            return True
        if str_value in self.STR_VALUES_FALSE:
            return False
        raise ValueError(
            f"Invalid string value '{str_value}' for boolean environment variable {self._key}."
        )


class EnvVar:
    class App:
        HTTPS_ONLY: BoolEnvVar = BoolEnvVar("HTTPS_ONLY")

    class Admin:
        SESSION_LIFETIME_IN_MINUTES: IntEnvVar = IntEnvVar(
            "ADMIN_SESSION_LIFETIME_IN_MINUTES"
        )
        PASSWORD: StrEnvVar = StrEnvVar("ADMIN_PASSWORD")

    class Storage:
        RESOURCE_DIR: StrEnvVar = StrEnvVar("STORAGE_RESOURCE_DIR")
        USER_AGENT: StrEnvVar = StrEnvVar("STORAGE_USER_AGENT")
        COROUTINES: IntEnvVar = IntEnvVar("STORAGE_COROUTINES")
        FILES: IntEnvVar = IntEnvVar("STORAGE_FILES")
        NUMERIC_BYTES: IntEnvVar = IntEnvVar("STORAGE_NUMERIC_BYTES")
        IS_MOCKED: BoolEnvVar = BoolEnvVar("IS_STORAGE_MOCKED")
        IS_TEXT: BoolEnvVar = BoolEnvVar("IS_STORAGE_TEXT")
