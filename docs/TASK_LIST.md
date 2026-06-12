# 📋 开发任务清单（Task-001 ~ Task-010）

> 贵港旅游智能助手 V6.1 → V7 详细开发任务分解

---

## Task-001: 景点详情页

### 任务概述
实现景点详情展示页面，用户点击任意景点卡片后进入详情页查看完整信息。

### 涉及文件

| 类型 | 路径 | 说明 |
|------|------|------|
| 模板 | `templates/spot_detail.html` | 详情页 HTML 结构 |
| 样式 | `static/css/spot_detail.css` | 详情页样式（新建） |
| 后端 | `app.py` | 新增 `/spot/<id>` 路由 |
| 知识库 | `knowledge_base_v4.py` | 新增字段支持 |

### 接口定义

```python
# 新增路由
@app.route('/spot/<int:spot_id>')
def spot_detail(spot_id):
    """景点详情页"""
    pass

# API 接口（供前端调用）
@app.route('/api/spot/<int:spot_id>')
def api_spot_detail(spot_id):
    """返回景点详情 JSON"""
    pass
```

### 知识库新增字段

```python
{
    "id": 1,
    "name": "景点名称",
    "image": "景点主图 URL",
    "open_time": "开放时间",
    "ticket_price": "门票价格",
    "best_season": "最佳游玩季节",
    # ... 现有字段保持不变
}
```

### 页面元素

- [ ] 景点名称（大标题）
- [ ] 景点图片（顶部大图）
- [ ] 景点简介（详细描述）
- [ ] 推荐指数（⭐⭐⭐⭐⭐）
- [ ] 开放时间
- [ ] 门票价格
- [ ] 最佳季节
- [ ] 导航按钮（调用地图）
- [ ] 收藏按钮（❤️）
- [ ] AI 讲解按钮（🤖）

### 验收标准

- [ ] 点击首页任意景点卡片后进入详情页
- [ ] 页面加载时间 < 1 秒
- [ ] 移动端适配良好
- [ ] 收藏按钮可点击（功能在 Task-002 实现）
- [ ] AI 讲解按钮可点击（功能在 Task-004 实现）

### 提交规范

```bash
# 提交信息
git commit -m "feat(Task-001): 实现景点详情页

- 新增 spot_detail.html 模板
- 新增 /spot/<id> 路由
- 新增 /api/spot/<id> API 接口
- 知识库新增 image/open_time/ticket_price/best_season 字段
- 新增 spot_detail.css 样式文件

Closes Task-001"
```

---

## Task-002: 收藏功能

### 任务概述
实现景点收藏功能，使用 LocalStorage 存储用户收藏数据。

### 涉及文件

| 类型 | 路径 | 说明 |
|------|------|------|
| 脚本 | `static/js/favorites.js` | 收藏功能逻辑（新建） |
| 模板 | `templates/index.html` | 首页添加收藏入口 |
| 模板 | `templates/spot_detail.html` | 详情页收藏按钮 |

### 数据结构

```javascript
// LocalStorage Key: guigang_favorites
const favorites = [
    {
        id: 1,
        name: "西山风景区",
        added_at: "2026-06-12T10:00:00"
    },
    // ...
];
```

### 接口定义

```javascript
// favorites.js
const FavoritesAPI = {
    getAll: () => favorites[],
    add: (spot) => boolean,
    remove: (spotId) => boolean,
    isFavorited: (spotId) => boolean,
    toggle: (spot) => boolean
};
```

### 页面元素

- [ ] 首页侧边栏「我的收藏」入口
- [ ] 收藏列表页面/弹窗
- [ ] 景点卡片收藏按钮（❤️/🤍）
- [ ] 详情页收藏按钮
- [ ] 收藏数量徽章

### 验收标准

- [ ] 点击收藏按钮后图标变化（❤️）
- [ ] 刷新页面后收藏数据仍存在
- [ ] 取消收藏后数据同步更新
- [ ] 收藏列表正确显示已收藏景点
- [ ] 最多显示最近 50 条收藏

### 提交规范

```bash
git commit -m "feat(Task-002): 实现景点收藏功能

- 新增 favorites.js 模块
- LocalStorage 存储收藏数据
- 首页添加我的收藏入口
- 景点卡片和详情页添加收藏按钮
- 收藏状态持久化

Closes Task-002"
```

---

## Task-003: 最近浏览

