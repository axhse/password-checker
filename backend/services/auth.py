import hashlib
import secrets
import time

import jwt
from starlette.requests import Request
from starlette.responses import Response

from backend.app.environment import EnvVar


class AuthService:
    SESSION_TOKEN_COOKIE_NAME = "session_token"
    DEFAULT_ADMIN_SESSION_LIFETIME_IN_MINUTES = 60

    def __init__(self):
        self.__session_secret_key: str = secrets.token_hex(32)
        self.__is_https_only: bool = EnvVar.App.HTTPS_ONLY.get()
        self.__admin_session_lifetime: int = (
            60
            * EnvVar.Admin.SESSION_LIFETIME_IN_MINUTES.get_or_default(
                self.DEFAULT_ADMIN_SESSION_LIFETIME_IN_MINUTES
            )
        )
        admin_password: str = EnvVar.Admin.PASSWORD.get()
        self.__encoded_admin_password: str = self.__encode_password(admin_password)

    def set_admin_session(self, response: Response) -> None:
        session_token = self.create_admin_session_token()
        response.set_cookie(
            key=AuthService.SESSION_TOKEN_COOKIE_NAME,
            value=session_token,
            secure=self.__is_https_only,
            httponly=True,
        )

    def create_admin_session_token(self) -> str:
        payload = {
            "sub": "admin",
            "exp": self.__get_current_ts() + self.__admin_session_lifetime,
        }
        return jwt.encode(payload, self.__session_secret_key, algorithm="HS256")

    def has_admin_session(self, request: Request) -> bool:
        if self.SESSION_TOKEN_COOKIE_NAME in request.headers:
            jwt_data = request.headers.get(self.SESSION_TOKEN_COOKIE_NAME)
        else:
            if self.SESSION_TOKEN_COOKIE_NAME not in request.cookies:
                return False
            jwt_data = request.cookies.get(self.SESSION_TOKEN_COOKIE_NAME)
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
