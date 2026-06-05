# 贵港旅游智能助手 — 开发移交文档

> 移交日期：2026-06-04
> 当前状态：✅ 运行中（localhost:5001，ngrok 公网可达）
> 交接给：Qclaw（后续开发方）
> 最新更新：2026-06-05（内容扩充 v2.0）

---

## 一、项目结构

```
guigang-travel-demo/
├── app.py                    # Flask 后端主程序
├── knowledge_base.py         # 知识库（13个景点 + 扩充旅游贴士 v2.0）
├── llm_client.py             # LLM API 调用封装
├── start_demo.sh             # 启动脚本
├── templates/
│   └── index.html            # 前端聊天界面（微信风格，支持景点图片）
├── static/
│   └── images/              # （景点图片目前使用 Unsplash 外链）
└── README-doc.md             # 本文件
```

## 二、架构总览

```
用户（手机/PC）
    │
    ├── Ngrok 隧道 ──→ localhost:5001 ──→ Flask app
    │   (公网地址: https://rarity-mushroom-jolly.ngrok-free.dev)
    │
    └── 前端 (index.html，微信小程序风格)
            │
            POST /api/chat { message: "..." }
            │
    ┌───────┴────────┐
    │   app.py 后端    │
    │                  │
    │  1. RAG 检索     │ ← knowledge_base.py (13个景点+扩充贴士)
    │   │               │
    │  2. LLM 优先     │ ← llm_client.py (OpenAI兼容接口)
    │   │               │     默认指向 Hermes API 8642 端口
    │   │               │
    │  3. 降级本地模式  │ ← generate_local_reply() 纯知识库回复
    │                  │
    └──────────────────┘
```

### 关键设计决策

1. **LLM 优先，本地兜底** — 有 LLM 用 LLM（RAG+LLM 回答），LLM 不可用时自动降级为纯本地知识库回复，前端永不报错
2. **零外部依赖** — 只用 Flask 和 Python 标准库，无需安装第三方包
3. **微信风格前端** — 单页应用，左侧抽屉景点列表（支持缩略图），快速提问按钮，打字动画
4. **景点全图片覆盖** — 13个景点均有 Unsplash 免费图片，聊天回复含图片链接

## 三、当前运行状态

| 项目 | 详情 |
|---|---|
| 后端端口 | localhost:5001 |
| LLM 接口 | Hermes API Server (127.0.0.1:8642) + DeepSeek V4 Flash |
| LLM 模式 | ✅ 已接通（AI 模式） |
| 知识库景点数 | 13 个 |
| 景点图片覆盖 | 13/13（100%） |
| 公网地址 | https://rarity-mushroom-jolly.ngrok-free.dev |
| 后端进程 | ✅ 运行中 |

### 当前 LLM 配置（app.py 第17-19行）

```python
LLM_API_BASE = os.environ.get("LLM_API_BASE", "http://127.0.0.1:8642/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "hermes-local-auth-key-2026")
LLM_MODEL = os.environ.get("LLM_MODEL", None)  # 不指定则服务端默认模型
```

通过环境变量切换 LLM：

```bash
set LLM_API_BASE=https://api.openai.com/v1
set LLM_API_KEY=sk-xxx
set LLM_MODEL=gpt-4o
python app.py
```

## 四、景点知识库列表（knowledge_base.py）

| ID | 景点名称 | 类别 | 票价 | 评级 | 图片 |
|---|---|---|---|---|---|
| xishan | 西山风景区 | 自然景观 | 80/60元 | AAAA | ✓ |
| longtan | 龙潭国家森林公园 | 自然景观 | 60元 | AAAA | ✓ |
| nanshan | 南山寺 | 人文景观 | 20元 | AAA | ✓ |
| donghu | 东湖公园 | 城市公园 | 免费 | - | ✓ |
| museum | 贵港博物馆 | 人文景观 | 免费(凭身份证) | - | ✓ |
| yujiang | 郁江沿岸风光带 | 自然景观 | 免费 | - | ✓ |
| dategxia | 大藤峡 | 自然景观 | 50元 | AAAA | ✓ |
| century_square | 世纪广场 | 城市公园 | 免费 | - | ✓ |
| culture_park | 民族文化公园 | 人文景观 | 免费 | AAA | ✓ |
| pingtian | 平天山国家森林公园 | 自然景观 | 40元 | AAAA | ✓ |
| yuanboyuan | 贵港园博园 | 城市公园 | 免费 | AAA | ✓ |
| laiyuan_pavilion | 桂平乳泉亭 | 自然景观 | 免费 | - | ✓ |
| guiping_old_street | 桂平市区老街 | 人文景观 | 免费 | - | ✓ |

