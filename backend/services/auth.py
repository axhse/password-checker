import hashlib
import secrets
import time
from typing import Dict

import jwt

from backend.app.environment import EnvKey, get_env_value


class AuthService:
    SESSION_TOKEN_COOKIE_NAME = "session_token"

    def __init__(self):
        self.__session_secret_key = secrets.token_hex(32)
        self.__admin_session_lifetime: int = 60 * get_env_value(
            EnvKey.ADMIN_SESSION_LIFETIME_IN_MINUTES, int
        )
        admin_password = get_env_value(EnvKey.ADMIN_PASSWORD, str)
        self.__encoded_admin_password: str = self.__encode_password(admin_password)

    def create_admin_session_token(self) -> str:
        payload = {
            "sub": "admin",
            "exp": self.__get_current_ts() + self.__admin_session_lifetime,
        }
        return jwt.encode(payload, self.__session_secret_key, algorithm="HS256")

    def has_admin_session(self, cookies: Dict) -> bool:
        if self.SESSION_TOKEN_COOKIE_NAME not in cookies:
            return False
        jwt_data = cookies.get(self.SESSION_TOKEN_COOKIE_NAME)
        try:
            payload = jwt.decode(
                jwt_data, self.__session_secret_key, algorithms=["HS256"]
            )
            if not isinstance(payload, dict) or "sub" not in payload:
                return False
            if payload["sub"] != "admin":
                return False
            if "exp" not in payload or not isinstance(payload["exp"], int):
                return False
            return self.__get_current_ts() <= payload["exp"]
        except jwt.InvalidTokenError:
            return False

    def is_admin_password(self, password: str) -> bool:
        return self.__encoded_admin_password == self.__encode_password(password)

    @staticmethod
    def __encode_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def __get_current_ts() -> int:
        return int(time.time())
