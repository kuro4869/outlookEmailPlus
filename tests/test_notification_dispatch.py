from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from outlook_web.repositories import settings as settings_repo
from outlook_web.security.crypto import encrypt_data
from tests._import_app import clear_login_attempts, import_web_app_module


class NotificationDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = import_web_app_module()
        cls.app = cls.module.app

    def setUp(self):
        with self.app.app_context():
            clear_login_attempts()
            from outlook_web.db import get_db

            db = get_db()
            db.execute("DELETE FROM account_claim_logs")
            db.execute("DELETE FROM account_refresh_logs")
            db.execute("DELETE FROM account_tags")
            db.execute("DELETE FROM notification_cursor_states")
            db.execute("DELETE FROM notification_delivery_logs")
            db.execute("DELETE FROM telegram_push_log")
            db.execute("DELETE FROM temp_email_messages")
            db.execute("DELETE FROM temp_emails")
            db.execute("DELETE FROM accounts")
            db.commit()
            settings_repo.set_setting("email_notification_enabled", "false")
            settings_repo.set_setting("email_notification_recipient", "")
            settings_repo.set_setting("telegram_bot_token", "")
            settings_repo.set_setting("telegram_chat_id", "")

    def _login(self, client):
        resp = client.post("/login", json={"password": "testpass123"})
        self.assertEqual(resp.status_code, 200)

    def _insert_account(
        self,
        email_addr: str,
        *,
        provider: str = "imap",
        telegram_enabled: int = 1,
        telegram_cursor: str | None = "2026-03-01T00:00:00",
    ) -> int:
        conn = self.module.create_sqlite_connection()
        try:
            cur = conn.execute(
                """
                INSERT INTO accounts (
                    email, password, client_id, refresh_token, account_type, provider,
                    imap_host, imap_port, imap_password, group_id, remark, status,
                    telegram_push_enabled, telegram_last_checked_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    email_addr,
                    "",
                    "cid_test",
                    "rt_test",
                    "outlook" if provider == "outlook" else "imap",
                    provider,
                    "imap.test.com",
                    993,
                    "enc:dummy",
                    1,
                    "",
                    "active",
                    telegram_enabled,
                    telegram_cursor,
                ),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def _insert_temp_email(self, email_addr: str):
        conn = self.module.create_sqlite_connection()
        try:
            conn.execute("INSERT INTO temp_emails (email, status) VALUES (?, 'active')", (email_addr,))
            conn.commit()
        finally:
            conn.close()

    def test_email_test_endpoint_sends_real_message_via_saved_recipient(self):
        client = self.app.test_client()
        self._login(client)
        with self.app.app_context():
            settings_repo.set_setting("email_notification_recipient", "notify@example.com")

        with patch.dict(
            os.environ,
            {
                "EMAIL_NOTIFICATION_SMTP_HOST": "smtp.example.com",
                "EMAIL_NOTIFICATION_SMTP_PORT": "587",
                "EMAIL_NOTIFICATION_FROM": "noreply@example.com",
            },
            clear=False,
        ), patch("smtplib.SMTP") as smtp_mock:
            resp = client.post("/api/settings/email-test", json={})

        self.assertEqual(resp.status_code, 200)
        data = resp.get_json() or {}
        self.assertEqual(data.get("success"), True)
        smtp_mock.return_value.__enter__.return_value.send_message.assert_called_once()
        sent_message = smtp_mock.return_value.__enter__.return_value.send_message.call_args[0][0]
        self.assertEqual(sent_message["To"], "notify@example.com")

    def test_first_email_notification_scan_only_initializes_cursor(self):
        with self.app.app_context():
            from outlook_web.repositories import notification_state as notification_state_repo
            from outlook_web.services import notification_dispatch

            self._insert_account("first@example.com")
            settings_repo.set_setting("email_notification_enabled", "true")
            settings_repo.set_setting("email_notification_recipient", "notify@example.com")

            with patch.dict(
                os.environ,
                {
                    "EMAIL_NOTIFICATION_SMTP_HOST": "smtp.example.com",
                    "EMAIL_NOTIFICATION_SMTP_PORT": "587",
                    "EMAIL_NOTIFICATION_FROM": "noreply@example.com",
                },
                clear=False,
            ), patch("outlook_web.services.notification_dispatch.send_business_email_notification") as send_mock:
                notification_dispatch.run_email_notification_job(self.app)

            send_mock.assert_not_called()
            cursor = notification_state_repo.get_cursor(
                notification_dispatch.CHANNEL_EMAIL,
                notification_dispatch.SOURCE_ACCOUNT,
                notification_dispatch.build_source_key(notification_dispatch.SOURCE_ACCOUNT, "first@example.com"),
            )
            self.assertTrue(cursor)

    def test_email_notification_job_covers_account_and_temp_email_and_uses_delivery_logs(self):
        with self.app.app_context():
            from outlook_web.db import get_db
            from outlook_web.services import notification_dispatch

            self._insert_account("notify-account@example.com")
            self._insert_temp_email("notify-temp@example.com")
            notification_dispatch.bootstrap_channel_cursors(
                notification_dispatch.CHANNEL_EMAIL,
                cursor_value="2026-03-01T00:00:00",
            )
            settings_repo.set_setting("email_notification_enabled", "true")
            settings_repo.set_setting("email_notification_recipient", "notify@example.com")

            def fake_fetch(source, since):
                if source["source_type"] == notification_dispatch.SOURCE_ACCOUNT:
                    return [
                        {
                            "message_id": "<account-1@example.com>",
                            "subject": "Account Subject",
                            "sender": "sender@example.com",
                            "received_at": "2026-03-02T10:00:00",
                            "content": "account body",
                            "folder": "inbox",
                        }
                    ]
                return [
                    {
                        "message_id": "temp-1",
                        "subject": "Temp Subject",
                        "sender": "temp@example.com",
                        "received_at": "2026-03-02T11:00:00",
                        "content": "temp body",
                        "folder": "inbox",
                    }
                ]

            with patch.dict(
                os.environ,
                {
                    "EMAIL_NOTIFICATION_SMTP_HOST": "smtp.example.com",
                    "EMAIL_NOTIFICATION_SMTP_PORT": "587",
                    "EMAIL_NOTIFICATION_FROM": "noreply@example.com",
                },
                clear=False,
            ), patch("outlook_web.services.notification_dispatch.fetch_source_messages", side_effect=fake_fetch), patch(
                "outlook_web.services.notification_dispatch.send_business_email_notification"
            ) as send_mock:
                notification_dispatch.run_email_notification_job(self.app)

            self.assertEqual(send_mock.call_count, 2)
            db = get_db()
            rows = db.execute(
                "SELECT channel, source_type, source_key, status FROM notification_delivery_logs ORDER BY source_type ASC"
            ).fetchall()
            self.assertEqual(len(rows), 2)
            self.assertEqual({row["source_type"] for row in rows}, {"account", "temp_email"})
            self.assertTrue(all(row["status"] == "sent" for row in rows))

    def test_unified_notification_job_skips_account_when_notification_disabled(self):
        with self.app.app_context():
            from outlook_web.db import get_db
            from outlook_web.services import notification_dispatch

            self._insert_account("disabled@example.com", telegram_enabled=0)
            notification_dispatch.bootstrap_channel_cursors(
                notification_dispatch.CHANNEL_EMAIL,
                cursor_value="2026-03-01T00:00:00",
            )
            settings_repo.set_setting("email_notification_enabled", "true")
            settings_repo.set_setting("email_notification_recipient", "notify@example.com")

            with patch.dict(
                os.environ,
                {
                    "EMAIL_NOTIFICATION_SMTP_HOST": "smtp.example.com",
                    "EMAIL_NOTIFICATION_SMTP_PORT": "587",
                    "EMAIL_NOTIFICATION_FROM": "noreply@example.com",
                },
                clear=False,
            ), patch(
                "outlook_web.services.notification_dispatch.fetch_source_messages"
            ) as fetch_mock, patch(
                "outlook_web.services.notification_dispatch.send_business_email_notification"
            ) as send_mock:
                notification_dispatch.run_notification_dispatch_job(self.app)

            fetch_mock.assert_not_called()
            send_mock.assert_not_called()
            rows = get_db().execute(
                "SELECT 1 FROM notification_delivery_logs WHERE source_key = ?",
                (
                    notification_dispatch.build_source_key(
                        notification_dispatch.SOURCE_ACCOUNT, "disabled@example.com"
                    ),
                ),
            ).fetchall()
            self.assertEqual(rows, [])

    def test_missing_message_id_uses_stable_fallback_dedup(self):
        with self.app.app_context():
            from outlook_web.db import get_db
            from outlook_web.services import notification_dispatch

            self._insert_account("fallback@example.com")
            notification_dispatch.bootstrap_channel_cursors(
                notification_dispatch.CHANNEL_EMAIL,
                cursor_value="2026-03-01T00:00:00",
            )
            sources = notification_dispatch.list_email_notification_sources()
            messages = [
                {
                    "subject": "Fallback Subject",
                    "sender": "sender@example.com",
                    "received_at": "2026-03-02T10:00:00",
                    "content": "same body",
                    "folder": "inbox",
                }
            ]
            sent = []

            def fake_sender(source, message):
                sent.append((source["source_key"], message["subject"]))

            with patch("outlook_web.services.notification_dispatch.fetch_source_messages", return_value=messages):
                notification_dispatch.process_channel_for_sources(
                    channel=notification_dispatch.CHANNEL_EMAIL,
                    sources=sources,
                    sender=fake_sender,
                )
                notification_dispatch.process_channel_for_sources(
                    channel=notification_dispatch.CHANNEL_EMAIL,
                    sources=sources,
                    sender=fake_sender,
                )

            self.assertEqual(len(sent), 1)
            row = get_db().execute("SELECT message_id FROM notification_delivery_logs").fetchone()
            self.assertTrue((row["message_id"] or "").startswith("fallback:"))

    def test_email_failure_keeps_cursor_for_retry(self):
        with self.app.app_context():
            from outlook_web.repositories import notification_state as notification_state_repo
            from outlook_web.services import email_push, notification_dispatch

            self._insert_account("retry@example.com")
            notification_dispatch.bootstrap_channel_cursors(
                notification_dispatch.CHANNEL_EMAIL,
                cursor_value="2026-03-01T00:00:00",
            )
            sources = notification_dispatch.list_email_notification_sources()
            messages = [
                {
                    "message_id": "<retry@example.com>",
                    "subject": "Retry",
                    "sender": "sender@example.com",
                    "received_at": "2026-03-02T10:00:00",
                    "content": "body",
                    "folder": "inbox",
                }
            ]
            attempts = []

            def flaky_sender(source, message):
                attempts.append(message["message_id"])
                if len(attempts) == 1:
                    raise email_push.EmailPushError(
                        "EMAIL_TEST_SEND_FAILED",
                        "测试邮件发送失败",
                        message_en="Failed to send test email",
                    )

            with patch("outlook_web.services.notification_dispatch.fetch_source_messages", return_value=messages):
                notification_dispatch.process_channel_for_sources(
                    channel=notification_dispatch.CHANNEL_EMAIL,
                    sources=sources,
                    sender=flaky_sender,
                )

            cursor = notification_state_repo.get_cursor(
                notification_dispatch.CHANNEL_EMAIL,
                notification_dispatch.SOURCE_ACCOUNT,
                notification_dispatch.build_source_key(notification_dispatch.SOURCE_ACCOUNT, "retry@example.com"),
            )
            self.assertEqual(cursor, "2026-03-01T00:00:00")

            with patch("outlook_web.services.notification_dispatch.fetch_source_messages", return_value=messages):
                notification_dispatch.process_channel_for_sources(
                    channel=notification_dispatch.CHANNEL_EMAIL,
                    sources=sources,
                    sender=flaky_sender,
                )

            self.assertEqual(len(attempts), 2)
            cursor = notification_state_repo.get_cursor(
                notification_dispatch.CHANNEL_EMAIL,
                notification_dispatch.SOURCE_ACCOUNT,
                notification_dispatch.build_source_key(notification_dispatch.SOURCE_ACCOUNT, "retry@example.com"),
            )
            self.assertEqual(cursor, "2026-03-02T10:00:00")

    def test_unified_notification_job_fetches_source_once_for_dual_channels(self):
        with self.app.app_context():
            from outlook_web.db import get_db
            from outlook_web.services import notification_dispatch

            self._insert_account(
                "shared-fetch@example.com",
                telegram_enabled=1,
                telegram_cursor="2026-03-01T00:00:00",
            )
            notification_dispatch.bootstrap_channel_cursors(
                notification_dispatch.CHANNEL_EMAIL,
                cursor_value="2026-03-01T00:00:00",
            )
            settings_repo.set_setting("email_notification_enabled", "true")
            settings_repo.set_setting("email_notification_recipient", "notify@example.com")
            settings_repo.set_setting("telegram_bot_token", encrypt_data("bot_token"))
            settings_repo.set_setting("telegram_chat_id", "123456")
            message = [
                {
                    "message_id": "<shared-fetch@example.com>",
                    "subject": "Shared fetch",
                    "sender": "sender@example.com",
                    "received_at": "2026-03-02T10:00:00",
                    "content": "body",
                    "preview": "body",
                    "folder": "inbox",
                }
            ]

            with patch.dict(
                os.environ,
                {
                    "EMAIL_NOTIFICATION_SMTP_HOST": "smtp.example.com",
                    "EMAIL_NOTIFICATION_SMTP_PORT": "587",
                    "EMAIL_NOTIFICATION_FROM": "noreply@example.com",
                },
                clear=False,
            ), patch(
                "outlook_web.services.notification_dispatch.fetch_source_messages",
                return_value=message,
            ) as fetch_mock, patch(
                "outlook_web.services.notification_dispatch.send_business_email_notification"
            ) as email_send, patch(
                "outlook_web.services.notification_dispatch.send_business_telegram_notification"
            ) as telegram_send:
                notification_dispatch.run_notification_dispatch_job(self.app)

            fetch_mock.assert_called_once()
            email_send.assert_called_once()
            telegram_send.assert_called_once()
            rows = get_db().execute(
                """
                SELECT channel, status
                FROM notification_delivery_logs
                WHERE source_key = ?
                ORDER BY channel ASC
                """,
                (notification_dispatch.build_source_key(notification_dispatch.SOURCE_ACCOUNT, "shared-fetch@example.com"),),
            ).fetchall()
            self.assertEqual([(row["channel"], row["status"]) for row in rows], [("email", "sent"), ("telegram", "sent")])

    def test_unified_notification_job_fetches_per_cursor_group_when_channels_diverge(self):
        with self.app.app_context():
            from outlook_web.services import notification_dispatch

            self._insert_account(
                "diverged-fetch@example.com",
                telegram_enabled=1,
                telegram_cursor="2026-03-10T00:00:00",
            )
            notification_dispatch.bootstrap_channel_cursors(
                notification_dispatch.CHANNEL_EMAIL,
                cursor_value="2026-03-01T00:00:00",
            )
            notification_dispatch.bootstrap_channel_cursors(
                notification_dispatch.CHANNEL_TELEGRAM,
                cursor_value="2026-03-10T00:00:00",
            )
            settings_repo.set_setting("email_notification_enabled", "true")
            settings_repo.set_setting("email_notification_recipient", "notify@example.com")
            settings_repo.set_setting("telegram_bot_token", encrypt_data("bot_token"))
            settings_repo.set_setting("telegram_chat_id", "123456")

            def fake_fetch(source, since):
                if since == "2026-03-01T00:00:00":
                    return [
                        {
                            "message_id": "<old-backlog@example.com>",
                            "subject": "Old backlog",
                            "sender": "sender@example.com",
                            "received_at": "2026-03-02T10:00:00",
                            "content": "old body",
                            "preview": "old body",
                            "folder": "inbox",
                        }
                    ]
                return [
                    {
                        "message_id": "<fresh-message@example.com>",
                        "subject": "Fresh",
                        "sender": "sender@example.com",
                        "received_at": "2026-03-11T10:00:00",
                        "content": "fresh body",
                        "preview": "fresh body",
                        "folder": "inbox",
                    }
                ]

            with patch.dict(
                os.environ,
                {
                    "EMAIL_NOTIFICATION_SMTP_HOST": "smtp.example.com",
                    "EMAIL_NOTIFICATION_SMTP_PORT": "587",
                    "EMAIL_NOTIFICATION_FROM": "noreply@example.com",
                },
                clear=False,
            ), patch(
                "outlook_web.services.notification_dispatch.fetch_source_messages",
                side_effect=fake_fetch,
            ) as fetch_mock, patch(
                "outlook_web.services.notification_dispatch.send_business_email_notification"
            ) as email_send, patch(
                "outlook_web.services.notification_dispatch.send_business_telegram_notification"
            ) as telegram_send:
                notification_dispatch.run_notification_dispatch_job(self.app)

            called_cursors = [call.args[1] for call in fetch_mock.call_args_list]
            self.assertEqual(called_cursors, ["2026-03-01T00:00:00", "2026-03-10T00:00:00"])
            self.assertEqual(email_send.call_args[0][1]["message_id"], "<old-backlog@example.com>")
            self.assertEqual(telegram_send.call_args[0][1]["message_id"], "<fresh-message@example.com>")

    def test_temp_email_html_body_is_converted_for_notification(self):
        with self.app.app_context():
            from outlook_web.db import get_db
            from outlook_web.services import notification_dispatch

            self._insert_temp_email("html-temp@example.com")
            notification_dispatch.bootstrap_channel_cursors(
                notification_dispatch.CHANNEL_EMAIL,
                cursor_value="2026-03-01T00:00:00",
            )
            settings_repo.set_setting("email_notification_enabled", "true")
            settings_repo.set_setting("email_notification_recipient", "notify@example.com")
            get_db().execute(
                """
                INSERT INTO temp_email_messages (
                    message_id, email_address, from_address, subject, content, html_content, has_html, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "html-only-message",
                    "html-temp@example.com",
                    "sender@example.com",
                    "HTML only",
                    "",
                    "<div>Hello <strong>HTML</strong> world</div>",
                    1,
                    1772407200,
                ),
            )
            get_db().commit()

            with patch.dict(
                os.environ,
                {
                    "EMAIL_NOTIFICATION_SMTP_HOST": "smtp.example.com",
                    "EMAIL_NOTIFICATION_SMTP_PORT": "587",
                    "EMAIL_NOTIFICATION_FROM": "noreply@example.com",
                },
                clear=False,
            ), patch(
                "outlook_web.services.notification_dispatch.gptmail.get_temp_emails_from_api",
                return_value=None,
            ), patch(
                "outlook_web.services.notification_dispatch.send_business_email_notification"
            ) as send_mock:
                notification_dispatch.run_email_notification_job(self.app)

            send_mock.assert_called_once()
            sent_message = send_mock.call_args[0][1]
            self.assertEqual(sent_message["content"], "Hello HTML world")
            self.assertEqual(sent_message["preview"], "Hello HTML world")

    def test_claim_delivery_attempt_is_atomic_for_same_message(self):
        with self.app.app_context():
            from outlook_web.repositories import notification_state as notification_state_repo

            result1 = notification_state_repo.claim_delivery_attempt(
                "email",
                "account",
                "account:atomic@example.com",
                "msg-atomic",
            )
            result2 = notification_state_repo.claim_delivery_attempt(
                "email",
                "account",
                "account:atomic@example.com",
                "msg-atomic",
            )
            notification_state_repo.complete_delivery_attempt(
                "email",
                "account",
                "account:atomic@example.com",
                "msg-atomic",
                status="sent",
            )
            result3 = notification_state_repo.claim_delivery_attempt(
                "email",
                "account",
                "account:atomic@example.com",
                "msg-atomic",
            )

            self.assertEqual(result1, "acquired")
            self.assertEqual(result2, "processing")
            self.assertEqual(result3, "sent")

    def test_upsert_cursor_is_monotonic(self):
        with self.app.app_context():
            from outlook_web.repositories import notification_state as notification_state_repo

            notification_state_repo.reset_channel_cursor(
                "email",
                "account",
                "account:cursor@example.com",
                "2026-03-10T10:00:00",
            )
            notification_state_repo.upsert_cursor(
                "email",
                "account",
                "account:cursor@example.com",
                "2026-03-12T10:00:00",
            )
            notification_state_repo.upsert_cursor(
                "email",
                "account",
                "account:cursor@example.com",
                "2026-03-11T10:00:00",
            )

            cursor = notification_state_repo.get_cursor("email", "account", "account:cursor@example.com")
            self.assertEqual(cursor, "2026-03-12T10:00:00")

    def test_inbox_to_junkemail_move_does_not_repeat_same_channel(self):
        with self.app.app_context():
            from outlook_web.services import notification_dispatch

            self._insert_account("folder-move@example.com")
            notification_dispatch.bootstrap_channel_cursors(
                notification_dispatch.CHANNEL_EMAIL,
                cursor_value="2026-03-01T00:00:00",
            )
            sources = notification_dispatch.list_email_notification_sources()
            sent = []

            def fake_sender(source, message):
                sent.append(message["folder"])

            with patch(
                "outlook_web.services.notification_dispatch.fetch_source_messages",
                side_effect=[
                    [
                        {
                            "message_id": "<same-message@example.com>",
                            "subject": "Move",
                            "sender": "sender@example.com",
                            "received_at": "2026-03-02T10:00:00",
                            "content": "body",
                            "folder": "inbox",
                        }
                    ],
                    [
                        {
                            "message_id": "<same-message@example.com>",
                            "subject": "Move",
                            "sender": "sender@example.com",
                            "received_at": "2026-03-02T10:01:00",
                            "content": "body",
                            "folder": "junkemail",
                        }
                    ],
                ],
            ):
                notification_dispatch.process_channel_for_sources(
                    channel=notification_dispatch.CHANNEL_EMAIL,
                    sources=sources,
                    sender=fake_sender,
                )
                notification_dispatch.process_channel_for_sources(
                    channel=notification_dispatch.CHANNEL_EMAIL,
                    sources=sources,
                    sender=fake_sender,
                )

            self.assertEqual(sent, ["inbox"])

    def test_email_failure_does_not_block_telegram_delivery(self):
        with self.app.app_context():
            from outlook_web.db import get_db
            from outlook_web.services import email_push, notification_dispatch

            account_id = self._insert_account(
                "dual-channel@example.com",
                telegram_enabled=1,
                telegram_cursor="2026-03-01T00:00:00",
            )
            notification_dispatch.bootstrap_channel_cursors(
                notification_dispatch.CHANNEL_EMAIL,
                cursor_value="2026-03-01T00:00:00",
            )
            notification_dispatch.bootstrap_channel_cursors(
                notification_dispatch.CHANNEL_TELEGRAM,
                cursor_value="2026-03-01T00:00:00",
            )
            settings_repo.set_setting("email_notification_enabled", "true")
            settings_repo.set_setting("email_notification_recipient", "notify@example.com")
            settings_repo.set_setting("telegram_bot_token", encrypt_data("bot_token"))
            settings_repo.set_setting("telegram_chat_id", "123456")

            message = [
                {
                    "message_id": "<dual-message@example.com>",
                    "subject": "Dual",
                    "sender": "sender@example.com",
                    "received_at": "2026-03-02T10:00:00",
                    "content": "body",
                    "preview": "body",
                    "folder": "inbox",
                }
            ]

            with patch(
                "outlook_web.services.notification_dispatch.fetch_source_messages",
                return_value=message,
            ), patch.dict(
                os.environ,
                {
                    "EMAIL_NOTIFICATION_SMTP_HOST": "smtp.example.com",
                    "EMAIL_NOTIFICATION_SMTP_PORT": "587",
                    "EMAIL_NOTIFICATION_FROM": "noreply@example.com",
                },
                clear=False,
            ), patch(
                "outlook_web.services.notification_dispatch.send_business_email_notification",
                side_effect=email_push.EmailPushError(
                    "EMAIL_TEST_SEND_FAILED",
                    "测试邮件发送失败",
                    message_en="Failed to send test email",
                ),
            ), patch(
                "outlook_web.services.notification_dispatch.send_business_telegram_notification"
            ) as telegram_send:
                notification_dispatch.run_notification_dispatch_job(self.app)

            telegram_send.assert_called_once()
            rows = get_db().execute(
                """
                SELECT channel, status
                FROM notification_delivery_logs
                WHERE source_key = ?
                ORDER BY channel ASC
                """,
                (notification_dispatch.build_source_key(notification_dispatch.SOURCE_ACCOUNT, "dual-channel@example.com"),),
            ).fetchall()
            self.assertEqual([(row["channel"], row["status"]) for row in rows], [("email", "failed"), ("telegram", "sent")])
            legacy_row = get_db().execute(
                "SELECT 1 FROM telegram_push_log WHERE account_id = ? AND message_id = ?",
                (account_id, "<dual-message@example.com>"),
            ).fetchone()
            self.assertIsNotNone(legacy_row)
