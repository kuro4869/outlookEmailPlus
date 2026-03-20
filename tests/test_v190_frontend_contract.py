from __future__ import annotations

import unittest

from tests._import_app import import_web_app_module


class V190FrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = import_web_app_module()
        cls.app = cls.module.app

    def _login(self, client):
        resp = client.post("/login", json={"password": "testpass123"})
        self.assertEqual(resp.status_code, 200)

    def _get_text(self, client, path):
        resp = client.get(path)
        try:
            return resp.data.decode("utf-8")
        finally:
            resp.close()

    def test_i18n_runtime_exposes_date_and_error_helpers(self):
        client = self.app.test_client()
        js = self._get_text(client, "/static/js/i18n.js")
        self.assertIn("window.formatUiDateTime", js)
        self.assertIn("window.formatUiRelativeTime", js)
        self.assertIn("window.resolveApiErrorMessage", js)
        self.assertIn("switcher-docked", js)
        self.assertIn("document.querySelector('.sidebar-bottom')", js)
        self.assertIn("root.querySelectorAll('[placeholder],[title],[aria-label],input[type=\"button\"][value]')", js)
        self.assertIn("const core = text.trim()", js)
        self.assertIn("characterData: true", js)
        self.assertIn("attributes: true", js)

    def test_main_js_does_not_override_i18n_runtime_helpers(self):
        client = self.app.test_client()
        main_js = self._get_text(client, "/static/js/main.js")
        self.assertIn("const pickApiMessage = (payload, fallbackZh, fallbackEn) =>", main_js)
        self.assertIn("const formatUiDateTime = (dateStr, options = {}) =>", main_js)
        self.assertIn("const formatUiRelativeTime = (dateStr, fallbackZh = '从未刷新', fallbackEn = 'Never refreshed') =>", main_js)
        self.assertNotIn("function pickApiMessage(payload, fallbackZh, fallbackEn)", main_js)
        self.assertNotIn("function formatUiDateTime(dateStr, options = {})", main_js)
        self.assertNotIn("function formatUiRelativeTime(dateStr, fallbackZh = '从未刷新', fallbackEn = 'Never refreshed')", main_js)

    def test_frontend_no_longer_uses_raw_error_object_toasts_on_key_paths(self):
        client = self.app.test_client()
        main_js = self._get_text(client, "/static/js/main.js")
        accounts_js = self._get_text(client, "/static/js/features/accounts.js")
        self.assertNotIn("showToast(data.error || '创建失败'", main_js)
        self.assertNotIn("showToast(data.error || '删除失败'", main_js)
        self.assertNotIn("showToast(data.error || '操作失败'", main_js)
        self.assertNotIn("showToast(result.error, 'error')", accounts_js)

    def test_settings_and_login_pages_load_i18n_script(self):
        client = self.app.test_client()
        self._login(client)
        index_html = self._get_text(client, "/")
        login_html = self._get_text(client, "/login")
        self.assertIn("/static/js/i18n.js", index_html)
        self.assertIn("/static/js/i18n.js", login_html)
        self.assertIn('id="telegramPollInterval" min="60" max="3600"', index_html)

    def test_key_email_notification_translations_exist(self):
        client = self.app.test_client()
        js = self._get_text(client, "/static/js/i18n.js")
        for text in [
            "邮件通知",
            "启用邮件通知",
            "接收通知邮箱",
            "发送测试邮件",
            "🔍 全屏查看",
            "🗑️ 删除",
            "🔄 获取邮件",
            "信任此邮件",
            "🔄 Token 刷新管理",
            "🔄 全量刷新",
            "🔁 重试失败",
            "失败邮箱",
            "全量刷新历史",
            "📤 导出",
            "🔄 全量刷新 Token",
            "＋ 添加账号",
            "＋ 创建邮箱",
            "🔑 验证码",
            "审计日志",
            "📋 审计日志",
            "暂无审计记录",
            "加载审计日志失败",
            "手动",
            "定时",
            "✉️ 邮件通知",
            "📬 Telegram 推送",
            "关闭时（默认）仅做 API Key 鉴权；开启后额外启用 IP 白名单、限流、高风险端点禁用等安全策略。",
            "建议设置为 30 天，防止 Token 因 90 天不使用而过期",
            "默认分组",
            "请从左侧选择一个邮箱账号",
            "选择一个临时邮箱查看邮件",
            "表达式有效",
            "下次执行:",
            "验证失败:",
            "自动按类型分组",
            "请选择标签...",
            "请选择分组...",
            "轮询中",
            "输入新密码（留空则不修改）",
            "用于 /api/external/* 的 X-API-Key",
            "每行一个 IP 或 CIDR，如 192.168.1.0/24",
            "输入 Bot Token",
            "输入 Chat ID",
            "http://host:port 或 socks5://user:pass@host:port",
            "授权成功后，浏览器会跳转到一个空白页，请复制地址栏中的完整 URL 并粘贴到这里",
            "确定要刷新所有账号的 Token 吗？",
            "确定要删除这个标签吗？",
            "Cron 表达式",
            "📨 收件箱",
            "⚠️ 垃圾邮件",
            "🔑 获取 Token",
            "🔔 推送",
            "QQ邮箱",
            "163邮箱",
            "126邮箱",
            "阿里云邮箱",
            "自定义IMAP",
            "该分组暂无邮箱",
            "收件箱为空",
            "暂无邮件",
            "未知发件人",
            "勾选后，新导入的 Outlook/IMAP 账号会以 `available` 状态进入邮箱池；不勾选则保持池外。",
            "（每个邮箱刷新之间的等待时间）",
            "访问 GitHub 仓库",
        ]:
            self.assertIn(text, js)

    def test_frontend_success_toasts_use_pick_api_message_on_key_paths(self):
        client = self.app.test_client()
        accounts_js = self._get_text(client, "/static/js/features/accounts.js")
        groups_js = self._get_text(client, "/static/js/features/groups.js")
        main_js = self._get_text(client, "/static/js/main.js")
        self.assertIn("pickApiMessage(result, result.message", accounts_js)
        self.assertIn("pickApiMessage(data, data.message", groups_js)
        self.assertIn("pickApiMessage(data, data.message", main_js)

    def test_frontend_dynamic_options_and_placeholders_use_i18n_helpers(self):
        client = self.app.test_client()
        accounts_js = self._get_text(client, "/static/js/features/accounts.js")
        main_js = self._get_text(client, "/static/js/main.js")
        groups_js = self._get_text(client, "/static/js/features/groups.js")
        emails_js = self._get_text(client, "/static/js/features/emails.js")
        temp_emails_js = self._get_text(client, "/static/js/features/temp_emails.js")
        self.assertIn("translateAppTextLocal('自动按类型分组')", accounts_js)
        self.assertIn("translateAppTextLocal('支持混合格式，每行一个账号", accounts_js)
        self.assertIn("translateAppTextLocal('请选择标签...')", main_js)
        self.assertIn("translateAppTextLocal('请选择分组...')", main_js)
        self.assertIn("translateAppTextLocal('推送')", groups_js)
        self.assertIn("translateAppTextLocal('收件箱为空')", emails_js)
        self.assertIn("translateAppTextLocal('暂无邮件')", temp_emails_js)
        self.assertIn("translateAppTextLocal('隐藏列表')", emails_js)
        self.assertIn("translateAppTextLocal('🔄 获取邮件')", temp_emails_js)

    def test_frontend_import_and_export_error_contract_helpers_are_consumed(self):
        client = self.app.test_client()
        accounts_js = self._get_text(client, "/static/js/features/accounts.js")
        main_js = self._get_text(client, "/static/js/main.js")
        self.assertIn("buildImportFailureToastMessage", accounts_js)
        self.assertIn("data.summary || Array.isArray(data.errors)", accounts_js)
        self.assertIn("if (verifyData.need_verify)", accounts_js)
        self.assertIn("if (data.need_verify)", accounts_js)
        self.assertIn("translateAppTextLocal('【用户错误信息】')", main_js)
        self.assertIn("translateAppTextLocal('【错误详情】')", main_js)
        self.assertIn("translateAppTextLocal('【技术堆栈/细节】')", main_js)

    def test_collapsed_sidebar_hides_github_label_to_avoid_overlap(self):
        client = self.app.test_client()
        css = self._get_text(client, "/static/css/main.css")
        i18n_js = self._get_text(client, "/static/js/i18n.js")
        self.assertIn(".sidebar-collapsed .btn-github span { display: none; }", css)
        self.assertIn(".sidebar-collapsed .btn-github {", css)
        self.assertIn(".sidebar-collapsed #globalLanguageSwitcher.switcher-docked", i18n_js)

    def test_frontend_runtime_copy_and_search_strings_use_i18n_contract(self):
        client = self.app.test_client()
        main_js = self._get_text(client, "/static/js/main.js")
        groups_js = self._get_text(client, "/static/js/features/groups.js")
        emails_js = self._get_text(client, "/static/js/features/emails.js")
        self.assertIn("translateAppTextLocal(`当前已配置 ${normalized.length} 个多 Key。保留已有脱敏 api_key 表示不修改该 Key；清空后保存表示清空全部多 Key。`)", main_js)
        self.assertIn("translateAppTextLocal('未设置（设置后可通过 /api/external/* 对外开放接口读取邮件与验证码）')", main_js)
        self.assertIn("translateAppTextLocal(`搜索结果 (${data.accounts.length})`)", groups_js)
        self.assertIn("replace(/\\s+\\((临时|Temp)\\)$/, '')", emails_js)
