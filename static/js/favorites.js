/**
 * FavoritesAPI - 收藏功能模块
 * 使用 localStorage 持久化，key: guigang_favorites
 * 提供给 index.html 和 spot_detail.html 共同使用
 */
const FavoritesAPI = {
    STORAGE_KEY: 'guigang_favorites',

    /** 获取全部收藏列表 */
    getAll() {
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
        } catch (e) {
            return [];
        }
    },

    /** 添加收藏，去重，上限 50 条。成功返回 true，失败返回 false */
    add(spot) {
        if (!spot || !spot.id) return false;
        const favs = this.getAll();
        // 去重
        if (favs.some(f => f.id === spot.id)) {
            return false;
        }
        // 上限 50 条
        if (favs.length >= 50) {
            return false;
        }
        favs.push({
            id: spot.id,
            name: spot.name || '',
            image_url: spot.image_url || '',
            ticket_price: spot.ticket_price || '',
            district: spot.district || '',
            added_at: new Date().toISOString()
        });
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(favs));
        return true;
    },

    /** 取消收藏，成功返回 true，失败返回 false */
    remove(spotId) {
        const favs = this.getAll();
        const idx = favs.findIndex(f => f.id === spotId);
        if (idx === -1) return false;
        favs.splice(idx, 1);
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(favs));
        return true;
    },

    /** 检查是否已收藏 */
    isFavorited(spotId) {
        return this.getAll().some(f => f.id === spotId);
    },

    /** 切换收藏状态。收藏后返回 true，取消收藏返回 false */
    toggle(spot) {
        if (!spot || !spot.id) return false;
        if (this.isFavorited(spot.id)) {
            this.remove(spot.id);
            return false;
        } else {
            this.add(spot);
            return true;
        }
    },

    /** 返回收藏数量 */
    count() {
        return this.getAll().length;
    },

    /** 清空所有收藏 */
    clearAll() {
        localStorage.removeItem(this.STORAGE_KEY);
    }
};
