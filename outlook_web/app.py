from __future__ import annotations

from typing import Optional

_APP_INSTANCE = None


def create_app(*, autostart_scheduler: Optional[bool] = None):
    """
    应用工厂（迁移期实现）：
    - 统一装配入口，便于测试与后续 Blueprint/分层拆分
    - 控制 import-time 副作用：初始化/调度器启动放到 create_app 中受控执行
    - routes 采用 Blueprint 模块化注册（URL 不变）
    """
    global _APP_INSTANCE

    if _APP_INSTANCE is None:
        from pathlib import Path

        from flask import Flask
        from werkzeug.middleware.proxy_fix import ProxyFix
        from werkzeug.exceptions import HTTPException

        from outlook_web import config, legacy
        from outlook_web.db import register_db
        from outlook_web.security.csrf import init_csrf
        from outlook_web.routes import (
            accounts,
            audit,
            emails,
            groups,
            oauth,
            pages,
            scheduler,
            settings,
            system,
            tags,
            temp_emails,
        )

        # 初始化（DB/目录等）
        legacy.init_app()

        repo_root = Path(__file__).resolve().parents[1]
        app = Flask(
            __name__,
            template_folder=str(repo_root / "templates"),
            static_folder=str(repo_root / "static"),
            static_url_path="/static",
        )

        app.secret_key = config.require_secret_key()
        app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 7  # 7 天
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

        # DB teardown（请求结束释放连接）
        register_db(app)

        # CSRF（可选）
        _csrf, csrf_exempt, _generate_csrf = init_csrf(app)

        # trace_id + error 结构标准化（复用 legacy 的 hooks 逻辑，保持契约一致）
        app.before_request(legacy.ensure_trace_id)
        app.after_request(legacy.attach_trace_id_and_normalize_errors)
        app.register_error_handler(HTTPException, legacy.handle_http_exception)
        app.register_error_handler(Exception, legacy.handle_exception)

        # Blueprint 路由注册（URL 不变）
        app.register_blueprint(pages.create_blueprint(csrf_exempt=csrf_exempt))
        app.register_blueprint(groups.create_blueprint())
        app.register_blueprint(tags.create_blueprint())
        app.register_blueprint(accounts.create_blueprint(impl=legacy))
        app.register_blueprint(emails.create_blueprint())
        app.register_blueprint(temp_emails.create_blueprint())
        app.register_blueprint(oauth.create_blueprint())
        app.register_blueprint(settings.create_blueprint())
        app.register_blueprint(scheduler.create_blueprint())
        app.register_blueprint(system.create_blueprint())
        app.register_blueprint(audit.create_blueprint())

        _APP_INSTANCE = app

    if autostart_scheduler is None:
        from outlook_web import legacy

        if legacy.should_autostart_scheduler():
            legacy.init_scheduler()
    elif autostart_scheduler:
        from outlook_web import legacy

        legacy.init_scheduler()

    return _APP_INSTANCE
