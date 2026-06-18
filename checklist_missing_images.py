"""
输出：已有多图 vs 待补全景点清单
"""
import json, sys
sys.path.insert(0, '.')
import knowledge_base_v4

# 已有图片的景点
with open('data/spot_images.json', 'r', encoding='utf-8') as f:
    img_data = json.load(f)
has_images = set(img_data['spot_images'].keys())

# 全部景点
all_spots = knowledge_base_v4.SCENIC_SPOTS

print("=" * 50)
print("贵港旅游助手 · 景点多图补全清单")
print("=" * 50)
print()

print(f"✅ 已有图片的景点（{len(has_images)} 个）：")
for sid in sorted(has_images):
    s = next((x for x in all_spots if x['id'] == sid), None)
    name = s['name'] if s else sid
    count = len(img_data['spot_images'][sid]['image_urls'])
    print(f"  - {name}（{sid}）— {count} 张")

print()
print("-" * 50)
print(f"⬜ 待补全图片的景点（{len(all_spots) - len(has_images)} 个）：")
print()

# 按行政区划分组
from collections import defaultdict
by_district = defaultdict(list)
for s in all_spots:
    if s['id'] not in has_images:
        by_district[s['district']].append(s)

for district in sorted(by_district.keys()):
    print(f"【{district}】（{len(by_district[district])} 个）")
    for s in by_district[district]:
        print(f"  ⬜ {s['name']}（id: {s['id']}）— 类别：{s['category']}")
    print()

print("=" * 50)
print(f"总结：{len(all_spots)} 个景点，已补全 {len(has_images)} 个，待补全 {len(all_spots) - len(has_images)} 个")
print()
print("📋 小红书找图建议：")
print("  1. 搜索「贵港 + 景点名」")
print("  2. 优先找：实景图、标志性建筑/风景")
print("  3. 图尺寸建议：800×500 以上，横图最佳")
print("  4. 每个景点建议 3-5 张")
