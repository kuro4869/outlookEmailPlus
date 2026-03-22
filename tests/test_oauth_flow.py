from __future__ import annotations

import unittest
import urllib.parse
from unittest.mock import Mock, patch

from outlook_web.db import get_db
from tests._import_app import clear_login_attempts, import_web_app_module


class OAuthFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = import_web_app_module()
        cls.app = cls.module.app

    def setUp(self):
        with self.app.app_context():
            clear_login_attempts()
            db = get_db()
            db.execute("DELETE FROM export_verify_tokens")
            db.commit()

    def _login(self, client):
        resp = client.post("/login", json={"password": "testpass123"})
        self.assertEqual(resp.status_code, 200)

    def _issue_verify_token(self, client, headers=None) -> str:
        resp = client.post("/api/export/verify", json={"password": "testpass123"}, headers=headers or {})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("success"), True)
        self.assertTrue(data.get("verify_token"))
        return data["verify_token"]

    def _issue_oauth_state(self, client) -> str:
        resp = client.get("/api/oauth/auth-url")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        parsed = urllib.parse.urlparse(data["auth_url"])
        query = urllib.parse.parse_qs(parsed.query)
        return query["state"][0]

    def test_oauth_auth_url_endpoint_uses_callback_redirect_uri(self):
        client = self.app.test_client()
        self._login(client)

        resp = client.get("/api/oauth/auth-url")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertEqual(data.get("success"), True)
        self.assertIn("auth_url", data)
        self.assertTrue(data.get("redirect_uri", "").endswith("/oauth/callback"))
        self.assertIn("redirect_uri=", data.get("auth_url", ""))
        self.assertIn("login.microsoftonline.com", data.get("auth_url", ""))
        parsed = urllib.parse.urlparse(data.get("auth_url", ""))
        query = urllib.parse.parse_qs(parsed.query)
        self.assertTrue(query.get("state", [""])[0])
        self.assertNotEqual(query.get("state", [""])[0], "12345")

    @patch("outlook_web.controllers.oauth.config.get_oauth_redirect_uri", return_value="https://prod.example.com/oauth/callback")
    @patch("outlook_web.controllers.oauth.config.get_oauth_client_id", return_value="client-from-config")
    def test_oauth_auth_url_returns_redirect_warning_when_origin_differs(self, _mock_client_id, _mock_redirect_uri):
        client = self.app.test_client()
        self._login(client)

        resp = client.get("/api/oauth/auth-url")

        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("redirect_uri"), "https://prod.example.com/oauth/callback")
        self.assertIn("redirect_uri", data.get("redirect_uri_warning", ""))
        self.assertIn("prod.example.com", data.get("redirect_uri_warning", ""))
        self.assertIn("localhost", data.get("redirect_uri_warning", ""))

    def test_oauth_callback_page_posts_message_to_opener(self):
        client = self.app.test_client()

        resp = client.get("/oauth/callback?code=test-code")
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode("utf-8")

        self.assertIn("window.opener.postMessage", body)
        self.assertIn("outlook-oauth-callback", body)
        self.assertIn("outlook-oauth-callback-ack", body)
        self.assertIn("callbackAcked", body)
        self.assertIn("自动回传未确认", body)
        self.assertIn("callbackUrl", body)

    def test_exchange_token_requires_verify_token(self):
        client = self.app.test_client()
        self._login(client)
        oauth_state = self._issue_oauth_state(client)

        resp = client.post(
            "/api/oauth/exchange-token",
            json={"redirected_url": f"http://localhost/oauth/callback?code=test-code&state={oauth_state}"},
        )
        self.assertEqual(resp.status_code, 401)
        data = resp.get_json()

        self.assertEqual(data.get("success"), False)
        self.assertEqual(data.get("code"), "OAUTH_VERIFY_TOKEN_REQUIRED")
        self.assertEqual(data.get("need_verify"), True)
        self.assertIn("verify_token", data.get("message", ""))

    @patch("outlook_web.controllers.oauth.requests.post")
    @patch("outlook_web.controllers.oauth.config.get_oauth_client_id", return_value="client-from-config")
    def test_exchange_token_succeeds_with_verify_token(self, _mock_client_id, mock_post):
        client = self.app.test_client()
        self._login(client)
        headers = {"User-Agent": "oauth-flow-test"}
        verify_token = self._issue_verify_token(client, headers=headers)
        oauth_state = self._issue_oauth_state(client)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "refresh_token": "refresh-token-value",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "offline_access User.Read",
        }
        mock_post.return_value = mock_response

        resp = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": f"http://localhost/oauth/callback?code=test-code&state={oauth_state}",
                "verify_token": verify_token,
            },
            headers=headers,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertEqual(data.get("success"), True)
        self.assertEqual(data.get("client_id"), "client-from-config")
        self.assertEqual(data.get("refresh_token"), "refresh-token-value")
        self.assertEqual(data.get("token_type"), "Bearer")

    @patch("outlook_web.controllers.oauth.requests.post")
    @patch("outlook_web.controllers.oauth.config.get_oauth_client_id", return_value="client-from-config")
    def test_exchange_token_accepts_query_string_only_input(self, _mock_client_id, mock_post):
        client = self.app.test_client()
        self._login(client)
        headers = {"User-Agent": "oauth-flow-test"}
        verify_token = self._issue_verify_token(client, headers=headers)
        oauth_state = self._issue_oauth_state(client)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "refresh_token": "refresh-token-query-only",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "offline_access User.Read",
        }
        mock_post.return_value = mock_response

        resp = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": f"?code=test-code&state={oauth_state}",
                "verify_token": verify_token,
            },
            headers=headers,
        )

        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("refresh_token"), "refresh-token-query-only")

    @patch("outlook_web.controllers.oauth.requests.post")
    def test_exchange_token_rejects_bound_verify_token_before_redeeming_code(self, mock_post):
        client = self.app.test_client()
        self._login(client)
        verify_token = self._issue_verify_token(client, headers={"User-Agent": "ua-a"})
        oauth_state = self._issue_oauth_state(client)

        resp = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": f"http://localhost/oauth/callback?code=test-code&state={oauth_state}",
                "verify_token": verify_token,
            },
            headers={"User-Agent": "ua-b"},
        )
        self.assertEqual(resp.status_code, 401)
        data = resp.get_json()

        self.assertEqual(data.get("code"), "EXPORT_VERIFY_CLIENT_MISMATCH")
        mock_post.assert_not_called()

    @patch("outlook_web.controllers.oauth.requests.post")
    @patch("outlook_web.controllers.oauth.config.get_oauth_client_id", return_value="client-from-config")
    def test_exchange_token_bound_failure_does_not_consume_verify_token_or_state(self, _mock_client_id, mock_post):
        client = self.app.test_client()
        self._login(client)
        verify_token = self._issue_verify_token(client, headers={"User-Agent": "ua-a"})
        oauth_state = self._issue_oauth_state(client)

        rejected = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": f"http://localhost/oauth/callback?code=test-code&state={oauth_state}",
                "verify_token": verify_token,
            },
            headers={"User-Agent": "ua-b"},
        )
        self.assertEqual(rejected.status_code, 401)
        self.assertEqual(rejected.get_json().get("code"), "EXPORT_VERIFY_CLIENT_MISMATCH")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "refresh_token": "refresh-token-retry",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "offline_access User.Read",
        }
        mock_post.return_value = mock_response

        retried = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": f"http://localhost/oauth/callback?code=test-code&state={oauth_state}",
                "verify_token": verify_token,
            },
            headers={"User-Agent": "ua-a"},
        )
        self.assertEqual(retried.status_code, 200)
        self.assertTrue(retried.get_json().get("success"))
        self.assertEqual(retried.get_json().get("refresh_token"), "refresh-token-retry")

    @patch("outlook_web.controllers.oauth.config.get_oauth_client_id", return_value="client-from-config")
    def test_exchange_token_rejects_redirect_uri_mismatch(self, _mock_client_id):
        client = self.app.test_client()
        self._login(client)
        headers = {"User-Agent": "oauth-flow-test"}
        verify_token = self._issue_verify_token(client, headers=headers)
        oauth_state = self._issue_oauth_state(client)

        resp = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": f"https://example.com/oauth/callback?code=test-code&state={oauth_state}",
                "verify_token": verify_token,
            },
            headers=headers,
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()

        self.assertEqual(data.get("code"), "OAUTH_REDIRECT_URI_MISMATCH")
        self.assertIn("/oauth/callback", data.get("message", ""))

    @patch("outlook_web.controllers.oauth.requests.post")
    def test_exchange_token_distinguishes_invalid_code(self, mock_post):
        client = self.app.test_client()
        self._login(client)
        headers = {"User-Agent": "oauth-flow-test"}
        verify_token = self._issue_verify_token(client, headers=headers)
        oauth_state = self._issue_oauth_state(client)

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "AADSTS70000: The provided value for the input parameter 'code' is not valid.",
        }
        mock_post.return_value = mock_response

        resp = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": f"http://localhost/oauth/callback?code=bad-code&state={oauth_state}",
                "verify_token": verify_token,
            },
            headers=headers,
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data.get("code"), "OAUTH_CODE_INVALID")

    @patch("outlook_web.controllers.oauth.requests.post")
    def test_exchange_token_distinguishes_invalid_client_configuration(self, mock_post):
        client = self.app.test_client()
        self._login(client)
        headers = {"User-Agent": "oauth-flow-test"}
        verify_token = self._issue_verify_token(client, headers=headers)
        oauth_state = self._issue_oauth_state(client)

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "error": "invalid_client",
            "error_description": "AADSTS700016: Application with identifier 'bad-client-id' was not found.",
        }
        mock_post.return_value = mock_response

        resp = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": f"http://localhost/oauth/callback?code=bad-code&state={oauth_state}",
                "verify_token": verify_token,
            },
            headers=headers,
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data.get("code"), "OAUTH_CONFIG_INVALID")

    def test_exchange_token_distinguishes_microsoft_authorization_failure(self):
        client = self.app.test_client()
        self._login(client)
        headers = {"User-Agent": "oauth-flow-test"}
        verify_token = self._issue_verify_token(client, headers=headers)
        oauth_state = self._issue_oauth_state(client)

        resp = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": (
                    "http://localhost/oauth/callback?error=access_denied"
                    f"&state={oauth_state}"
                    "&error_description=The+user+cancelled+the+authorization"
                ),
                "verify_token": verify_token,
            },
            headers=headers,
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()

        self.assertEqual(data.get("code"), "OAUTH_MICROSOFT_AUTH_FAILED")
        self.assertIn("微软授权失败", data.get("message", ""))

    def test_exchange_token_rejects_mismatched_oauth_state(self):
        client = self.app.test_client()
        self._login(client)
        headers = {"User-Agent": "oauth-flow-test"}
        verify_token = self._issue_verify_token(client, headers=headers)
        self._issue_oauth_state(client)

        resp = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": "http://localhost/oauth/callback?code=test-code&state=wrong-state",
                "verify_token": verify_token,
            },
            headers=headers,
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data.get("code"), "OAUTH_STATE_INVALID")

    @patch("outlook_web.controllers.oauth.requests.post")
    @patch("outlook_web.controllers.oauth.config.get_oauth_client_id", return_value="client-from-config")
    def test_exchange_token_accepts_earlier_pending_state_in_same_session(self, _mock_client_id, mock_post):
        client = self.app.test_client()
        self._login(client)
        headers = {"User-Agent": "oauth-flow-test"}
        verify_token = self._issue_verify_token(client, headers=headers)
        first_state = self._issue_oauth_state(client)
        second_state = self._issue_oauth_state(client)
        self.assertNotEqual(first_state, second_state)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "refresh_token": "refresh-token-value",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "offline_access User.Read",
        }
        mock_post.return_value = mock_response

        resp = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": f"http://localhost/oauth/callback?code=test-code&state={first_state}",
                "verify_token": verify_token,
            },
            headers=headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json().get("success"))

    @patch("outlook_web.controllers.oauth.requests.post")
    def test_exchange_token_rejects_replayed_consumed_oauth_state(self, mock_post):
        client = self.app.test_client()
        self._login(client)
        headers = {"User-Agent": "oauth-flow-test"}
        first_verify_token = self._issue_verify_token(client, headers=headers)
        oauth_state = self._issue_oauth_state(client)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "refresh_token": "refresh-token-value",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "offline_access User.Read",
        }
        mock_post.return_value = mock_response

        first_resp = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": f"http://localhost/oauth/callback?code=test-code&state={oauth_state}",
                "verify_token": first_verify_token,
            },
            headers=headers,
        )
        self.assertEqual(first_resp.status_code, 200)

        second_verify_token = self._issue_verify_token(client, headers=headers)
        replay_resp = client.post(
            "/api/oauth/exchange-token",
            json={
                "redirected_url": f"http://localhost/oauth/callback?code=another-code&state={oauth_state}",
                "verify_token": second_verify_token,
            },
            headers=headers,
        )
        self.assertEqual(replay_resp.status_code, 400)
        self.assertEqual(replay_resp.get_json().get("code"), "OAUTH_STATE_INVALID")
