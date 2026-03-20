        // ==================== 临时邮箱相关 ====================

        // 复制临时邮箱页面顶栏当前邮箱地址
        function copyTempEmailCurrent() {
            const el = document.getElementById('tempEmailCurrentName');
            if (el && el.textContent && el.textContent !== '选择一个临时邮箱') {
                copyEmail(el.textContent.trim());
            }
        }

        // 加载临时邮箱列表
        async function loadTempEmails(forceRefresh = false) {
            const container = document.getElementById('accountList');
            const pageContainer = document.getElementById('tempEmailContainer');

            if (!forceRefresh && accountsCache['temp']) {
                renderTempEmailList(accountsCache['temp']);
                return;
            }

            const loadingHTML = `<div class="loading-overlay"><span class="spinner"></span> ${translateAppTextLocal('加载中…')}</div>`;
            if (container) container.innerHTML = loadingHTML;
            if (pageContainer) pageContainer.innerHTML = loadingHTML;

            try {
                const response = await fetch('/api/temp-emails');
                const data = await response.json();

                if (data.success) {
                    accountsCache['temp'] = data.emails;
                    renderTempEmailList(data.emails);

                    const group = groups.find(g => g.name === '临时邮箱');
                    if (group) {
                        group.account_count = data.emails.length;
                        renderGroupList(groups);
                    }
                }
            } catch (error) {
                const errHTML = `<div class="empty-state"><p>${translateAppTextLocal('加载失败')}</p></div>`;
                if (container) container.innerHTML = errHTML;
                if (pageContainer) pageContainer.innerHTML = errHTML;
            }
        }

        // 渲染临时邮箱列表
        function renderTempEmailList(emails) {
            const container = document.getElementById('accountList');
            const pageContainer = document.getElementById('tempEmailContainer');

            if (emails.length === 0) {
                const emptyAccountHTML = `
                    <div class="empty-state">
                        <span class="empty-icon">⚡</span>
                        <p>${translateAppTextLocal('暂无临时邮箱')}<br>${translateAppTextLocal('点击按钮生成')}</p>
                    </div>
                `;
                const emptyPageHTML = `
                    <div class="empty-state">
                        <span class="empty-icon">📭</span>
                        <p>${translateAppTextLocal('暂无临时邮箱')}</p>
                        <button class="btn btn-primary" onclick="generateTempEmail()">${translateAppTextLocal('创建第一个临时邮箱')}</button>
                    </div>
                `;
                if (container) container.innerHTML = emptyAccountHTML;
                if (pageContainer) pageContainer.innerHTML = emptyPageHTML;
                return;
            }

            const colors = ['var(--clr-accent)', 'var(--clr-jade)', 'var(--clr-primary)', '#6C5CE7', '#00B894', '#E17055'];

            const cardHTML = emails.map((email, idx) => {
                const initial = (email.email || '?')[0].toUpperCase();
                const color = colors[idx % colors.length];
                return `
                <div class="account-card ${currentAccount === email.email ? 'active' : ''}"
                     onclick="selectTempEmail('${escapeJs(email.email)}')">
                    <div class="account-card-top">
                        <div class="account-avatar" style="background:${color};">${initial}</div>
                        <div class="account-info">
                            <div class="account-email" onclick="event.stopPropagation(); copyEmail('${escapeJs(email.email)}')" style="cursor:pointer;" title="点击复制">${escapeHtml(email.email)}</div>
                            <div style="font-size:0.72rem;color:var(--text-muted);">${translateAppTextLocal('⚡ 临时邮箱')}</div>
                        </div>
                    </div>
                    <div class="account-card-bottom">
                        <div class="account-actions">
                            <button class="btn btn-sm btn-accent" onclick="event.stopPropagation(); copyVerificationInfo('${escapeJs(email.email)}', this)" title="提取验证码" style="font-size:0.72rem;padding:2px 8px;">🔑 验证码</button>
                            <button class="btn-icon" onclick="event.stopPropagation(); copyEmail('${escapeJs(email.email)}')" title="复制">📋</button>
                            <button class="btn-icon" onclick="event.stopPropagation(); clearTempEmailMessages('${escapeJs(email.email)}')" title="清空">🧹</button>
                            <button class="btn-icon" onclick="event.stopPropagation(); deleteTempEmail('${escapeJs(email.email)}')" title="删除" style="color:var(--clr-danger);">🗑️</button>
                        </div>
                    </div>
                </div>
            `}).join('');

            if (container) container.innerHTML = cardHTML;
            if (pageContainer) pageContainer.innerHTML = cardHTML;
        }

        // 生成临时邮箱
        async function generateTempEmail() {
            try {
                showToast('正在生成临时邮箱…', 'info');
                const response = await fetch('/api/temp-emails/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });

                const data = await response.json();

                if (data.success) {
                    showToast(`临时邮箱已生成: ${data.email}`, 'success');
                    delete accountsCache['temp'];
                    loadTempEmails(true);
                    loadGroups();
                } else {
                    handleApiError(data, '生成临时邮箱失败');
                }
            } catch (error) {
                showToast('生成临时邮箱失败', 'error');
            }
        }

        // 选择临时邮箱
        function selectTempEmail(email) {
            currentAccount = email;
            isTempEmailGroup = true;

            // Update mailbox page bar (if visible)
            const bar = document.getElementById('currentAccountBar');
            if (bar) bar.style.display = '';
            const emailLabel = document.getElementById('currentAccountEmail');
            if (emailLabel) emailLabel.textContent = getUiLanguage() === 'en' ? `${email} (Temp)` : `${email} (临时)`;

            // Update active state on all account cards
            document.querySelectorAll('.account-card').forEach(item => {
                item.classList.remove('active');
                const emailEl = item.querySelector('.account-email');
                if (emailEl && emailEl.textContent.includes(email)) {
                    item.classList.add('active');
                }
            });

            // Update temp-emails independent page header
            const tempName = document.getElementById('tempEmailCurrentName');
            if (tempName) tempName.textContent = email;
            const tempRefreshBtn = document.getElementById('tempEmailRefreshBtn');
            if (tempRefreshBtn) tempRefreshBtn.style.display = '';

            // Hide folder tabs (temp emails don't support folders)
            const folderTabs = document.getElementById('folderTabs');
            if (folderTabs) folderTabs.style.display = 'none';

            // Show loading in message area (prefer temp-emails page container)
            const tempMsgList = document.getElementById('tempEmailMessageList');
            const emailList = document.getElementById('emailList');
            const loadingHTML = `<div class="empty-state"><span class="empty-icon">📬</span><p>${translateAppTextLocal('点击"获取邮件"按钮获取邮件')}</p></div>`;

            if (tempMsgList) tempMsgList.innerHTML = loadingHTML;
            if (emailList) {
                emailList.innerHTML = loadingHTML;
            }

            const emailDetail = document.getElementById('emailDetail');
            if (emailDetail) {
                emailDetail.innerHTML = '<div class="empty-state"><span class="empty-icon">📄</span><p>选择一封邮件查看详情</p></div>';
            }
            const toolbar = document.getElementById('emailDetailToolbar');
            if (toolbar) toolbar.style.display = 'none';
            const count = document.getElementById('emailCount');
            if (count) count.textContent = '';
            const tag = document.getElementById('methodTag');
            if (tag) tag.style.display = 'none';

            // Auto-fetch messages
            loadTempEmailMessages(email);
        }

        // 清空临时邮箱的所有邮件
        async function clearTempEmailMessages(email) {
            if (!confirm(`确定要清空临时邮箱 ${email} 的所有邮件吗？`)) {
                return;
            }

            try {
                const response = await fetch(`/api/temp-emails/${encodeURIComponent(email)}/clear`, {
                    method: 'DELETE'
                });

                const data = await response.json();

                if (data.success) {
                    showToast(translateAppTextLocal('邮件已清空'), 'success');

                    // 如果当前选中的就是这个邮箱，清空邮件列表
                    if (currentAccount === email) {
                        currentEmails = [];
                        document.getElementById('emailCount').textContent = '(0)';
                        document.getElementById('emailList').innerHTML = `
                            <div class="empty-state">
                                <span class="empty-icon">📭</span><p>${translateAppTextLocal('收件箱为空')}</p>
                            </div>
                        `;
                        document.getElementById('emailDetail').innerHTML = `
                            <div class="empty-state">
                                <span class="empty-icon">📄</span><p>${translateAppTextLocal('选择一封邮件查看详情')}</p>
                            </div>
                        `;
                        document.getElementById('emailDetailToolbar').style.display = 'none';
                    }
                } else {
                    handleApiError(data, '清空临时邮箱失败');
                }
            } catch (error) {
                showToast(translateAppTextLocal('清空失败'), 'error');
            }
        }

        // 删除临时邮箱
        async function deleteTempEmail(email) {
            if (!confirm(`确定要删除临时邮箱 ${email} 吗？\n该邮箱的所有邮件也将被删除。`)) {
                return;
            }

            try {
                const response = await fetch(`/api/temp-emails/${encodeURIComponent(email)}`, {
                    method: 'DELETE'
                });

                const data = await response.json();

                if (data.success) {
                    showToast('临时邮箱已删除', 'success');
                    delete accountsCache['temp'];

                    if (currentAccount === email) {
                        currentAccount = null;
                        document.getElementById('currentAccountBar').style.display = 'none';
                        document.getElementById('emailList').innerHTML = `
                            <div class="empty-state">
                                <span class="empty-icon">📬</span><p>请从左侧选择一个邮箱账号</p>
                            </div>
                        `;
                        document.getElementById('emailDetail').innerHTML = `
                            <div class="empty-state">
                                <span class="empty-icon">📄</span><p>选择一封邮件查看详情</p>
                            </div>
                        `;
                    }

                    loadTempEmails(true);
                    loadGroups();
                } else {
                    handleApiError(data, '删除临时邮箱失败');
                }
            } catch (error) {
                showToast('删除失败', 'error');
            }
        }

        // 加载临时邮箱的邮件
        async function loadTempEmailMessages(email) {
            const container = document.getElementById('emailList');
            const tempContainer = document.getElementById('tempEmailMessageList');
            const loadingHTML = '<div class="loading-overlay"><span class="spinner"></span></div>';

            if (container) container.innerHTML = loadingHTML;
            if (tempContainer) tempContainer.innerHTML = loadingHTML;

            // 禁用按钮
            const refreshBtn = document.getElementById('tempEmailRefreshBtn');
            if (refreshBtn) {
                refreshBtn.disabled = true;
                refreshBtn.textContent = translateAppTextLocal('获取中...');
            }

            try {
                const response = await fetch(`/api/temp-emails/${encodeURIComponent(email)}/messages`);
                const data = await response.json();

                if (data.success) {
                    currentEmails = data.emails;
                    currentMethod = 'gptmail';

                    const methodTag = document.getElementById('methodTag');
                    if (methodTag) {
                        methodTag.textContent = 'GPTMail';
                        methodTag.style.display = 'inline';
                        methodTag.style.backgroundColor = '#00bcf2';
                        methodTag.style.color = 'white';
                    }

                    const emailCount = document.getElementById('emailCount');
                    if (emailCount) emailCount.textContent = `(${data.count})`;

                    // Render to mailbox emailList
                    renderEmailList(data.emails);

                    // Also render to temp-emails page container
                    if (tempContainer) {
                        renderTempEmailMessageList(tempContainer, data.emails);
                    }
                } else {
                    handleApiError(data, '加载临时邮件失败');
                    const errHTML = `<div class="empty-state"><span class="empty-icon">⚠️</span><p>${window.resolveApiErrorMessage ? window.resolveApiErrorMessage(data.error || data, '加载失败', 'Load failed') : (data.error && data.error.message ? data.error.message : '加载失败')}</p></div>`;
                    if (container) container.innerHTML = errHTML;
                    if (tempContainer) tempContainer.innerHTML = errHTML;
                }
            } catch (error) {
                const errHTML = '<div class="empty-state"><span class="empty-icon">⚠️</span><p>网络错误，请重试</p></div>';
                if (container) container.innerHTML = errHTML;
                if (tempContainer) tempContainer.innerHTML = errHTML;
            } finally {
                if (refreshBtn) {
                    refreshBtn.disabled = false;
                    refreshBtn.textContent = translateAppTextLocal('🔄 获取邮件');
                }
            }
        }

        // 渲染临时邮箱邮件列表到独立页面
        function renderTempEmailMessageList(container, emails) {
            if (!emails || emails.length === 0) {
                container.innerHTML = `<div class="empty-state"><span class="empty-icon">📭</span><p>${translateAppTextLocal('暂无邮件')}</p></div>`;
                return;
            }
            container.innerHTML = emails.map((email, index) => {
                const subject = email.subject || translateAppTextLocal('无主题');
                const from = email.from || email.sender || translateAppTextLocal('未知发件人');
                const date = email.receivedDateTime || email.date || '';
                const preview = (email.bodyPreview || email.body_preview || '').substring(0, 80);
                return `
                    <div class="email-item ${index === 0 ? '' : ''}" onclick="getTempEmailDetail('${escapeJs(email.id || email.message_id || '')}', ${index})">
                        <div class="email-subject">${escapeHtml(subject)}</div>
                        <div class="email-from">${escapeHtml(from)}</div>
                        <div class="email-preview">${escapeHtml(preview)}</div>
                        <div class="email-date">${escapeHtml(date)}</div>
                    </div>
                `;
            }).join('');
        }

        // 获取临时邮件详情
        async function getTempEmailDetail(messageId, index) {
            document.querySelectorAll('.email-item').forEach((item, i) => {
                item.classList.toggle('active', i === index);
            });

            document.getElementById('emailDetailToolbar').style.display = 'flex';

            const container = document.getElementById('emailDetail');
            container.innerHTML = '<div class="loading-overlay"><span class="spinner"></span></div>';

            try {
                const response = await fetch(`/api/temp-emails/${encodeURIComponent(currentAccount)}/messages/${encodeURIComponent(messageId)}`);
                const data = await response.json();

                if (data.success) {
                    renderEmailDetail(data.email);
                } else {
                    handleApiError(data, '加载邮件详情失败');
                    container.innerHTML = `
                        <div class="empty-state">
                            <span class="empty-icon">⚠️</span><p>${window.resolveApiErrorMessage ? window.resolveApiErrorMessage(data.error || data, '加载失败', 'Load failed') : (data.error && data.error.message ? data.error.message : '加载失败')}</p>
                        </div>
                    `;
                }
            } catch (error) {
                container.innerHTML = `
                    <div class="empty-state">
                        <span class="empty-icon">⚠️</span><p>网络错误，请重试</p>
                    </div>
                `;
            }
        }

