// 行程生成模块
const ItineraryAPI = {
    TYPES: {
        photo: { name: '摄影路线', icon: '📸', prompt: '请为贵港市规划一条摄影爱好者一日游行程' },
        family: { name: '亲子路线', icon: '👨‍👩‍👧', prompt: '请为贵港市规划一条亲子一日游行程' },
        food: { name: '美食路线', icon: '🍜', prompt: '请为贵港市规划一条美食一日游行程' },
        weekend: { name: '周末路线', icon: '🏖️', prompt: '请为贵港市规划一条周末放松一日游行程' }
    },
    generate(type) {
        const t = this.TYPES[type];
        if (!t) return;
        // 跳转到首页聊天并自动提问
        window.location.href = '/?ask=' + encodeURIComponent(t.prompt);
    }
};
