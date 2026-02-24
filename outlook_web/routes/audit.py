from __future__ import annotations

from flask import Blueprint

from outlook_web.controllers import audit as audit_controller


def create_blueprint() -> Blueprint:
    """创建 audit Blueprint"""
    bp = Blueprint("audit", __name__)
    bp.add_url_rule("/api/audit-logs", view_func=audit_controller.api_get_audit_logs, methods=["GET"])
    return bp
