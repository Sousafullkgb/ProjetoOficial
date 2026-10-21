from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlsplit


class ConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class AuthConfig:
    api_base_url: str


def validate_api_base_url(value: str) -> str:
    if not isinstance(value, str):
        raise ConfigurationError("XANO_API_BASE_URL deve ser um URL válido.")

    api_base_url = value.strip().rstrip("/")
    try:
        parsed = urlsplit(api_base_url)
    except ValueError:
        raise ConfigurationError("XANO_API_BASE_URL deve ser um URL válido.") from None

    is_local_http = parsed.scheme == "http" and parsed.hostname in {
        "localhost",
        "127.0.0.1",
        "::1",
    }

    if (
        not parsed.hostname
        or (parsed.scheme != "https" and not is_local_http)
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or "/api:" not in parsed.path
    ):
        raise ConfigurationError(
            "XANO_API_BASE_URL deve ser a URL HTTPS do grupo de APIs Xano "
            "(por exemplo, https://instancia.n7.xano.io/api:ZnpRG7wg)."
        )

    return api_base_url


def load_auth_config(
    secrets: Mapping[str, str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> AuthConfig:
    environment = os.environ if environ is None else environ
    configured_secrets = {} if secrets is None else secrets
    api_base_url = environment.get("XANO_API_BASE_URL") or configured_secrets.get(
        "XANO_API_BASE_URL"
    )

    if not isinstance(api_base_url, str) or not api_base_url.strip():
        raise ConfigurationError(
            "Configure XANO_API_BASE_URL no ambiente ou em "
            ".streamlit/secrets.toml para conectar ao backend."
        )

    return AuthConfig(api_base_url=validate_api_base_url(api_base_url))
