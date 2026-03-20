from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any, Callable

from outlook_web.repositories import accounts as accounts_repo
from outlook_web.repositories import notification_state as notification_state_repo
from outlook_web.repositories import settings as settings_repo
from outlook_web.repositories import temp_emails as temp_emails_repo
from outlook_web.services import email_push, gptmail

logger = logging.getLogger(__name__)

CHANNEL_EMAIL = "email"
CHANNEL_TELEGRAM = "telegram"
SOURCE_ACCOUNT = "account"
SOURCE_TEMP_EMAIL = "temp_email"
DEFAULT_EMAIL_JOB_INTERVAL_SECONDS = 60
MAX_EMAIL_NOTIFICATIONS_PER_JOB = 50
MAX_TELEGRAM_NOTIFICATIONS_PER_JOB = 20
ACCOUNT_INCLUDED_FOLDERS = ("inbox", "junkemail")
MAX_EMAIL_BODY_LENGTH = 4000
MAX_TEMP_EMAIL_PREVIEW_LENGTH = 200


class NotificationDispatchError(Exception):
    def __init__(self, code: str, message: str, *, message_en: str, status: int = 502) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.message_en = message_en
        self.status = status


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _max_cursor_value(current: str, candidate: str) -> str:
    if not current:
        return candidate or ""
    if not candidate:
        return current
    return candidate if candidate > current else current


def _html_to_plain(html_text: str) -> str:
    if not html_text:
        return ""
    text = re.sub(r"<[^>]+>", " ", html_text)
    return re.sub(r"\s+", " ", text).strip()


def build_source_key(source_type: str, raw_key: str) -> str:
    return f"{source_type}:{(raw_key or '').strip().lower()}"


def _normalize_account_source(account: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_type": SOURCE_ACCOUNT,
        "source_key": build_source_key(SOURCE_ACCOUNT, account.get("email", "")),
        "email": account.get("email", ""),
        "label": account.get("email", ""),
        "account": account,
    }


def _normalize_temp_email_source(temp_email: dict[str, Any]) -> dict[str, Any]:
    address = temp_email.get("email", "")
    return {
        "source_type": SOURCE_TEMP_EMAIL,
        "source_key": build_source_key(SOURCE_TEMP_EMAIL, address),
        "email": address,
        "label": address,
        "temp_email": temp_email,
    }


def list_email_notification_sources() -> list[dict[str, Any]]:
    accounts = [acc for acc in accounts_repo.load_accounts() if (acc.get("status") or "active") == "active"]
    temp_emails = [item for item in temp_emails_repo.load_temp_emails() if (item.get("status") or "active") == "active"]
    return [_normalize_account_source(acc) for acc in accounts] + [_normalize_temp_email_source(item) for item in temp_emails]


def bootstrap_channel_cursors(channel: str, *, cursor_value: str | None = None) -> None:
    target_cursor = cursor_value or utc_now_iso()
    for source in list_email_notification_sources():
        notification_state_repo.reset_channel_cursor(
            channel,
            source["source_type"],
            source["source_key"],
            target_cursor,
        )


