from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import requests

from ggreviews.config import validate_api_base_url


class AuthAPIError(Exception):
    def __init__(self, message: str, *, code: str = "api_error") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


@dataclass(frozen=True)
class AuthSession:
    token: str
    user_id: int | str


class AuthAPI:
    def __init__(
        self,
        api_base_url: str,
        *,
        timeout: float = 10,
        session: requests.Session | None = None,
    ) -> None:
        self._api_base_url = validate_api_base_url(api_base_url)
        self._timeout = timeout
        self._session = session or requests.Session()

    def signup(self, name: str, email: str, password: str) -> AuthSession:
        response = self._request(
            "POST",
            "auth/signup",
            payload={
                "name": name.strip(),
                "email": email.strip().lower(),
                "password": password.strip(),
            },
            failure_message="Não foi possível criar a conta. Confira os dados e tente novamente.",
        )
        return self._auth_session(response)

    def login(self, email: str, password: str) -> AuthSession:
        response = self._request(
            "POST",
            "auth/login",
            payload={"email": email.strip().lower(), "password": password.strip()},
            failure_message="Não foi possível entrar agora. Tente novamente.",
        )
        return self._auth_session(response)

    def current_user(self, token: str) -> dict[str, Any]:
        response = self._request(
            "GET",
            "auth/me",
            token=token,
            failure_message="Não foi possível validar sua sessão agora.",
        )
        return response

    def request_password_reset(self, email: str) -> None:
        self._request(
            "POST",
            "reset/request-reset-link",
            payload={"email": email.strip().lower()},
            failure_message=(
                "Não foi possível processar a solicitação agora. Tente novamente mais tarde."
            ),
        )

    def complete_password_reset(
        self,
        magic_token: str,
        email: str,
        password: str,
        confirm_password: str,
    ) -> None:
        self._request(
            "POST",
            "reset/complete",
            payload={
                "magic_token": magic_token,
                "email": email.strip().lower(),
                "password": password.strip(),
                "confirm_password": confirm_password.strip(),
            },
            failure_message="Não foi possível redefinir a senha. Tente novamente.",
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, str] | None = None,
        token: str | None = None,
        failure_message: str,
    ) -> dict[str, Any]:
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            response = self._session.request(
                method,
                f"{self._api_base_url}/{path}",
                json=payload,
                headers=headers,
                timeout=self._timeout,
            )
        except requests.Timeout:
            raise AuthAPIError(
                "O serviço de autenticação demorou para responder. Tente novamente.",
                code="timeout",
            ) from None
        except requests.RequestException:
            raise AuthAPIError(
                "Não foi possível conectar ao serviço de autenticação.",
                code="connection_error",
            ) from None

        if response.status_code in (401, 403):
            if path == "auth/login":
                raise AuthAPIError(
                    "E-mail ou senha inválidos.", code="invalid_credentials"
                )
            if path == "auth/me":
                raise AuthAPIError(
                    "Sua sessão expirou. Entre novamente.", code="unauthenticated"
                )
            if path == "reset/complete":
                raise AuthAPIError(
                    "Este link é inválido ou expirou. Solicite um novo link.",
                    code="invalid_reset_link",
                )
            raise AuthAPIError(failure_message)

        if not response.ok:
            raise AuthAPIError(failure_message)

        try:
            data = response.json()
        except ValueError:
            raise AuthAPIError(
                "O serviço de autenticação retornou uma resposta inválida."
            ) from None

        if not isinstance(data, dict):
            raise AuthAPIError(
                "O serviço de autenticação retornou uma resposta inválida."
            )
        return data

    @staticmethod
    def _auth_session(response: dict[str, Any]) -> AuthSession:
        token = response.get("authToken")
        user_id = response.get("user_id")
        if not isinstance(token, str) or not token or not isinstance(
            user_id, (int, str)
        ):
            raise AuthAPIError(
                "O serviço de autenticação retornou uma resposta inválida."
            )
        return AuthSession(token=token, user_id=user_id)


def password_policy_error(password: str) -> str | None:
    normalized = password.strip()
    if len(normalized) < 8:
        return "A senha deve ter pelo menos 8 caracteres."
    if not any(character.isalpha() for character in normalized):
        return "A senha deve conter pelo menos uma letra."
    if not any(character.isdigit() for character in normalized):
        return "A senha deve conter pelo menos um número."
    return None


def email_validation_error(email: str) -> str | None:
    normalized = email.strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
        return "Informe um e-mail válido."
    return None
