# -*- coding: utf-8 -*-
"""知识库验证脚本"""
import sys
sys.path.insert(0, '.')
from knowledge_base_v4 import SCENIC_SPOTS, TRAVEL_TIPS, CATEGORY_INDEX, DISTRICT_STATS
from collections import Counter

errors = []
warnings = []

REQUIRED_FIELDS = ['id', 'name', 'alias', 'category', 'location', 'district', 'rating', 'ticket_price', 'open_time', 'description', 'highlights', 'recommended_route', 'tips', 'nearby_spots']

for spot in SCENIC_SPOTS:
    for field in REQUIRED_FIELDS:
        if field not in spot:
            errors.append(f'{spot["name"]}: 缺少字段 {field}')
        elif field in ('alias', 'highlights', 'nearby_spots') and not isinstance(spot[field], list):
            errors.append(f'{spot["name"]}: {field} 不是列表')
    if 'lat' not in spot or 'lng' not in spot:
        errors.append(f'{spot["name"]}: 缺少经纬度')

# 重复ID检查
ids = [s['id'] for s in SCENIC_SPOTS]
dupes = [id for id in set(ids) if ids.count(id) > 1]
if dupes:
    errors.append(f'重复ID: {dupes}')

# 区县统计一致性
actual_district = Counter(s['district'] for s in SCENIC_SPOTS)
for d, expected in DISTRICT_STATS.items():
    if d == '总计':
        continue
    actual = actual_district.get(d, 0)
    if actual != expected:
        errors.append(f'{d}: 声明{expected}个，实际{actual}个')

if DISTRICT_STATS.get('总计', 0) != len(SCENIC_SPOTS):
    errors.append(f'总计数: 声明{DISTRICT_STATS["总计"]}个，实际{len(SCENIC_SPOTS)}个')

# 分类索引一致性
actual_cat = Counter(s['category'] for s in SCENIC_SPOTS)
for cat, spots in CATEGORY_INDEX.items():
    expected = len(spots)
    actual = actual_cat.get(cat, 0)
    if actual != expected:
        errors.append(f'分类「{cat}」: 索引{expected}个，实际{actual}个')

# nearby_spots 有效性
all_names = set(s['name'] for s in SCENIC_SPOTS)
for spot in SCENIC_SPOTS:
    for nearby in spot.get('nearby_spots', []):
        if nearby not in all_names:
            warnings.append(f'{spot["name"]}的nearby_spots包含未知景点「{nearby}」')

# 统计分类中是否有景点名拼写错误
for cat, spots in CATEGORY_INDEX.items():
    for s in spots:
        if s not in all_names:
            warnings.append(f'分类索引「{cat}」包含未知景点名「{s}」')

print(f'===== 知识库验证报告 =====')
print(f'景点总数: {len(SCENIC_SPOTS)}')
print(f'旅游贴士: {len(TRAVEL_TIPS)} 条')
print(f'分类索引: {len(CATEGORY_INDEX)} 类')
print()
if errors:
    print(f'错误 ({len(errors)} 个):')
    for e in errors:
        print(f'   - {e}')
else:
    print(f'数据一致性检查全部通过！')
print()
if warnings:
    print(f'警告 ({len(warnings)} 个):')
    for w in warnings:
        print(f'   - {w}')
else:
    print(f'无警告')
