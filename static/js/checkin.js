/**
 * CheckinAPI - 打卡功能模块 v3
 * 使用 localStorage 持久化，key: guigang_checkins
 * v3: 支持多次打卡（entries数组），每次打卡独立笔记/照片/评分/日期
 */
const CheckinAPI = {
    STORAGE_KEY: 'guigang_checkins',

    getAll() {
        try { return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]'); }
        catch (e) { return []; }
    },

    _save(records) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(records));
    },

    /** 获取景点记录（不存在则返回 null） */
    getRecord(spotId) {
        return this.getAll().find(r => r.id === spotId) || null;
    },

    /** 获取当前状态 */
    getStatus(spotId) {
        const r = this.getRecord(spotId);
        return r ? r.status : null;
    },

    /** 设置状态 + 创建/更新记录 */
    setStatus(spotId, name, status) {
        if (!spotId) return false;
        let records = this.getAll();
        let idx = records.findIndex(r => r.id === spotId);

        if (status === null) {
            // 取消打卡 — 删除整条
            if (idx !== -1) records.splice(idx, 1);
        } else {
            const entry = { id: spotId, name: name || '', status, updated_at: new Date().toISOString(), entries: [] };
            if (idx !== -1) {
                entry.entries = records[idx].entries || [];
                records[idx] = { ...records[idx], ...entry };
            } else {
                records.push(entry);
            }
        }

        this._save(records);
        return true;
    },

    /** 循环切换状态 */
    cycleStatus(spot) {
        if (!spot?.id) return null;
        const cur = this.getStatus(spot.id);
        const next = !cur ? 'want_to_go' : cur === 'want_to_go' ? 'visited' : null;
        this.setStatus(spot.id, spot.name || '', next);
        return next;
    },

    // ── 多次打卡 entries 操作 ──

    /** 新增一条打卡记录（含笔记/照片/评分/日期） */
    addEntry(spotId, data) {
        const record = this.getRecord(spotId);
        if (!record) return false;
        const entry = {
            id: 'e_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
            date: data.date || new Date().toISOString().slice(0, 10),
            rating: data.rating || null,
            note: data.note || '',
            photos: data.photos || [],
            created_at: new Date().toISOString()
        };
        record.entries = record.entries || [];
        record.entries.unshift(entry); // 最新的在前
        record.updated_at = new Date().toISOString();
        // 同步更新主记录的快捷字段
        if (!record.date) record.date = entry.date;
        if (!record.rating && entry.rating) record.rating = entry.rating;

        const records = this.getAll();
        const idx = records.findIndex(r => r.id === spotId);
        records[idx] = record;
        this._save(records);
        return entry.id;
    },

    /** 更新某条 entry */
    updateEntry(spotId, entryId, data) {
        const record = this.getRecord(spotId);
        if (!record?.entries) return false;
        const ei = record.entries.findIndex(e => e.id === entryId);
        if (ei === -1) return false;
        Object.assign(record.entries[ei], data, { created_at: record.entries[ei].created_at });
        record.updated_at = new Date().toISOString();
        const records = this.getAll();
        records[records.findIndex(r => r.id === spotId)] = record;
        this._save(records);
        return true;
    },

    /** 删除某条 entry */
    removeEntry(spotId, entryId) {
        const record = this.getRecord(spotId);
        if (!record?.entries) return false;
        record.entries = record.entries.filter(e => e.id !== entryId);
        record.updated_at = new Date().toISOString();
        const records = this.getAll();
        records[records.findIndex(r => r.id === spotId)] = record;
        this._save(records);
        return true;
    },

    /** 给某条 entry 添加照片 */
    addPhotoToEntry(spotId, entryId, base64Data) {
        const record = this.getRecord(spotId);
        if (!record?.entries) return false;
        const entry = record.entries.find(e => e.id === entryId);
        if (!entry) return false;
        if (!entry.photos) entry.photos = [];
        if (entry.photos.length >= 9) return false;
        entry.photos.push({ data: base64Data, added_at: new Date().toISOString() });

        const records = this.getAll();
        records[records.findIndex(r => r.id === spotId)] = record;
        this._save(records);
        return true;
    },

    /** 删除某条 entry 的某张照片 */
    removePhotoFromEntry(spotId, entryId, photoIdx) {
        const record = this.getRecord(spotId);
        if (!record?.entries) return false;
        const entry = record.entries.find(e => e.id === entryId);
        if (!entry?.photos?.[photoIdx]) return false;
        entry.photos.splice(photoIdx, 1);

        const records = this.getAll();
        records[records.findIndex(r => r.id === spotId)] = record;
        this._save(records);
        return true;
    },

    // ── 查询 ──

    getByStatus(status) { return this.getAll().filter(r => r.status === status); },
    count() { return this.getAll().length; },
    visitedCount() { return this.getByStatus('visited').length; },
    wantToGoCount() { return this.getByStatus('want_to_go').length; },
    clearAll() { localStorage.removeItem(this.STORAGE_KEY); }
};
