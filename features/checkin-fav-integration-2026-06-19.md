# 贵港旅游助手 — 收藏/打卡功能开发日志

## 改动说明

### 1. 详情页底部打卡按钮（spot_detail.html）
- 新增 `cycleCheckin()` 函数：循环切换 未打卡→想去→去过→未打卡
- 按钮样式随状态变化：默认灰色 → 想去(橙色) → 去过(绿色)
- 页面加载时调用 `updateCheckinBtn()` 同步状态

### 2. 景点列表收藏按钮（index.html）
- `renderSpotList()` 和 `initSpotList()` 每个景点卡片右侧加 ♡/❤️ 按钮
- `toggleListFav()` 点击即切换收藏，实时更新徽章
- 页面加载时自动显示已收藏的❤️状态

### 3. 收藏面板改双 Tab（index.html）
- 面板顶部加 Tab 导航：❤️ 收藏 | 📍 打卡
- 「打卡」Tab 按状态分组：「想去」和「去过」，各显示数量
- 每条支持取消打卡
- `switchFavTab()` 切换时动态刷新对应列表

### 文件清单
- `templates/index.html` +179行（Tab结构、列表收藏、checkin.js引入）
- `templates/spot_detail.html` +14行（打卡按钮+JS逻辑）
- `static/css/spot_detail.css` +11行（打卡按钮三态样式）
- `static/js/checkin.js`（已存在，未修改，提供 CheckinAPI 纯 frontend localStorage 模块）

### Git
- commit `310cb2c` → `origin/main` ✅
