# Outlook Email Plus

> 一个功能完整的 Outlook 邮件管理解决方案，支持多账号管理、多种邮件读取方式和现代化 Web 界面。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://hub.docker.com/r/guangshanshui/outlook-email-plus)

## ✨ 核心特性

- 🔐 **多账号管理** - 支持批量导入和管理多个 Outlook 邮箱账号
- 📁 **分组管理** - 自定义分组，支持分组级别代理设置
- 📧 **多种读取方式** - Graph API / IMAP(新) / IMAP(旧) 自动回退
- 🔄 **Token 自动刷新** - 支持定时刷新，防止 90 天过期
- 🏷️ **标签系统** - 为邮箱打标签，支持筛选和批量操作
- 🔍 **全局搜索** - 快速搜索邮箱和邮件
- 🌐 **代理支持** - 分组级别 HTTP/SOCKS5 代理配置
- 🔒 **安全加密** - 敏感数据加密存储，CSRF 防护，登录速率限制
- 🎨 **现代化 UI** - 四栏式界面，响应式设计
- 🐳 **Docker 部署** - 一键部署，开箱即用

## 📸 界面预览

> 四栏式布局：分组面板 | 邮箱列表 | 邮件列表 | 邮件详情

```
┌─────────────┬──────────────┬──────────────┬──────────────┐
│   分组管理   │   邮箱账号    │   邮件列表    │   邮件详情    │
│             │              │              │              │
│ 📁 默认分组  │ 📧 账号1     │ ✉️ 邮件1     │ 📄 邮件内容   │
│ 📁 工作邮箱  │ 📧 账号2     │ ✉️ 邮件2     │              │
│ 📁 个人邮箱  │ 📧 账号3     │ ✉️ 邮件3     │              │
│             │              │              │              │
└─────────────┴──────────────┴──────────────┴──────────────┘
```

### 仪表盘
![仪表盘](img/仪表盘.png)

### 邮箱管理界面
![邮箱界面](img/邮箱界面.png)

### 验证码提取功能
![提取验证码](img/提取验证码.png)

### 系统设置
![设置界面](img/设置界面.png)

## 🚀 快速开始

### 使用 Docker（推荐）

```bash
# 拉取镜像
docker pull guangshanshui/outlook-email-plus:latest

# 运行容器
docker run -d \
  --name outlook-email-plus \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e LOGIN_PASSWORD=admin123 \
  -e SECRET_KEY=your-secret-key-here \
  guangshanshui/outlook-email-plus:latest

# 访问应用
# 浏览器打开 http://localhost:5000
```

### 使用 Docker Compose

```yaml
version: '3.8'

services:
  outlook-email-plus:
    image: guangshanshui/outlook-email-plus:latest
    container_name: outlook-email-plus
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - LOGIN_PASSWORD=admin123
      - SECRET_KEY=your-secret-key-here
      - FLASK_ENV=production
    restart: unless-stopped
```

```bash
docker-compose up -d
```

### 本地运行

```bash
# 克隆仓库
git clone https://github.com/ZeroPointSix/outlookEmailPlus.git
cd outlookEmailPlus

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export LOGIN_PASSWORD=admin123
export SECRET_KEY=your-secret-key-here

# 运行应用
python web_outlook_app.py
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Session 密钥（必须设置） | 无 |
| `LOGIN_PASSWORD` | 登录密码 | `admin123` |
| `PORT` | 应用端口 | `5000` |
| `HOST` | 监听地址 | `0.0.0.0` |
| `FLASK_ENV` | 运行环境 | `production` |
| `DATABASE_PATH` | 数据库路径 | `data/outlook_accounts.db` |

**生成 SECRET_KEY：**
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

## 📖 使用说明

### 1. 获取 OAuth2 凭证

访问 [Azure Portal](https://portal.azure.com/) 注册应用：

1. 进入「应用注册」→「新注册」
2. 填写应用名称，选择「任何组织目录中的账户和个人 Microsoft 账户」
3. 重定向 URI 选择「公共客户端/本机」，填写 `http://localhost:8080`
4. 复制「应用程序(客户端) ID」
5. 使用本工具内置的 OAuth2 助手获取 Refresh Token

### 2. 导入邮箱账号

格式：`邮箱----密码----client_id----refresh_token`

```
user@outlook.com----password123----24d9a0ed-xxxx----0.AXEA...
```

支持批量导入，每行一个账号。

### 3. 查看邮件

1. 选择分组和邮箱
2. 点击「获取邮件」
3. 切换文件夹（收件箱/垃圾邮件/已删除）
4. 点击邮件查看详情

### 4. Token 刷新管理

- **全量刷新** - 一键刷新所有账号 Token
- **定时刷新** - 支持按天数或 Cron 表达式配置
- **失败重试** - 查看失败原因并重试

建议每 30 天刷新一次，防止 Token 过期。

## 🔐 安全特性

- ✅ 敏感数据加密存储（Fernet + bcrypt）
- ✅ CSRF 防护（Flask-WTF）
- ✅ XSS 防护（DOMPurify + iframe 沙箱）
- ✅ 登录速率限制（5 次失败锁定 15 分钟）
- ✅ 导出功能二次验证
- ✅ 审计日志记录

## 🛠️ 技术栈

**后端：**
- Flask 3.0+ - Web 框架
- SQLite 3 - 数据库
- Microsoft Graph API - Outlook 邮件 API
- APScheduler - 定时任务

**前端：**
- 原生 JavaScript - 无框架依赖
- CSS3 - 现代化样式
- DOMPurify - XSS 防护

## 📦 项目结构

```
outlookEmailPlus/
├── outlook_web/          # 后端源代码
│   ├── app.py           # Flask 应用入口
│   ├── routes/          # 路由模块
│   ├── services/        # 业务逻辑
│   ├── repositories/    # 数据访问
│   └── security/        # 安全模块
├── static/              # 前端资源
│   ├── css/
│   └── js/
├── templates/           # HTML 模板
├── web_outlook_app.py   # 应用入口
├── requirements.txt     # Python 依赖
├── Dockerfile           # Docker 构建
└── README.md
```

## 🔄 更新应用

```bash
# 拉取最新镜像
docker pull guangshanshui/outlook-email-plus:latest

# 重启容器
docker-compose down
docker-compose up -d
```

## ❓ 常见问题

**Q: 无法获取邮件？**
A: 检查 Refresh Token 是否有效，Client ID 是否正确，API 权限是否配置。

**Q: 如何修改登录密码？**
A: 登录后点击「⚙️ 设置」在线修改，或通过环境变量 `LOGIN_PASSWORD` 设置。

**Q: 数据存储在哪里？**
A: SQLite 数据库位于 `data/outlook_accounts.db`，建议定期备份。

**Q: 支持哪些邮件文件夹？**
A: 收件箱、垃圾邮件、已删除邮件。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

- GitHub Issues: [https://github.com/ZeroPointSix/outlookEmailPlus/issues](https://github.com/ZeroPointSix/outlookEmailPlus/issues)

---

**⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！**
