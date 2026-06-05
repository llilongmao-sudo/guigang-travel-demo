# -*- coding: utf-8 -*-
"""知识库差异分析"""
from knowledge_base_v4 import SCENIC_SPOTS, CATEGORY_INDEX
from collections import Counter

actual_cat = Counter(s['category'] for s in SCENIC_SPOTS)
print('=== 实际分类 ===')
for cat, count in sorted(actual_cat.items()):
    names = [s['name'] for s in SCENIC_SPOTS if s['category'] == cat]
    print(f'  {cat} ({count}): {names}')

print()
print('=== CATEGORY_INDEX 内容 ===')
for cat, spots in sorted(CATEGORY_INDEX.items()):
    print(f'  {cat} ({len(spots)}): {spots}')

print()
print('=== 缺失分析 ===')
for s in SCENIC_SPOTS:
    cat = s['category']
    if cat not in CATEGORY_INDEX:
        print(f'  CATEGORY_INDEX 缺少分类「{cat}」')
    elif s['name'] not in CATEGORY_INDEX[cat]:
        print(f'  分类「{cat}」索引中缺少 {s["name"]}')

print()
print('=== CATEGORY_INDEX 中多余的/错误分类的景点 ===')
all_names = set(s['name'] for s in SCENIC_SPOTS)
for cat, spots in CATEGORY_INDEX.items():
    for sn in spots:
        if sn not in all_names:
            print(f'  CATEGORY_INDEX「{cat}」包含不存在的景点「{sn}」')
        else:
            # Check if it's in the right category
            actual = [s['category'] for s in SCENIC_SPOTS if s['name'] == sn][0]
            if actual != cat:
                print(f'  {sn}: CATEGORY_INDEX 分类为「{cat}」,实际为「{actual}」')
