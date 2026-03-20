import unittest
from unittest.mock import MagicMock, patch

from tests._import_app import clear_login_attempts, import_web_app_module


class SettingsSchedulerReloadTests(unittest.TestCase):
    """
    对齐：PRD-00007 / FD-00007 / TDD-00007 / PRD-00008 / Resolve 文档
    目标：
    - 更新 settings 触发调度器重载时，必须把真实 Flask app 实例传给 scheduler jobs。
    - 调度器应恢复为统一通知分发 Job（而非只挂 Telegram Job）。
    - 邮件通知设置变更应触发 scheduler reload。
    """

    @classmethod
    def setUpClass(cls):
        cls.module = import_web_app_module()
        cls.app = cls.module.app

    def setUp(self):
        with self.app.app_context():
            clear_login_attempts()

    def _login(self, client, password: str = "testpass123"):
        resp = client.post("/login", json={"password": password})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("success"), True)

    def test_update_settings_reload_scheduler_passes_real_app_object(self):
        client = self.app.test_client()
        self._login(client)

        fake_scheduler = MagicMock(name="scheduler")

        with (
            patch(
                "outlook_web.services.scheduler.get_scheduler_instance",
                return_value=fake_scheduler,
            ),
            patch(
                "outlook_web.services.scheduler.configure_scheduler_jobs"
            ) as configure_jobs,
        ):
            resp = client.put("/api/settings", json={"telegram_poll_interval": 60})

        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json() or {}
        self.assertEqual(payload.get("success"), True)
        self.assertEqual(payload.get("scheduler_reloaded"), True)

        self.assertTrue(
            configure_jobs.called,
            "预期触发调度器重载，但 configure_scheduler_jobs 未被调用",
        )
        args, kwargs = configure_jobs.call_args
        self.assertEqual(
            kwargs, {}, "此处调用应使用位置参数，避免未来签名变化导致静默错配"
        )
        self.assertIs(args[0], fake_scheduler)
        self.assertIs(args[1], self.app)

    def test_configure_scheduler_jobs_uses_unified_notification_dispatch_job(self):
        """PRD-00008 / Resolve 文档：调度器应调用统一通知分发 Job 而非单独的 Telegram Job。"""
        fake_scheduler = MagicMock(name="scheduler")

        with (
            patch(
                "outlook_web.services.scheduler._configure_telegram_push_job"
            ) as configure_telegram,
            patch(
                "outlook_web.services.scheduler._configure_email_notification_job"
            ) as configure_email,
            patch("outlook_web.services.scheduler._configure_probe_poll_job"),
            patch("outlook_web.services.scheduler._configure_pool_maintenance_jobs"),
        ):
            from outlook_web.services import scheduler as scheduler_service

            scheduler_service.configure_scheduler_jobs(
                fake_scheduler, self.app, lambda *_args, **_kwargs: None
            )

        # 正确语义：应调用统一通知分发 Job，不应调用单独的 Telegram Job
        configure_email.assert_called_once_with(fake_scheduler, self.app)
        configure_telegram.assert_not_called()

    def test_email_notification_settings_trigger_scheduler_reload(self):
        """PRD-00008 / Resolve 文档：邮件通知设置变更应触发调度器重载。"""
        client = self.app.test_client()
        self._login(client)

        fake_scheduler = MagicMock(name="scheduler")

        with (
            patch(
                "outlook_web.services.scheduler.get_scheduler_instance",
                return_value=fake_scheduler,
            ),
            patch(
                "outlook_web.services.scheduler.configure_scheduler_jobs"
            ) as configure_jobs,
        ):
            # 更新邮件通知开关
            resp = client.put(
                "/api/settings", json={"email_notification_enabled": False}
            )

        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json() or {}
        self.assertEqual(payload.get("success"), True)
        self.assertEqual(payload.get("scheduler_reloaded"), True)
        self.assertTrue(configure_jobs.called, "邮件通知设置变更应触发调度器重载")
