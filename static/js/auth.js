/**
 * AuthUI - 登录 / 注册 / 用户菜单
 * 独立模块，被 index.html 引用
 */
const AuthUI = {
    _user: null,
    _modalEl: null,

    /** 初始化：检查登录状态，渲染用户菜单 */
    async init() {
        // 先尝试从 session 恢复
        const cached = sessionStorage.getItem('guigang_user');
        if (cached) {
            try { this._user = JSON.parse(cached); } catch(e) {}
        }

        // 向服务端确认状态
        try {
            const resp = await fetch('/api/auth/status');
            const data = await resp.json();
            if (data.logged_in) {
                this._user = data.user;
                sessionStorage.setItem('guigang_user', JSON.stringify(data.user));
            } else {
                this._user = null;
                sessionStorage.removeItem('guigang_user');
            }
        } catch(e) {
            // 网络错误，使用缓存
        }

        this.renderMenu();
    },

    /** 渲染顶部用户菜单 */
    renderMenu() {
        let container = document.getElementById('userMenuContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'userMenuContainer';
            container.className = 'user-menu';
            document.body.appendChild(container);
        }

        if (this._user) {
            const name = this._user.nickname || this._user.username;
            container.innerHTML = `
                <button class="user-btn" id="userMenuBtn" onclick="AuthUI.toggleDropdown()">
                    <span class="avatar-icon">👤</span>
                    <span>${this._escape(name)}</span>
                    <span class="dropdown-arrow">▾</span>
                </button>
                <div class="user-dropdown" id="userDropdown">
                    <div class="dropdown-header">
                        <div class="user-name">${this._escape(name)}</div>
                        <div class="user-email">${this._escape(this._user.email || '未绑定邮箱')}</div>
                    </div>
                    <div class="dropdown-divider"></div>
                    <button class="dropdown-item" onclick="AuthUI.showProfile()">
                        ⚙️ 修改昵称
                    </button>
                    <button class="dropdown-item danger" onclick="AuthUI.logout()">
                        🚪 退出登录
                    </button>
                </div>
            `;
        } else {
            container.innerHTML = `
                <button class="user-btn" onclick="AuthUI.showAuth('login')">
                    <span class="avatar-icon">👤</span>
                    <span>登录</span>
                </button>
            `;
        }
    },

    /** 切换下拉菜单 */
    toggleDropdown() {
        const dd = document.getElementById('userDropdown');
        const btn = document.getElementById('userMenuBtn');
        if (!dd || !btn) return;
        const show = !dd.classList.contains('show');
        dd.classList.toggle('show', show);
        btn.classList.toggle('open', show);

        if (show) {
            const close = (e) => {
                if (!e.target.closest('#userMenuContainer')) {
                    dd.classList.remove('show');
                    btn.classList.remove('open');
                    document.removeEventListener('click', close);
                }
            };
            setTimeout(() => document.addEventListener('click', close), 0);
        }
    },

    /** 显示登录/注册弹窗 */
    showAuth(mode) {
        const isLogin = mode === 'login';
        const title = isLogin ? '欢迎回来' : '注册账号';
        const subtitle = isLogin ? '登录后可以跨设备同步收藏和打卡' : '注册后即可使用全部功能';

        this._closeModal();
        const overlay = document.createElement('div');
        overlay.className = 'auth-overlay';
        overlay.id = 'authOverlay';
        overlay.innerHTML = `
            <div class="auth-modal" onclick="event.stopPropagation()">
                <div class="auth-header">
                    <button class="auth-close" onclick="AuthUI._closeModal()">✕</button>
                    <h2>${title}</h2>
                    <p>${subtitle}</p>
                </div>
                <div class="auth-body">
                    <div class="auth-error" id="authError"></div>
                    ${!isLogin ? `
                    <div class="auth-field">
                        <label>邮箱（选填）</label>
                        <input type="email" id="authEmail" placeholder="用于找回密码">
                    </div>` : ''}
                    <div class="auth-field">
                        <label>用户名</label>
                        <input type="text" id="authUsername" placeholder="2~20个字符" autocomplete="username">
                    </div>
                    <div class="auth-field">
                        <label>密码</label>
                        <input type="password" id="authPassword" placeholder="${isLogin ? '输入密码' : '至少6位'}" autocomplete="${isLogin ? 'current-password' : 'new-password'}">
                    </div>
                    <button class="auth-submit" id="authSubmitBtn" onclick="AuthUI._submitAuth('${mode}')">
                        ${isLogin ? '登 录' : '注 册'}
                    </button>
                    <div class="auth-switch">
                        ${isLogin
                            ? '还没有账号？<a onclick="AuthUI.showAuth(\'register\')">立即注册</a>'
                            : '已有账号？<a onclick="AuthUI.showAuth(\'login\')">去登录</a>'}
                    </div>
                </div>
            </div>
        `;
        overlay.onclick = (e) => { if (e.target === overlay) this._closeModal(); };
        document.body.appendChild(overlay);

        // 自动聚焦
        setTimeout(() => {
            const el = document.getElementById('authUsername');
            if (el) el.focus();
        }, 200);

        // 回车提交
        overlay.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this._submitAuth(mode);
        });
    },

    /** 提交登录/注册 */
    async _submitAuth(mode) {
        const btn = document.getElementById('authSubmitBtn');
        const errEl = document.getElementById('authError');
        const username = document.getElementById('authUsername')?.value.trim();
        const password = document.getElementById('authPassword')?.value.trim();

        if (!username || !password) {
            this._showError('请填写用户名和密码');
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<span class="auth-spinner"></span>处理中...';
        this._hideError();

        try {
            const body = mode === 'login'
                ? { username, password }
                : { username, password, email: document.getElementById('authEmail')?.value.trim() || '' };

            const resp = await fetch(`/api/auth/${mode}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await resp.json();

            if (data.success) {
                this._user = data.user;
                sessionStorage.setItem('guigang_user', JSON.stringify(data.user));
                this._closeModal();

                // 登录后合并 LocalStorage 数据
                if (data.need_sync || mode === 'register') {
                    await SyncManager.syncAll();
                }

                this.renderMenu();
                this._toast(`✅ ${mode === 'login' ? '登录成功' : '注册成功'}，数据已同步`);

                // 通知其他模块刷新
                window.dispatchEvent(new CustomEvent('auth-change', { detail: { user: data.user } }));
            } else {
                this._showError(data.error || '操作失败');
            }
        } catch(e) {
            this._showError('网络错误，请稍后重试');
        } finally {
            btn.disabled = false;
            btn.innerHTML = mode === 'login' ? '登 录' : '注 册';
        }
    },

    /** 退出登录 */
    async logout() {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
        } catch(e) {}

        this._user = null;
        sessionStorage.removeItem('guigang_user');
        this.renderMenu();
        this._toast('已退出登录，数据保留在本地');
        window.dispatchEvent(new CustomEvent('auth-change', { detail: { user: null } }));
    },

    /** 修改昵称弹窗 */
    showProfile() {
        this.toggleDropdown(); // 先关菜单
        const name = prompt('修改昵称：', this._user?.nickname || '');
        if (!name || !name.trim()) return;

        fetch('/api/auth/update-profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nickname: name.trim() })
        }).then(r => r.json()).then(data => {
            if (data.success) {
                this._user = data.user;
                sessionStorage.setItem('guigang_user', JSON.stringify(data.user));
                this.renderMenu();
                this._toast('✅ 昵称已更新');
            }
        });
    },

    /** 获取当前用户（null = 未登录） */
    getUser() {
        return this._user;
    },

    /** 是否已登录 */
    isLoggedIn() {
        return !!this._user;
    },

    /* ── 工具方法 ── */

    _closeModal() {
        const el = document.getElementById('authOverlay');
        if (el) el.remove();
    },

    _showError(msg) {
        const el = document.getElementById('authError');
        if (el) { el.textContent = msg; el.classList.add('show'); }
    },

    _hideError() {
        const el = document.getElementById('authError');
        if (el) el.classList.remove('show');
    },

    _escape(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    _toast(msg) {
        const t = document.getElementById('toast');
        if (t) {
            t.textContent = msg;
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 2500);
        }
    }
};


/**
 * SyncManager - 首次登录时把 LocalStorage 数据合并到服务端
 */
const SyncManager = {
    async syncAll() {
        const results = { favorites: 0, checkins: 0, preferences: false };

        // 同步收藏
        try {
            const local = JSON.parse(localStorage.getItem('guigang_favorites') || '[]');
            if (local.length > 0) {
                await fetch('/api/user/favorites/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ favorites: local })
                });
                results.favorites = local.length;
            }
        } catch(e) {}

        // 同步打卡
        try {
            const local = JSON.parse(localStorage.getItem('guigang_checkins') || '{}');
            if (Object.keys(local).length > 0) {
                await fetch('/api/user/checkins/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ checkins: local })
                });
                results.checkins = Object.keys(local).length;
            }
        } catch(e) {}

        // 同步偏好
        try {
            const local = JSON.parse(localStorage.getItem('guigang_preferences'));
            if (local?.interests?.length > 0) {
                await fetch('/api/user/preferences', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ interests: local.interests })
                });
                results.preferences = true;
            }
        } catch(e) {}

        console.log('[Sync] 同步完成:', results);
    }
};
