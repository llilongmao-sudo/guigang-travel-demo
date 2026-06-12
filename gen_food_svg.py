# -*- coding: utf-8 -*-
"""为16道贵港美食生成 emoji SVG 占位图 + 写入 image 字段"""
import os, json

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, 'data')
IMG_DIR = os.path.join(BASE, 'static', 'images', 'food')
os.makedirs(IMG_DIR, exist_ok=True)

with open(os.path.join(DATA, 'food.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

foods = data['foods']

# emoji 背景色映射
emoji_bg = {
    "🥬": "#e8f5e9", "🍜": "#fff3e0", "🌿": "#e8f5e9", "🍗": "#fff8e1",
    "🦆": "#e3f2fd", "🍙": "#fce4ec", "🐟": "#e0f7fa", "🍖": "#fbe9e7",
    "🌶️": "#fce4ec", "🥣": "#e8f5e9", "🍵": "#f1f8e9", "🥣": "#fff8e1",
    "🍡": "#f3e5f5", "🍢": "#efebe9", "🐟": "#e0f2f1", "🥗": "#e8f5e9",
}

for food in foods:
    fid = food['id']
    emoji = food.get('emoji', '🍽️')
    bg = emoji_bg.get(emoji, '#f5f5f5')
    save_path = os.path.join(IMG_DIR, f'{fid}.svg')

    # 生成 SVG（emoji 居中）
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <rect width="200" height="200" fill="{bg}"/>
  <text x="100" y="130" text-anchor="middle" dominant-baseline="middle" font-size="80">{emoji}</text>
</svg>'''
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(svg)

    rel_path = f'/static/images/food/{fid}.svg'
    food['image'] = rel_path
    food['image_alt'] = f"{food['name']} {emoji}"
    print(f"  ✅ {emoji} {food['name']} → {rel_path}")

# 写回 food.json（保留 meta）
with open(os.path.join(DATA, 'food.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\n✅ 完成！共 {len(foods)} 道美食图片生成完毕')
print(f'图片目录: {IMG_DIR}')
print('提示: 后续可替换为真实美食照片，只需将 JPG/PNG 放到同一目录并更新 food.json 的 image 字段')
