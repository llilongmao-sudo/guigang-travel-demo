/**
 * RecentAPI - 最近浏览模块（V8 云端同步版）
 * - 已登录：双写 LocalStorage + 服务端 API
 * - 未登录：纯 LocalStorage
 */
const RecentAPI = {
    STORAGE_KEY: 'guigang_recent_views',

    async getAll() {
        if (AuthUI.isLoggedIn()) {
            try {
                const resp = await fetch('/api/user/recent');
                const data = await resp.json();
                if (data.recent_views) {
                    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data.recent_views));
                    return data.recent_views;
                }
            } catch(e) {}
        }
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
        } catch (e) {
            return [];
        }
    },

    getAllSync() {
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
        } catch (e) {
            return [];
        }
    },

    add(spot) {
        if (!spot || !spot.id) return;
        let views = this.getAllSync();
        views = views.filter(v => v.id !== spot.id);
        views.unshift({
            id: spot.id,
            name: spot.name || '',
            image_url: spot.image_url || '',
            ticket_price: spot.ticket_price || '',
            district: spot.district || '',
            viewed_at: new Date().toISOString()
        });
        if (views.length > 20) views = views.slice(0, 20);
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(views));

        // 服务端同步
        if (AuthUI.isLoggedIn()) {
            fetch('/api/user/recent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    spot_id: spot.id,
                    spot_name: spot.name || '',
                    spot_data: spot
                })
            }).catch(() => {});
        }
    },

    clear() {
        localStorage.removeItem(this.STORAGE_KEY);
        if (AuthUI.isLoggedIn()) {
            fetch('/api/user/recent', { method: 'DELETE' }).catch(() => {});
        }
    },

    remove(spotId) {
        const views = this.getAllSync().filter(v => v.id !== spotId);
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(views));
        // 服务端不单独删除（下次浏览会覆盖）
    }
};
