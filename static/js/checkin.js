/**
 * CheckinAPI - 打卡功能模块
 * 使用 localStorage 持久化，key: guigang_checkins
 * 支持三种状态：visited（去过）、want_to_go（想去）、null（未打卡）
 */
const CheckinAPI = {
    STORAGE_KEY: 'guigang_checkins',

    /** 获取全部打卡记录 */
    getAll() {
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
        } catch (e) {
            return [];
        }
    },

    /** 设置打卡状态 */
    setStatus(spotId, name, status) {
        if (!spotId) return false;
        const records = this.getAll();
        const idx = records.findIndex(r => r.id === spotId);

        if (status === null) {
            // 取消打卡
            if (idx !== -1) records.splice(idx, 1);
        } else if (status === 'visited' || status === 'want_to_go') {
            const entry = {
                id: spotId,
                name: name || '',
                status: status,
                updated_at: new Date().toISOString()
            };
            if (idx !== -1) {
                records[idx] = { ...records[idx], ...entry };
            } else {
                records.push(entry);
            }
        } else {
            return false;
        }

        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(records));
        return true;
    },

    /** 获取某个景点的打卡状态 */
    getStatus(spotId) {
        const record = this.getAll().find(r => r.id === spotId);
        return record ? record.status : null;
    },

    /** 按状态筛选 */
    getByStatus(status) {
        return this.getAll().filter(r => r.status === status);
    },

    /** 切换打卡（循环：无→想去→去过→无） */
    cycleStatus(spot) {
        if (!spot || !spot.id) return null;
        const current = this.getStatus(spot.id);
        let next;
        if (!current) next = 'want_to_go';
        else if (current === 'want_to_go') next = 'visited';
        else next = null;
        this.setStatus(spot.id, spot.name || '', next);
        return next; // 返回新状态
    },

    /** 获取打卡数量 */
    count() {
        return this.getAll().length;
    },

    /** 获取去过数量 */
    visitedCount() {
        return this.getByStatus('visited').length;
    },

    /** 获取想去数量 */
    wantToGoCount() {
        return this.getByStatus('want_to_go').length;
    },

    /** 清空所有打卡 */
    clearAll() {
        localStorage.removeItem(this.STORAGE_KEY);
    }
};
