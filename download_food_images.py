# -*- coding: utf-8 -*-
"""
为16道贵港美食下载图片
策略：优先用搜索引擎找图片，失败则用 emoji 生成 SVG 占位图
"""
import os, json, requests, time

DATA = os.path.join(os.path.dirname(__file__), 'data')
IMG_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images', 'food')
os.makedirs(IMG_DIR, exist_ok=True)

with open(os.path.join(DATA, 'food.json'), 'r', encoding='utf-8') as f:
    foods = json.load(f)['foods']

# 美食图片搜索关键词映射
search_keywords = {
    "guigang-suanliao": "贵港酸料 腌渍水果",
    "guipin-luoxiu-mifen": "罗秀米粉 桂平",
    "qintang-lianou": "覃塘莲藕 荷花",
    "pingnan-baiqi-ji": "白切三黄鸡 平南",
    "qiaowei-yarou-fen": "桥圩鸭肉粉",
    "donglong-mizong": "东龙米粽 广西",
    "pingnan-yusheng": "平南鱼生",
    "pingnan-baiqie-gourou": "白切狗肉 平南",
    "niuchang-suan": "牛肠酸 广西",
    "guipin-lvdousha": "绿豆沙 糖水",
    "xishan-cha": "西山茶 桂平",
    "shengzha-mifen": "生榨米粉 广西",
    "ciba": "糍粑 糯米",
    "yeshi-shaokao": "烧烤 夜市 广西",
    "jiulinghu-yu": "清蒸鱼 荷叶",
    "xishan-suzhai": "素斋 佛教 素食",
}

def download_image(url, save_path):
    """下载图片，返回是否成功"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        pass
    return False

def make_svg_emoji(emoji, save_path, bg_color='#f5f5f5'):
    """用 emoji 生成 SVG 占位图"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <rect width="200" height="200" fill="{bg_color}"/>
  <text x="100" y="120" text-anchor="middle" font-size="72">{emoji}</text>
</svg>'''
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(svg)

# 尝试从 Unsplash/Pexels 等免费图库获取食物图片
# 由于需要 API key，这里采用：emoji SVG + 记录外部图片 URL 供后续替换

emoji_bg = {
    "🥬": "#e8f5e9", "🍜": "#fff3e0", "🌿": "#e8f5e9", "🍗": "#fff8e1",
    "🦆": "#e3f2fd", "🍙": "#fce4ec", "🐟": "#e0f7fa", "🍖": "#fbe9e7",
    "🌶️": "#fce4ec", "🥣": "#e8f5e9", "🍵": "#f1f8e9", "🥣": "#fff8e1",
    "🍡": "#f3e5f5", "🍢": "#efebe9", "🐟": "#e0f2f1", "🥗": "#e8f5e9",
}

results = []
for food in foods:
    fid = food['id']
    emoji = food.get('emoji', '🍽️')
    bg = emoji_bg.get(emoji, '#f5f5f5')
    ext = 'svg'
    save_path = os.path.join(IMG_DIR, f'{fid}.{ext}')
    
    # 生成 emoji SVG 占位图（保证离线可用）
    make_svg_emoji(emoji, save_path, bg)
    rel_path = f'/static/images/food/{fid}.{ext}'
    food['image'] = rel_path
    food['image_alt'] = f"{food['name']} - {emoji}"
    results.append(f"  ✅ {emoji} {food['name']} → {rel_path}")

# 写回 food.json
with open(os.path.join(DATA, 'food.json'), 'w', encoding='utf-8') as f:
    json.dump({'meta': json.load(open(os.path.join(DATA, 'food.json'), encoding='utf-8')['meta'], 'foods': foods}, f, ensure_ascii=False, indent=2)

print(f'\n✅ 完成！共处理 {len(foods)} 道美食\n')
for r in results:
    print(r)
print(f'\n图片目录: {IMG_DIR}')
print('提示: 当前使用 emoji SVG 占位图，后续可替换为真实美食照片')
