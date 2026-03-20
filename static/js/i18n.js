(function () {
    const STORAGE_KEY = 'ui_language';
    const exactMap = {
        '登录 - Outlook 邮件管理': 'Login - Outlook Email Management',
        'Outlook 邮件管理': 'Outlook Email Management',
        '安全登录以管理您的邮箱账号': 'Secure sign-in to manage your mail accounts',
        '登录密码': 'Login Password',
        '请输入密码': 'Please enter your password',
        '登 录': 'Sign In',
        '登录中...': 'Signing in...',
        '⏳ 发送中…': '⏳ Sending...',
        '登录失败': 'Login failed',
        '网络错误，请重试': 'Network error. Please try again.',
        'Outlook 邮件管理工具 · 安全访问': 'Outlook Email Management Tool · Secure Access',
        'Outlook 邮件': 'Outlook Mail',
        '概览': 'Overview',
        '仪表盘': 'Dashboard',
        '邮箱管理': 'Mailbox',
        '账号管理': 'Accounts',
        '临时邮箱': 'Temp Mailboxes',
        'Token': 'Token',
        '刷新日志': 'Refresh Logs',
        '系统': 'System',
        '系统设置': 'Settings',
        '审计日志': 'Audit Logs',
        '⚙️ 系统设置': '⚙️ Settings',
        '🔄 刷新日志': '🔄 Refresh Logs',
        '🔄 最近刷新': '🔄 Recent Refreshes',
        '管理员': 'Administrator',
        'Outlook 管理': 'Outlook Admin',
        'GitHub': 'GitHub',
        '☀ 浅色模式': '☀ Light Mode',
        '☾ 深色模式': '☾ Dark Mode',
        '退出登录': 'Logout',
        '系统概览': 'System overview',
        '管理邮箱账号与查看邮件': 'Manage accounts and read emails',
        '创建和管理临时邮箱': 'Create and manage temp mailboxes',
        'Token 刷新历史记录': 'Token refresh history',
        '配置系统参数': 'Configure system settings',
        '系统操作记录': 'System activity logs',
        '总账号数': 'Total Accounts',
        'Token 有效': 'Valid Tokens',
        'Token 过期': 'Expired Tokens',
        '分组概览': 'Group Summary',
        '最近刷新': 'Recent Refreshes',
        '加载中…': 'Loading...',
        '分组': 'Groups',
        '添加分组': 'Add Group',
        '搜索分组…': 'Search groups...',
        '选择分组': 'Select a group',
        '管理标签': 'Manage tags',
        '导入账号': 'Import Accounts',
        '📤 导出': '📤 Export',
        '🔄 全量刷新 Token': '🔄 Refresh All Tokens',
        '＋ 添加账号': '＋ Add Account',
        '＋ 创建邮箱': '＋ Create Mailbox',
        '+ 创建': '+ Create',
        '搜索邮箱地址…': 'Search email address...',
        '排序：': 'Sort:',
        '刷新时间': 'Refresh Time',
        '🕐 刷新时间': '🕐 Refresh Time',
        '📧 邮箱名': '📧 Email',
        '上次刷新时间': 'Last refresh time',
        '成功账号数': 'Successful accounts',
        '失败账号数': 'Failed accounts',
        '邮箱名': 'Email',
        '全选': 'Select All',
        '请从左侧选择一个分组': 'Select a group from the left',
        '打标签': 'Add Tags',
        '去标签': 'Remove Tags',
        '移动分组': 'Move Group',
        '删除': 'Delete',
        '🗑️ 删除': '🗑️ Delete',
        '编辑': 'Edit',
        '复制': 'Copy',
        '保存': 'Save',
        '清空': 'Clear',
        '导入': 'Import',
        '成功': 'Success',
        '失败': 'Failed',
        '跳过': 'Skipped',
        '按类型统计': 'By provider',
        '自动创建分组': 'Auto-created groups',
        '收件箱': 'Inbox',
        '垃圾邮件': 'Junk Email',
        '📨 收件箱': '📨 Inbox',
        '⚠️ 垃圾邮件': '⚠️ Junk Email',
        '获取邮件': 'Fetch Emails',
        '🔄 获取邮件': '🔄 Fetch Emails',
        '当前邮箱：': 'Current mailbox:',
        '点击复制邮箱地址': 'Click to copy email address',
        '访问 GitHub 仓库': 'Open the GitHub repository',
        '已选 0 项': '0 selected',
        '返回': 'Back',
        '全屏查看': 'Fullscreen',
        '🔍 全屏查看': '🔍 Fullscreen',
        '验证码': 'Verification',
        '🔑 验证码': '🔑 Verification',
        '提取验证码': 'Extract Verification',
        '信任此邮件': 'Trust this email',
        '选择一封邮件查看详情': 'Select an email to view details',
        '发件人': 'From',
        '收件人': 'To',
        '抄送': 'Cc',
        '时间': 'Time',
        '无主题': 'No Subject',
        '创建': 'Create',
        '创建第一个临时邮箱': 'Create the first temp mailbox',
        '暂无临时邮箱': 'No temp mailboxes yet',
        '选择一个临时邮箱': 'Select a temp mailbox',
        '刷新日志': 'Refresh Logs',
        '邮件通知': 'Email Notification',
        '启用邮件通知': 'Enable Email Notifications',
        '接收通知邮箱': 'Notification Recipient',
        '输入接收通知的邮箱地址': 'Enter the notification recipient email address',
        '发送测试邮件': 'Send Test Email',
        'Telegram 推送': 'Telegram Notifications',
        'Telegram 推送（已开启）': 'Telegram Notifications (Enabled)',
        'Telegram推送已开启': 'Telegram notifications enabled',
        'Telegram推送已关闭': 'Telegram notifications disabled',
        '发送测试消息': 'Send Test Message',
        '保存设置': 'Save Settings',
        '💾 保存设置': '💾 Save Settings',
        '📨 发送测试邮件': '📨 Send Test Email',
        '📨 发送测试消息': '📨 Send Test Message',
        '📬 Telegram 推送': '📬 Telegram Notifications',
        '✉️ 邮件通知': '✉️ Email Notification',
        '📋 审计日志': '📋 Audit Logs',
        '📂 分组概览': '📂 Group Summary',
        '对外开放 API Key': 'External API Key',
        '对外开放 API 多 Key 配置（JSON）': 'External API Multi-Key Configuration (JSON)',
        '对外 API 公网模式': 'External API Public Mode',
        '对外 API IP 白名单': 'External API IP Allowlist',
        '对外 API 限流阈值': 'External API Rate Limit',
        '对外 API 禁用 raw 端点': 'External API Disable Raw Endpoint',
        '对外 API 禁用 wait-message 端点': 'External API Disable Wait-Message Endpoint',
        '🛡️ 公网安全配置（P1）': '🛡️ Public Security Settings (P1)',
        '启用公网模式': 'Enable Public Mode',
        'IP 白名单': 'IP Allowlist',
        '每分钟每 IP 限流': 'Per-IP Rate Limit Per Minute',
        '禁用 raw（原始内容）端点': 'Disable raw content endpoint',
        '禁用 wait-message（等待新邮件）端点': 'Disable wait-message endpoint',
        '（仅公网模式生效，留空则不限制）': '(effective only in public mode; leave blank for no restriction)',
        '（仅公网模式生效）': '(effective only in public mode)',
        '（每隔 X 天自动刷新所有账号）': '(refresh all accounts every X days)',
        '（每个邮箱刷新之间的等待时间）': '(wait time between refreshing each mailbox)',
        '（检查新邮件的时间间隔）': '(interval for checking new emails)',
        '（最多轮询多少次后停止）': '(maximum number of polling attempts before stopping)',
        '（接收推送的用户/群组 ID）': '(user/group ID that receives notifications)',
        '（从 @BotFather 获取）': '(get it from @BotFather)',
        '🔄 Token 刷新设置': '🔄 Token Refresh Settings',
        '启用定时刷新': 'Enable Scheduled Refresh',
        '刷新策略': 'Refresh Strategy',
        '按天数': 'By Days',
        'Cron 表达式': 'Cron Expression',
        '定时刷新周期': 'Scheduled Refresh Interval',
        '常用样例': 'Common Examples',
        '验证表达式': 'Validate Expression',
        '邮箱间刷新间隔': 'Delay Between Mailboxes',
        '🔔 自动轮询设置': '🔔 Auto Polling Settings',
        '启用自动轮询': 'Enable Auto Polling',
        '轮询间隔': 'Polling Interval',
        '轮询次数': 'Polling Count',
        'Bot Token': 'Bot Token',
        'Chat ID': 'Chat ID',
        '用于登录系统的密码': 'Password used to sign in to the system',
        '关闭后将不会自动执行定时刷新任务': 'When disabled, scheduled refresh jobs will not run automatically',
        '格式：分 时 日 月 星期（例如：0 2 * * * 表示每天凌晨 2:00）': 'Format: minute hour day month weekday (for example: 0 2 * * * means every day at 02:00)',
        '天': 'days',
        '次': 'times',
        '秒': 'sec',
        '每 12 小时': 'Every 12 hours',
        '每天凌晨 2:00': 'Every day at 02:00',
        '每周一凌晨 2:00': 'Every Monday at 02:00',
        '每月 1 号凌晨 2:00': 'On the 1st day of each month at 02:00',
        '每 3 天凌晨 2:00': 'Every 3 days at 02:00',
        '范围：5-300 秒，建议设置为 10-30 秒': 'Range: 5-300 seconds, recommended 10-30 seconds',
        '范围：1-100 次，设置为 0 表示持续轮询': 'Range: 1-100, set to 0 for continuous polling',
        '范围：60-3600 秒，默认 600 秒（10 分钟）': 'Range: 60-3600 seconds, default 600 seconds (10 minutes)',
        '开启后自动检查当前账号是否有新邮件': 'When enabled, automatically check whether the current account has new emails',
        '全局生效，覆盖普通邮箱和临时邮箱；仅从启用后新到达的邮件开始通知。': 'Applies globally to regular and temp mailboxes. Only newly arrived emails after enabling will trigger notifications.',
        '只需填写接收邮箱，不暴露复杂邮件网关配置。关闭通知后可保留该邮箱。': 'Only the recipient email is required. The address can be retained after notifications are disabled.',
        '按“先保存，再测试”处理；成功语义为“请求已提交，请检查收件箱”。': 'Follow the save-then-test flow. Success means the request was accepted. Please check your inbox.',
        '格式：1234567890:AAxxxxxx（留空则禁用推送）': 'Format: 1234567890:AAxxxxxx (leave blank to disable notifications)',
        '可用 @userinfobot 获取你的 Chat ID': 'Use @userinfobot to get your Chat ID',
        '验证 Bot Token 和 Chat ID 是否配置正确': 'Verify that the Bot Token and Chat ID are configured correctly',
        '用于临时邮箱功能，可从': 'Used for the temp mailbox feature. You can get it from',
        '勾选后，新导入的 Outlook/IMAP 账号会以 `available` 状态进入邮箱池；不勾选则保持池外。': 'When checked, newly imported Outlook/IMAP accounts enter the mailbox pool with `available` status. Otherwise, they remain outside the pool.',
        '获取': 'get',
        '生成临时邮箱': 'Created temp mailbox',
        '用于按调用方维护多个 Key、邮箱范围授权和启停状态。保留已有脱敏 api_key 表示不修改该 Key；清空后保存表示清空全部多 Key。': 'Use this to maintain multiple keys, mailbox scopes, and enabled states by caller. Keeping a masked api_key means it will not be changed; saving an empty value clears all multi-key entries.',
        '关闭时（默认）仅做 API Key 鉴权；开启后额外启用 IP 白名单、限流、高风险端点禁用等安全策略。': 'When disabled (default), only API key authentication is applied. When enabled, IP allowlists, rate limits, and risky endpoint restrictions are also enforced.',
        '每个 IP 每分钟最大请求数（默认 60）。': 'Maximum requests per IP per minute (default 60).',
        '公网模式下建议禁用，防止泄露完整邮件原文。': 'Recommended in public mode to avoid exposing full raw email content.',
        '公网模式下建议禁用，防止长连接资源耗尽（Slowloris 风险）。': 'Recommended in public mode to avoid exhausting long-connection resources (Slowloris risk).',
        '建议设置为 30 天，防止 Token 因 90 天不使用而过期': 'Recommended: 30 days to prevent token expiration after 90 days of inactivity.',
        '建议设置为 5-10 秒，避免频繁请求触发 API 限流': 'Recommended: 5-10 seconds to avoid triggering API rate limits with frequent requests.',
        '输入新密码（留空则不修改）': 'Enter a new password (leave blank to keep unchanged)',
        '输入 GPTMail API Key': 'Enter the GPTMail API key',
        '用于 /api/external/* 的 X-API-Key': 'Used as the X-API-Key for /api/external/*',
        '用于对外开放接口鉴权（请求头：X-API-Key）。如需禁用对外开放接口，可清空后保存。': 'Used to authorize external APIs with the X-API-Key header. Clear it and save to disable external APIs.',
        '每行一个 IP 或 CIDR，如 192.168.1.0/24': 'One IP or CIDR per line, for example 192.168.1.0/24',
        '支持精确 IP 和 CIDR 格式。每行一个，保存时自动转为 JSON 数组。': 'Supports exact IPs and CIDR notation. One per line, automatically saved as a JSON array.',
        '输入 Bot Token': 'Enter the bot token',
        '输入 Chat ID': 'Enter the chat ID',
        'http://host:port 或 socks5://user:pass@host:port': 'http://host:port or socks5://user:pass@host:port',
        '授权成功后，浏览器会跳转到一个空白页，请复制地址栏中的完整 URL 并粘贴到这里': 'After authorization succeeds, the browser will open a blank page. Copy the full URL from the address bar and paste it here.',
        '确定要刷新所有账号的 Token 吗？': 'Refresh tokens for all accounts?',
        '确定要删除这个标签吗？': 'Delete this tag?',
        '刷新失败': 'Refresh Failed',
        '前往刷新日志查看详情': 'Open refresh logs for details',
        '解决建议': 'Suggestions',
        '关闭': 'Close',
        '邮件详情': 'Email Details',
        '错误详情': 'Error Details',
        '❌ 错误详情': '❌ Error Details',
        '错误信息 (用户友好)': 'Error Message',
        '技术详情': 'Technical Details',
        '【用户错误信息】': '[User Error Message]',
        '【错误详情】': '[Error Details]',
        '【技术堆栈/细节】': '[Technical Details]',
        '显示堆栈/细节': 'Show Details',
        '隐藏堆栈/细节': 'Hide Details',
        '复制全部': 'Copy All',
        '📋 复制全部': '📋 Copy All',
        '错误代码/类型': 'Error Code / Type',
        '无详细错误信息': 'No detailed error information',
        '错误代码:': 'Error Code:',
        '获取邮件失败': 'Failed to Fetch Emails',
        '所有获取方式均失败，以下是各方式的失败原因：': 'All fetch methods failed. See the reason for each method below:',
        '恢复默认布局': 'Reset Layout',
        '确定要恢复到默认布局吗？': 'Reset the layout to default?',
        '当前的面板宽度和折叠状态将被重置。': 'Current panel widths and collapse states will be reset.',
        '取消': 'Cancel',
        '确定': 'Confirm',
        '邮箱地址已复制': 'Email address copied',
        '复制失败，请手动复制': 'Copy failed. Please copy it manually.',
        '正在删除...': 'Deleting...',
        '网络错误': 'Network error',
        '请先选择一个邮箱账号': 'Please select an email account first',
        '请先选择一个邮箱账号': 'Please select an email account first',
        '确认退出登录？': 'Confirm logout?',
        '确定要退出登录吗？': 'Confirm logout?',
        '刷新已停止': 'Refresh stopped',
        '加载更多…': 'Loading more...',
        '没有更多邮件了': 'No more emails',
        '加载中...': 'Loading...',
        '加载失败': 'Load failed',
        '加载分组失败': 'Failed to load groups',
        '加载账号信息失败': 'Failed to load account details',
        '加载分组信息失败': 'Failed to load group details',
        '点击按钮生成': 'Click the button to create one',
        '获取中...': 'Fetching...',
        '获取中…': 'Fetching...',
        '点击查看详情': 'View details',
        '获取邮件失败，': 'Failed to fetch emails, ',
        '错误详情已复制': 'Error details copied',
        '暂无详细技术堆栈信息': 'No technical details available',
        '表达式有效': 'Expression is valid',
        '下次执行:': 'Next run:',
        '验证失败:': 'Validation failed:',
        '暂无标签': 'No tags yet',
        '[详情]': '[Details]',
        '获取授权链接失败': 'Failed to get authorization URL',
        '授权链接已复制到剪贴板': 'Authorization URL copied to clipboard',
        '已在新窗口打开授权页面': 'Authorization page opened in a new window',
        '请先粘贴授权后的完整 URL': 'Please paste the full redirected URL first',
        '✅ Token 获取成功！请将邮箱和密码替换后点导入': 'Token received. Replace the email and password, then import.',
        '换取 Token': 'Exchange Token',
        '⏳ 换取中...': '⏳ Exchanging...',
        '加载设置失败': 'Failed to load settings',
        '多 Key 配置必须是合法 JSON': 'Multiple API keys must be valid JSON',
        '多 Key 配置必须是 JSON 数组': 'Multiple API keys must be a JSON array',
        '多 Key 配置格式无效': 'Invalid multiple API keys format',
        '刷新周期必须在 1-90 天之间': 'Refresh interval must be between 1 and 90 days',
        '刷新间隔必须在 0-60 秒之间': 'Refresh delay must be between 0 and 60 seconds',
        '请输入 Cron 表达式': 'Please enter a cron expression',
        '轮询间隔必须在 5-300 秒之间': 'Polling interval must be between 5 and 300 seconds',
        '轮询次数必须在 0-100 次之间（0 表示持续轮询）': 'Polling count must be between 0 and 100 (0 means continuous polling)',
        'Telegram 轮询间隔必须在 60-3600 秒之间': 'Telegram polling interval must be between 60 and 3600 seconds',
        '设置已保存，重启应用后生效': 'Settings saved successfully',
        '保存设置失败': 'Failed to save settings',
        '已停止轮询': 'Polling stopped',
        '轮询连续失败，已自动停止': 'Polling stopped automatically after repeated failures',
        '没有需要重试的失败账号': 'There are no failed accounts to retry',
        '刷新过程中出现错误': 'An error occurred during refresh',
        '刷新请求失败': 'Refresh request failed',
        '重试请求失败': 'Retry request failed',
        '加载失败邮箱列表失败': 'Failed to load failed accounts',
        '加载刷新历史失败': 'Failed to load refresh history',
        '请选择要删除的账号': 'Please select the accounts to delete',
        '请选择标签': 'Please select a tag',
        '请选择标签...': 'Please select a tag...',
        '请选择分组...': 'Please select a group...',
        '请选择要导出的分组': 'Please select the groups to export',
        '请求失败': 'Request failed',
        '加载标签失败': 'Failed to load tags',
        '请输入标签名称': 'Please enter a tag name',
        '标签创建成功': 'Tag created successfully',
        '创建失败': 'Create failed',
        '创建标签失败': 'Failed to create tag',
        '标签已删除': 'Tag deleted',
        '删除失败': 'Delete failed',
        '操作失败': 'Operation failed',
        '删除标签失败': 'Failed to delete tag',
        '请选择目标分组': 'Please select a target group',
        '暂无分组': 'No groups yet',
        '暂无刷新记录': 'No refresh records yet',
        '暂无': 'N/A',
        '点击"获取邮件"按钮获取邮件': 'Click "Fetch Emails" to load messages',
        '点击"获取邮件"按钮获取收件箱': 'Click "Fetch Emails" to load inbox messages',
        '点击"获取邮件"按钮获取垃圾邮件': 'Click "Fetch Emails" to load junk email messages',
        '导出成功': 'Export completed',
        '导出失败': 'Export failed',
        '请输入密码': 'Please enter your password',
        '密码错误': 'Invalid password',
        '邮件已清空': 'Messages cleared',
        '临时邮箱已删除': 'Temp mailbox deleted',
        'telegram_push_开启': 'Telegram notifications enabled',
        'telegram_push_关闭': 'Telegram notifications disabled',
        '清空失败': 'Failed to clear',
        '删除账号失败': 'Failed to delete account',
        '添加失败': 'Failed to add',
        '更新失败': 'Update failed',
        '删除成功': 'Deleted successfully',
        '启用成功': 'Enabled successfully',
        '停用成功': 'Disabled successfully',
        '停用账号失败': 'Failed to disable account',
        '启用账号失败': 'Failed to enable account',
        '导入后加入邮箱池': 'Add to mailbox pool after import',
        '邮箱地址不能为空': 'Email address cannot be empty',
        '邮箱、Client ID 和 Refresh Token 不能为空': 'Email, Client ID, and Refresh Token are required',
        '请填写 IMAP 服务器地址（或在文本中每行包含 host/port）': 'Please enter the IMAP host, or provide host/port in each line',
        '请输入账号信息': 'Please enter account information',
        '请输入密码': 'Please enter your password',
        '导出邮箱': 'Export Mailboxes',
        '正在生成临时邮箱…': 'Creating temp mailbox...',
        '生成临时邮箱失败': 'Failed to create temp mailbox',
        '邮件正文为空，无法提取': 'The email body is empty and cannot be extracted',
        '未找到验证码或链接': 'No verification code or link was found',
        '提取失败，请手动查看': 'Extraction failed. Please inspect the email manually',
        '⚡ 临时邮箱': '⚡ Temp mailbox',
        '安全验证': 'Security Verification',
        '前往设置页面': 'Open Settings Page',
        '设置已迁移到独立页面': 'Settings moved to a dedicated page',
        '新建标签': 'Create Tag',
        '已有标签': 'Existing Tags',
        '批量打标': 'Bulk Tag',
        '批量添加标签': 'Bulk Add Tags',
        '批量移除标签': 'Bulk Remove Tags',
        '移动到分组': 'Move to Group',
        '选择目标分组': 'Select Target Group',
        '重试': 'Retry',
        '重试中...': 'Retrying...',
        '正在重试失败的账号...': 'Retrying failed accounts...',
        '隐藏列表': 'Hide List',
        '显示列表': 'Show List',
        '轮询中': 'Polling',
        '是否停止轮询？': 'Stop polling?',
        '刷新中...': 'Refreshing...',
        '正在初始化...': 'Initializing...',
        '总共': 'Total',
        '个账号': 'accounts',
        '准备开始刷新...': 'ready to start refreshing...',
        '正在处理': 'Processing',
        '进度': 'Progress',
        '等待': 'Waiting',
        '秒后继续...': 'seconds before continuing...',
        '请输入有效的十六进制颜色（如 #FF5500）': 'Please enter a valid hexadecimal color such as #FF5500',
        '换取 Token 失败': 'Failed to exchange token',
        '搜索中…': 'Searching...',
        '搜索失败': 'Search failed',
        '搜索失败，请重试': 'Search failed. Please try again.',
        '请选择要导出的分组': 'Please select the groups to export',
        '支持混合格式，每行一个账号...\nOutlook: 邮箱----密码----client_id----refresh_token\nIMAP: 邮箱----授权码----provider\n或: 邮箱----密码（自动识别类型）\nGPTMail: 仅邮箱地址': 'Mixed formats are supported, one account per line...\nOutlook: email----password----client_id----refresh_token\nIMAP: email----app-password----provider\nOr: email----password (auto-detect type)\nGPTMail: email only',
        '智能识别模式：自动按每行格式和邮箱域名判断类型，自动分组': 'Smart detection mode: identify account type by line format and email domain, then group automatically',
        '自动按类型分组': 'Group automatically by type',
        '格式：邮箱----密码----client_id----refresh_token，支持批量导入（每行一个）': 'Format: email----password----client_id----refresh_token, supports bulk import (one per line)',
        '格式：邮箱----IMAP授权码/应用密码（每行一个）。自定义 IMAP 需填写上方服务器/端口；也支持：邮箱----授权码----imap_host----imap_port': 'Format: email----IMAP app password (one per line). Custom IMAP also requires the server and port above, or use: email----password----imap_host----imap_port',
        '格式：邮箱----IMAP授权码/应用密码，支持批量导入（每行一个）': 'Format: email----IMAP app password, supports bulk import (one per line)',
        '邮箱----密码----client_id----refresh_token': 'email----password----client_id----refresh_token',
        '邮箱----IMAP授权码/应用密码': 'email----IMAP app password',
        '导入邮箱账号': 'Import Mail Accounts',
        '默认分组': 'Default Group',
        '🔑 注册': '🔑 Register',
        '🔑 获取 Token': '🔑 Get Token',
        '获取 Token': 'Get Token',
        '🔔 推送': '🔔 Notifications',
        '邮箱类型': 'Mailbox Type',
        '🔍 智能识别（混合导入）': '🔍 Smart Detection (Mixed Import)',
        'QQ邮箱': 'QQ Mail',
        'QQ 邮箱': 'QQ Mail',
        '163邮箱': '163 Mail',
        '163 邮箱': '163 Mail',
        '126邮箱': '126 Mail',
        '126 邮箱': '126 Mail',
        'Yahoo': 'Yahoo',
        'Yahoo 邮箱': 'Yahoo Mail',
        '阿里邮箱': 'Aliyun Mail',
        '阿里云邮箱': 'Aliyun Mail',
        '自定义 IMAP': 'Custom IMAP',
        '自定义IMAP': 'Custom IMAP',
        '提示：QQ/网易/Gmail 等请使用授权码/应用专用密码（非网页登录密码）': 'Tip: QQ, NetEase, Gmail and similar providers should use an app password instead of the website login password',
        '自定义 IMAP 配置': 'Custom IMAP Configuration',
        '仅自定义 IMAP 需要填写；端口通常为 993（SSL）': 'Only required for custom IMAP. The port is usually 993 (SSL)',
        '重复账号处理': 'Duplicate Account Handling',
        '跳过重复（已存在的账号保持不变）': 'Skip duplicates (keep existing accounts unchanged)',
        '覆盖更新（用导入数据更新已存在账号的凭据）': 'Overwrite duplicates (replace existing credentials with imported data)',
        '未知域名的 IMAP 设置（可选）': 'IMAP settings for unknown domains (optional)',
        '当邮箱域名无法自动识别时，使用此 IMAP 服务器地址': 'Use this IMAP server when the mailbox domain cannot be identified automatically',
        '账号信息': 'Account Information',
        '编辑邮箱账号': 'Edit Mail Account',
        '邮箱地址': 'Email Address',
        '授权码 / 应用密码': 'App Password',
        '留空则不修改': 'Leave blank to keep unchanged',
        '可选，留空则不修改': 'Optional, leave blank to keep unchanged',
        '所属分组': 'Group',
        '备注': 'Remark',
        '状态': 'Status',
        '正常': 'Active',
        '停用': 'Inactive',
        '分组名称': 'Group Name',
        '输入分组名称': 'Enter group name',
        '分组描述': 'Group Description',
        '可选': 'Optional',
        '分组颜色': 'Group Color',
        '自定义颜色': 'Custom Color',
        '代理设置': 'Proxy Settings',
        '可选，设置后该分组下所有邮箱获取邮件时走此代理（支持 HTTP/SOCKS5）': 'Optional. When set, all mail fetching in this group uses the proxy (HTTP/SOCKS5 supported)',
        '导出邮箱': 'Export Mailboxes',
        '选择要导出的分组': 'Select groups to export',
        '请输入登录密码以确认导出操作': 'Enter your login password to confirm export',
        '输入登录密码': 'Enter login password',
        '导出文件包含敏感信息（Refresh Token），请妥善保管': 'The export file contains sensitive information (Refresh Token). Keep it secure',
        '确认导出': 'Confirm Export',
        'Token 刷新管理': 'Token Refresh Manager',
        '🔄 Token 刷新管理': '🔄 Token Refresh Manager',
        '刷新统计': 'Refresh Summary',
        '上次全量刷新': 'Last full refresh',
        '总邮箱数': 'Total mailboxes',
        '成功邮箱': 'Successful mailboxes',
        '失败邮箱': 'Failed mailboxes',
        '全量刷新': 'Refresh All',
        '🔄 全量刷新': '🔄 Refresh All',
        '重试失败': 'Retry Failed',
        '🔁 重试失败': '🔁 Retry Failed',
        '失败邮箱': 'Failed Mailboxes',
        '刷新历史': 'Refresh History',
        '手动': 'Manual',
        '自动': 'Automatic',
        '定时': 'Scheduled',
        '正在刷新...': 'Refreshing...',
        '请稍候': 'Please wait',
        '当前失败状态的邮箱': 'Mailboxes currently in failed state',
        '隐藏': 'Hide',
        '全量刷新历史': 'Full Refresh History',
        '暂无失败状态的邮箱': 'No failed mailboxes',
        '请从左侧选择一个邮箱账号': 'Select an email account from the left',
        '选择一个临时邮箱查看邮件': 'Select a temp mailbox to view messages',
        '该分组暂无邮箱': 'No mailboxes in this group',
        '收件箱为空': 'Inbox is empty',
        '暂无邮件': 'No messages yet',
        '未知': 'Unknown',
        '未知错误': 'Unknown error',
        '未知发件人': 'Unknown sender',
        '有效': 'Valid',
        '过期': 'Expired',
        '即将过期': 'Expiring Soon',
        '推送': 'Notifications',
        '🔔 推送': '🔔 Notifications',
        '点击关闭推送': 'Click to disable notifications',
        '点击复制': 'Click to copy',
        '暂无审计记录': 'No audit logs yet',
        '加载审计日志失败': 'Failed to load audit logs',
        '标签名称': 'Tag Name',
        '添加': 'Add',
        '移动到分组': 'Move to Group',
        '确定要删除该分组吗？分组下的邮箱将移至默认分组。': 'Delete this group? Accounts in the group will be moved to the default group.',
        '请输入分组名称': 'Please enter a group name',
        '保存失败': 'Save failed',
        '加载失败邮箱列表失败': 'Failed to load failed mailbox list',
        '暂无全量刷新历史': 'No full refresh history yet',
        '近半年刷新历史（共': 'Refresh history for the last six months (total ',
        '查看错误': 'View error',
        '点击关闭推送': 'Click to disable notifications',
        '移动到分组': 'Move to Group',
        '未设置（设置后可通过 /api/external/* 对外开放接口读取邮件与验证码）': 'Not configured yet. After saving, /api/external/* can expose emails and verification codes.',
        '⚠️ 警告：启用信任模式将直接显示邮件原始内容，不进行任何安全过滤。\n\n这可能包含恶意脚本或不安全的内容。您确定要继续吗？': '⚠️ Warning: Trust mode shows the raw email content without any safety filtering.\n\nThis may include malicious scripts or unsafe content. Do you want to continue?'
    };

    const reverseMap = Object.fromEntries(
        Object.entries(exactMap).map(([zh, en]) => [en, zh])
    );

    const patterns = [
        { zh: /^已更新：(.+)$/, en: 'Updated: $1' },
        { zh: /^已设置：(.+)$/, en: 'Configured: $1' },
        { zh: /^共 (\d+) 个账号 · (\d+) 个 Token 有效$/, en: '$1 accounts · $2 valid tokens' },
        { zh: /^共 (\d+) 条记录$/, en: '$1 records total' },
        { zh: /^导入完成：成功 (\d+) 个，失败 (\d+) 个，目标分组ID=(\d+)$/, en: 'Import completed: $1 succeeded, $2 failed, target group ID=$3' },
        { zh: /^导入完成：成功 (\d+) 个，失败 (\d+) 个，目标分组ID=(\d+)，provider=(.+)$/, en: 'Import completed: $1 succeeded, $2 failed, target group ID=$3, provider=$4' },
        { zh: /^删除账号：(.+)$/, en: 'Deleted account: $1' },
        { zh: /^创建分组：(.+)$/, en: 'Created group: $1' },
        { zh: /^导出选中分组的 (\d+) 个账号 \+ (\d+) 个临时邮箱$/, en: 'Exported selected groups: $1 accounts + $2 temp mailboxes' },
        { zh: /^覆盖更新 email=(.+), provider=(.+)$/, en: 'Overwritten account: email=$1, provider=$2' },
        { zh: /^已选 (\d+) 项$/, en: '$1 selected' },
        { zh: /^已复制: (.+)$/, en: 'Copied: $1' },
        { zh: /^成功删除 (\d+) 封邮件$/, en: 'Deleted $1 emails' },
        { zh: /^部分删除失败 \((\d+) 封\)$/, en: 'Partial deletion failed ($1 emails)' },
        { zh: /^刷新完成！成功: (\d+), 失败: (\d+)$/, en: 'Refresh completed. Success: $1, Failed: $2' },
        { zh: /^重试完成！成功: (\d+), 失败: (\d+)$/, en: 'Retry completed. Success: $1, Failed: $2' },
        { zh: /^账号：(.+)$/, en: 'Account: $1' },
        { zh: /^临时邮箱已生成: (.+)$/, en: 'Temp mailbox created: $1' },
        { zh: /^(.+) \(临时\)$/, en: '$1 (Temp)' },
        { zh: /^当前已配置 (\d+) 个多 Key。保留已有脱敏 api_key 表示不修改该 Key；清空后保存表示清空全部多 Key。$/, en: '$1 API keys configured. Keeping a masked api_key leaves it unchanged; saving an empty value clears all multi-key entries.' },
        { zh: /^当前邮箱：(.+)$/, en: 'Current mailbox: $1' },
        { zh: /^搜索结果 \((\d+)\)$/, en: 'Search Results ($1)' },
        { zh: /^近半年刷新历史（共 (\d+) 条）$/, en: 'Refresh history for the last six months (total $1)' },
        { zh: /^确认删除账号 (.+)\?$/, en: 'Delete account $1?' },
        { zh: /^确定要删除账号 (.+) 吗？$/, en: 'Delete account $1?' },
        { zh: /^确定要删除临时邮箱 (.+) 吗？\n该邮箱的所有邮件也将被删除。$/, en: 'Delete temp mailbox $1?\nAll messages in this mailbox will also be deleted.' },
        { zh: /^确定要清空临时邮箱 (.+) 的所有邮件吗？$/, en: 'Clear all messages in temp mailbox $1?' },
        { zh: /^确定要永久删除选中的 (\d+) 封邮件吗？此操作不可恢复！$/, en: 'Permanently delete $1 selected emails? This action cannot be undone.' },
        { zh: /^确定要永久删除这封邮件吗？此操作不可恢复！$/, en: 'Permanently delete this email? This action cannot be undone.' },
        { zh: /^确定要删除选中的 (\d+) 个账号吗？此操作不可恢复！$/, en: 'Delete $1 selected accounts? This action cannot be undone.' },
        { zh: /^📬 (.+): (.+) 等 (\d+) 封新邮件$/, en: '📬 $1: $2 and $3 new emails' },
        { zh: /^📬 (.+): (.+)$/, en: '📬 $1: $2' },
        { zh: /^Telegram推送(已开启)?$/, en: 'Telegram Notifications$1' },
        { zh: /^(.+) 刷新成功$/, en: '$1 refreshed successfully' },
        { zh: /^(.+) 刷新失败$/, en: '$1 refresh failed' }
    ];

    const reversePatterns = [
        { en: /^Updated: (.+)$/, zh: '已更新：$1' },
        { en: /^Configured: (.+)$/, zh: '已设置：$1' },
        { en: /^(\d+) accounts · (\d+) valid tokens$/, zh: '共 $1 个账号 · $2 个 Token 有效' },
        { en: /^(\d+) records total$/, zh: '共 $1 条记录' },
        { en: /^Import completed: (\d+) succeeded, (\d+) failed, target group ID=(\d+)$/, zh: '导入完成：成功 $1 个，失败 $2 个，目标分组ID=$3' },
        { en: /^Import completed: (\d+) succeeded, (\d+) failed, target group ID=(\d+), provider=(.+)$/, zh: '导入完成：成功 $1 个，失败 $2 个，目标分组ID=$3，provider=$4' },
        { en: /^Deleted account: (.+)$/, zh: '删除账号：$1' },
        { en: /^Created group: (.+)$/, zh: '创建分组：$1' },
        { en: /^Exported selected groups: (\d+) accounts \+ (\d+) temp mailboxes$/, zh: '导出选中分组的 $1 个账号 + $2 个临时邮箱' },
        { en: /^Overwritten account: email=(.+), provider=(.+)$/, zh: '覆盖更新 email=$1, provider=$2' },
        { en: /^(\d+) selected$/, zh: '已选 $1 项' },
        { en: /^Copied: (.+)$/, zh: '已复制: $1' },
        { en: /^Deleted (\d+) emails$/, zh: '成功删除 $1 封邮件' },
        { en: /^Partial deletion failed \((\d+) emails\)$/, zh: '部分删除失败 ($1 封)' },
        { en: /^Refresh completed\. Success: (\d+), Failed: (\d+)$/, zh: '刷新完成！成功: $1, 失败: $2' },
        { en: /^Retry completed\. Success: (\d+), Failed: (\d+)$/, zh: '重试完成！成功: $1, 失败: $2' },
        { en: /^Account: (.+)$/, zh: '账号：$1' },
        { en: /^Temp mailbox created: (.+)$/, zh: '临时邮箱已生成: $1' },
        { en: /^(.+) \(Temp\)$/, zh: '$1 (临时)' },
        { en: /^(\d+) API keys configured\. Keeping a masked api_key leaves it unchanged; saving an empty value clears all multi-key entries\.$/, zh: '当前已配置 $1 个多 Key。保留已有脱敏 api_key 表示不修改该 Key；清空后保存表示清空全部多 Key。' },
        { en: /^Current mailbox: (.+)$/, zh: '当前邮箱：$1' },
        { en: /^Search Results \((\d+)\)$/, zh: '搜索结果 ($1)' },
        { en: /^Refresh history for the last six months \(total (\d+)\)$/, zh: '近半年刷新历史（共 $1 条）' },
        { en: /^Delete account (.+)\?$/, zh: '确定要删除账号 $1 吗？' },
        { en: /^Delete temp mailbox (.+)\?\nAll messages in this mailbox will also be deleted\.$/, zh: '确定要删除临时邮箱 $1 吗？\n该邮箱的所有邮件也将被删除。' },
        { en: /^Clear all messages in temp mailbox (.+)\?$/, zh: '确定要清空临时邮箱 $1 的所有邮件吗？' },
        { en: /^Permanently delete (\d+) selected emails\? This action cannot be undone\.$/, zh: '确定要永久删除选中的 $1 封邮件吗？此操作不可恢复！' },
        { en: /^Permanently delete this email\? This action cannot be undone\.$/, zh: '确定要永久删除这封邮件吗？此操作不可恢复！' },
        { en: /^Delete (\d+) selected accounts\? This action cannot be undone\.$/, zh: '确定要删除选中的 $1 个账号吗？此操作不可恢复！' },
        { en: /^📬 (.+): (.+) and (\d+) new emails$/, zh: '📬 $1: $2 等 $3 封新邮件' },
        { en: /^📬 (.+): (.+)$/, zh: '📬 $1: $2' },
        { en: /^Telegram Notifications(\(已开启\))?$/, zh: 'Telegram推送$1' },
        { en: /^(.+) refreshed successfully$/, zh: '$1 刷新成功' },
        { en: /^(.+) refresh failed$/, zh: '$1 刷新失败' }
    ];

    function getLanguage() {
        return localStorage.getItem(STORAGE_KEY) || 'zh';
    }

    function setLanguage(language) {
        localStorage.setItem(STORAGE_KEY, language === 'en' ? 'en' : 'zh');
        applyLanguage();
    }

    function translateByPattern(text, items, targetKey) {
        for (const item of items) {
            const sourcePattern = targetKey === 'en' ? item.zh : item.en;
            const targetTemplate = targetKey === 'en' ? item.en : item.zh;
            if (!sourcePattern || !sourcePattern.test(text)) {
                continue;
            }
            return text.replace(sourcePattern, targetTemplate);
        }
        return text;
    }

    function translateAppText(text, language) {
        if (typeof text !== 'string' || !text) {
            return text;
        }
        const lang = language || getLanguage();
        const leading = text.match(/^\s*/)?.[0] || '';
        const trailing = text.match(/\s*$/)?.[0] || '';
        const core = text.trim();
        if (!core) {
            return text;
        }
        if (lang === 'en') {
            const translated = exactMap[core] || translateByPattern(core, patterns, 'en');
            return translated ? `${leading}${translated}${trailing}` : text;
        }
        const translated = reverseMap[core] || translateByPattern(core, reversePatterns, 'zh');
        return translated ? `${leading}${translated}${trailing}` : text;
    }

    function translateAttribute(element, attrName) {
        const value = element.getAttribute(attrName);
        if (!value) {
            return;
        }
        const translated = translateAppText(value);
        if (translated !== value) {
            element.setAttribute(attrName, translated);
        }
    }

    function translateNode(root) {
        if (!root) {
            return;
        }

        if (root.nodeType === Node.TEXT_NODE) {
            const value = root.nodeValue;
            if (value && value.trim()) {
                const translated = translateAppText(value);
                if (translated !== value) {
                    root.nodeValue = translated;
                }
            }
            return;
        }

        if (root.nodeType !== Node.ELEMENT_NODE) {
            return;
        }

        translateAttribute(root, 'placeholder');
        translateAttribute(root, 'title');
        translateAttribute(root, 'aria-label');
        if (root.tagName === 'INPUT' && root.type === 'button' && root.value) {
            const translatedValue = translateAppText(root.value);
            if (translatedValue !== root.value) {
                root.value = translatedValue;
            }
        }
        root.querySelectorAll('[placeholder],[title],[aria-label],input[type="button"][value]').forEach((element) => {
            translateAttribute(element, 'placeholder');
            translateAttribute(element, 'title');
            translateAttribute(element, 'aria-label');
            if (element.tagName === 'INPUT' && element.type === 'button' && element.value) {
                const translatedValue = translateAppText(element.value);
                if (translatedValue !== element.value) {
                    element.value = translatedValue;
                }
            }
        });

        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
        const textNodes = [];
        while (walker.nextNode()) {
            textNodes.push(walker.currentNode);
        }
        textNodes.forEach((node) => {
            if (!node.parentElement || ['SCRIPT', 'STYLE'].includes(node.parentElement.tagName)) {
                return;
            }
            if (node.nodeValue && node.nodeValue.trim()) {
                const translated = translateAppText(node.nodeValue);
                if (translated !== node.nodeValue) {
                    node.nodeValue = translated;
                }
            }
        });
    }

    function updateSwitcherState() {
        document.querySelectorAll('[data-ui-language]').forEach((button) => {
            const active = button.getAttribute('data-ui-language') === getLanguage();
            button.classList.toggle('active', active);
        });
    }

    function injectSwitcher() {
        if (document.getElementById('globalLanguageSwitcher')) {
            updateSwitcherState();
            return;
        }

        const style = document.createElement('style');
        style.textContent = `
            #globalLanguageSwitcher {
                display: inline-flex;
                gap: 4px;
                padding: 4px;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.92);
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
                border: 1px solid rgba(15, 23, 42, 0.08);
                backdrop-filter: blur(8px);
            }
            #globalLanguageSwitcher.switcher-floating {
                position: fixed;
                top: 16px;
                right: 16px;
                z-index: 3000;
            }
            #globalLanguageSwitcher.switcher-docked {
                width: 100%;
                margin-top: 0.4rem;
                justify-content: center;
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.1);
                box-shadow: none;
                backdrop-filter: none;
            }
            #globalLanguageSwitcher button {
                border: none;
                background: transparent;
                color: #334155;
                border-radius: 999px;
                padding: 6px 10px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 600;
            }
            #globalLanguageSwitcher.switcher-docked button {
                flex: 1;
                min-width: 0;
                color: rgba(250,235,215,0.72);
            }
            #globalLanguageSwitcher button.active {
                background: #0f172a;
                color: #fff;
            }
            #globalLanguageSwitcher.switcher-docked button.active {
                background: rgba(184,92,56,0.9);
            }
            .sidebar-collapsed #globalLanguageSwitcher.switcher-docked {
                padding: 3px;
                gap: 3px;
                border-radius: 16px;
            }
            .sidebar-collapsed #globalLanguageSwitcher.switcher-docked button {
                padding: 6px 0;
                font-size: 11px;
                line-height: 1;
            }
            @media (max-width: 768px) {
                #globalLanguageSwitcher.switcher-docked {
                    position: fixed;
                    top: auto;
                    right: 12px;
                    bottom: 12px;
                    width: auto;
                    margin-top: 0;
                    z-index: 3000;
                    background: rgba(255, 255, 255, 0.92);
                    border: 1px solid rgba(15, 23, 42, 0.08);
                    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
                    backdrop-filter: blur(8px);
                }
                #globalLanguageSwitcher.switcher-docked button {
                    flex: initial;
                    color: #334155;
                }
                #globalLanguageSwitcher.switcher-docked button.active {
                    background: #0f172a;
                }
            }
        `;
        document.head.appendChild(style);

        const container = document.createElement('div');
        container.id = 'globalLanguageSwitcher';
        container.innerHTML = `
            <button type="button" data-ui-language="zh" title="中文">中</button>
            <button type="button" data-ui-language="en" title="English">EN</button>
        `;
        container.addEventListener('click', (event) => {
            const button = event.target.closest('[data-ui-language]');
            if (!button) {
                return;
            }
            setLanguage(button.getAttribute('data-ui-language'));
        });

        const dockTarget = document.querySelector('.sidebar-bottom');
        if (dockTarget) {
            container.classList.add('switcher-docked');
            dockTarget.appendChild(container);
        } else {
            container.classList.add('switcher-floating');
            document.body.appendChild(container);
        }
        updateSwitcherState();
    }

    function applyLanguage() {
        document.documentElement.lang = getLanguage() === 'en' ? 'en' : 'zh-CN';
        if (document.title) {
            document.title = translateAppText(document.title);
        }
        translateNode(document.body);
        updateSwitcherState();
    }

    function observeMutations() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => translateNode(node));
                    return;
                }
                if (mutation.type === 'characterData') {
                    translateNode(mutation.target);
                    return;
                }
                if (mutation.type === 'attributes' && mutation.target) {
                    if (mutation.attributeName === 'value' && mutation.target.tagName === 'INPUT' && mutation.target.type === 'button') {
                        const translatedValue = translateAppText(mutation.target.value);
                        if (translatedValue !== mutation.target.value) {
                            mutation.target.value = translatedValue;
                        }
                    } else if (mutation.attributeName) {
                        translateAttribute(mutation.target, mutation.attributeName);
                    }
                }
            });
        });
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true,
            attributes: true,
            attributeFilter: ['placeholder', 'title', 'aria-label', 'value']
        });
    }

    const nativeConfirm = window.confirm.bind(window);
    window.confirm = function (message) {
        return nativeConfirm(translateAppText(message));
    };

    window.getCurrentUiLanguage = getLanguage;
    window.setUiLanguage = setLanguage;
    window.translateAppText = translateAppText;
    window.pickApiMessage = function (payload, fallbackZh, fallbackEn) {
        const lang = getLanguage();
        if (lang === 'en') {
            return (payload && payload.message_en) || fallbackEn || fallbackZh || '';
        }
        return (payload && payload.message) || fallbackZh || fallbackEn || '';
    };
    window.resolveApiErrorMessage = function (error, fallbackZh, fallbackEn) {
        if (!error || typeof error !== 'object') {
            return translateAppText(fallbackZh || fallbackEn || '请求失败');
        }
        return window.pickApiMessage(error, fallbackZh || error.message, fallbackEn || error.message_en);
    };
    window.formatUiDateTime = function (dateStr, options = {}) {
        const fallback = options.fallback || dateStr || '';
        if (!dateStr) {
            return fallback;
        }
        let date = dateStr instanceof Date ? dateStr : null;
        if (!(date instanceof Date)) {
            let normalized = dateStr;
            if (typeof normalized === 'string' && !normalized.includes('T') && /^\d{4}-\d{2}-\d{2}$/.test(normalized)) {
                normalized += 'T00:00:00Z';
            } else if (typeof normalized === 'string' && !normalized.includes('Z') && !/[+-]\d{2}:?\d{2}$/.test(normalized)) {
                normalized += 'Z';
            }
            date = new Date(normalized);
        }
        if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
            return fallback;
        }
        const locale = getLanguage() === 'en' ? 'en-US' : 'zh-CN';
        const formatter = new Intl.DateTimeFormat(locale, {
            year: 'numeric',
            month: options.longMonth ? 'long' : '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: options.includeSeconds ? '2-digit' : undefined,
            hour12: false
        });
        return formatter.format(date);
    };
    window.formatUiRelativeTime = function (dateStr, fallbackZh = '从未刷新', fallbackEn = 'Never refreshed') {
        if (!dateStr) {
            return getLanguage() === 'en' ? fallbackEn : fallbackZh;
        }
        let normalized = dateStr;
        if (typeof normalized === 'string' && !normalized.includes('Z') && !/[+-]\d{2}:?\d{2}$/.test(normalized)) {
            normalized += 'Z';
        }
        const date = new Date(normalized);
        if (Number.isNaN(date.getTime())) {
            return getLanguage() === 'en' ? fallbackEn : fallbackZh;
        }
        const diffMs = Date.now() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        if (getLanguage() === 'en') {
            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins} minutes ago`;
            if (diffHours < 24) return `${diffHours} hours ago`;
            if (diffDays < 30) return `${diffDays} days ago`;
            return `${Math.floor(diffDays / 30)} months ago`;
        }
        if (diffMins < 1) return '刚刚';
        if (diffMins < 60) return `${diffMins} 分钟前`;
        if (diffHours < 24) return `${diffHours} 小时前`;
        if (diffDays < 30) return `${diffDays} 天前`;
        return `${Math.floor(diffDays / 30)} 月前`;
    };

    document.addEventListener('DOMContentLoaded', () => {
        injectSwitcher();
        applyLanguage();
        observeMutations();
    });
})();
