"""
贵港旅游智能助手 - Flask 后端
核心：RAG（检索增强生成）+ 可选 LLM 调用
支持本地纯知识库模式（无 LLM 也可运行）
"""

import os
import json
import random
from flask import Flask, request, jsonify, render_template

from knowledge_base_v4 import SCENIC_SPOTS, TRAVEL_TIPS, CATEGORY_INDEX, DISTRICT_STATS

app = Flask(__name__)

# ── 对话上下文存储（内存存储，重启后清空） ───────────────
# 格式: {session_id: [ {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."} ] }
SESSION_HISTORY = {}
MAX_HISTORY_LEN = 10  # 保留最近10轮对话

# ── LLM 配置（可选） ──────────────────────────────
LLM_API_BASE = os.environ.get("LLM_API_BASE", "http://127.0.0.1:11434/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "ollama")
LLM_MODEL = os.environ.get("LLM_MODEL", None)

# 检查 LLM 是否可用
_llm_available = False
_llm_client = None

def get_llm_client():
    global _llm_available, _llm_client
    if _llm_client is not None:
        return _llm_client

    try:
        import urllib.request
        req = urllib.request.Request(
            f"{LLM_API_BASE}/models",
            headers={"Authorization": f"Bearer {LLM_API_KEY}"},
        )
        urllib.request.urlopen(req, timeout=3)
        # 如果通了，导入 LLM 客户端
        from llm_client import LLMClient
        _llm_client = LLMClient(LLM_API_BASE, LLM_API_KEY, LLM_MODEL)
        _llm_available = True
        print(f"  LLM API 已连接: {LLM_API_BASE}")
    except Exception as e:
        _llm_available = False
        print(f"  LLM API 未连接（使用纯本地模式）: {e}")
    return _llm_client

# ── 知识检索（RAG） ───────────────────────────────

def extract_spot_from_query(query):
    """从用户查询中提取明确提到的景点（支持完整名、别名、部分名匹配）"""
    for spot in SCENIC_SPOTS:
        # 完整名称匹配
        if spot["name"] in query:
            return spot
        # 别名精确匹配
        for alias in spot["alias"]:
            if alias and alias in query:
                return spot
    # 部分匹配：查询中包含景点名的核心词（如"平天山"匹配"平天山国家森林公园"）
    for spot in SCENIC_SPOTS:
        # 取景点名去掉"国家森林公园"等常见后缀后的核心词
        core_name = spot["name"]
        for suffix in ["国家森林公园", "旅游区", "风景区", "国家湿地公园", "公园"]:
            if core_name.endswith(suffix):
                core_name = core_name[:-len(suffix)]
                break
        if core_name and len(core_name) >= 3 and core_name in query:
            return spot
        # 别名也做部分匹配
        for alias in spot["alias"]:
            if alias and len(alias) >= 3 and alias in query:
                return spot
    return None

def search_scenic_spots(query):
    """根据用户输入检索相关景点"""
    results = []
    query_lower = query.lower()
    # 行政区划关键词映射
    district_map = {
        "港北": "港北区", "港北区": "港北区",
        "港南": "港南区", "港南区": "港南区",
        "覃塘": "覃塘区", "覃塘区": "覃塘区",
        "桂平": "桂平市", "桂平市": "桂平市",
        "平南": "平南县", "平南县": "平南县",
    }
    
    # 检测是否按行政区划查询
    target_district = None
    for kw, district in district_map.items():
        if kw in query:
            target_district = district
            break
    
    for spot in SCENIC_SPOTS:
        score = 0
        # 名称匹配
        if spot["name"] in query:
            score += 10
        for alias in spot["alias"]:
            if alias in query:
                score += 8
        if spot["category"] in query:
            score += 5
        
        # 行政区划匹配
        if target_district and spot.get("district") == target_district:
            score += 15  # 高优先级匹配行政区划
        
        # 喜好匹配（只在已有匹配分数时生效，避免误匹配）
        if score > 0:
            pref_map = {
                "自然": "自然景观", "爬山": "自然景观", "风景": "自然景观",
                "山水": "自然景观", "人文": "人文景观", "历史": "人文景观",
                "文化": "人文景观", "寺庙": "人文景观", "公园": "城市公园",
                "免费": "免费", "小孩": "城市公园", "亲子": "城市公园",
                "峡谷": "自然景观", "瀑布": "自然景观", "森林": "自然景观",
                "广场": "城市公园", "民族": "人文景观", "登山": "自然景观",
                "日出": "自然景观", "氧吧": "自然景观", "徒步": "自然景观",
                "夜景": "城市公园", "拍照": "城市公园", "摄影": "自然景观",
                "博物馆": "人文景观", "展馆": "人文景观", "历史": "人文景观",
                "老街": "人文景观", "古镇": "人文景观", "步行街": "人文景观",
                "动物": "主题乐园", "动物园": "主题乐园", "玻璃": "自然景观",
                "湿地": "自然景观", "荷花": "农业观光", "湖": "自然景观",
                "道教": "人文景观", "起义": "人文景观", "北回归线": "科普教育",
            }
            for kw, cat in pref_map.items():
                if kw in query_lower and (spot["category"] == cat or "免费" in spot.get("ticket_price", "")):
                    score += 3

        if score > 0:
            results.append((score, spot))

    results.sort(key=lambda x: -x[0])
    return [r[1] for r in results[:5]]  # 增加到5个结果

def get_travel_tips(query):
    """检索旅游贴士——整键匹配，避免单字符误匹配"""
    return [(k, v) for k, v in TRAVEL_TIPS.items() if k in query]

def build_context(spots, tips):
    """组装知识上下文"""
    parts = []
    if spots:
        parts.append("【贵港市相关景点信息】")
        for s in spots:
            hls = "\n".join(f"  - {h}" for h in s["highlights"])
            parts.append(
                f"景点：{s['name']}\n类别：{s['category']}\n位置：{s['location']}\n"
                f"票价：{s['ticket_price']}\n开放时间：{s['open_time']}\n"
                f"简介：{s['description']}\n亮点：\n{hls}\n推荐路线：{s['recommended_route']}\n"
                f"小贴士：{s['tips']}"
            )
    if tips:
        parts.append("【旅游贴士】")
        parts.extend(f"{k}：{v}" for k, v in tips)
    return "\n".join(parts)

def _build_free_spots_reply():
    """生成免费景点推荐列表"""
    free_spots = [s for s in SCENIC_SPOTS if "免费" in s.get("ticket_price", "")]
    district_order = ["港北区", "港南区", "覃塘区", "桂平市", "平南县"]
    grouped = {d: [] for d in district_order}
    for s in free_spots:
        d = s.get("district", "")
        if d in grouped:
            grouped[d].append(s)
    lines = [f"贵港市免费景点共 **{len(free_spots)}** 个\n"]
    for d in district_order:
        ds = grouped[d]
        if not ds:
            continue
        lines.append(f"**{d}（{len(ds)}个）**")
        for s in ds:
            lines.append(f"• {s['name']} — {s['description'][:50]}...")
        lines.append("")
    lines.append("💡 免费景点性价比超高，适合周末休闲、亲子出游！")
    return "\n".join(lines)


def generate_local_reply(query, spots, tips, current_topic=None):
    """纯本地模式：不依赖 LLM，直接根据知识库生成回答"""
    lines = []
    explicit_spot = None  # 初始化，防止未定义
    
    # 函数入口处统一计算 explicit_spot，供后续分支复用
    explicit_spot = extract_spot_from_query(query)
    
    # 处理模糊查询（如"怎么去"、"门票多少"）
    fuzzy_keywords = ["怎么去", "怎么去那里", "怎么去啊", "怎么去呢", "怎么去这个地方", 
                      "怎么走", "怎么去方便", "怎么去最快", "怎么去最方便",
                      "门票多少", "多少钱", "票价", "票价多少", "门票价格",
                      "开放时间", "几点开门", "几点关门", "什么时候开",
                      "附近有什么", "周边", "附近景点", "旁边有什么",
                      "有什么好吃的", "吃什么", "附近美食", "周边美食",
                      "住哪里", "住宿", "酒店", "民宿",
                      "拍照", "摄影", "打卡", "哪里好看", "哪里拍照",
                      "有什么玩的", "玩什么", "好玩吗", "怎么样", "值得去吗",
                      "有什么特色", "特色", "推荐", "介绍", "简介", "亮点"]
    
    is_fuzzy = any(kw in query for kw in fuzzy_keywords)

    # 模糊查询：优先用明确提到的景点，其次用当前话题
    if is_fuzzy:
        target_spot = extract_spot_from_query(query)
        if not target_spot and current_topic:
            for spot in SCENIC_SPOTS:
                if spot["name"] == current_topic or current_topic in spot.get("alias", []):
                    target_spot = spot
                    break

        if target_spot:
            # 根据问题类型返回精准回答，不输出景点全量信息
            if any(kw in query for kw in ["怎么去", "怎么走", "怎么去方便"]):
                return (f"去{target_spot['name']}的交通方式：\n\n"
                        f"📍 位置：{target_spot['location']}\n"
                        f"🚗 自驾：导航至「{target_spot['name']}」\n"
                        f"🚌 公交：{target_spot.get('tips', '建议查询实时公交').split('；')[0] if '公交' in target_spot.get('tips', '') else '市区可乘公交或打车前往'}\n\n"
                        f"💡 {target_spot['tips'][:100]}")

            if any(kw in query for kw in ["门票", "多少钱", "票价"]):
                return (f"{target_spot['name']}的门票信息：\n\n"
                        f"💰 票价：{target_spot['ticket_price']}\n"
                        f"🕐 开放时间：{target_spot['open_time']}\n\n"
                        f"💡 {target_spot['tips'][:100]}...")

            if any(kw in query for kw in ["附近", "周边", "旁边"]):
                nearby = target_spot.get('nearby_spots', [])
                if nearby:
                    return (f"{target_spot['name']}附近的景点：\n\n" +
                            '\n'.join(f"• {s}" for s in nearby) +
                            f"\n\n可以安排在同一天游览，节省时间~")
                else:
                    return f"{target_spot['name']}周边还有其他景点，建议查看旅游攻略规划路线~"

            if any(kw in query for kw in ["吃", "美食", "好吃的"]):
                return (f"{target_spot['name']}附近的美食推荐：\n\n"
                        f"• 贵港米粉：当地特色，汤鲜粉滑\n"
                        f"• 桂平西山茶：清香甘醇\n"
                        f"• 郁江鱼鲜：新鲜河鱼\n"
                        f"• 壮乡糯米饭：香甜软糯\n\n"
                        f"建议去老街夜市或当地餐厅品尝，人均30-80元。")

            if any(kw in query for kw in ["住", "住宿", "酒店", "民宿", "住哪里"]):
                nearby_hotels = target_spot.get('nearby_hotels', [])
                if nearby_hotels:
                    lines = [f"{target_spot['name']}附近的住宿推荐（按距离由近到远）：\n"]
                    for i, hotel in enumerate(nearby_hotels, 1):
                        lines.append(f"{i}. **{hotel['name']}**")
                        lines.append(f"   🏷️ {hotel['type']} | 💰 {hotel['price']}")
                        lines.append(f"   📍 {hotel['distance']}")
                        lines.append(f"   💡 {hotel['note']}")
                    return "\n".join(lines)
                else:
                    district = target_spot.get('district', '')
                    if district == "覃塘区":
                        return (f"{target_spot['name']}附近的住宿推荐（先近后远）：\n\n"
                                f"🏨 覃塘镇商务酒店（最近，约15分钟车程）：120-200元/晚\n"
                                f"🏡 蒙公农家乐（约20分钟）：100-180元/晚\n"
                                f"🏨 贵港市区酒店（约30-40分钟）：200-350元/晚\n\n"
                                f"💡 建议优先选覃塘镇或蒙公镇，距离更近。")
                    elif district == "桂平市":
                        return (f"{target_spot['name']}附近的住宿推荐（先近后远）：\n\n"
                                f"🏡 西山脚下民宿群（最近）：280-450元/晚\n"
                                f"🏨 桂平市区酒店：150-250元/晚（经济型）\n\n"
                                f"💡 游览西山建议住西山脚下，其他景点住市区更方便。")
                    elif district == "平南县":
                        return (f"{target_spot['name']}附近的住宿推荐（先近后远）：\n\n"
                                f"🏡 大鹏镇民宿（北帝山附近，最近）：150-300元/晚\n"
                                f"🏨 平南县城酒店：150-220元/晚（经济型）\n\n"
                                f"💡 游览北帝山建议住大鹏镇，其他情况住县城。")
                    else:
                        return (f"{target_spot['name']}附近的住宿推荐（先近后远）：\n\n"
                                f"🏨 港北区市中心（最近）：200-350元/晚\n"
                                f"🏨 港南区（近南山寺）：各档次均有\n\n"
                                f"💡 建议根据行程选择，市区选择最多。")

            if any(kw in query for kw in ["拍照", "摄影", "打卡"]):
                return (f"{target_spot['name']}的拍照打卡点：\n\n" +
                        '\n'.join(f"📷 {h}" for h in target_spot.get('highlights', [])[:3]) +
                        f"\n\n💡 {target_spot['tips'][:80]}...")

        else:
            if any(kw in query for kw in ["住", "住宿", "酒店", "民宿", "住哪里"]):
                return "你想了解哪个景点的住宿信息？请告诉我景点名称，比如「平天山」、「西山」等。"
            elif any(kw in query for kw in ["吃", "美食", "好吃的"]):
                return "你想了解哪个景点附近的美食？请告诉我景点名称，比如「平天山」、「西山」等。"
            elif any(kw in query for kw in ["怎么去", "怎么走"]):
                return "你想去哪个景点？请告诉我景点名称，比如「平天山」、「西山」等。"

    # 以下是非模糊查询的正常流程
    # 注意：模糊查询已在上面的分支中 return，不会走到这里

    # 免费景点查询（优先拦截，不走景点详情分支）
    if "免费" in query:
        return _build_free_spots_reply()

    # 问候类
    greetings = ["你好", "您好", "hi", "hello", "在吗", "在不在"]
    if any(g in query.lower() for g in greetings):
        return ("你好！我是贵港旅游智能助手 🏞️\n\n"
                "我可以帮你：\n"
                "• 查询景点信息（按区县：港北区、港南区、覃塘区、桂平市、平南县）\n"
                "• 推荐旅游行程（一日/两日/三日/五日游）\n"
                "• 介绍贵港美食和特产\n"
                "• 解答交通、住宿等问题\n\n"
                "你想了解什么？")
    
    if not spots and not tips:
        # 尝试理解意图
        intent_keywords = {
            "港北": "港北区是贵港市中心城区，主要景点有：\n• 东湖公园（免费）：市区最大公园\n• 贵港博物馆（免费）：了解贵港历史文化\n• 世纪广场（免费）：市中心广场\n• 民族文化公园（免费）：壮族文化主题\n• 贵港园博园（免费）：园林景观公园\n• 郁江沿岸风光带（免费）：滨江散步赏日落\n• 港北老街（免费）：百年骑楼建筑、夜市美食",
            "港南": "港南区是老城区，主要景点：\n• 南山寺（20元）：唐代古刹，广西最古老佛教寺院\n• 南山公园（免费）：登山健身、俯瞰市区",
            "覃塘": "覃塘区是北部山区，主要景点：\n• 平天山国家森林公园（40元）：贵港最高峰，登山观日出\n• 九凌湖（免费）：最大水库，观鸟钓鱼\n• 覃塘荷花基地（免费）：6-8月千亩荷塘",
            "桂平": "桂平市是贵港下辖县级市，景点最丰富：\n• 西山风景区（80元）：佛教圣地，龙华寺、乳泉\n• 龙潭国家森林公园（60元）：原始森林、瀑布\n• 大藤峡（50元）：峡谷风光、乘船游览\n• 桂平乳泉亭（免费）：岭南第一泉\n• 桂平市区老街（免费）：百年骑楼\n• 北回归线标志公园（15元）：夏至立竿无影\n• 金田起义遗址（30元）：太平天国发源地\n• 白石山（35元）：道教圣地\n• 桂平湿地公园（免费）：湿地生态",
            "平南": "平南县是贵港东部县，主要景点：\n• 北帝山旅游区（80元）：玻璃栈道、悬崖秋千\n• 平南雄森动物大世界（120元）：野生动物园\n• 龚州公园（免费）：县城中心公园\n• 平南古镇（免费）：明清建筑、传统手工艺\n• 大坦水库（免费）：钓鱼露营",
            "美食": "贵港的特色美食包括：\n• 贵港米粉：当地特色米粉，汤鲜粉滑\n• 罗秀米粉：广西第一米粉，300年历史\n• 桂平西山茶：广西名茶，清香甘醇\n• 郁江鱼鲜：郁江出产的淡水鱼，鲜美可口\n• 壮乡糯米饭：壮族传统美食，香甜软糯\n• 平南石硖龙眼：平南特产，肉厚核小\n\n推荐去老街夜市和贵港饭店品尝，人均30-80元。",
            "米粉": "贵港米粉是当地最具代表性的小吃！大米制成，口感爽滑，汤底用猪骨熬制，配叉烧、花生、酸豆角。推荐去老街的[老贵港米粉店]品尝，一碗约10-15元。\n\n还有罗秀米粉（桂平特产），被誉为「广西第一米粉」，已有300年历史，洁白细嫩，久煮不烂。",
            "交通": "贵港市交通便利：\n🚄 高铁：贵港站连接南宁（40分钟）、广州（2小时）\n🚗 自驾：南广高速、贵梧高速经过\n🚌 市内：公交1-2元，出租车起步7元\n✈️ 机场：南宁吴圩机场转高铁1小时到贵港",
            "高铁": "贵港站位于港北区，每天多趟高铁往返：\n• 南宁东→贵港：约40分钟\n• 广州南→贵港：约2小时\n• 深圳北→贵港：约2.5小时\n• 桂林→贵港：约1.5小时",
            "住宿": "住宿推荐：\n🏨 市区（港北区）：贵港国际大酒店（四星）、雅斯特酒店（连锁）\n🏨 桂平市区：宇洋国际大酒店（四星，近西山）\n🏨 平南：雄景酒店（四星）或城市便捷酒店\n💰 经济型：如家/汉庭等连锁，120-200元/晚\n🏡 特色民宿：西山脚下、北帝山附近有多家",
            "酒店": "市区推荐贵港国际大酒店（四星，港北区）或雅斯特酒店（连锁性价比高）。桂平推荐宇洋国际大酒店（四星，近西山）。平南推荐雄景酒店或城市便捷。经济型可选如家、汉庭，120-200元/晚。",
            "季节": "最佳旅游季节：春秋两季（3-5月、9-11月），气候宜人，最适合出行。",
            "行程": "推荐行程：\n\n【一日游】上午西山→中午桂平美食→下午龙潭/大藤峡\n【两日游】Day1西山（住桂平）→Day2龙潭+大藤峡\n【三日游深度】Day1西山→Day2龙潭+大藤峡→Day3市区人文\n【五日全景游】覆盖港北区+覃塘区+桂平市+平南县\n\n输入「一日游」「两日游」「三日游」「五日游」查看详细行程。",
            "一日游": "推荐经典一日游方案：\n\n方案A【桂平方向】：\n上午：西山风景区（3-4h）→中午桂平美食→下午龙潭/大藤峡\n\n方案B【市区方向】：\n上午：博物馆+民族文化公园→中午贵港米粉→下午南山寺→傍晚郁江夜景\n\n方案C【平南方向】：\n上午：北帝山→中午平南美食→下午雄森动物世界",
            "两日游": "推荐两日游方案：\n\nDay1【桂平精华】：\n• 上午高铁抵达，前往桂平\n• 西山风景区深度游（4h）\n• 傍晚桂平市区，入住酒店\n\nDay2【自然探索】：\n• 上午龙潭国家森林公园（3-4h）\n• 下午大藤峡乘船（2-3h）\n• 傍晚返回或高铁返程",
            "三日游": "推荐三日游方案：\n\nDay1：西山+乳泉→住桂平\nDay2：龙潭+大藤峡+桂平老街→住桂平\nDay3：博物馆+民族文化公园+南山寺+郁江夜景→返程",
            "五日游": "推荐五日全景游：\n\nDay1：港北区（东湖、博物馆、世纪广场、老街夜市）\nDay2：港南区+覃塘区（南山寺、平天山或九凌湖）→住桂平\nDay3：桂平市（西山、乳泉亭、老街）→住桂平\nDay4：桂平市（龙潭、大藤峡）→住平南\nDay5：平南县（北帝山、雄森动物世界、古镇）→返程",
            "亲子": "亲子游推荐：\n• 东湖公园：免费，可划船、喂鱼\n• 龙潭国家森林公园：自然探索、观鸟\n• 贵港博物馆：互动体验区\n• 平南雄森动物大世界：野生动物园，动物表演\n\n住宿建议选市区，备好防蚊用品和零食。",
            "购物|特产": "贵港特产推荐：\n• 桂平西山茶：送礼佳品\n• 壮锦：壮族传统织锦工艺品\n• 桂圆干：广西特产\n• 罗秀米粉：方便携带\n• 平南石硖龙眼：平南特产\n\n购买地点：市区特产店、西山茶庄、桂平老街。",
            "电话|联系": "紧急联系：\n• 旅游投诉：0775-12345\n• 公安：110 / 急救：120\n• 贵港市人民医院：0775-4200120",
        }
        for kw, reply in intent_keywords.items():
            if any(w in query for w in kw.split("|")):
                return reply
        
        return (f"关于「{query}」这个问题，我目前的知识库中还没有详细信息。\n\n"
                "你可以试试问：\n"
                "• 「西山风景区有什么好玩的？」\n"
                "• 「推荐一日游行程」\n"
                "• 「贵港有什么特色美食？」\n"
                "• 「有哪些免费景点？」\n"
                "• 「贵港博物馆值得去吗？」")
    
    # 有匹配景点 → 生成推荐
    if spots:
        # ★ 关键修复：如果用户明确提到了某个具体景点名，强制走单景点详情模式
        # 即使查询中包含区县名（如"平南古镇"包含"平南"），也不应列出全区所有景点
        explicit_spot = extract_spot_from_query(query)
        if explicit_spot:
            s = explicit_spot
            img_hint = f"\n📷 [点击查看景点图片]({s.get('image_url', '')})\n" if s.get('image_url') else ""
            lines.append(f"## {s['name']}{img_hint}")
            lines.append("")
            lines.append(s['description'])
            lines.append("")
            lines.append(f"📍 位置：{s['location']}")
            lines.append(f"🗺️ 行政区：{s.get('district', '贵港市')}")
            lines.append(f"💰 票价：{s['ticket_price']}")
            lines.append(f"🕐 开放时间：{s['open_time']}")
            if s.get('image_url'):
                lines.append(f"🖼️ 图片：{s['image_url']}")
            lines.append("")
            lines.append("**亮点：**")
            for h in s['highlights']:
                lines.append(f"• {h}")
            lines.append("")
            lines.append(f"🗺️ 推荐路线：{s['recommended_route']}")
            lines.append(f"💡 {s['tips']}")
            if s.get("nearby_spots"):
                lines.append(f"\n附近景点：{'、'.join(s['nearby_spots'])}")
        # 如果是按行政区划查询（且用户没有明确提到具体景点），列出该区所有景点
        elif True:
            district_map = {"港北": "港北区", "港南区": "港南区", "港南区": "港南区", "覃塘": "覃塘区", "覃塘区": "覃塘区", "桂平": "桂平市", "桂平市": "桂平市", "平南": "平南县", "平南县": "平南县"}
            target_district = None
            for kw, district in district_map.items():
                if kw in query:
                    target_district = district
                    break
            
            if target_district and len(spots) > 1:
                # 列出该区所有景点
                lines.append(f"## {target_district}景点推荐\n")
                for s in spots:
                    img_icon = " 🖼️" if s.get('image_url') else ""
                    lines.append(f"### {s['name']}{img_icon}")
                    lines.append(f"📍 {s['location']} | 💰 {s['ticket_price']} | 🕐 {s['open_time']}")
                    lines.append(f"{s['description'][:80]}...")
                    lines.append("")
                lines.append(f"💡 输入具体景点名称可查看详细信息，如「{spots[0]['name']}」")
            else:
                # 单个景点详情（区县查询只匹配到一个，或无区县关键词）
                s = spots[0]
                img_hint = f"\n📷 [点击查看景点图片]({s.get('image_url', '')})\n" if s.get('image_url') else ""
                lines.append(f"## {s['name']}{img_hint}")
                lines.append("")
                lines.append(s['description'])
                lines.append("")
                lines.append(f"📍 位置：{s['location']}")
                lines.append(f"🗺️ 行政区：{s.get('district', '贵港市')}")
                lines.append(f"💰 票价：{s['ticket_price']}")
                lines.append(f"🕐 开放时间：{s['open_time']}")
                if s.get('image_url'):
                    lines.append(f"🖼️ 图片：{s['image_url']}")
                lines.append("")
                lines.append("**亮点：**")
                for h in s['highlights']:
                    lines.append(f"• {h}")
                lines.append("")
                lines.append(f"🗺️ 推荐路线：{s['recommended_route']}")
                lines.append(f"💡 {s['tips']}")
                if s.get("nearby_spots"):
                    lines.append(f"\n附近景点：{'、'.join(s['nearby_spots'])}")
        else:
            # 单个景点详情
            s = spots[0]
            img_hint = f"\n📷 [点击查看景点图片]({s.get('image_url', '')})\n" if s.get('image_url') else ""
            lines.append(f"## {s['name']}{img_hint}")
            lines.append("")
            lines.append(s['description'])
            lines.append("")
            lines.append(f"📍 位置：{s['location']}")
            lines.append(f"🗺️ 行政区：{s.get('district', '贵港市')}")
            # 地图跳转链接
            lat = s.get('lat', 0)
            lng = s.get('lng', 0)
            # 地图链接由前端 enrichWithMapLinks 自动生成，此处不再输出URL
            lines.append(f"💰 票价：{s['ticket_price']}")
            lines.append(f"🕐 开放时间：{s['open_time']}")
            if s.get('image_url'):
                lines.append(f"🖼️ 图片：{s['image_url']}")
            lines.append("")
            lines.append("**亮点：**")
            for h in s['highlights']:
                lines.append(f"• {h}")
            lines.append("")
            lines.append(f"🗺️ 推荐路线：{s['recommended_route']}")
            lines.append(f"💡 {s['tips']}")
            
            # 附近景点
            if s.get("nearby_spots"):
                lines.append(f"\n附近景点：{'、'.join(s['nearby_spots'])}")

    # 只有在用户问的是"具体景点"时才附加 tips；区县/主题类查询已足够完整，无需 tips
    if tips and explicit_spot:
        lines.append("")
        for k, v in tips:
            lines.append(f"**{k}**：{v}")
    
    return "\n".join(lines)

# ── API 路由 ──────────────────────────────────────

@app.route("/")
def index():
    auto_ask = request.args.get("ask", "")
    return render_template("index.html", spots=SCENIC_SPOTS, auto_ask=auto_ask)

@app.route("/api/debug_search")
def debug_search():
    q = request.args.get("q", "")
    results = search_scenic_spots(q)
    return jsonify({
        "query": q,
        "matched_count": len(results),
        "matched_names": [s["name"] for s in results],
        "matched_aliases": {s["name"]: s["alias"] for s in results}
    })

@app.route("/api/test_extract")
def test_extract():
    q = request.args.get("q", "")
    spot = extract_spot_from_query(q)
    if spot:
        return jsonify({"query": q, "found": True, "name": spot["name"], "alias": spot["alias"]})
    return jsonify({"query": q, "found": False})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")
    
    if not user_message:
        return jsonify({"reply": "请输入您的问题。"})

    # 获取历史对话
    history = SESSION_HISTORY.get(session_id, [])
    
    # 提取当前话题（最近提到的景点）
    current_topic = None
    for msg in reversed(history):
        if msg["role"] == "assistant":
            # 从助手回复中提取景点名称（通常是回复的第一行标题）
            lines = msg["content"].split('\n')
            for line in lines[:3]:
                if line.startswith('## '):
                    current_topic = line.replace('## ', '').strip()
                    break
                # 匹配 "XX有什么特色" 中的 XX
                if '有什么特色' in line or '简介' in line or '亮点' in line:
                    for spot in SCENIC_SPOTS:
                        if spot["name"] in line or any(alias in line for alias in spot["alias"]):
                            current_topic = spot["name"]
                            break
            if current_topic:
                break
    
    # 1. RAG 检索（结合上下文）
    # 如果用户问的是模糊问题（如"怎么去"），且知道当前话题，自动补充
    search_query = user_message
    fuzzy_keywords = ["怎么去", "怎么去那里", "怎么去啊", "怎么去呢", "怎么去这个地方", 
                      "怎么走", "怎么去方便", "怎么去最快", "怎么去最方便",
                      "门票多少", "多少钱", "票价", "开放时间", "几点开门", "几点关门",
                      "附近有什么", "周边", "附近", "旁边", "附近景点",
                      "有什么好吃的", "吃什么", "附近美食", "周边美食",
                      "住哪里", "住宿", "酒店", "民宿",
                      "拍照", "摄影", "打卡", "哪里好看"]
    is_fuzzy = any(kw in user_message for kw in fuzzy_keywords)

    # 修复：模糊查询时，优先用明确提到的景点，其次用当前话题
    if is_fuzzy:
        explicit_spot = extract_spot_from_query(user_message)
        if explicit_spot:
            search_query = explicit_spot["name"]
        elif current_topic:
            search_query = f"{current_topic} {user_message}"
    matched_spots = search_scenic_spots(search_query)
    matched_tips = get_travel_tips(search_query)
    
    # 如果没匹配到景点，但知道当前话题，尝试直接用当前话题查询
    if not matched_spots and current_topic:
        for spot in SCENIC_SPOTS:
            if spot["name"] == current_topic or current_topic in spot["alias"]:
                matched_spots = [spot]
                break

    # 2. 尝试调用 LLM，失败则降级到本地模式
    client = get_llm_client()
    if client:
        # 只传用户明确提到的景点（如有），避免 LLM 拿到多个景点信息后输出冗余内容
        explicit_spot = extract_spot_from_query(user_message)
        if explicit_spot:
            llm_spots = [explicit_spot]
            print(f"[LLM上下文] 用户明确提到景点：{explicit_spot['name']}，只传该景点信息")
        else:
            llm_spots = matched_spots

        context = build_context(llm_spots, matched_tips)
        # 检查是否有 nearby_hotels 信息，如果有则加入上下文
        hotels_context = ""
        if llm_spots:
            spot = matched_spots[0]
            nearby_hotels = spot.get('nearby_hotels', [])
            if nearby_hotels:
                hotels_lines = ["\n【该景点附近住宿（按距离排序）】"]
                for hotel in nearby_hotels:
                    hotels_lines.append(f"• {hotel['name']}（{hotel['type']}，{hotel['price']}，{hotel['distance']}）- {hotel['note']}")
                hotels_context = "\n".join(hotels_lines)
        
        system_prompt = (
            "你是一个专业的贵港市旅游智能助手。\n\n回答规则：\n"
            "- 优先使用下方提供的景点信息回答问题\n"
            "- 如果知识库中没有相关信息，请诚实告知，不要编造\n"
            "- 回答亲切、热情、简洁，控制在300字以内\n"
            "- 如果用户问'怎么去'、'门票多少'等模糊问题，结合上下文理解用户指的是哪个景点\n"
            "- 推荐住宿时遵循'先近后远'原则：优先推荐距离景点最近的住宿，再推荐稍远的备选\n"
            f"\n{context}{hotels_context}"
        )

        # 明确景点时注入结构化输出模板
        if explicit_spot:
            system_prompt += (
                "\n\n请严格按以下格式回答（每个段落以 emoji 标题开头）：\n"
                "🏞️ 景点介绍\n"
                "[简要介绍50字]\n"
                "⭐ 推荐指数\n"
                "[1-5星]\n"
                "🕐 最佳游玩时间\n"
                "[建议时长]\n"
                "🌸 推荐季节\n"
                "[最佳季节]\n"
                "🍜 附近美食\n"
                "- 列表\n"
                "📍 附近景点\n"
                "- 列表\n"
                "🚗 出行建议\n"
                "[交通/注意事项]"
            )
        messages = [{"role": "system", "content": system_prompt}]
        # 加入历史对话（最近3轮）
        for msg in history[-6:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})
        
        reply = client.chat(messages)
        if not reply.startswith("[API 错误") and not reply.startswith("[请求失败"):
            # 如果匹配到了景点，在LLM回复后追加位置和地图信息
            if matched_spots:
                s = matched_spots[0]
                reply += f"\n\n📍 位置：{s['location']}"
                if s.get('lat') and s.get('lng'):
                    reply += f"\n🗺️ [在地图中查看](https://uri.amap.com/search?keyword={('贵港市' + s['name'])})"
            # 保存对话历史
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": reply})
            SESSION_HISTORY[session_id] = history[-MAX_HISTORY_LEN:]
            return jsonify({"reply": reply, "session_id": session_id, "context_topic": current_topic})

    # 3. 降级：纯本地知识库回复
    local_reply = generate_local_reply(user_message, matched_spots, matched_tips, current_topic)
    
    # 保存对话历史
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": local_reply})
    SESSION_HISTORY[session_id] = history[-MAX_HISTORY_LEN:]
    
    return jsonify({"reply": local_reply, "session_id": session_id, "context_topic": current_topic})

