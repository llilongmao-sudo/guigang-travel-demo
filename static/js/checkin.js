/**
 * CheckinAPI - 打卡功能模块（V8 云端同步版）
 * - 已登录：双写 LocalStorage + 服务端 API
 * - 未登录：纯 LocalStorage
 * 
 * LocalStorage 格式: [{id, name, status, entries, updated_at}]
 * 服务端格式: {spotId: {spot_name, status, entries, updated_at}}
 */
const CheckinAPI = {
    STORAGE_KEY: 'guigang_checkins',

    getAll() {
        try { return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]'); }
        catch (e) { return []; }
    },

    _save(records) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(records));
        // 异步同步到服务端
        this._syncToServer(records);
    },

    /** 同步当前数据到服务端 */
    _syncToServer(records) {
        if (!AuthUI.isLoggedIn()) return;
        const data = {};
        records.forEach(r => {
            data[r.id] = {
                spot_name: r.name || '',
                status: r.status || 'none',
                entries: r.entries || [],
                updated_at: r.updated_at || new Date().toISOString()
            };
        });
        fetch('/api/user/checkins', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                spot_id: Object.keys(data)[0] || '__batch__', // dummy
                spot_name: '__batch__',
                status: '__batch__',
                entries: [],
                _batch: data
            })
        }).catch(() => {});
    },

    /** 批量覆盖同步（用于首次登录合并） */
    _batchUpload(records) {
        if (!AuthUI.isLoggedIn() || !records || records.length === 0) return;
        const data = {};
        records.forEach(r => {
            data[r.id] = {
                spot_name: r.name || '',
                status: r.status || 'none',
                entries: r.entries || [],
                updated_at: r.updated_at || new Date().toISOString()
            };
        });
        fetch('/api/user/checkins/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ checkins: data })
        }).catch(() => {});
    },

    /** 获取景点记录 */
    getRecord(spotId) {
        return this.getAll().find(r => r.id === spotId) || null;
    },

    getStatus(spotId) {
        const r = this.getRecord(spotId);
        return r ? r.status : null;
    },

    setStatus(spotId, name, status) {
        if (!spotId) return false;
        let records = this.getAll();
        let idx = records.findIndex(r => r.id === spotId);

        if (status === null) {
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

        // 单条同步
        if (AuthUI.isLoggedIn()) {
            fetch('/api/user/checkins', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    spot_id: spotId,
                    spot_name: name || '',
                    status: status || 'none',
                    entries: (idx !== -1 && records[idx] ? records[idx].entries : []) || []
                })
            }).catch(() => {});
        }
        return true;
    },

    cycleStatus(spot) {
        if (!spot?.id) return null;
        const cur = this.getStatus(spot.id);
        const next = !cur ? 'want_to_go' : cur === 'want_to_go' ? 'visited' : null;
        this.setStatus(spot.id, spot.name || '', next);
        return next;
    },

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
        record.entries.unshift(entry);
        record.updated_at = new Date().toISOString();
        if (!record.date) record.date = entry.date;
        if (!record.rating && entry.rating) record.rating = entry.rating;

        const records = this.getAll();
        records[records.findIndex(r => r.id === spotId)] = record;
        this._save(records);
        return entry.id;
    },

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

    getByStatus(status) { return this.getAll().filter(r => r.status === status); },
    count() { return this.getAll().length; },
    visitedCount() { return this.getByStatus('visited').length; },
    wantToGoCount() { return this.getByStatus('want_to_go').length; },
    clearAll() { localStorage.removeItem(this.STORAGE_KEY); }
};
