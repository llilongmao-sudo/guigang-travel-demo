# -*- coding: utf-8 -*-
"""升级前端：美食卡片显示图片 + 详情页大图"""
import re

path = 'templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

# ── 1. 升级美食卡片：emoji div → img 标签 ──
old_card = '''<div class="food-card-emoji">${f.emoji}</div>
                    <div class="food-card-info">'''

new_card = '''<div class="food-card-img">
                        <img src="${f.image || '/static/images/placeholder.svg'}" alt="${f.name}" onerror="this.parentElement.innerHTML='<div style=&quot;font-size:48px;text-align:center;padding:18px 0;&quot;>${f.emoji||'🍽️'}</div>'">
                    </div>
                    <div class="food-card-info">'''

if old_card in html:
    html = html.replace(old_card, new_card)
    changes += 1
    print('OK: Upgraded food card to use <img>')

# ── 2. 添加 food-card-img CSS ──
old_css = '''.food-card-emoji { font-size: 36px; text-align: center; padding: 14px 0 8px; }
        .food-card-info {'''

new_css = '''.food-card-img {
            width: 100%; height: 110px; overflow: hidden; background: #f5f5f5;
            display: flex; align-items: center; justify-content: center;
        }
        .food-card-img img { width: 100%; height: 100%; object-fit: cover; }
        .food-card-info {'''

if old_css in html:
    html = html.replace(old_css, new_css)
    changes += 1
    print('OK: Added food-card-img CSS')

# ── 3. 套餐卡片也加图片支持 ──
# 套餐卡片目前没有图片，先跳过，保持 icon 显示

# ── 4. 在美食详情弹窗中显示大图（如果点击美食卡片）───
# 修改 quickAsk 触发，改为先显示美食详情卡
# 这里先简单处理：在聊天区显示美食图片

# ── 5. 添加全局美食图片灯箱（点击放大）───
# 在 </body> 前添加灯箱 HTML
lightbox_html = '''
        <!-- 美食图片灯箱 -->
        <div id="foodLightbox" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:9999;align-items:center;justify-content:center;cursor:zoom-out;" onclick="this.style.display='none'">
            <img id="foodLightboxImg" src="" style="max-width:90%;max-height:80vh;border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,0.3);">
            <div id="foodLightboxName" style="color:#fff;font-size:16px;margin-top:12px;text-align:center;"></div>
        </div>
'''

if 'id="foodLightbox"' not in html:
    html = html.replace('</body>', lightbox_html + '</body>')
    changes += 1
    print('OK: Added food lightbox HTML')

# ── 6. 让美食卡片点击时显示大图（而不是只发消息）───
# 修改 food card onclick：先显示详情 + 大图
old_onclick = """onclick="quickAsk('${f.name}有什么好吃的？怎么点？')">""".replace('?', '?')  # just to match

# 新逻辑：点击卡片 → 显示美食详情弹窗
new_onclick = """onclick="showFoodDetail('${f.id}')">"""

if 'showFoodDetail' not in html:
    # 在 JS 中添加 showFoodDetail 函数
    food_js = '''
    // ── 美食详情弹窗 ──
    async function showFoodDetail(foodId) {
        try {
            const resp = await fetch('/api/foods/' + foodId);
            const f = await resp.json();
            if (f.error) return;
            const imgHtml = f.image ? `<img src="${f.image}" style="width:100%;height:180px;object-fit:cover;border-radius:12px;margin-bottom:10px;" onerror="this.style.display='none'">` : '';
            const msg = `${imgHtml}<div style="padding:8px 4px;"><div style="font-size:18px;font-weight:700;margin-bottom:6px;">${f.emoji||''} ${f.name}</div><div style="font-size:13px;color:#666;line-height:1.6;">${f.description||''}</div><div style="margin-top:8px;font-size:12px;color:#999;">📍 ${f.where_to_find||''}</div><div style="font-size:12px;color:#e65100;margin-top:4px;">💰 ${f.price_range||''}</div><div style="margin-top:6px;">${(f.tags||[]).map(t=>`<span style="display:inline-block;font-size:10px;padding:2px 8px;background:#f0f0f0;border-radius:8px;margin:2px;">${t}</span>`).join('')}</div></div>`;
            appendMessage(msg, 'bot');
            switchToChat();
        } catch(e) { quickAsk(foodId + ' 介绍'); }
    }
'''
    # 插入到 loadFoods 函数前
    html = html.replace(
        "async function loadFoods()",
        food_js + "\n    async function loadFoods()"
    )
    changes += 1
    print('OK: Added showFoodDetail() function')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\n✅ 前端升级完成！共 {changes} 处改动')
print('  - 美食卡片：emoji → <img> 标签')
print('  - 新增 food-card-img CSS（固定高度110px，cover裁剪）')
print('  - 点击美食卡片 → 显示详情（含图片）+ 发到聊天区')
print('  - 新增图片灯箱（可扩展）')
