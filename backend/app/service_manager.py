from backend.app.environment import EnvKey, get_env_value
from devops.common.utils import get_numeric_type, get_storage_file_quantity
from storage.implementations.binary_storage import BinaryPwnedStorage
from storage.implementations.mocked_requester import MockedPwnedRequester
from storage.implementations.requester import PwnedRequester
from storage.implementations.storage_base import PwnedStorageBase
from storage.implementations.text_storage import TextPwnedStorage
from storage.models.abstract import PwnedStorage
from storage.models.settings import BinaryPwnedStorageSettings


class ServiceManager:
    def __init__(self):
        user_agent = get_env_value(EnvKey.STORAGE_USER_AGENT, str)
        is_mocked = get_env_value(EnvKey.IS_STORAGE_MOCKED, bool, default=False)
        requester = (
            MockedPwnedRequester(user_agent)
            if is_mocked
            else PwnedRequester(user_agent)
        )
        is_text = get_env_value(EnvKey.IS_STORAGE_TEXT, bool, default=False)
        resource_dir = get_env_value(EnvKey.STORAGE_RESOURCE_DIR, str)
        coroutine_quantity = get_env_value(
            EnvKey.STORAGE_COROUTINES,
            int,
            default=PwnedStorageBase.DEFAULT_REVISION_COROUTINE_QUANTITY,
        )
        if is_text:
            storage = TextPwnedStorage(resource_dir, requester, coroutine_quantity)
        else:
            file_quantity_number = get_env_value(
                EnvKey.STORAGE_FILES,
                int,
                default=BinaryPwnedStorageSettings.DEFAULT_FILE_QUANTITY.value,
            )
            file_quantity = get_storage_file_quantity(file_quantity_number)
            occasion_bytes = get_env_value(
                EnvKey.STORAGE_NUMERIC_BYTES,
                int,
                default=BinaryPwnedStorageSettings.DEFAULT_OCCASION_NUMERIC_TYPE.byte_length,
            )
            occasion_type = get_numeric_type(occasion_bytes)
            settings = BinaryPwnedStorageSettings(file_quantity, occasion_type)
            storage = BinaryPwnedStorage(
                resource_dir, requester, coroutine_quantity, settings
            )
        self.__storage: PwnedStorage = storage

    @property
    def storage(self) -> PwnedStorage:
        return self.__storage