def _extract_message_timestamp(raw_value: Any) -> str:
    if raw_value is None:
        return ""
    if isinstance(raw_value, (int, float)):
        return datetime.fromtimestamp(float(raw_value), timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    text = str(raw_value).strip()
    if not text:
        return ""
    if text.endswith("Z"):
        text = text[:-1]
    return text.split(".")[0]


def _message_sort_key(message: dict[str, Any]) -> tuple[str, str]:
    return (
        str(message.get("received_at") or ""),
        str(message.get("message_id") or ""),
    )


def _persist_channel_cursor(channel: str, source: dict[str, Any], cursor_value: str) -> None:
    notification_state_repo.upsert_cursor(channel, source["source_type"], source["source_key"], cursor_value)

    if channel == CHANNEL_TELEGRAM and source["source_type"] == SOURCE_ACCOUNT:
        from outlook_web.repositories.accounts import update_telegram_cursor

        account_id = source.get("account", {}).get("id")
        if account_id:
            update_telegram_cursor(int(account_id), cursor_value)


def _get_initial_cursor_value(channel: str, source: dict[str, Any], job_start: str) -> str:
    if channel == CHANNEL_TELEGRAM and source["source_type"] == SOURCE_ACCOUNT:
        legacy_cursor = str(source.get("account", {}).get("telegram_last_checked_at") or "").strip()
        if legacy_cursor:
            return legacy_cursor
    return job_start


def _ensure_channel_cursor(channel: str, source: dict[str, Any], job_start: str) -> tuple[str, bool]:
    cursor = notification_state_repo.get_cursor(channel, source["source_type"], source["source_key"])
    if cursor:
        return cursor, False
    initial_cursor = _get_initial_cursor_value(channel, source, job_start)
    _persist_channel_cursor(channel, source, initial_cursor)
    return initial_cursor, initial_cursor == job_start


def _fetch_account_messages(source: dict[str, Any], since: str) -> list[dict[str, Any]]:
    from outlook_web.services import telegram_push

    account = source["account"]
    emails: list[dict[str, Any]] = []
    for folder in ACCOUNT_INCLUDED_FOLDERS:
        try:
            if (account.get("provider") or "outlook") == "outlook":
                fetched = telegram_push._fetch_new_emails_graph(account, since, folder=folder)
            else:
                fetched = telegram_push._fetch_new_emails_imap(account, since, folder=folder)
            for item in fetched:
                enriched = dict(item)
                enriched["folder"] = folder
                emails.append(enriched)
        except Exception as exc:
            logger.warning("[notification_dispatch] account fetch failed source=%s folder=%s err=%s", source["label"], folder, exc)
            raise
    return emails


def _fetch_temp_email_messages(source: dict[str, Any], since: str) -> list[dict[str, Any]]:
    address = source["email"]
    api_messages = gptmail.get_temp_emails_from_api(address)
    if api_messages is not None:
        temp_emails_repo.save_temp_email_messages(address, api_messages)
    messages = temp_emails_repo.get_temp_email_messages(address)
    results: list[dict[str, Any]] = []
    for item in messages:
        received_at = _extract_message_timestamp(item.get("timestamp") or item.get("created_at"))
        if received_at and received_at <= since:
            continue
        plain_content = (item.get("content", "") or "").strip()
        if not plain_content and item.get("has_html"):
            plain_content = _html_to_plain(item.get("html_content", "") or "")
        preview = plain_content[:MAX_TEMP_EMAIL_PREVIEW_LENGTH]
        results.append(
            {
                "message_id": item.get("message_id", ""),
                "subject": item.get("subject", "") or "无主题",
                "sender": item.get("from_address", "") or "unknown",
                "received_at": received_at,
                "preview": preview,
                "content": plain_content,
                "folder": "inbox",
            }
        )
    return results


def fetch_source_messages(source: dict[str, Any], since: str) -> list[dict[str, Any]]:
    if source["source_type"] == SOURCE_ACCOUNT:
        return _fetch_account_messages(source, since)
    if source["source_type"] == SOURCE_TEMP_EMAIL:
        return _fetch_temp_email_messages(source, since)
    return []


def build_message_key(source: dict[str, Any], message: dict[str, Any]) -> str:
    return notification_state_repo.build_stable_message_key(
        source_type=source["source_type"],
        source_key=source["source_key"],
        message_id=message.get("message_id"),
        subject=message.get("subject"),
        sender=message.get("sender"),
        received_at=message.get("received_at"),
        preview=message.get("preview"),
        content=message.get("content"),
    )


def send_business_email_notification(source: dict[str, Any], message: dict[str, Any]) -> None:
    recipient = email_push.get_saved_notification_recipient()
    subject = f"[Outlook Email Plus] {source['label']} 收到新邮件"
    received_at = message.get("received_at") or "-"
    folder = message.get("folder") or "inbox"
    body_text = (message.get("content") or message.get("preview") or "").strip()
    if len(body_text) > MAX_EMAIL_BODY_LENGTH:
        body_text = body_text[:MAX_EMAIL_BODY_LENGTH].rstrip() + "\n\n...[truncated]"
    if not body_text:
        body_text = "(正文为空)"
    text_body = (
        f"邮箱来源: {source['label']}\n"
        f"来源类型: {'普通邮箱' if source['source_type'] == SOURCE_ACCOUNT else '临时邮箱'}\n"
        f"目录: {folder}\n"
        f"发件人: {message.get('sender') or '-'}\n"
        f"主题: {message.get('subject') or '无主题'}\n"
        f"时间: {received_at}\n\n"
        f"正文:\n{body_text}"
    )
    html_body = (
        f"<p><strong>邮箱来源:</strong> {source['label']}</p>"
        f"<p><strong>来源类型:</strong> {'普通邮箱' if source['source_type'] == SOURCE_ACCOUNT else '临时邮箱'}</p>"
        f"<p><strong>目录:</strong> {folder}</p>"
        f"<p><strong>发件人:</strong> {message.get('sender') or '-'}</p>"
        f"<p><strong>主题:</strong> {message.get('subject') or '无主题'}</p>"
        f"<p><strong>时间:</strong> {received_at}</p>"
        f"<p><strong>正文:</strong><br>{body_text.replace(chr(10), '<br>')}</p>"
    )
    email_push.send_email_message(
        recipient=recipient,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )


def send_business_telegram_notification(
    source: dict[str, Any],
    message: dict[str, Any],
    *,
    bot_token: str,
    chat_id: str,
) -> None:
    from outlook_web.services.telegram_push import _build_telegram_message, _send_telegram_message

    account_email = source.get("account", {}).get("email", source.get("label", ""))
    payload = _build_telegram_message(account_email, message)
    if not _send_telegram_message(bot_token, chat_id, payload):
        raise NotificationDispatchError(
            "TELEGRAM_SEND_FAILED",
            "Telegram 发送失败",
            message_en="Failed to send Telegram notification",
        )


def _record_telegram_legacy_delivery(source: dict[str, Any], message_key: str) -> None:
    if source["source_type"] != SOURCE_ACCOUNT:
        return

    account_id = source.get("account", {}).get("id")
    if not account_id:
        return

    from outlook_web.db import get_db
    from outlook_web.services.telegram_push import _record_pushed_message

    _record_pushed_message(get_db(), int(account_id), message_key)


def _process_messages_for_channel(
    *,
    channel: str,
    source: dict[str, Any],
    cursor: str,
    messages: list[dict[str, Any]],
    sender: Callable[[dict[str, Any], dict[str, Any]], None],
    max_notifications: int | None,
) -> dict[str, int | str]:
    sent_count = 0
    failed_count = 0
    dedup_skipped = 0
    next_cursor = cursor

    for message in sorted(messages, key=_message_sort_key):
        if max_notifications is not None and sent_count >= max_notifications:
            break

        message_received_at = str(message.get("received_at") or "")
        if message_received_at and cursor and message_received_at <= cursor:
            continue

        message_key = build_message_key(source, message)
        claim_result = notification_state_repo.claim_delivery_attempt(
            channel,
            source["source_type"],
            source["source_key"],
            message_key,
        )
        if claim_result == "sent":
            dedup_skipped += 1
            if message_received_at:
                next_cursor = _max_cursor_value(next_cursor, message_received_at)
            continue
        if claim_result != "acquired":
            logger.info(
                "[notification_dispatch] skip delivery without lock channel=%s source=%s message=%s state=%s",
                channel,
                source.get("label"),
                message_key,
                claim_result,
            )
            continue

        try:
            sender(source, message)
            notification_state_repo.complete_delivery_attempt(
                channel,
                source["source_type"],
                source["source_key"],
                message_key,
                status="sent",
            )
            if channel == CHANNEL_TELEGRAM:
                _record_telegram_legacy_delivery(source, message_key)
            sent_count += 1
            if message_received_at:
                next_cursor = _max_cursor_value(next_cursor, message_received_at)
        except Exception as exc:
            notification_state_repo.complete_delivery_attempt(
                channel,
                source["source_type"],
                source["source_key"],
                message_key,
                status="failed",
                error_code=getattr(exc, "code", "NOTIFICATION_SEND_FAILED"),
                error_message=str(exc),
            )
            failed_count += 1
            break

    _persist_channel_cursor(channel, source, next_cursor)
    return {
        "sent_count": sent_count,
        "failed_count": failed_count,
        "dedup_skipped": dedup_skipped,
        "next_cursor": next_cursor,
    }


def process_channel_for_sources(
    *,
    channel: str,
    sources: list[dict[str, Any]],
    sender: Callable[[dict[str, Any], dict[str, Any]], None],
    max_notifications: int | None = None,
) -> dict[str, int]:
    job_start = utc_now_iso()
    sent_count = 0
    failed_count = 0
    dedup_skipped = 0

    for source in sources:
        cursor, initialized = _ensure_channel_cursor(channel, source, job_start)
        if initialized:
            continue

        try:
            messages = fetch_source_messages(source, cursor)
        except Exception:
            failed_count += 1
            continue

        result = _process_messages_for_channel(
            channel=channel,
            source=source,
            cursor=cursor,
            messages=messages,
            sender=sender,
            max_notifications=None if max_notifications is None else max(max_notifications - sent_count, 0),
        )
        sent_count += int(result["sent_count"])
        failed_count += int(result["failed_count"])
        dedup_skipped += int(result["dedup_skipped"])

    notification_state_repo.cleanup_delivery_logs()
    return {
        "sent_count": sent_count,
        "failed_count": failed_count,
        "dedup_skipped": dedup_skipped,
    }


def _get_telegram_runtime_config() -> dict[str, str] | None:
    from outlook_web.security.crypto import decrypt_data, is_encrypted

    bot_token_raw = settings_repo.get_setting("telegram_bot_token", "")
    chat_id = settings_repo.get_setting("telegram_chat_id", "").strip()
    if not bot_token_raw or not chat_id:
        return None

    bot_token = decrypt_data(bot_token_raw) if is_encrypted(bot_token_raw) else bot_token_raw
    bot_token = str(bot_token or "").strip()
    if not bot_token:
        return None
    return {"bot_token": bot_token, "chat_id": chat_id}


def _is_email_channel_enabled() -> bool:
    enabled = settings_repo.get_setting("email_notification_enabled", "false").lower() == "true"
    return enabled and email_push.is_email_notification_ready()


def _is_source_notification_enabled(source: dict[str, Any]) -> bool:
    """账号级通知开关。

    Resolve 文档约定：
    - 普通邮箱是否参与自动通知，由账号级开关决定
    - 临时邮箱本轮继续沿用默认参与的兼容语义
    """
    if source.get("source_type") != SOURCE_ACCOUNT:
        return True

    account = source.get("account") or {}
    return bool(account.get("telegram_push_enabled"))


def _build_active_channels_for_source(
    source: dict[str, Any],
    *,
    email_enabled: bool,
    telegram_runtime: dict[str, str] | None,
) -> list[tuple[str, Callable[[dict[str, Any], dict[str, Any]], None], int]]:
    active_channels: list[tuple[str, Callable[[dict[str, Any], dict[str, Any]], None], int]] = []

    if not _is_source_notification_enabled(source):
        return active_channels

    if email_enabled:
        active_channels.append((CHANNEL_EMAIL, send_business_email_notification, MAX_EMAIL_NOTIFICATIONS_PER_JOB))

    if telegram_runtime and source["source_type"] == SOURCE_ACCOUNT:
        active_channels.append(
            (
                CHANNEL_TELEGRAM,
                lambda current_source, message, bot_token=telegram_runtime["bot_token"], chat_id=telegram_runtime["chat_id"]: send_business_telegram_notification(  # noqa: E731
                    current_source,
                    message,
                    bot_token=bot_token,
                    chat_id=chat_id,
                ),
                MAX_TELEGRAM_NOTIFICATIONS_PER_JOB,
            )
        )

    return active_channels


def run_notification_dispatch_job(app) -> None:
    with app.app_context():
        sources = list_email_notification_sources()
        if not sources:
            return

        email_enabled = _is_email_channel_enabled()
        telegram_runtime = _get_telegram_runtime_config()
        if not email_enabled and not telegram_runtime:
            return

        job_start = utc_now_iso()
        channel_totals = {
            CHANNEL_EMAIL: {"sent_count": 0, "failed_count": 0, "dedup_skipped": 0},
            CHANNEL_TELEGRAM: {"sent_count": 0, "failed_count": 0, "dedup_skipped": 0},
        }

        for source in sources:
            active_channels = _build_active_channels_for_source(
                source,
                email_enabled=email_enabled,
                telegram_runtime=telegram_runtime,
            )
            if not active_channels:
                continue

            channel_cursors: dict[str, str] = {}
            initialized_channels: set[str] = set()
            for channel, _, _ in active_channels:
                cursor, initialized = _ensure_channel_cursor(channel, source, job_start)
                channel_cursors[channel] = cursor
                if initialized:
                    initialized_channels.add(channel)

            fetch_plan: dict[str, list[tuple[str, Callable[[dict[str, Any], dict[str, Any]], None], int]]] = {}
            for channel, sender, channel_limit in active_channels:
                if channel in initialized_channels:
                    continue
                fetch_plan.setdefault(channel_cursors[channel], []).append((channel, sender, channel_limit))

            if not fetch_plan:
                continue

            for fetch_cursor, planned_channels in fetch_plan.items():
                try:
                    messages = fetch_source_messages(source, fetch_cursor)
                except Exception as exc:
                    logger.warning(
                        "[notification_dispatch] grouped fetch failed source=%s cursor=%s err=%s",
                        source.get("label"),
                        fetch_cursor,
                        exc,
                    )
                    for channel, _, _ in planned_channels:
                        channel_totals[channel]["failed_count"] += 1
                    continue

                for channel, sender, channel_limit in planned_channels:
                    remaining = channel_limit - int(channel_totals[channel]["sent_count"])
                    if remaining <= 0:
                        continue
                    result = _process_messages_for_channel(
                        channel=channel,
                        source=source,
                        cursor=channel_cursors[channel],
                        messages=messages,
                        sender=sender,
                        max_notifications=remaining,
                    )
                    channel_totals[channel]["sent_count"] += int(result["sent_count"])
                    channel_totals[channel]["failed_count"] += int(result["failed_count"])
                    channel_totals[channel]["dedup_skipped"] += int(result["dedup_skipped"])

        notification_state_repo.cleanup_delivery_logs()


def run_email_notification_job(app) -> None:
    with app.app_context():
        enabled = settings_repo.get_setting("email_notification_enabled", "false").lower() == "true"
        if not enabled or not email_push.is_email_notification_ready():
            return
        sources = [
            source
            for source in list_email_notification_sources()
            if _is_source_notification_enabled(source)
        ]
        if not sources:
            return
        process_channel_for_sources(
            channel=CHANNEL_EMAIL,
            sources=sources,
            sender=send_business_email_notification,
            max_notifications=MAX_EMAIL_NOTIFICATIONS_PER_JOB,
        )
