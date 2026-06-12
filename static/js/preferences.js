const PreferencesAPI = {
    STORAGE_KEY: 'guigang_preferences',
    TYPES: [
        { id: 'photo', name: '摄影', icon: '📸', desc: '风景摄影打卡点' },
        { id: 'food', name: '美食', icon: '🍜', desc: '特色美食探店' },
        { id: 'family', name: '亲子', icon: '👨‍👩‍👧', desc: '适合带娃出游' },
        { id: 'drive', name: '自驾', icon: '🚗', desc: '自驾游路线' },
        { id: 'camping', name: '露营', icon: '⛺', desc: '户外露营体验' },
        { id: 'culture', name: '历史文化', icon: '🏛️', desc: '人文古迹探索' },
    ],
    get() {
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || null;
        } catch { return null; }
    },
    save(interests) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify({
            interests,
            selected_at: new Date().toISOString(),
            version: '1.0'
        }));
    },
    hasSelected() {
        return this.get() !== null;
    },
    getInterests() {
        const data = this.get();
        return data ? data.interests : [];
    },
    getInterestLabels() {
        const interests = this.getInterests();
        return interests.map(id => {
            const type = this.TYPES.find(t => t.id === id);
            return type ? type.name : id;
        });
    }
};