### 任务概述
记录用户浏览历史，保存最近 20 条浏览记录。

### 涉及文件

| 类型 | 路径 | 说明 |
|------|------|------|
| 脚本 | `static/js/recent.js` | 浏览记录逻辑（新建） |
| 模板 | `templates/index.html` | 首页添加最近浏览模块 |

### 数据结构

```javascript
// LocalStorage Key: guigang_recent_views
const recentViews = [
    {
        id: 1,
        name: "西山风景区",
        viewed_at: "2026-06-12T10:00:00"
    },
    // 最多保留 20 条
];
```

### 接口定义

```javascript
// recent.js
const RecentAPI = {
    getAll: () => recentViews[],
    add: (spot) => void,
    clear: () => void,
    remove: (spotId) => void
};
```

### 页面元素

- [ ] 首页「最近浏览」模块（横向滚动）
- [ ] 浏览记录卡片（缩略图 + 名称）
- [ ] 清空浏览记录按钮
- [ ] 单条删除功能

### 验收标准

- [ ] 浏览景点后自动记录
- [ ] 首页显示最近浏览模块
- [ ] 最多显示 20 条记录
- [ ] 新记录排在最前面
- [ ] 清空功能正常工作
- [ ] 刷新页面后记录仍存在

### 提交规范

```bash
git commit -m "feat(Task-003): 实现最近浏览功能

- 新增 recent.js 模块
- LocalStorage 存储浏览记录
- 首页添加最近浏览模块（横向滚动）
- 自动记录用户浏览行为
- 支持清空和单条删除

Closes Task-003"
```

---

## Task-004: AI 回答增强

### 任务概述
统一 AI 回答格式，让输出内容结构化、标准化。

### 涉及文件

| 类型 | 路径 | 说明 |
|------|------|------|
| 后端 | `llm_client.py` | 修改 Prompt 模板 |
| 后端 | `app.py` | 调整 AI 接口 |
| 模板 | `templates/index.html` | 优化回答展示样式 |

### Prompt 模板

```
你是一位专业的贵港旅游顾问。请根据以下景点信息，以结构化方式回答用户问题。

景点信息：
{spot_info}

用户问题：{user_question}

请按以下格式回答：

## 🏞️ 景点介绍
[简要介绍]

## ⭐ 推荐指数
⭐⭐⭐⭐⭐（1-5星）

## 🕐 最佳游玩时间
[建议游玩时长]

## 🌸 推荐季节
[最佳季节]

## 🍜 附近美食
- 美食1
- 美食2

## 📍 附近景点
- 景点1
- 景点2

## 🚗 出行建议
[交通/停车/注意事项]

如果信息不足，请说明"暂无相关信息"。
```

### 接口定义

```python
# llm_client.py
def ask_spot_ai(spot_id, question):
    """
    返回结构化 AI 回答
    {
        "intro": "景点介绍",
        "rating": 5,
        "best_time": "最佳游玩时间",
        "best_season": "推荐季节",
        "nearby_foods": [...],
        "nearby_spots": [...],
        "transport": "出行建议"
    }
    """
    pass
```

### 验收标准

- [ ] 所有景点问答统一格式输出
- [ ] 包含推荐指数（1-5星）
- [ ] 包含景点介绍
- [ ] 包含最佳游玩时间
- [ ] 包含推荐季节
- [ ] 包含附近美食
- [ ] 包含附近景点
- [ ] 包含出行建议

### 提交规范

```bash
git commit -m "feat(Task-004): AI 回答增强，统一输出格式

- 新增结构化 Prompt 模板
- llm_client.py 添加 ask_spot_ai 方法
- 统一 AI 回答格式（推荐指数/介绍/时间/季节/美食/景点/建议）
- 优化回答展示样式

Closes Task-004"
```

---

## Task-005: AI 一日游

### 任务概述
根据用户选择生成一日游行程，以时间轴形式展示。

### 涉及文件

| 类型 | 路径 | 说明 |
|------|------|------|
| 模板 | `templates/index.html` | 首页添加一日游入口 |
| 脚本 | `static/js/itinerary.js` | 行程生成逻辑（新建） |
| 后端 | `app.py` | 新增 `/api/itinerary` 接口 |

### 路线类型

- [ ] 摄影路线
- [ ] 亲子路线
- [ ] 美食路线
- [ ] 周末路线

### Prompt 模板

