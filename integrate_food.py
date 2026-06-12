# -*- coding: utf-8 -*-
"""
将美食模块集成到首页
1. 在CSS中添加美食卡片样式
2. 在chatArea欢迎卡片后添加美食推荐区块HTML
3. 在JS中添加loadFoods()函数
4. 更新status badge显示美食数量
"""
import re

path = 'templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

# ──── 1. Add food card CSS before </style> ────
food_css = '''
        /* ── Food Cards ── */
        .food-section { padding: 16px; }
        .food-section h3 {
            font-size: 15px; font-weight: 600; color: #333; margin-bottom: 12px;
            display: flex; align-items: center; gap: 6px;
        }
        .food-scroll { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 8px; -webkit-overflow-scrolling: touch; }
        .food-scroll::-webkit-scrollbar { display: none; }
        .food-card {
            min-width: 140px; max-width: 140px; background: #fff; border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden; cursor: pointer;
            transition: transform 0.2s;
        }
        .food-card:active { transform: scale(0.97); }
        .food-card-emoji { font-size: 36px; text-align: center; padding: 14px 0 8px; }
        .food-card-info { padding: 0 10px 12px; }
        .food-card-name { font-size: 13px; font-weight: 600; color: #333; margin-bottom: 3px; }
        .food-card-price { font-size: 11px; color: #888; }
        .food-card-tag {
            display: inline-block; font-size: 10px; padding: 1px 6px; border-radius: 8px;
            margin-top: 4px; background: #fff3e0; color: #e65100;
        }
        .food-card-tag.must-try { background: #e8f5e9; color: #2e7d32; }
'''

if '.food-card' not in html:
    html = html.replace('</style>', food_css + '\n    </style>')
    changes += 1
    print('OK: Added food CSS')

# ──── 2. Add food HTML after welcome-card in chatArea ────
food_html = '''
        <!-- 美食推荐 -->
        <div class="food-section" id="foodSection" style="display:none;">
            <h3>🍜 贵港必吃美食 <span style="font-size:11px;color:#888;font-weight:400;">| 向左滑动查看更多</span></h3>
            <div class="food-scroll" id="foodScroll"></div>
        </div>
'''

if 'id="foodSection"' not in html:
    # Insert after the quick-actions-bar (which is inside welcome-card)
    html = html.replace(
        '<div class="chat-area" id="chatArea">',
        '<div class="chat-area" id="chatArea">\n' + food_html
    )
    changes += 1
    print('OK: Added food HTML section')

# ──── 3. Add loadFoods() JS function ────
food_js = '''
    // ── Load Foods ──
    async function loadFoods() {
        try {
            const resp = await fetch('/api/foods/must-try');
            const foods = await resp.json();
            const container = document.getElementById('foodScroll');
            const section = document.getElementById('foodSection');
            if (!foods.length) { section.style.display = 'none'; return; }
            section.style.display = 'block';
            container.innerHTML = foods.map(f => `
                <div class="food-card" onclick="quickAsk('${f.name}有什么好吃的？怎么点？')">
                    <div class="food-card-emoji">${f.emoji}</div>
                    <div class="food-card-info">
                        <div class="food-card-name">${f.name}</div>
                        <div class="food-card-price">${f.price_range}</div>
                        ${f.must_try ? '<span class="food-card-tag must-try">必吃</span>' : ''}
                        <span class="food-card-tag">${f.flavor || f.tags[0] || ''}</span>
                    </div>
                </div>
            `).join('');
        } catch(e) { console.warn('Food load failed:', e); }
    }
'''

if 'async function loadFoods' not in html:
    # Insert before DOMContentLoaded
    html = html.replace(
        "document.addEventListener('DOMContentLoaded', () => {",
        food_js + "\n    document.addEventListener('DOMContentLoaded', () => {"
    )
    changes += 1
    print('OK: Added loadFoods() function')

# ──── 4. Call loadFoods in DOMContentLoaded ────
if 'loadFoods' not in html.split("DOMContentLoaded")[1][:500]:
    html = html.replace(
        "initHero();\n        loadCategories(); loadRoutes();",
        "initHero();\n        loadFoods();\n        loadCategories(); loadRoutes();"
    )
    changes += 1
    print('OK: Added loadFoods() call in DOMContentLoaded')

# ──── 5. Update status badge to show food count ────
old_badge = "📱 本地模式 · 30景点"
new_badge = "📱 本地模式 · 30景点 · 14美食"
if old_badge in html:
    html = html.replace(old_badge, new_badge)
    changes += 1
    print('OK: Updated status badge')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\nTotal changes: {changes}')
