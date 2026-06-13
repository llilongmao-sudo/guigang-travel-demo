# -*- coding: utf-8 -*-
"""将美食数据内嵌到 index.html 中，彻底解决加载问题"""
import json, os

BASE = os.path.dirname(__file__)

# 读取 food.json
with open(os.path.join(BASE, 'data', 'food.json'), 'r', encoding='utf-8') as f:
    food_data = json.load(f)

# 精简字段
foods_inline = []
for fd in food_data['foods']:
    foods_inline.append({
        'id': fd['id'],
        'name': fd['name'],
        'emoji': fd.get('emoji', ''),
        'image': fd.get('image', ''),
        'description': (fd.get('description') or '')[:100],
        'price_range': fd.get('price_range', ''),
        'must_try': fd.get('must_try', False),
        'signature': fd.get('signature', False),
        'tags': (fd.get('tags') or [])[:3],
    })

foods_json_str = json.dumps(foods_inline, ensure_ascii=False)

# 读取 index.html
html_path = os.path.join(BASE, 'templates', 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 替换 loadFoods 函数：改为从内嵌数据加载
old_func = '''async function loadFoods() {
        try {
            // 从静态JSON文件加载（绕过API 404问题）
            const resp = await fetch('/static/data/food.json');
            const data = await resp.json();
            // 过滤 must_try=True 的美食
            const foods = (data.foods || data).filter(f => f.must_try || f.signature);'''

new_func = '''// 美食数据（内嵌，无需网络请求）
    const FOODS_DATA = ''' + foods_json_str + ''';

    async function loadFoods() {
        try {
            // 直接使用内嵌数据，不请求网络
            const foods = FOODS_DATA.filter(f => f.must_try || f.signature);'''

if old_func in html:
    html = html.replace(old_func, new_func)
    print('OK: Replaced loadFoods with inline data')
    print(f'   Inline data size: {len(foods_json_str)} chars, {len(foods_inline)} foods')
else:
    print('ERROR: Could not find old loadFoods function')
    # 尝试查找当前内容
    idx = html.find('async function loadFoods')
    if idx >= 0:
        print(f'  Found at position {idx}')
        print(f'  Context: ...{html[idx:idx+120]}...')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Done! index.html updated with inline food data.')