```
请为贵港市规划一条{type}一日游行程。

要求：
1. 时间从 08:00 到 20:00
2. 包含 3-4 个景点
3. 包含午餐和晚餐推荐
4. 每个景点标注建议游玩时长
5. 考虑景点间距离，合理安排路线

请按时间轴格式输出：

08:00 - 出发
09:00 - 景点A（建议游玩2小时）
[景点简介]
12:00 - 午餐推荐：[餐厅名称]
...
```

### 接口定义

```python
@app.route('/api/itinerary', methods=['POST'])
def generate_itinerary():
    """
    生成一日游行程
    Request: { "type": "摄影路线" }
    Response: {
        "type": "摄影路线",
        "schedule": [
            { "time": "08:00", "activity": "出发", "desc": "" },
            { "time": "09:00", "activity": "西山风景区", "desc": "建议游玩2小时", "spot_id": 1 },
            ...
        ]
    }
    """
    pass
```

### 页面元素

- [ ] 首页「生成一日游」按钮
- [ ] 路线类型选择弹窗
- [ ] 行程展示页面（时间轴形式）
- [ ] 保存行程按钮

### 验收标准

- [ ] 点击按钮后自动生成行程
- [ ] 行程以时间轴形式展示
- [ ] 包含合理的景点安排
- [ ] 包含餐饮推荐
- [ ] 生成时间 < 3 秒

### 提交规范

```bash
git commit -m "feat(Task-005): 实现 AI 一日游功能

- 新增 itinerary.js 模块
- 新增 /api/itinerary API 接口
- 支持 4 种路线类型（摄影/亲子/美食/周末）
- 时间轴形式展示行程
- 包含景点和餐饮推荐

Closes Task-005"
```

---

## Task-006: 首页推荐卡

### 任务概述
在首页添加多种推荐卡片，点击自动发起 AI 请求。

### 涉及文件

| 类型 | 路径 | 说明 |
|------|------|------|
| 模板 | `templates/index.html` | 首页添加推荐卡区域 |
| 样式 | `static/css/index.css` | 推荐卡样式（已有） |

### 推荐类型

- [ ] 今日推荐
- [ ] 周末推荐
- [ ] 雨天推荐
- [ ] 摄影路线
- [ ] 亲子路线

### 页面元素

```html
<!-- 推荐卡结构 -->
<div class="recommend-cards">
    <div class="rec-card" data-type="today">
        <div class="rec-icon">🌟</div>
        <div class="rec-title">今日推荐</div>
    </div>
    <div class="rec-card" data-type="weekend">
        <div class="rec-icon">🏖️</div>
        <div class="rec-title">周末推荐</div>
    </div>
    <!-- ... -->
</div>
```

### 交互逻辑

```javascript
// 点击推荐卡 → 自动发送 AI 请求
function onRecCardClick(type) {
    const prompts = {
        today: "今天去贵港哪里玩比较好？",
        weekend: "推荐贵港周末游玩的地方",
        rainy: "下雨天贵港适合去哪里？",
        photo: "推荐贵港适合摄影的地方",
        family: "推荐贵港适合亲子游的地方"
    };
    quickAsk(prompts[type]);
}
```

### 验收标准

- [ ] 首页显示推荐卡区域
- [ ] 5 种推荐类型全部实现
- [ ] 点击后自动发起 AI 请求
- [ ] 卡片样式美观，响应式布局

### 提交规范

```bash
git commit -m "feat(Task-006): 首页添加推荐卡功能

- 首页新增推荐卡区域
- 支持 5 种推荐类型（今日/周末/雨天/摄影/亲子）
- 点击自动发起 AI 问答
- 响应式卡片布局

Closes Task-006"
```

---

## Task-007: 图片库

### 任务概述
为每个景点添加图片库，支持轮播展示。

### 涉及文件

| 类型 | 路径 | 说明 |
|------|------|------|
| 目录 | `static/images/spots/` | 景点图片目录（新建） |
| 模板 | `templates/spot_detail.html` | 添加图片轮播 |
| 知识库 | `knowledge_base_v4.py` | 图片字段支持 |

### 目录结构

```
static/images/spots/
├── 1/                    # 景点 ID 为 1
│   ├── 1.jpg
│   ├── 2.jpg
│   └── 3.jpg
├── 2/
│   ├── 1.jpg
│   ├── 2.jpg
│   └── 3.jpg
└── ...
```

### 知识库字段

