from __future__ import annotations

from typing import Any

from flask import jsonify, request

from outlook_web import config
from outlook_web.audit import log_audit
from outlook_web.db import get_db
from outlook_web.errors import build_error_payload
from outlook_web.repositories import accounts as accounts_repo
from outlook_web.repositories import groups as groups_repo
from outlook_web.security.auth import login_required
from outlook_web.services import email_delete as email_delete_service
from outlook_web.services import graph as graph_service
from outlook_web.services import imap as imap_service


# IMAP 服务器配置
IMAP_SERVER_OLD = "outlook.office365.com"
IMAP_SERVER_NEW = "outlook.live.com"


# ==================== 邮件 API ====================


@login_required
def api_get_emails(email_addr: str) -> Any:
    """获取邮件列表（支持分页，不使用缓存）"""
    account = accounts_repo.get_account_by_email(email_addr)

    if not account:
        error_payload = build_error_payload(
            "ACCOUNT_NOT_FOUND",
            "账号不存在",
            "NotFoundError",
            404,
            f"email={email_addr}"
        )
        return jsonify({'success': False, 'error': error_payload})

    folder = request.args.get('folder', 'inbox')  # inbox, junkemail, deleteditems
    skip = int(request.args.get('skip', 0))
    top = int(request.args.get('top', 20))

    # 获取分组代理设置
    proxy_url = ''
    if account.get('group_id'):
        group = groups_repo.get_group_by_id(account['group_id'])
        if group:
            proxy_url = group.get('proxy_url', '') or ''

    # 收集所有错误信息
    all_errors = {}

    # 1. 尝试 Graph API
    graph_result = graph_service.get_emails_graph(account['client_id'], account['refresh_token'], folder, skip, top, proxy_url)
    if graph_result.get("success"):
        emails = graph_result.get("emails", [])
        # 更新刷新时间
        db = get_db()
        db.execute('''
            UPDATE accounts
            SET last_refresh_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
        ''', (email_addr,))
        db.commit()

        # 格式化 Graph API 返回的数据
        formatted = []
        for e in emails:
            formatted.append({
                'id': e.get('id'),
                'subject': e.get('subject', '无主题'),
                'from': e.get('from', {}).get('emailAddress', {}).get('address', '未知'),
                'date': e.get('receivedDateTime', ''),
                'is_read': e.get('isRead', False),
                'has_attachments': e.get('hasAttachments', False),
                'body_preview': e.get('bodyPreview', '')
            })

        return jsonify({
            'success': True,
            'emails': formatted,
            'method': 'Graph API',
            'has_more': len(formatted) >= top
        })
    else:
        graph_error = graph_result.get("error")
        all_errors["graph"] = graph_error

        # 如果是代理错误，不再回退 IMAP
        if isinstance(graph_error, dict) and graph_error.get('type') in ('ProxyError', 'ConnectionError'):
            return jsonify({
                'success': False,
                'error': '代理连接失败，请检查分组代理设置',
                'details': all_errors
            })

    imap_new_result = imap_service.get_emails_imap_with_server(
        account['email'], account['client_id'], account['refresh_token'],
        folder, skip, top, IMAP_SERVER_NEW
    )
    if imap_new_result.get("success"):
        return jsonify({
            'success': True,
            'emails': imap_new_result.get("emails", []),
            'method': 'IMAP (New)',
            'has_more': False  # IMAP 分页暂未完全实现
        })
    else:
        all_errors["imap_new"] = imap_new_result.get("error")

    # 3. 尝试旧版 IMAP (outlook.office365.com)
    imap_old_result = imap_service.get_emails_imap_with_server(
        account['email'], account['client_id'], account['refresh_token'],
        folder, skip, top, IMAP_SERVER_OLD
    )
    if imap_old_result.get("success"):
        return jsonify({
            'success': True,
            'emails': imap_old_result.get("emails", []),
            'method': 'IMAP (Old)',
            'has_more': False
        })
    else:
        all_errors["imap_old"] = imap_old_result.get("error")

    return jsonify({
        'success': False,
        'error': '无法获取邮件，所有方式均失败',
        'details': all_errors
    })


