"""
1. 提取 routes.json 中所有 location + title
2. 在 knowledge_base_v4.py 的景点列表中模糊匹配，建立映射
3. 输出映射表到文件，同时将 lat/lng/spot_id 写入 routes_new.json
"""
import json
import re

# ── 读取景点数据 ──────────────────────────────────────────
with open('knowledge_base_v4.py', 'r', encoding='utf-8') as f:
    kb_content = f.read()

# 用正则提取 SCENIC_SPOTS 列表中的景点 id / name / lat / lng
# 格式： "id": "donghu", "name": "东湖公园", "lat": 23.113, "lng": 109.598
spot_pattern = re.compile(
    r'"id"\s*:\s*"([^"]+)"[\s\S]*?'
    r'"name"\s*:\s*"([^"]+)"[\s\S]*?'
    r'"lat"\s*:\s*([0-9.]+)[\s\S]*?'
    r'"lng"\s*:\s*([0-9.]+)',
    re.DOTALL
)

spots = []
for m in spot_pattern.finditer(kb_content):
    spots.append({
        'id': m.group(1),
        'name': m.group(2),
        'lat': float(m.group(3)),
        'lng': float(m.group(4))
    })

print(f"从 knowledge_base_v4.py 提取到 {len(spots)} 个景点")
print("样例：", spots[:3])

# ── 读取路线数据 ──────────────────────────────────────────
with open('data/routes.json', 'r', encoding='utf-8') as f:
    routes_data = json.load(f)

# ── 建立映射 ──────────────────────────────────────────────
# 对每条路线的每个 step，用 location 和 title 模糊匹配景点
def find_spot(keyword):
    """在景点列表中模糊匹配，返回 (id, lat, lng) 或 None"""
    keyword = keyword.strip()
    for s in spots:
        # 精确 id 匹配
        if keyword == s['id']:
            return s
        # name 包含 keyword 或 keyword 包含 name
        if keyword in s['name'] or s['name'] in keyword:
            return s
    return None

mapping = []  # 记录映射结果

for route in routes_data['routes']:
    for step in route.get('itinerary', []):
        loc = step.get('location', '')
        title = step.get('title', '')
        
        # 用 location 和 title 分别尝试匹配
        matched = None
        for kw in [loc, title]:
            if kw:
                matched = find_spot(kw)
                if matched:
                    break
        
        entry = {
            'route_id': route['id'],
            'step': step.get('step'),
            'title': title,
            'location': loc,
            'matched_spot': matched['id'] if matched else None,
            'lat': matched['lat'] if matched else None,
            'lng': matched['lng'] if matched else None,
        }
        mapping.append(entry)
        
        # 写入 step
        if matched:
            step['spot_id'] = matched['id']
            step['lat'] = matched['lat']
            step['lng'] = matched['lng']
        else:
            step['spot_id'] = None
            step['lat'] = None
            step['lng'] = None

# ── 输出映射表 ─────────────────────────────────────────────
with open('data/routes_mapping.txt', 'w', encoding='utf-8') as f:
    f.write('=== 路线 location/title → 景点匹配映射表 ===\n\n')
    for entry in mapping:
        f.write(f"路线: {entry['route_id']} | step {entry['step']}\n")
        f.write(f"  title:     {entry['title']}\n")
        f.write(f"  location:  {entry['location']}\n")
        f.write(f"  匹配景点:  {entry['matched_spot']}  (lat={entry['lat']}, lng={entry['lng']})\n\n")

print(f"映射表已写入 data/routes_mapping.txt")
print(f"未匹配到的 step 数: {sum(1 for e in mapping if e['matched_spot'] is None)}")

# ── 写回 routes_new.json ───────────────────────────────────
with open('data/routes_new.json', 'w', encoding='utf-8') as f:
    json.dump(routes_data, f, ensure_ascii=False, indent=2)

print("更新后的路线数据已写入 data/routes_new.json")
print("请检查无误后执行：mv data/routes_new.json data/routes.json")
