# Readable Summary

<analysis>
1. 用户希望我先充分阅读整个项目的前端与后端代码，并在后续只接受命令式指令，所以我首先梳理了 README 以掌握项目简介与目录布局。
2. 之后深入查看了后端入口 `web_outlook_app.py` 及核心工厂 `outlook_web/app.py`，确认使用 Flask 工厂模式、Blueprint 注册、调度器控制与错误处理中间件的配置。
3. 为完成“前端代码”阅读要求，我又审阅了 `static/js/main.js`、`static/js/features/emails.js` 以及 `static/css/main.css`，了解状态管理、邮件渲染、主题切换等关键逻辑与配色体系。
</analysis>

<plan>
# Session Handoff Plan

## 1. Primary Request and Intent
- 浏览项目前后端代码，提前准备好接收命令式指令。当前需求尚未指定具体修改/功能，只需掌握项目结构与核心逻辑。

## 2. Key Technical Concepts
- Flask 应用工厂+Blueprint；
- 自定义中间件（Trace ID、异常捕获）与 CSRF 初始化；
- 定时任务调度自动启动逻辑；
- 前端全局状态管理、页面导航、邮件列表渲染、轮询/缓存；
- 自定义国风主题 CSS 变量与布局；
- API 依赖 `/api/*` 路径（groups, accounts, emails, temp-emails, settings）。

## 3. Files and Code Sections
### README.md
- **Why important**: 介绍技术栈、部署方式、项目结构和核心特性，确认后端模块位于 `outlook_web/`，前端资源在 `static/` 与 `templates/`。
- **Changes made**: 无修改，仅参考。

### outlook_web/app.py
- **Why important**: 提供 Flask 工厂实现并按需初始化数据库、CSRF、错误处理与 Blueprint。它是后端模块化的核心集成点。
- **Code snippet**:
```python
        app.register_blueprint(pages.create_blueprint(csrf_exempt=csrf_exempt))
        app.register_blueprint(groups.create_blueprint())
        app.register_blueprint(tags.create_blueprint())
        ...
        app.register_error_handler(Exception, handle_exception)
```

### web_outlook_app.py
- **Why important**: 兼容旧入口，导出常用 helper，控制调度器在 debug 自动重载下的启动，并保持 `app` 变量可用。

### static/js/main.js
- **Why important**: 管理主题、导航、不同页面的数据加载、登录/登出流程以及顶部操作栏，直接驱动 Web UI 页面切换。
- **Code snippet**:
```javascript
        function navigate(page) {
            currentPage = page;
            document.querySelectorAll('.page').forEach(p => p.classList.add('page-hidden'));
            const target = document.getElementById('page-' + page);
            if (target) target.classList.remove('page-hidden');
            if (page === 'mailbox') { ... }
        }
```

### static/js/features/emails.js
- **Why important**: 控制邮件列表与批量操作、根据方法（Graph/IMAP）缓存结果并在 UI 中显示详细错误信息。

### static/css/main.css
- **Why important**: 定义国风调色、深色模式变量、登录页、侧边栏与按钮样式，是前端主题与可访问性基础。

## 4. Problem Solving
- 通过多个工具（glob、view）逐步确认目录结构并读取关键文件，未遇到技术问题，仅需适当缩减超大文件的展示范围。

## 5. Pending Tasks
- 等待用户逐条下达命令；当前仅完成代码预览与总结。

## 6. Current Work
- 正在响应“充分阅读前后端代码”的要求，重点查看后端工厂/入口、静态 JS 管理逻辑与配色文件。

## 7. Optional Next Step
- 若下一步指令仍是“研究/阅读”类内容，可继续深入 controllers/services 或 templates；如需具体改动，则等待用户提供任务描述。
</plan>
