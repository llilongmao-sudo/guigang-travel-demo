# -*- coding: utf-8 -*-
"""综合整合：food.json(16道) + meal_combos.json(7套餐) + routes.json(5路线) + food_by_area.json"""
import os, json

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, 'data')
LOADER = os.path.join(BASE, 'data_loader.py')
APP = os.path.join(BASE, 'app.py')
TML = os.path.join(BASE, 'templates', 'index.html')

# ── 0. Verify data files ──
for fn in ['food.json', 'meal_combos.json', 'routes.json', 'food_by_area.json']:
    fp = os.path.join(DATA, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        d = json.load(f)
    if 'foods' in d: print(f"  {fn}: {len(d['foods'])} foods")
    elif 'combos' in d: print(f"  {fn}: {len(d['combos'])} combos")
    elif 'routes' in d: print(f"  {fn}: {len(d['routes'])} routes")
    elif 'areas' in d: print(f"  {fn}: {len(d['areas'])} areas")

# ── 1. Update data_loader.py ──
with open(LOADER, 'r', encoding='utf-8') as f:
    code = f.read()

# Add meal_combos and food_by_area loaders if not present
additions = '''
    # ── Meal Combos ──
    @classmethod
    def get_meal_combos(cls) -> list:
        if not hasattr(cls, '_combos') or cls._combos is None:
            data = cls._load_json('meal_combos.json')
            cls._combos = data.get('combos', [])
        return cls._combos

    @classmethod
    def get_combo_by_id(cls, cid: str) -> dict | None:
        for c in cls.get_meal_combos():
            if c.get('id') == cid:
                return c
        return None

    @classmethod
    def get_food_by_area(cls) -> list:
        if not hasattr(cls, '_food_areas') or cls._food_areas is None:
            data = cls._load_json('food_by_area.json')
            cls._food_areas = data.get('areas', [])
        return cls._food_areas

'''

if 'get_meal_combos' not in code:
    # Insert before get_stats
    pos = code.find('    @classmethod\n    def get_stats(')
    if pos > 0:
        code = code[:pos] + additions + code[pos:]
        print('OK: Added combo/area loaders')

with open(LOADER, 'w', encoding='utf-8') as f:
    f.write(code)

# ── 2. Update app.py with new APIs ──
with open(APP, 'r', encoding='utf-8') as f:
    app_code = f.read()

new_apis = '''

# ── 美食套餐 API ────────────────────────────────────────

@app.route("/api/meal-combos")
def get_meal_combos():
    return jsonify(DataLoader.get_meal_combos())

@app.route("/api/meal-combos/<combo_id>")
def get_meal_combo(combo_id):
    combo = DataLoader.get_combo_by_id(combo_id)
    if combo:
        # Resolve food_ids to food details
        foods = []
        for fid in combo.get('food_ids', []):
            food = DataLoader.get_food_by_id(fid)
            if food:
                foods.append(food)
        return jsonify({**combo, "foods_detail": foods})
    return jsonify({"error": "未找到该套餐"}), 404


# ── 美食区域 API ────────────────────────────────────────

@app.route("/api/food-by-area")
def get_food_by_area():
    return jsonify(DataLoader.get_food_by_area())


# ── 路线数据升级（从新版 routes.json）─────────────────────

@app.route("/api/routes-v2")
def get_routes_v2():
    """新版路线（含详细行程、美食、预算）"""
    return jsonify(DataLoader.get_routes())

@app.route("/api/routes-v2/<route_id>")
def get_route_v2(route_id):
    for r in DataLoader.get_routes():
        if r.get('id') == route_id:
            return jsonify(r)
    return jsonify({"error": "未找到该路线"}), 404


'''

if '/api/meal-combos' not in app_code:
    # Insert before if __name__
    main_pos = app_code.find("if __name__ == '__main__':")
    app_code = app_code[:main_pos] + new_apis + app_code[main_pos:]
    print('OK: Added combo/area/route-v2 APIs')

with open(APP, 'w', encoding='utf-8') as f:
    f.write(app_code)

# ── 3. Update frontend index.html ──
with open(TML, 'r', encoding='utf-8') as f:
    html = f.read()

# 3a. Add combo CSS
combo_css = '''
        /* ── Meal Combo Cards ── */
        .combo-section { padding: 0 16px 16px; }
        .combo-section h3 { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }
        .combo-scroll { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 8px; -webkit-overflow-scrolling: touch; }
        .combo-scroll::-webkit-scrollbar { display: none; }
        .combo-card {
            min-width: 200px; max-width: 200px; background: #fff; border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden; cursor: pointer;
            transition: transform 0.2s;
        }
        .combo-card:active { transform: scale(0.97); }
        .combo-card-header { padding: 12px; color: #fff; }
        .combo-card-header .combo-icon { font-size: 28px; }
        .combo-card-header .combo-name { font-size: 14px; font-weight: 600; margin-top: 4px; }
        .combo-card-header .combo-price { font-size: 11px; opacity: 0.9; }
        .combo-card-body { padding: 10px 12px; }
        .combo-card-body .combo-desc { font-size: 11px; color: #666; line-height: 1.4; }
        .combo-card-body .combo-foods { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px; }
        .combo-card-body .combo-food-tag { font-size: 10px; padding: 1px 6px; border-radius: 8px; background: #f0f0f0; color: #555; }
'''

if '.combo-card' not in html:
    html = html.replace('</style>', combo_css + '\n    </style>')
    print('OK: Added combo CSS')

# 3b. Add combo HTML after food section
combo_html = '''
        <!-- 美食套餐推荐 -->
        <div class="combo-section" id="comboSection" style="display:none;">
            <h3>🍱 吃什么？场景套餐</h3>
            <div class="combo-scroll" id="comboScroll"></div>
        </div>
'''

if 'id="comboSection"' not in html:
    html = html.replace(
        '<div class="food-section"',
        combo_html + '\n        <div class="food-section"'
    )
    print('OK: Added combo HTML')

# 3c. Add loadCombos JS
combo_js = '''
    // ── Load Meal Combos ──
    async function loadCombos() {
        try {
            const resp = await fetch('/api/meal-combos');
            const combos = await resp.json();
            const container = document.getElementById('comboScroll');
            const section = document.getElementById('comboSection');
            if (!combos.length) { section.style.display = 'none'; return; }
            section.style.display = 'block';
            container.innerHTML = combos.map(c => `
                <div class="combo-card" onclick="showComboDetail('${c.id}')">
                    <div class="combo-card-header" style="background:${c.color}">
                        <span class="combo-icon">${c.icon}</span>
                        <div class="combo-name">${c.name}</div>
                        <div class="combo-price">${c.price_range}</div>
                    </div>
                    <div class="combo-card-body">
                        <div class="combo-desc">${c.description}</div>
                        <div class="combo-foods">
                            ${(c.food_ids||[]).slice(0,3).map(id => '<span class="combo-food-tag">'+id.split('-').pop()+'</span>').join('')}
                        </div>
                    </div>
                </div>
            `).join('');
        } catch(e) { console.warn('Combo load failed:', e); }
    }

    function showComboDetail(comboId) {
        fetch('/api/meal-combos/' + comboId)
            .then(r => r.json())
            .then(data => {
                const foods = (data.foods_detail || []).map(f => f.emoji + ' ' + f.name + ' (' + f.price_range + ')').join('\\n');
                const msg = `🍽️ ${data.icon} ${data.name}\\n\\n${data.description}\\n\\n📋 包含美食:\\n${foods}\\n\\n💡 搭配思路:\\n${data.pairing_logic}\\n\\n💰 预算: ${data.price_range}\\n⏰ 最佳时段: ${data.best_time}`;
                appendMessage(msg, 'bot');
                switchToChat();
            });
    }
'''

if 'async function loadCombos' not in html:
    html = html.replace(
        "async function loadFoods()",
        combo_js + "\n    // ── Load Foods (existing) ──\n    async function loadFoods()"
    )
    print('OK: Added loadCombos JS')

# 3d. Call loadCombos in DOMContentLoaded
if 'loadCombos()' not in html.split("DOMContentLoaded")[1][:600]:
    html = html.replace(
        "loadFoods();\n        loadCategories();",
        "loadCombos();\n        loadFoods();\n        loadCategories();"
    )
    print('OK: Added loadCombos() call')

# 3e. Update status badge
html = html.replace('14美食', '16美食')

with open(TML, 'w', encoding='utf-8') as f:
    f.write(html)

print('\n✅ All done!')
print('  - food.json: 14→16 dishes (added 九凌湖鱼, 西山素斋)')
print('  - meal_combos.json: 7 combos')
print('  - routes.json: upgraded with full itinerary')
print('  - food_by_area.json: 5 areas')
print('  - New APIs: /api/meal-combos, /api/food-by-area, /api/routes-v2')
print('  - Frontend: combo cards on homepage')
