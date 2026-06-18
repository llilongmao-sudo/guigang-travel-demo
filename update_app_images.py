"""
更新 app.py：
1. 在文件顶部加载 spot_images.json
2. 在 spot_detail_page 函数中给 spot 附加 image_urls
3. 在 get_spot_detail API 中返回 image_urls
"""
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. 在文件顶部（import 后）加载 spot_images.json ──────────
# 找到 # -*- coding -*- 或第一个 import 后的位置
# 在 app = Flask(__name__) 前插入加载代码
load_code = '''
# 加载景点多图数据
import json as _json
_SPOT_IMAGES = {}
try:
    with open('data/spot_images.json', 'r', encoding='utf-8') as _f:
        _data = _json.load(_f)
        _SPOT_IMAGES = {k: v['image_urls'] for k, v in _data.get('spot_images', {}).items()}
except Exception:
    _SPOT_IMAGES = {}
'''

# 在 Flask 初始化前插入
marker = 'app = Flask(__name__)'
if marker in content and 'SPOT_IMAGES' not in content:
    content = content.replace(marker, load_code + '\n' + marker, 1)
    print('OK: 插入 _SPOT_IMAGES 加载代码')
else:
    print('SKIP: 加载代码已存在或找不到标记')

# ── 2. 在 spot_detail_page 中给 spot 附加 image_urls ──────────
# 找到 return render_template("spot_detail.html", spot=spot)
old_render = '    return render_template("spot_detail.html", spot=spot)'
new_render = '''    # 附加多图 URL
    spot_id = spot.get('id', '')
    spot['image_urls'] = _SPOT_IMAGES.get(spot_id, [spot.get('image_url', '')])
    return render_template("spot_detail.html", spot=spot)'''

if old_render in content:
    content = content.replace(old_render, new_render, 1)
    print('OK: 更新 spot_detail_page 渲染')
else:
    print('WARN: 未找到 spot_detail_page 的 render 行')

# ── 3. 在 get_spot_detail API 中返回 image_urls ──────────────
# 找到 "image_url": s.get("image_url", "") or s.get("image", ""),
old_api_img = '"image_url": s.get("image_url", "") or s.get("image", ""),'
new_api_img = '"image_url": s.get("image_url", "") or s.get("image", ""),\n        "image_urls": _SPOT_IMAGES.get(spot_id, [s.get("image_url", "") or s.get("image", "")]),'

if old_api_img in content:
    content = content.replace(old_api_img, new_api_img, 1)
    print('OK: 更新 get_spot_detail API')
else:
    print('WARN: 未找到 get_spot_detail 的 image_url 行')

# 写回
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n完成：app.py 已更新')
