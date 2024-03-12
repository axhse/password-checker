from backend.app.environment import EnvVar
from backend.services.auth import AuthService
from backend.services.password_strength_checker import PasswordStrengthChecker
from devops.common.utils import get_numeric_type, get_storage_file_quantity
from storage.implementations.binary_storage import BinaryPwnedStorage
from storage.implementations.mocked_requester import MockedPwnedRequester
from storage.implementations.requester import PwnedRequester
from storage.implementations.storage_base import PwnedStorageBase
from storage.implementations.text_storage import TextPwnedStorage
from storage.models.abstract import PwnedStorage
from storage.models.settings import BinaryPwnedStorageSettings


class Services:
    def __init__(self):
        """Initialize a new ServiceManager instance."""
        self.__auth_service: AuthService = AuthService()
        self.__strength_checker: PasswordStrengthChecker = PasswordStrengthChecker()
        self.__storage: PwnedStorage = build_pwned_storage()

    @property
    def auth(self) -> AuthService:
        """
        Get the authentication service.
        :return: The authentication service.
        """
        return self.__auth_service

    @property
    def storage(self) -> PwnedStorage:
        """
        Get the Pwned storage.
        :return: The Pwned storage.
        """
        return self.__storage

    @property
    def strength_checker(self) -> PasswordStrengthChecker:
        """
        Get the password strength checker.
        :return: The password strength checker.
        """
        return self.__strength_checker


def build_pwned_storage() -> PwnedStorage:
    """
    Build a Pwned storage instance.
    :return: A PwnedStorage instance.
    """
    user_agent = EnvVar.Storage.USER_AGENT.get()
    is_mocked = EnvVar.Storage.IS_MOCKED.get_or_default(False)
    requester = (
        MockedPwnedRequester(user_agent) if is_mocked else PwnedRequester(user_agent)
    )
    is_text = EnvVar.Storage.IS_TEXT.get_or_default(False)
    resource_dir = EnvVar.Storage.RESOURCE_DIR.get()
    coroutine_quantity = EnvVar.Storage.COROUTINES.get_or_default(
        PwnedStorageBase.DEFAULT_REVISION_COROUTINE_QUANTITY
    )
    if is_text:
        return TextPwnedStorage(resource_dir, requester, coroutine_quantity)
    file_quantity_number = EnvVar.Storage.FILES.get_or_default(
        BinaryPwnedStorageSettings.DEFAULT_FILE_QUANTITY.value
    )
    file_quantity = get_storage_file_quantity(file_quantity_number)
    occasion_bytes = EnvVar.Storage.NUMERIC_BYTES.get_or_default(
        BinaryPwnedStorageSettings.DEFAULT_OCCASION_NUMERIC_TYPE.byte_length
    )
    occasion_type = get_numeric_type(occasion_bytes)
    settings = BinaryPwnedStorageSettings(file_quantity, occasion_type)
    return BinaryPwnedStorage(resource_dir, requester, coroutine_quantity, settings)
