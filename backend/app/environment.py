import os
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

TEnvVar = TypeVar("TEnvVar")


class GenericEnvVar(Generic[TEnvVar], ABC):
    """Generic environment variable."""

    def __init__(self, name: str):
        """
        Initialize GenericEnvVar instance.
        :param name: The name of the environment variable.
        """
        self.__name = name

    def get(self) -> TEnvVar:
        """
        Get the value of the environment variable.
        :return: The value of the environment variable.
        """
        nullable_str_value = self.__get_nullable_str_value()
        if nullable_str_value is None:
            raise ValueError(f"Environment variable {self.__name} is not set.")
        return self._convert_value(nullable_str_value)

    def get_nullable(self) -> Optional[TEnvVar]:
        """
        Get the nullable value of the environment variable.
        :return: The value of the environment variable if defined, otherwise None.
        """
        nullable_str_value = self.__get_nullable_str_value()
        if nullable_str_value is None:
            return None
        return self._convert_value(nullable_str_value)

    def get_or_default(self, default: TEnvVar) -> Optional[TEnvVar]:
        """
        Get the value of the environment variable or a default value if not defined.

        :param default: The default value to return if the environment variable is not defined.
        :return: The value of the environment variable if defined, otherwise the default value.
        """
        nullable_str_value = self.__get_nullable_str_value()
        if nullable_str_value is None:
            return default
        return self._convert_value(nullable_str_value)

    @property
    def _name(self) -> str:
        return self.__name

    @abstractmethod
    def _convert_value(self, str_value: str) -> TEnvVar:
        pass

    def __get_nullable_str_value(self) -> str:
        return os.environ.get(self.__name)


class StrEnvVar(GenericEnvVar[str]):
    """String environment variable."""

    def __init__(self, name: str):
        """
        Initialize a new StrEnvVar instance.
        :param name: The name of the environment variable.
        """
        super().__init__(name)

    def _convert_value(self, str_value: str) -> str:
        return str_value


class IntEnvVar(GenericEnvVar[int]):
    """Integer environment variable."""

    def __init__(self, name: str):
        """
        Initialize a new IntEnvVar instance.
        :param name: The name of the environment variable.
        """
        super().__init__(name)

    def _convert_value(self, str_value: str) -> int:
        return int(str_value)


class FloatEnvVar(GenericEnvVar[float]):
    """Float environment variable."""

    def __init__(self, name: str):
        """
        Initialize a new FloatEnvVar instance.
        :param name: The name of the environment variable.
        """
        super().__init__(name)

    def _convert_value(self, str_value: str) -> float:
        return float(str_value)


class BoolEnvVar(GenericEnvVar[bool]):
    """Boolean environment variable."""

    STR_VALUES_TRUE = ["TRUE", "True", "true"]
    """All allowed string values representing boolean 'True'"""

    STR_VALUES_FALSE = ["FALSE", "False", "false"]
    """All allowed string values representing boolean 'False'"""

    def __init__(self, name: str):
        """
        Initialize a new BoolEnvVar instance.
        :param name: The name of the environment variable.
        """
        super().__init__(name)

    def _convert_value(self, str_value: str) -> bool:
        if str_value in self.STR_VALUES_TRUE:
            return True
        if str_value in self.STR_VALUES_FALSE:
            return False
        raise ValueError(
            f"Invalid string value '{str_value}' for boolean environment variable {self._name}."
        )


class EnvVar:
    """All environment variables."""

    class App:
        """Application variables."""

        HTTPS_ONLY: BoolEnvVar = BoolEnvVar("HTTPS_ONLY")
        """Whether to forbid all unsecured connections"""

    class Admin:
        """Administrator variables."""

        SESSION_LIFETIME_IN_MINUTES: IntEnvVar = IntEnvVar(
            "ADMIN_SESSION_LIFETIME_IN_MINUTES"
        )
        """Lifetime of the admin session in minutes"""

        PASSWORD: StrEnvVar = StrEnvVar("ADMIN_PASSWORD")
        """Password for administration"""

    class Storage:
        """Storage variables."""

        RESOURCE_DIR: StrEnvVar = StrEnvVar("STORAGE_RESOURCE_DIR")
        """Directory to store data"""

        USER_AGENT: StrEnvVar = StrEnvVar("STORAGE_USER_AGENT")
        """User agent header value to be sent to the Pwned API"""

        COROUTINES: IntEnvVar = IntEnvVar("STORAGE_COROUTINES")
        """Number of coroutines for requesting hashes during revision"""

        FILES: IntEnvVar = IntEnvVar("STORAGE_FILES")
        """Number of files to store data"""

        NUMERIC_BYTES: IntEnvVar = IntEnvVar("STORAGE_NUMERIC_BYTES")
        """Size of stored leak occasion unsigned number in bytes"""

        IS_MOCKED: BoolEnvVar = BoolEnvVar("IS_STORAGE_MOCKED")
        """Whether to use a mocked Pwned requester"""

        IS_TEXT: BoolEnvVar = BoolEnvVar("IS_STORAGE_TEXT")
        """Whether to use a text implementation of storage"""