@login_required
def api_delete_emails() -> Any:
    """批量删除邮件（永久删除）"""
    data = request.json
    email_addr = data.get('email', '')
    message_ids = data.get('ids', [])

    if not email_addr or not message_ids:
        return jsonify({'success': False, 'error': '参数不完整'})

    account = accounts_repo.get_account_by_email(email_addr)
    if not account:
        return jsonify({'success': False, 'error': '账号不存在'})

    # 获取分组代理设置
    proxy_url = ''
    if account.get('group_id'):
        group = groups_repo.get_group_by_id(account['group_id'])
        if group:
            proxy_url = group.get('proxy_url', '') or ''

    response_data, method_used = email_delete_service.delete_emails_with_fallback(
        email_addr=email_addr,
        client_id=account["client_id"],
        refresh_token=account["refresh_token"],
        message_ids=message_ids,
        proxy_url=proxy_url,
        delete_emails_graph=graph_service.delete_emails_graph,
        delete_emails_imap=imap_service.delete_emails_imap,
        imap_server_new=IMAP_SERVER_NEW,
        imap_server_old=IMAP_SERVER_OLD,
    )

    if method_used == "graph":
        log_audit("delete", "email", email_addr, f"删除邮件 {len(message_ids)} 封（Graph API）")
    elif method_used == "imap_new":
        log_audit("delete", "email", email_addr, f"删除邮件 {len(message_ids)} 封（IMAP New）")
    elif method_used == "imap_old":
        log_audit("delete", "email", email_addr, f"删除邮件 {len(message_ids)} 封（IMAP Old）")

    return jsonify(response_data)


@login_required
def api_get_email_detail(email_addr: str, message_id: str) -> Any:
    """获取邮件详情"""
    account = accounts_repo.get_account_by_email(email_addr)

    if not account:
        return jsonify({'success': False, 'error': '账号不存在'})

    method = request.args.get('method', 'graph')
    folder = request.args.get('folder', 'inbox')

    if method == 'graph':
        # 获取分组代理设置
        proxy_url = ''
        if account.get('group_id'):
            group = groups_repo.get_group_by_id(account['group_id'])
            if group:
                proxy_url = group.get('proxy_url', '') or ''

        detail = graph_service.get_email_detail_graph(account['client_id'], account['refresh_token'], message_id, proxy_url)
        if detail:
            return jsonify({
                'success': True,
                'email': {
                    'id': detail.get('id'),
                    'subject': detail.get('subject', '无主题'),
                    'from': detail.get('from', {}).get('emailAddress', {}).get('address', '未知'),
                    'to': ', '.join([r.get('emailAddress', {}).get('address', '') for r in detail.get('toRecipients', [])]),
                    'cc': ', '.join([r.get('emailAddress', {}).get('address', '') for r in detail.get('ccRecipients', [])]),
                    'date': detail.get('receivedDateTime', ''),
                    'body': detail.get('body', {}).get('content', ''),
                    'body_type': detail.get('body', {}).get('contentType', 'text')
                }
            })

    # 如果 Graph API 失败，尝试 IMAP
    detail = imap_service.get_email_detail_imap(account['email'], account['client_id'], account['refresh_token'], message_id, folder)
    if detail:
        return jsonify({'success': True, 'email': detail})

    return jsonify({'success': False, 'error': '获取邮件详情失败'})