每个景点包含：名称/别名/位置/票价/开放时间/简介/亮点/推荐路线/小贴士/附近景点/**图片URL**

**新增景点预览：**
- 🏛️ **世纪广场** — 城市中心，免费，音乐喷泉，城市客厅
- 🏺 **民族文化公园** — 壮族文化，壮锦织造坊，三月三歌圩
- ⛰️ **平天山国家森林公园** — 贵港最高峰（1157m），高山草甸，日出云海
- 🌺 **贵港园博园** — 广西园林精华，四季花海，免费
- 💧 **桂平乳泉亭** — 免费品泉古井，千年古樟，无需门票
- 🏮 **桂平市区老街** — 民国骑楼，百年老字号，桂圆干制作

旅游贴士涵盖：交通（高铁/自驾/市内/机场/停车指南）、住宿（经济/酒店/特色民宿/预订建议）、美食（特色/餐厅/罗秀米粉/壮乡美食/老街夜市/特产伴手礼）、行程（1-4日/亲子/文化/自然/摄影/避峰）、购物（壮锦/桂圆干）、夜生活、紧急联系

## 五、内容扩充统计（v2.0）

| 类别 | v1.0 | v2.0 |
|------|------|------|
| 景点数量 | 7个 | 13个 |
| 景点图片 | 0 | 13个(100%覆盖) |
| 旅游贴士分类 | ~10个 | ~28个 |
| 行程方案 | 3个 | 6个（含四日深度游+摄影+避峰） |
| 美食专题 | 2个 | 9个（含罗秀米粉/老街夜市/特产区/壮乡美食） |
| 住宿方案 | 基础3段 | 4段+经济住宿+预订建议 |
| 交通指南 | 4段 | 5段+停车指南 |
| 检索关键词 | ~15个 | ~35个 |

## 六、启动与维护

### 正常启动

```bash
cd C:\Users\shish\Desktop\guigang-travel-demo
set PORT=5001
python app.py
```

### 启动 ngrok 公网隧道

```bash
"C:\Users\shish\AppData\Local\hermes\bin\ngrok.exe" http 5001
```

### 验证端到端

```bash
# 测试后端
curl http://localhost:5001/api/status

# 测试 LLM
curl http://localhost:5001/api/test-llm

# 测试公网
curl -sk https://rarity-mushroom-jolly.ngrok-free.dev/api/status
```

## 七、API 接口文档

### GET / — 首页（渲染前端模板）

### POST /api/chat — 聊天接口
```json
// 请求
{ "message": "西山风景区有什么好玩的？" }

// 响应
{ "reply": "## 西山风景区\n📍 位置：桂平市西山镇\n..." }
```

### GET /api/spots — 获取所有景点列表（精简信息，含图片URL）
```json
[
  { "id": "xishan", "name": "西山风景区", "category": "自然景观",
    "rating": "AAAA", "description": "西山风景区是...",
    "image_url": "https://...", "ticket_price": "80元", "location": "桂平市西山镇" }
]
```

### GET /api/spot/<id> — 获取单个景点详情（完整信息）

### GET /api/status — 系统状态
```json
{ "llm_available": true, "llm_api": "http://127.0.0.1:8642/v1",
  "mode": "llm", "spots_count": 13 }
```

## 八、后续可扩展方向（供 Qclaw 参考）

### 短期（1-2天）
- [x] **补充更多景点** — 世纪广场、民族文化公园、平天山等（✅ 已完成，13个景点）
- [x] **增加景点图片** — 添加 image_url 字段，前端侧边栏展示（✅ 已完成）
- [x] **多轮对话上下文** — 支持追问（如"怎么去"自动关联前文提到的景点）（✅ 已完成）
- [ ] **接入地图 API** — 点击位置直接跳转高德/百度地图
- [ ] **美食攻略细化** — 增加餐厅地址、电话、营业时间

### 中期（1-2周）
- [ ] **对话历史持久化** — SQLite 存储历史记录（目前内存存储，重启清空）
- [ ] **用户反馈机制** — 回答好评/差评，优化知识库
- [x] **多轮对话上下文** — ✅ 已完成（支持"怎么去"/"门票多少"/"附近有什么"等模糊追问）
- [ ] **嵌入 Qclaw 平台** — 对接 Qclaw 的对话管理
- [ ] **语音输入** — Web Speech API 支持语音提问

### 长期
- [ ] **微信小程序封装** — 这套前端本身就是微信风格，可移植
- [ ] **实时票务查询** — 对接景区官方接口查余票/排队
- [ ] **个性化推荐** — 基于用户偏好推荐行程
- [ ] **多语言支持** — 英文/粤语/壮语

## 九、技术细节

### 后端（app.py）
- Flask 单线程开发服务器（如需生产环境，建议换 gunicorn/uvicorn）
- RAG 检索算法：关键词匹配 + 评分排序（名称10分 > 别名8分 > 类别5分 > 意图3分）
- 检索关键词扩充至 ~35 个，覆盖新增景点和意图（广场/民族/登山/日出/夜景/摄影/老街等）
- LLM 调用：urllib 原生请求，零依赖
- 自动降级：LLM 返回 [API 错误] 或 [请求失败] 时切换到本地模式

### 前端（index.html）
- Pure CSS + Vanilla JS，无框架依赖
- 类微信气泡聊天 UI，适配手机屏幕
- 快速提问按钮 6 个预设问题
- 左侧抽屉景点列表，点击快速提问（支持景点缩略图，图片加载失败自动隐藏）
- AI 模式/本地模式状态指示
- `/api/spots` 接口新增 `image_url` / `ticket_price` / `location` 字段

### 知识库（knowledge_base.py）
- Python dict 字典，可直接追加景点
- 每个景点新增 `image_url` 字段（Unsplash 免费图片 URL）
- 景点数据结构：id/name/alias/category/location/rating/ticket_price/open_time/**image_url**/description/highlights/recommended_route/tips/nearby_spots
- 意图匹配关键词表在 `generate_local_reply()` 中，已扩充

---

**移交人：Hermes（INTJ 战略伙伴）**
**编写时间：2026-06-04 18:00**
**最后更新：2026-06-05（v2.0 内容扩充）**