@app.route("/api/feedback", methods=["POST"])
def feedback():
    """接收用户反馈并保存到文件"""
    data = request.get_json()
    msg_id = data.get("msg_id", "")
    feedback_type = data.get("feedback_type", "")
    text = data.get("text", "")
    print(f"[反馈] msg_id={msg_id}, type={feedback_type}, text={text}")
    # 保存到 feedback.json
    import datetime
    fb_record = {
        "time": datetime.datetime.now().isoformat(),
        "msg_id": msg_id,
        "type": feedback_type,
        "text": text,
    }
    fb_file = os.path.join(os.path.dirname(__file__), "feedback.json")
    try:
        existing = []
        if os.path.exists(fb_file):
            with open(fb_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
        existing.append(fb_record)
        with open(fb_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[反馈] 保存失败: {e}")
    return jsonify({"status": "ok", "message": "感谢反馈！"})

@app.route("/spot/<spot_id>")
def spot_detail_page(spot_id):
    """景点详情页"""
    spot = None
    for s in SCENIC_SPOTS:
        if s["id"] == spot_id:
            spot = s
            break
    if not spot:
        return render_template("index.html", spots=SCENIC_SPOTS, error="未找到该景点"), 404
    return render_template("spot_detail.html", spot=spot)


@app.route("/api/spot/<spot_id>")
def get_spot_detail(spot_id):
    for spot in SCENIC_SPOTS:
        if spot["id"] == spot_id:
            return jsonify(spot)
    return jsonify({"error": "未找到该景点"}), 404

@app.route("/api/spots")
def list_spots():
    return jsonify([{
        "id": s["id"], "name": s["name"],
        "category": s["category"], "rating": s["rating"],
        "description": s["description"][:80] + "...",
        "image_url": s.get("image_url", ""),
        "ticket_price": s["ticket_price"],
        "location": s["location"],
        "district": s.get("district", ""),
        "lat": s.get("lat", 0),
        "lng": s.get("lng", 0),
    } for s in SCENIC_SPOTS])

@app.route("/api/weather")
def weather():
    """返回贵港真实天气（wttr.in API）"""
    import datetime
    import urllib.request
    try:
        req = urllib.request.Request(
            'https://wttr.in/Guigang?format=j1',
            headers={'User-Agent': 'curl/7.68.0'}
        )
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        cc = data['current_condition'][0]
        temp = cc['temp_C']
        feels = cc['FeelsLikeC']
        desc = cc['weatherDesc'][0]['value']
        humidity = cc['humidity']
        wind = cc['windspeedKmph']

        # 根据天气生成旅游建议
        t = int(temp)
        if t <= 15:
            suggest = "❄️ 气温较低，建议穿着保暖外套。适合游览西山风景区（可拜佛祈福）、南山寺，或参观贵港博物馆了解本地历史。"
        elif t <= 25:
            suggest = "🌸 气候宜人，适合户外活动！推荐大藤峡、龙潭国家森林公园踏青，或去平天山登山看日出。"
        elif t <= 32:
            suggest = "☀️ 天气较热，建议上午或傍晚出行，注意防晒补水。推荐东湖公园、园博园等室内外结合景点，或去龙潭瀑布戏水。"
        else:
            suggest = "🔥 高温预警！建议避开正午，选择室内或水上景点：龙潭瀑布、东湖公园（树荫多）、贵港博物馆。注意防暑降温。"
        if 'rain' in desc.lower() or 'drizzle' in desc.lower():
            suggest += " 当前有雨，建议携带雨具，优先选择室内或近市区的景点。"

        return jsonify({
            "temp": f"{feels}°C（体感）",
            "weather": desc,
            "wind": f"{wind}km/h",
            "humidity": f"{humidity}%",
            "suggestion": suggest,
            "source": "wttr.in",
        })
    except Exception as e:
        print(f"[天气] wttr.in 请求失败: {e}")
        # 降级到季节性模拟数据
        month = datetime.datetime.now().month
        if month in [12, 1, 2]:
            fallback = {"temp": "10~18", "weather": "多云转晴", "wind": "北风2级", "humidity": "65%", "suggestion": "❄️ 冬季气温较低，建议穿着保暖外套。适合游览西山风景区、南山寺，或参观贵港博物馆。", "source": "模拟"}
        elif month in [3, 4, 5]:
            fallback = {"temp": "18~26", "weather": "晴转多云", "wind": "东南风2级", "humidity": "75%", "suggestion": "🌸 春季气候宜人，适合户外活动！推荐大藤峡、龙潭国家森林公园踏青。", "source": "模拟"}
        elif month in [6, 7, 8]:
            fallback = {"temp": "28~35", "weather": "多云转晴", "wind": "东南风2级", "humidity": "80%", "suggestion": "☀️ 夏季炎热，建议上午或傍晚出行。推荐龙潭瀑布戏水或东湖公园。", "source": "模拟"}
        else:
            fallback = {"temp": "22~30", "weather": "晴", "wind": "东风1级", "humidity": "70%", "suggestion": "🍂 秋季凉爽，最佳旅游季节！推荐西山看日落、大藤峡游船。", "source": "模拟"}
        return jsonify(fallback)

@app.route("/api/status")
def status():
    """返回系统状态"""
    client = get_llm_client()
    return jsonify({
        "llm_available": _llm_available,
        "llm_api": LLM_API_BASE,
        "mode": "llm" if _llm_available else "local",
        "spots_count": len(SCENIC_SPOTS),
    })

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5001))
    print("=" * 50)
    print("  贵港旅游智能助手 v4.0")
    print("=" * 50)
    print(f"  LLM API: {LLM_API_BASE}")
    print(f"  运行模式: 自动（有 LLM 用 LLM，无 LLM 用本地知识库）")
    print(f"  启动地址: http://localhost:{PORT}")
    print("=" * 50)
    get_llm_client()  # 启动时检测并提示
    app.run(host="0.0.0.0", port=PORT, debug=True)
