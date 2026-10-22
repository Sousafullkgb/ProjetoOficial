from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest


API_URL = "https://example.xano.io/api:ZnpRG7wg"
APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def response(status_code: int, payload: dict[str, object]) -> Mock:
    result = Mock()
    result.status_code = status_code
    result.ok = 200 <= status_code < 300
    result.json.return_value = payload
    return result


class AuthenticationAppTests(unittest.TestCase):
    def run_app(self, app: AppTest) -> AppTest:
        with patch.dict(os.environ, {"XANO_API_BASE_URL": API_URL}):
            return app.run()

    def test_authentication_forms_are_available(self) -> None:
        app = self.run_app(AppTest.from_file(str(APP_PATH)))

        self.assertEqual(
            [tab.label for tab in app.tabs],
            ["Entrar", "Criar conta", "Recuperar senha"],
        )
        self.assertEqual(app.exception, [])

    @patch("requests.Session.request")
    def test_invalid_email_is_rejected_before_api_call(self, request: Mock) -> None:
        app = self.run_app(AppTest.from_file(str(APP_PATH)))
        app.text_input[0].set_value("not-an-email")
        app.text_input[1].set_value("Password1")
        self.run_app(app.button[0].click())

        request.assert_not_called()
        self.assertIn("Informe um e-mail válido.", [error.value for error in app.error])

    @patch("requests.Session.request")
    def test_signup_validates_password_and_opens_session(
        self, request: Mock
    ) -> None:
        request.side_effect = [
            response(200, {"authToken": "session-token", "user_id": 7}),
            response(200, {"id": 7, "name": "Jogador", "email": "user@example.com"}),
        ]
        app = self.run_app(AppTest.from_file(str(APP_PATH)))
        app.text_input[2].set_value("Jogador")
        app.text_input[3].set_value("USER@example.com")
        app.text_input[4].set_value("Password1")
        app.text_input[5].set_value("Password1")
        self.run_app(app.button[1].click())

        self.assertEqual(app.exception, [])
        self.assertIn("Bem-vindo, Jogador!", [message.value for message in app.success])
        self.assertEqual(
            request.call_args_list[0].args[1],
            f"{API_URL}/auth/signup",
        )

    @patch("requests.Session.request")
    def test_password_recovery_confirmation_is_generic(self, request: Mock) -> None:
        request.return_value = response(
            200, {"message": "If an account exists, a reset link has been sent."}
        )
        app = self.run_app(AppTest.from_file(str(APP_PATH)))
        app.text_input[6].set_value("user@example.com")
        self.run_app(app.button[2].click())

        self.assertEqual(app.exception, [])
        self.assertIn(
            "Se houver uma conta associada a esse e-mail, você receberá um link de recuperação.",
            [message.value for message in app.success],
        )

    @patch("requests.Session.request")
    def test_reset_link_is_removed_from_url_and_completes_reset(
        self, request: Mock
    ) -> None:
        request.return_value = response(200, {"message": "Password updated."})
        app = AppTest.from_file(str(APP_PATH))
        app.query_params["magic_token"] = "one-time-token"
        app.query_params["email"] = "user@example.com"
        self.run_app(app)

        self.assertEqual(dict(app.query_params), {})
        self.assertEqual([field.label for field in app.text_input], [
            "Nova senha",
            "Confirme a nova senha",
        ])
        app.text_input[0].set_value("Password1")
        app.text_input[1].set_value("Password1")
        self.run_app(app.button[0].click())

        self.assertEqual(app.exception, [])
        self.assertIn("Senha atualizada. Entre com sua nova senha.", [
            message.value for message in app.success
        ])
        self.assertEqual(request.call_args.kwargs["json"]["magic_token"], "one-time-token")

    @patch("requests.Session.request")
    def test_login_validates_session_and_shows_authenticated_view(
        self, request: Mock
    ) -> None:
        request.side_effect = [
            response(200, {"authToken": "session-token", "user_id": 7}),
            response(200, {"id": 7, "name": "Jogador", "email": "user@example.com"}),
        ]
        app = self.run_app(AppTest.from_file(str(APP_PATH)))
        app.text_input[0].set_value("user@example.com")
        app.text_input[1].set_value("Password1")
        self.run_app(app.button[0].click())

        self.assertEqual(app.exception, [])
        self.assertIn("Bem-vindo, Jogador!", [message.value for message in app.success])
        self.assertTrue(any(button.label == "Sair" for button in app.button))

    @patch("requests.Session.request")
    def test_expired_session_is_cleared_and_login_is_shown(
        self, request: Mock
    ) -> None:
        request.return_value = response(401, {"error": "expired"})
        app = AppTest.from_file(str(APP_PATH))
        app.session_state["auth_token"] = "expired-token"
        self.run_app(app)

        self.assertNotIn("auth_token", app.session_state)
        self.assertIn("Sua sessão expirou. Entre novamente.", [
            warning.value for warning in app.warning
        ])
        self.assertEqual([tab.label for tab in app.tabs], [
            "Entrar",
            "Criar conta",
            "Recuperar senha",
        ])

    @patch("requests.Session.request")
    def test_logout_removes_local_token(self, request: Mock) -> None:
        request.return_value = response(
            200, {"id": 7, "name": "Jogador", "email": "user@example.com"}
        )
        app = AppTest.from_file(str(APP_PATH))
        app.session_state["auth_token"] = "session-token"
        self.run_app(app)
        self.run_app(app.button[0].click())

        self.assertNotIn("auth_token", app.session_state)
        self.assertEqual(app.exception, [])


if __name__ == "__main__":
    unittest.main()
