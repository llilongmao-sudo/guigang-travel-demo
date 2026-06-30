/**
 * FavoritesAPI - 收藏功能模块（V8 云端同步版）
 * - 已登录：双写 LocalStorage + 服务端 API
 * - 未登录：纯 LocalStorage（回退兼容）
 */
const FavoritesAPI = {
    STORAGE_KEY: 'guigang_favorites',

    /** 获取全部收藏列表 */
    async getAll() {
        // 已登录 → 从服务端获取
        if (AuthUI.isLoggedIn()) {
            try {
                const resp = await fetch('/api/user/favorites');
                const data = await resp.json();
                if (data.favorites) {
                    // 同步到 LocalStorage 作为缓存
                    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data.favorites));
                    return data.favorites;
                }
            } catch(e) {}
        }
        // 降级 LocalStorage
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
        } catch (e) {
            return [];
        }
    },

    /** 同步获取（用于需要即时返回的场景） */
    getAllSync() {
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
        } catch (e) {
            return [];
        }
    },

    /** 添加收藏 */
    async add(spot) {
        if (!spot || !spot.id) return false;
        const favs = this.getAllSync();
        if (favs.some(f => f.id === spot.id)) return false;
        if (favs.length >= 50) return false;

        const entry = {
            id: spot.id,
            name: spot.name || '',
            image_url: spot.image_url || '',
            ticket_price: spot.ticket_price || '',
            district: spot.district || '',
            added_at: new Date().toISOString()
        };
        favs.push(entry);
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(favs));

        // 服务端同步
        if (AuthUI.isLoggedIn()) {
            fetch('/api/user/favorites', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    spot_id: spot.id,
                    spot_name: spot.name || '',
                    spot_data: entry
                })
            }).catch(() => {});
        }

        return true;
    },

    /** 取消收藏 */
    async remove(spotId) {
        const favs = this.getAllSync();
        const idx = favs.findIndex(f => f.id === spotId);
        if (idx === -1) return false;
        favs.splice(idx, 1);
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(favs));

        // 服务端同步
        if (AuthUI.isLoggedIn()) {
            fetch('/api/user/favorites?spot_id=' + spotId, {
                method: 'DELETE'
            }).catch(() => {});
        }
        return true;
    },

    /** 检查是否已收藏 */
    isFavorited(spotId) {
        return this.getAllSync().some(f => f.id === spotId);
    },

    /** 切换收藏状态 */
    async toggle(spot) {
        if (!spot || !spot.id) return false;
        if (this.isFavorited(spot.id)) {
            await this.remove(spot.id);
            return false;
        } else {
            await this.add(spot);
            return true;
        }
    },

    /** 返回收藏数量 */
    count() {
        return this.getAllSync().length;
    },

    /** 清空所有收藏 */
    async clearAll() {
        localStorage.removeItem(this.STORAGE_KEY);
        if (AuthUI.isLoggedIn()) {
            fetch('/api/user/recent', { method: 'DELETE' }).catch(() => {});
        }
    }
};