@login_required
def api_extract_verification(email_addr: str) -> Any:
    """
    提取验证码和链接接口

    功能：从指定邮箱的最新邮件中提取验证码和链接

    实现策略（多 API 回退机制）：
    1. Graph API (inbox) - 优先从收件箱获取
    2. Graph API (junkemail) - 从垃圾邮件获取
    3. IMAP (新服务器) - Graph API 失败时回退
    4. IMAP (旧服务器) - 最后的回退方案
    """
    from outlook_web.services.verification_extractor import extract_verification_info

    # 获取账号信息
    account = accounts_repo.get_account_by_email(email_addr)

    if not account:
        error_payload = build_error_payload(
            "ACCOUNT_NOT_FOUND",
            "邮箱不存在",
            "NotFoundError",
            404,
            f"email={email_addr}"
        )
        return jsonify({'success': False, 'error': error_payload}), 404

    # 获取分组代理设置
    proxy_url = ''
    if account.get('group_id'):
        group = groups_repo.get_group_by_id(account['group_id'])
        if group:
            proxy_url = group.get('proxy_url', '') or ''

    # 收集邮件（同时从收件箱和垃圾邮件获取）
    emails = []
    graph_success = False

    # 1. 尝试 Graph API 从收件箱获取最新邮件
    try:
        inbox_result = graph_service.get_emails_graph(
            account['client_id'],
            account['refresh_token'],
            folder='inbox',
            skip=0,
            top=1,
            proxy_url=proxy_url
        )
        if inbox_result.get("success"):
            emails.extend(inbox_result.get("emails", []))
            graph_success = True
    except Exception:
        pass

    # 2. 尝试 Graph API 从垃圾邮件获取最新邮件
    try:
        junk_result = graph_service.get_emails_graph(
            account['client_id'],
            account['refresh_token'],
            folder='junkemail',
            skip=0,
            top=1,
            proxy_url=proxy_url
        )
        if junk_result.get("success"):
            emails.extend(junk_result.get("emails", []))
            graph_success = True
    except Exception:
        pass

    # 3. 如果 Graph API 失败，尝试 IMAP 回退
    if not graph_success or not emails:
        # 尝试新版 IMAP 服务器
        try:
            imap_new_result = imap_service.get_emails_imap_with_server(
                account['email'], account['client_id'], account['refresh_token'],
                folder='inbox', skip=0, top=1, server=IMAP_SERVER_NEW
            )
            if imap_new_result.get("success"):
                emails.extend(imap_new_result.get("emails", []))
        except Exception:
            pass

        # 尝试旧版 IMAP 服务器
        try:
            imap_old_result = imap_service.get_emails_imap_with_server(
                account['email'], account['client_id'], account['refresh_token'],
                folder='inbox', skip=0, top=1, server=IMAP_SERVER_OLD
            )
            if imap_old_result.get("success"):
                emails.extend(imap_old_result.get("emails", []))
        except Exception:
            pass

    if not emails:
        error_payload = build_error_payload(
            "EMAIL_NOT_FOUND",
            "未找到邮件",
            "NotFoundError",
            404,
            f"email={email_addr}"
        )
        return jsonify({'success': False, 'error': error_payload}), 404

    # 按时间排序，取最新的一封
    emails.sort(key=lambda x: x.get('receivedDateTime', '') or x.get('date', ''), reverse=True)
    latest_email = emails[0]

    # 获取邮件详情以获取完整内容
    email_detail = None

    # 尝试 Graph API 获取详情
    try:
        email_detail = graph_service.get_email_detail_graph(
            account['client_id'],
            account['refresh_token'],
            latest_email.get('id'),
            proxy_url
        )
    except Exception:
        pass

    # 如果 Graph API 失败，尝试 IMAP 获取详情
    if not email_detail:
        try:
            email_detail = imap_service.get_email_detail_imap(
                account['email'],
                account['client_id'],
                account['refresh_token'],
                latest_email.get('id'),
                'inbox'
            )
        except Exception:
            pass

    # 构建邮件对象用于提取
    email_obj = {
        'subject': latest_email.get('subject', ''),
        'body_preview': latest_email.get('bodyPreview', '') or latest_email.get('body_preview', '')
    }

    if email_detail:
        # Graph API 格式
        if 'body' in email_detail:
            body_content = email_detail.get('body', {})
            email_obj['body'] = body_content.get('content', '') if body_content.get('contentType') == 'text' else ''
            email_obj['body_html'] = body_content.get('content', '') if body_content.get('contentType') == 'html' else ''
            email_obj['bodyContent'] = body_content.get('content', '')
            email_obj['bodyContentType'] = body_content.get('contentType', 'text')
        # IMAP 格式
        elif 'body' in email_detail or 'body_html' in email_detail:
            email_obj['body'] = email_detail.get('body', '')
            email_obj['body_html'] = email_detail.get('body_html', '')

    try:
        # 尝试从邮件详情提取验证信息
        result = extract_verification_info(email_obj)

        return jsonify({
            'success': True,
            'data': result,
            'message': '提取成功'
        })

    except ValueError as e:
        # 未找到验证信息
        error_payload = build_error_payload(
            "VERIFICATION_NOT_FOUND",
            str(e),
            "NotFoundError",
            404,
            f"email={email_addr}"
        )
        return jsonify({'success': False, 'error': error_payload}), 404

    except Exception as e:
        # 其他错误
        error_payload = build_error_payload(
            "EXTRACT_ERROR",
            "提取失败",
            "ExtractError",
            500,
            str(e)
        )
        return jsonify({'success': False, 'error': error_payload}), 500
