from __future__ import annotations

from typing import Any

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from ggreviews.auth_client import (
    AuthAPI,
    AuthAPIError,
    email_validation_error,
    password_policy_error,
)
from ggreviews.config import ConfigurationError, load_auth_config


def _capture_password_reset_link() -> None:
    magic_token = st.query_params.get("magic_token")
    email = st.query_params.get("email")
    if magic_token is None and email is None:
        return

    st.query_params.clear()
    if isinstance(magic_token, str) and magic_token and isinstance(email, str) and email:
        st.session_state["password_reset_link"] = {
            "magic_token": magic_token,
            "email": email,
        }
    else:
        st.session_state["password_reset_link"] = None


def _render_password_reset(api: AuthAPI, link: dict[str, str]) -> None:
    st.subheader("Redefinir senha")
    with st.form("complete_password_reset"):
        password = st.text_input("Nova senha", type="password")
        confirm_password = st.text_input("Confirme a nova senha", type="password")
        submitted = st.form_submit_button("Salvar nova senha")

    if not submitted:
        return
    if error := password_policy_error(password):
        st.error(error)
        return
    if password.strip() != confirm_password.strip():
        st.error("As senhas não correspondem.")
        return

    try:
        api.complete_password_reset(
            link["magic_token"], link["email"], password, confirm_password
        )
    except AuthAPIError as error:
        if error.code == "invalid_reset_link":
            st.session_state.pop("password_reset_link", None)
        st.error(error.message)
        return

    st.session_state.pop("password_reset_link", None)
    st.session_state["auth_notice"] = "Senha atualizada. Entre com sua nova senha."
    st.rerun()


def _render_signup(api: AuthAPI) -> None:
    with st.form("signup"):
        name = st.text_input("Nome")
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        confirm_password = st.text_input("Confirme a senha", type="password")
        submitted = st.form_submit_button("Criar conta")

    if not submitted:
        return
    if not name.strip():
        st.error("Informe seu nome.")
        return
    if email_error := email_validation_error(email):
        st.error(email_error)
        return
    if password_policy := password_policy_error(password):
        st.error(password_policy)
        return
    if password.strip() != confirm_password.strip():
        st.error("As senhas não correspondem.")
        return

    try:
        result = api.signup(name, email, password)
    except AuthAPIError as error:
        st.error(error.message)
        return

    st.session_state["auth_token"] = result.token
    st.rerun()


def _render_login(api: AuthAPI) -> None:
    with st.form("login"):
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

    if not submitted:
        return
    if email_error := email_validation_error(email):
        st.error(email_error)
        return
    try:
        result = api.login(email, password)
    except AuthAPIError as error:
        st.error(error.message)
        return

    st.session_state["auth_token"] = result.token
    st.rerun()


def _render_recovery(api: AuthAPI) -> None:
    with st.form("request_password_reset"):
        email = st.text_input("E-mail da conta")
        submitted = st.form_submit_button("Enviar link de recuperação")

    if not submitted:
        return
    if email_error := email_validation_error(email):
        st.error(email_error)
        return
    try:
        api.request_password_reset(email)
    except AuthAPIError as error:
        st.error(error.message)
        return

    st.success(
        "Se houver uma conta associada a esse e-mail, você receberá um link de recuperação."
    )


def _render_auth_forms(api: AuthAPI) -> None:
    login_tab, signup_tab, recovery_tab = st.tabs(
        ["Entrar", "Criar conta", "Recuperar senha"]
    )
    with login_tab:
        _render_login(api)
    with signup_tab:
        _render_signup(api)
    with recovery_tab:
        _render_recovery(api)


def _render_authenticated(api: AuthAPI, token: str) -> None:
    try:
        user: dict[str, Any] = api.current_user(token)
    except AuthAPIError as error:
        if error.code == "unauthenticated":
            st.session_state.pop("auth_token", None)
            st.warning(error.message)
        else:
            st.error(error.message)
            return
        _render_auth_forms(api)
        return

    st.success(f"Bem-vindo, {user.get('name') or user.get('email') or 'jogador'}!")
    if st.button("Sair"):
        st.session_state.pop("auth_token", None)
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="GGReviews", page_icon="🎮")
    _capture_password_reset_link()
    st.title("GGReviews")

    try:
        secrets = dict(st.secrets)
    except StreamlitSecretNotFoundError:
        secrets = {}

    try:
        config = load_auth_config(secrets=secrets)
    except ConfigurationError as error:
        st.error(str(error))
        st.stop()

    api = AuthAPI(config.api_base_url)
    if notice := st.session_state.pop("auth_notice", None):
        st.success(notice)

    reset_link = st.session_state.get("password_reset_link")
    if isinstance(reset_link, dict):
        _render_password_reset(api, reset_link)
        return
    if reset_link is None and "password_reset_link" in st.session_state:
        st.error("Link de recuperação inválido. Solicite um novo link.")
        st.session_state.pop("password_reset_link", None)
        return

    token = st.session_state.get("auth_token")
    if isinstance(token, str) and token:
        _render_authenticated(api, token)
    else:
        st.session_state.pop("auth_token", None)
        _render_auth_forms(api)


if __name__ == "__main__":
    main()