```python
{
    "id": 1,
    "name": "西山风景区",
    "images": [
        "/static/images/spots/1/1.jpg",
        "/static/images/spots/1/2.jpg",
        "/static/images/spots/1/3.jpg"
    ],
    # ...
}
```

### 页面元素

- [ ] 图片轮播组件
- [ ] 左右切换按钮
- [ ] 指示器（小圆点）
- [ ] 图片计数（1/3）
- [ ] 全屏查看功能

### 验收标准

- [ ] 每个景点至少 3 张图片
- [ ] 轮播自动播放（5秒间隔）
- [ ] 支持手动切换
- [ ] 图片加载优化（懒加载）
- [ ] 移动端手势支持（左右滑动）

### 提交规范

```bash
git commit -m "feat(Task-007): 实现景点图片库功能

- 新增 static/images/spots/ 目录结构
- 知识库新增 images 字段
- 详情页添加图片轮播组件
- 支持自动播放和手动切换
- 移动端手势支持

Closes Task-007"
```

---

## Task-008: 附近推荐

### 任务概述
在景点详情页展示附近景点、美食、住宿。

### 涉及文件

| 类型 | 路径 | 说明 |
|------|------|------|
| 知识库 | `knowledge_base_v4.py` | 新增附近数据字段 |
| 模板 | `templates/spot_detail.html` | 添加附近推荐区域 |
| 后端 | `app.py` | 新增附近推荐 API |

### 知识库新增字段

```python
{
    "id": 1,
    "name": "西山风景区",
    "nearby_spots": [
        {"id": 2, "name": "景点B", "distance": "2.5km"},
        {"id": 3, "name": "景点C", "distance": "3.8km"}
    ],
    "nearby_foods": [
        {"name": "餐厅A", "type": "本地菜", "distance": "1.2km"},
        {"name": "餐厅B", "type": "小吃", "distance": "2.0km"}
    ],
    "nearby_hotels": [
        {"name": "酒店A", "stars": 4, "distance": "3.0km"},
        {"name": "民宿B", "stars": 3, "distance": "1.5km"}
    ]
}
```

### 接口定义

```python
@app.route('/api/spot/<int:spot_id>/nearby')
def get_nearby(spot_id):
    """
    返回附近推荐
    {
        "spots": [...],
        "foods": [...],
        "hotels": [...]
    }
    """
    pass
```

### 页面元素

- [ ] 「附近景点」横向滚动卡片
- [ ] 「附近美食」列表
- [ ] 「附近住宿」列表
- [ ] 距离标签
- [ ] 点击跳转功能

### 验收标准

- [ ] 详情页显示附近推荐区域
- [ ] 附近景点可点击跳转
- [ ] 距离信息准确显示
- [ ] 无数据时显示友好提示

### 提交规范

```bash
git commit -m "feat(Task-008): 实现附近推荐功能

- 知识库新增 nearby_spots/nearby_foods/nearby_hotels 字段
- 新增 /api/spot/<id>/nearby API 接口
- 详情页添加附近推荐区域
- 支持附近景点/美食/住宿展示

Closes Task-008"
```

---

## Task-009: 路线推荐

### 任务概述
预置多条经典旅游路线，用户可以查看和选择。

### 涉及文件

| 类型 | 路径 | 说明 |
|------|------|------|
| 数据 | `data/routes.json` | 路线数据（新建） |
| 模板 | `templates/index.html` | 首页添加路线推荐 |
| 模板 | `templates/route_detail.html` | 路线详情页（新建） |
| 后端 | `app.py` | 新增路线相关路由 |

### 路线数据

```json
{
    "routes": [
        {
            "id": "classic-1day",
            "name": "贵港经典一日游",
            "type": "经典",
            "duration": "1天",
            "spots": [1, 2, 3],
            "description": "涵盖贵港最经典的景点...",
            "cover_image": "/static/images/routes/classic.jpg"
        },
        {
            "id": "photo-1day",
            "name": "摄影爱好者路线",
            "type": "摄影",
            "duration": "1天",
            "spots": [4, 5, 6],
            "description": "最佳摄影点位...",
            "cover_image": "/static/images/routes/photo.jpg"
        }
    ]
}
```

### 预置路线

- [ ] 贵港经典一日游
- [ ] 摄影路线
- [ ] 亲子路线
- [ ] 自驾路线

### 页面元素

