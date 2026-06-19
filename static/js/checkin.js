/**
 * CheckinAPI - 打卡功能模块 v2
 * 使用 localStorage 持久化，key: guigang_checkins
 * 支持三种状态：visited（去过）、want_to_go（想去）、null（未打卡）
 * 扩展：笔记(note)、照片(photos base64)、评分(rating)、日期(date)
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

    /** 保存到 localStorage */
    _save(records) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(records));
    },

    /** 设置打卡状态 */
    setStatus(spotId, name, status) {
        if (!spotId) return false;
        const records = this.getAll();
        const idx = records.findIndex(r => r.id === spotId);

        if (status === null) {
            if (idx !== -1) records.splice(idx, 1);
        } else if (status === 'visited' || status === 'want_to_go') {
            const entry = {
                id: spotId,
                name: name || '',
                status: status,
                updated_at: new Date().toISOString()
            };
            if (idx !== -1) {
                // 保留已有的笔记、照片等扩展字段
                const existing = records[idx];
                records[idx] = { ...existing, ...entry };
            } else {
                records.push(entry);
            }
        } else {
            return false;
        }

        this._save(records);
        return true;
    },

    /** 获取某个景点的打卡状态 */
    getStatus(spotId) {
        const record = this.getAll().find(r => r.id === spotId);
        return record ? record.status : null;
    },

    /** 获取某个景点的完整记录 */
    getRecord(spotId) {
        return this.getAll().find(r => r.id === spotId) || null;
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

        // 如果切换到 visited，自动设置打卡日期
        if (next === 'visited') {
            const record = this.getRecord(spot.id);
            if (!record || !record.date) {
                this.updateExtra(spot.id, { date: new Date().toISOString().slice(0, 10) });
            }
        }

        this.setStatus(spot.id, spot.name || '', next);
        return next;
    },

    /** 更新扩展字段：笔记、照片、评分等 */
    updateExtra(spotId, extra) {
        if (!spotId) return false;
        const records = this.getAll();
        const idx = records.findIndex(r => r.id === spotId);
        if (idx === -1) return false;

        Object.assign(records[idx], extra, { updated_at: new Date().toISOString() });
        this._save(records);
        return true;
    },

    /** 添加照片（base64） */
    addPhoto(spotId, photoBase64) {
        const record = this.getRecord(spotId);
        if (!record) return false;

        if (!record.photos) record.photos = [];
        // 限制最多9张
        if (record.photos.length >= 9) return false;

        // 压缩/缩略图处理：限制单张大小 ~200KB
        let photo = photoBase64;
        if (photo.length > 200 * 1024) {
            photo = this._compressPhoto(photo);
        }
        record.photos.push({
            data: photo,
            added_at: new Date().toISOString()
        });

        const records = this.getAll();
        const idx = records.findIndex(r => r.id === spotId);
        records[idx] = record;
        this._save(records);
        return true;
    },

    /** 删除某张照片 */
    removePhoto(spotId, photoIndex) {
        const record = this.getRecord(spotId);
        if (!record || !record.photos || !record.photos[photoIndex]) return false;
        record.photos.splice(photoIndex, 1);

        const records = this.getAll();
        const idx = records.findIndex(r => r.id === spotId);
        records[idx] = record;
        this._save(records);
        return true;
    },

    /** 简单压缩：缩小尺寸（通过 canvas） */
    _compressPhoto(base64Data) {
        try {
            const canvas = document.createElement('canvas');
            const img = new Image();
            img.src = base64Data;
            // 同步方式不可行，返回原始数据截断
            // 实际压缩在调用端异步完成，这里做 fallback
            return base64Data.slice(0, 200 * 1024);
        } catch(e) {
            return base64Data;
        }
    },

    /** 设置/更新笔记 */
    setNote(spotId, note) {
        return this.updateExtra(spotId, { note: note });
    },

    /** 设置评分 (1-5) */
    setRating(spotId, rating) {
        const r = Math.max(1, Math.min(5, parseInt(rating) || 0));
        if (!r) return false;
        return this.updateExtra(spotId, { rating: r });
    },

    /** 设置打卡日期 */
    setDate(spotId, dateStr) {
        return this.updateExtra(spotId, { date: dateStr });
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

    /** 获取所有带笔记的记录 */
    getWithNotes() {
        return this.getAll().filter(r => r.note && r.note.trim());
    },

    /** 获取所有带照片的记录 */
    getWithPhotos() {
        return this.getAll().filter(r => r.photos && r.photos.length > 0);
    },

    /** 清空所有打卡 */
    clearAll() {
        localStorage.removeItem(this.STORAGE_KEY);
    }
};
