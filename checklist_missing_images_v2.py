"""
输出：已有多图 vs 待补全景点清单 → 写入 data/images_checklist.txt
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

lines = []
lines.append("=" * 50)
lines.append("贵港旅游助手 · 景点多图补全清单")
lines.append("=" * 50)
lines.append("")

lines.append("[已有图片的景点]（{} 个）".format(len(has_images)))
for sid in sorted(has_images):
    s = next((x for x in all_spots if x['id'] == sid), None)
    name = s['name'] if s else sid
    count = len(img_data['spot_images'][sid]['image_urls'])
    lines.append("  ✓ {}".format(name))

lines.append("")
lines.append("-" * 50)
lines.append("[待补全图片的景点]（{} 个）".format(len(all_spots) - len(has_images)))
lines.append("")

# 按行政区划分组
from collections import defaultdict
by_district = defaultdict(list)
for s in all_spots:
    if s['id'] not in has_images:
        by_district[s['district']].append(s)

for district in sorted(by_district.keys()):
    lines.append("[{}]（{} 个）".format(district, len(by_district[district])))
    for s in by_district[district]:
        lines.append("  □ {}（id: {}）— 类别：{}".format(s['name'], s['id'], s['category']))
    lines.append("")

lines.append("=" * 50)
lines.append("总结：{} 个景点，已补全 {} 个，待补全 {} 个".format(
    len(all_spots), len(has_images), len(all_spots) - len(has_images)))
lines.append("")
lines.append("[小红书找图建议]")
lines.append("  1. 搜索「贵港 + 景点名」")
lines.append("  2. 优先找：实景图、标志性建筑/风景")
lines.append("  3. 图尺寸建议：800x500 以上，横图最佳")
lines.append("  4. 每个景点建议 3-5 张")
lines.append("")
lines.append("[操作说明]")
lines.append("  找到图后，把图片 URL 或本地路径告诉我，")
lines.append("  我会更新 data/spot_images.json")

# 写文件
with open('data/images_checklist.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("清单已写入 data/images_checklist.txt")
print("已有图片：{}".format(len(has_images)))
print("待补全：{}".format(len(all_spots) - len(has_images)))