- [ ] 路线卡片（封面图 + 名称 + 时长）
- [ ] 路线详情页
- [ ] 路线地图
- [ ] 景点列表（可点击跳转）
- [ ] 使用此路线按钮

### 接口定义

```python
@app.route('/api/routes')
def get_routes():
    """返回所有路线"""
    pass

@app.route('/api/routes/<route_id>')
def get_route_detail(route_id):
    """返回路线详情"""
    pass
```

### 验收标准

- [ ] 首页显示路线推荐区域
- [ ] 至少 4 条预置路线
- [ ] 路线详情页完整展示
- [ ] 景点可点击跳转
- [ ] 路线数据可扩展

### 提交规范

```bash
git commit -m "feat(Task-009): 实现路线推荐功能

- 新增 data/routes.json 路线数据
- 新增 /api/routes 和 /api/routes/<id> 接口
- 首页添加路线推荐区域
- 新增 route_detail.html 路线详情页
- 预置 4 条经典路线

Closes Task-009"
```

---

## Task-010: 用户偏好

### 任务概述
首次进入系统时让用户选择偏好，用于个性化推荐。

### 涉及文件

| 类型 | 路径 | 说明 |
|------|------|------|
| 脚本 | `static/js/preferences.js` | 偏好设置逻辑（新建） |
| 模板 | `templates/index.html` | 添加偏好选择弹窗 |

### 偏好选项

- [ ] 摄影
- [ ] 美食
- [ ] 亲子
- [ ] 自驾
- [ ] 露营
- [ ] 历史文化

### 数据结构

```javascript
// LocalStorage Key: guigang_preferences
const preferences = {
    interests: ["摄影", "美食"],  // 用户选择的偏好
    selected_at: "2026-06-12T10:00:00",
    version: "1.0"
};
```

### 页面元素

- [ ] 首次进入弹窗（欢迎 + 偏好选择）
- [ ] 偏好选项（多选）
- [ ] 确认按钮
- [ ] 跳过按钮
- [ ] 设置入口（侧边栏）
- [ ] 修改偏好功能

### 交互逻辑

```javascript
// 首次进入检测
function checkFirstVisit() {
    const prefs = localStorage.getItem('guigang_preferences');
    if (!prefs) {
        showPreferenceModal();
    }
}

// 根据偏好推荐
function getRecommendationsByPreference() {
    const prefs = PreferencesAPI.get();
    // 根据偏好筛选推荐内容
}
```

### 验收标准

- [ ] 首次进入显示偏好选择弹窗
- [ ] 支持多选偏好
- [ ] 偏好数据持久化
- [ ] 根据偏好调整首页推荐
- [ ] 可随时修改偏好

### 提交规范

```bash
git commit -m "feat(Task-010): 实现用户偏好功能

- 新增 preferences.js 模块
- 首次进入显示偏好选择弹窗
- 支持 6 种偏好类型（摄影/美食/亲子/自驾/露营/历史文化）
- LocalStorage 存储偏好数据
- 根据偏好个性化推荐内容
- 支持随时修改偏好

Closes Task-010"
```

---

## 📊 任务总览

| 任务 | 名称 | 预计工时 | 优先级 | 依赖 |
|------|------|----------|--------|------|
| Task-001 | 景点详情页 | 4h | P0 | - |
| Task-002 | 收藏功能 | 3h | P0 | Task-001 |
| Task-003 | 最近浏览 | 2h | P0 | Task-001 |
| Task-004 | AI 回答增强 | 4h | P0 | - |
| Task-005 | AI 一日游 | 4h | P1 | Task-004 |
| Task-006 | 首页推荐卡 | 2h | P1 | - |
| Task-007 | 图片库 | 4h | P1 | Task-001 |
| Task-008 | 附近推荐 | 3h | P1 | Task-001, Task-007 |
| Task-009 | 路线推荐 | 4h | P2 | - |
| Task-010 | 用户偏好 | 3h | P2 | Task-006 |

**总预计工时：** 33 小时（约 4-5 天）

---

## 🔄 工作流程

```
1. 领取任务 → 创建 feature 分支
        ↓
2. 开发实现 → 本地测试
        ↓
3. 提交代码 → 规范 commit message
        ↓
4. 更新文档 → README / CHANGELOG
        ↓
5. 合并分支 → 标记任务完成
        ↓
6. 领取下一个任务
```

---

**最后更新：** 2026-06-12  
**版本：** V1.0
