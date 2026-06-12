/**
 * RecentAPI - 最近浏览记录模块
 * 使用 localStorage 持久化，key: guigang_recent_views
 * 提供给 index.html 和 spot_detail.html 共同使用
 */
const RecentAPI = {
    STORAGE_KEY: 'guigang_recent_views',
    MAX_ITEMS: 20,

    /** 获取全部浏览记录，按 viewed_at 降序 */
    getAll() {
        try {
            const list = JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
            return list.sort((a, b) => new Date(b.viewed_at) - new Date(a.viewed_at));
        } catch (e) {
            return [];
        }
    },

    /** 添加/更新浏览记录（去重，更新 viewed_at，超限移除最旧） */
    add(spot) {
        if (!spot || !spot.id) return false;
        let views = this.getAll();
        // 去重：移除已有同 ID 记录
        views = views.filter(v => v.id !== spot.id);
        // 新记录插入最前
        views.unshift({
            id: spot.id,
            name: spot.name || '',
            image_url: spot.image_url || '',
            ticket_price: spot.ticket_price || '',
            district: spot.district || '',
            viewed_at: new Date().toISOString()
        });
        // 超限移除最旧
        if (views.length > this.MAX_ITEMS) {
            views = views.slice(0, this.MAX_ITEMS);
        }
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(views));
        return true;
    },

    /** 删除单条浏览记录 */
    remove(spotId) {
        let views = this.getAll();
        views = views.filter(v => v.id !== spotId);
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(views));
        return true;
    },

    /** 清空所有浏览记录 */
    clear() {
        localStorage.removeItem(this.STORAGE_KEY);
        return true;
    }
};
