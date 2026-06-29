"""
POI匹配构建脚本 v2
1. 从 data/attractions.json 读取完整32个景点（替代旧版 knowledge_base_v4.py）
2. 对每条路线的每个step进行智能匹配
3. transit/纯餐饮步骤自动跳过（不强制要求匹配）
4. 输出映射表和更新后的 routes.json
"""
import json
import re

# ── 读取景点数据（32个）──────────────────────────────────────
with open('data/attractions.json', 'r', encoding='utf-8') as f:
    attractions_data = json.load(f)

spots = []
for s in attractions_data.get('attractions', []):
    spots.append({
        'id': s.get('id', ''),
        'name': s.get('name', ''),
        'lat': s.get('lat'),
        'lng': s.get('lng'),
    })

print(f"从 attractions.json 提取到 {len(spots)} 个景点")

# ── 建立索引：名称映射表 ─────────────────────────────────────
# 手动补充别名映射（应付不精确的路线step标注）
ALIAS_MAP = {
    # 北帝山
    '北帝山': 'beidishan',
    '平南北帝山': 'beidishan',
    '北帝山漂流': 'beidishan',
    # 荷美覃塘
    '荷美覃塘': 'hemeitantang',
    '覃塘荷花': 'hemeitantang',
    '覃塘': 'hemeitantang',
    # 九凌湖
    '九凌湖': 'jiulinghu',
    '九凌山': 'jiulinghu',
    # 西山
    '桂平西山': 'xishan',
    '西山': 'xishan',
    # 龙潭
    '龙潭': 'longtansi',
    '龙潭公园': 'longtansi',
    '龙潭国家森林公园': 'longtansi',
    # 大藤峡
    '大藤峡': 'datengxia',
    '大藤峡游船': 'datengxia',
    # 市区
    '吾园': 'wuyuan',
    '东湖公园': 'donghu',
    '东湖': 'donghu',
    '郁江': 'donghu',
    '郁江夜游': 'donghu',
    '贵港市区': 'donghu',
    # 龙头山
    '龙头山': 'longtoushan',
    # 博物馆
    '博物馆': 'museum',
    '贵港博物馆': 'museum',
    # 雄森
    '雄森': 'xiongsen-animal',
    '动物大世界': 'xiongsen-animal',
    '雄森动物大世界': 'xiongsen-animal',
    '平南雄森动物大世界': 'xiongsen-animal',
    # 平南
    '平南县博物馆': 'pingnanxianbowuguan',
    '平南': 'pingnanxianbowuguan',
    '平南县城': 'pingnanxianbowuguan',
    '平南县': 'pingnanxianbowuguan',
    # 桂平
    '桂平市': 'xishan',
    '桂平': 'xishan',
    '桂平市区': 'guipin-laostreet',
    # 覃塘
    '覃塘区': 'hemeitantang',
    '覃塘农家乐': 'hemeitantang',
    # 平天山
    '平天山': 'pingtianshan',
    # 园博园
    '园博园': 'yuanboyuan',
    # 南山寺
    '南山寺': 'nanshansi',
    # 白石山
    '白石山': 'baishishan',
}

# ── 判定是否应跳过匹配的步骤 ─────────────────────────────────
def should_skip(step):
    """纯交通/出发/返程/早餐等步骤不需要POI坐标"""
    title = step.get('title', '')
    stype = step.get('type', '')
    if stype == 'transit':
        return True
    if any(kw in title for kw in ['出发', '返程', '回市区', '下山', '早餐', '晚餐', '午餐', '看星空']):
        return True
    if any(kw in title for kw in ['农家乐', '粉店', '鱼生', '莲藕宴', '素斋', '米粉', '酸料', '鸭肉', '野餐']):
        return True
    return False

# ── 景点匹配函数 ────────────────────────────────────────────
def find_spot(keyword):
    """模糊匹配景点，返回 (id, lat, lng) 或 None"""
    keyword = keyword.strip()
    if not keyword:
        return None

    # 1. 别名表精确匹配
    for alias, sid in ALIAS_MAP.items():
        if alias in keyword or keyword in alias:
            for s in spots:
                if s['id'] == sid:
                    return s

    # 2. 景点id精确匹配
    for s in spots:
        if keyword == s['id']:
            return s

    # 3. 名称包含匹配
    for s in spots:
        name = s['name']
        if keyword in name or name in keyword:
            return s

    # 4. 双向拆词模糊匹配
    words = re.split(r'[/·\s、,，]+', keyword)
    for s in spots:
        name = s['name']
        for w in words:
            if len(w) >= 2 and w in name:
                return s

    return None

# ── 读取路线数据 ─────────────────────────────────────────────
with open('data/routes.json', 'r', encoding='utf-8') as f:
    routes_data = json.load(f)

mapping = []
total = 0
matched = 0
skipped = 0
unmatched = 0

for route in routes_data['routes']:
    for step in route.get('itinerary', []):
        total += 1
        loc = step.get('location', '')
        title = step.get('title', '')

        if should_skip(step):
            skipped += 1
            # 清除可能残留的旧 spot_id/坐标
            step.pop('spot_id', None)
            step.pop('lat', None)
            step.pop('lng', None)
            mapping.append({
                'route_id': route['id'],
                'step': step.get('step'),
                'title': title,
                'location': loc,
                'status': 'skipped (transit)',
                'matched_spot': None,
            })
            continue

        # 用 location 和 title 分别尝试匹配
        found = None
        for kw in [title, loc]:
            if kw:
                found = find_spot(kw)
                if found:
                    break

        entry = {
            'route_id': route['id'],
            'step': step.get('step'),
            'title': title,
            'location': loc,
            'matched_spot': found['id'] if found else None,
            'lat': found['lat'] if found else None,
            'lng': found['lng'] if found else None,
        }
        mapping.append(entry)

        if found:
            matched += 1
            step['spot_id'] = found['id']
            step['lat'] = found['lat']
            step['lng'] = found['lng']
        else:
            unmatched += 1
            step['spot_id'] = None
            step['lat'] = None
            step['lng'] = None

# ── 输出映射表 ───────────────────────────────────────────────
with open('data/routes_mapping.txt', 'w', encoding='utf-8') as f:
    f.write('=== POI匹配映射表 (v2) ===\n\n')
    for entry in mapping:
        status = entry.get('status', 'matched' if entry['matched_spot'] else 'UNMATCHED')
        f.write(f"[{status}] {entry['route_id']} step {entry['step']}\n")
        f.write(f"  title:     {entry['title']}\n")
        f.write(f"  location:  {entry['location']}\n")
        f.write(f"  → {entry.get('matched_spot', 'N/A')}  (lat={entry.get('lat')}, lng={entry.get('lng')})\n\n")

# ── 统计 ──────────────────────────────────────────────────────
matchable = total - skipped
rate = matched / matchable * 100 if matchable else 0
print(f"\n总步骤: {total}")
print(f"跳过(transit等): {skipped}")
print(f"需匹配步骤: {matchable}")
print(f"已匹配: {matched}")
print(f"未匹配: {unmatched}")
print(f"匹配率: {matched}/{matchable} = {rate:.1f}%")

# ── 未匹配列表 ───────────────────────────────────────────────
print(f"\n未匹配步骤:")
for entry in mapping:
    if not entry.get('status') and not entry.get('matched_spot'):
        print(f"  {entry['route_id']} | step {entry['step']} | {entry['title']}")

# ── 写回 routes.json ─────────────────────────────────────────
with open('data/routes.json', 'w', encoding='utf-8') as f:
    json.dump(routes_data, f, ensure_ascii=False, indent=2)
print(f"\nroutes.json 已更新")
