# 贵港旅游智能助手

基于 **RAG（检索增强生成）** + **LLM** 的贵港市旅游问答助手，支持景点推荐、美食攻略、住宿建议、行程规划。

## 功能特性

- 31个景点/美食覆盖港北区、港南区、覃塘区、桂平市、平南县
- 智能住宿推荐，先近后远，每个景点配备 nearby_hotels
- 美食推荐，本地特色美食问答
- LLM 增强回答，接入大语言模型，知识库覆盖不到时也能回答
- 模糊查询，支持别名匹配（平天山 → 平天山国家森林公园）
- 多轮对话，支持上下文记忆（最近10轮）
- PWA 支持，可安装到手机桌面

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Flask (Python) |
| 知识库 | 本地 Python 数据结构（RAG） |
| LLM | OpenAI 兼容 API（可选，无 LLM 也可纯本地运行） |
| 前端 | HTML + CSS + JavaScript |
| 部署 | cloudflared / cpolar 公网隧道 |

## 快速开始

### 环境要求

- Python 3.8+
- Flask: `pip install flask`

### 启动服务

```bash
cd guigang-travel-demo
python app.py
```

服务默认运行在 `http://0.0.0.0:5001`

### 配置 LLM（可选）

```bash
# 设置环境变量
export LLM_API_BASE=http://127.0.0.1:8642/v1
export LLM_API_KEY=your-api-key
export LLM_MODEL=your-model-name
```

或使用一键启动脚本：
```powershell
.\start_all.ps1
```

## 项目结构

```
guigang-travel-demo/
├── app.py                  # Flask 主程序（路由、对话、推荐逻辑）
├── knowledge_base_v4.py   # 知识库数据（31个景点/美食 + 附近住宿）
├── llm_client.py           # LLM API 客户端
├── start_all.ps1           # 一键启动脚本（Flask + cpolar）
├── static/                 # 前端静态资源 + PWA
├── templates/
│   └── index.html          # 前端页面
└── README.md
```

## 知识库覆盖

| 行政区 | 景点/美食数量 |
|--------|-------------|
| 港北区 | 7 |
| 港南区 | 3 |
| 覃塘区 | 3 |
| 桂平市 | 9 |
| 平南县 | 7 |

## License

MIT
