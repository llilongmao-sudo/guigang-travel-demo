# -*- coding: utf-8 -*-
"""添加新 API 端点到 app.py"""
import os

APP_PATH = os.path.join(os.path.dirname(__file__), 'app.py')

# 读取现有文件
with open(APP_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到最后的 route 定义位置
insert_pos = content.find('if __name__ == "__main__":')

new_routes = '''

# ── 新数据 API 端点（基于 DataLoader） ──────────────────────────────

@app.route("/api/attractions")
def get_attractions_list():
    """获取所有景点数据"""
    return jsonify({
        "meta": DataLoader._load_json('attractions.json').get('meta', {}),
        "attractions": DataLoader.get_attractions()
    })

@app.route("/api/attractions/<attraction_id>")
def get_attraction_detail(attraction_id):
    """获取单个景点详情"""
    attraction = DataLoader.get_attraction_by_id(attraction_id)
    if attraction:
        return jsonify(attraction)
    return jsonify({"error": "未找到该景点"}), 404

@app.route("/api/categories")
def get_categories_list():
    """获取所有分类数据"""
    return jsonify({
        "meta": DataLoader._load_json('categories.json').get('meta', {}),
        "categories": DataLoader.get_categories()
    })

@app.route("/api/categories/<category_id>/attractions")
def get_attractions_by_category(category_id):
    """获取某分类下的所有景点"""
    attractions = DataLoader.get_attractions_by_category(category_id)
    category = DataLoader.get_category_by_id(category_id)
    return jsonify({
        "category": category,
        "attractions": attractions,
        "count": len(attractions)
    })

@app.route("/api/data/stats")
def get_data_stats():
    """获取数据统计"""
    return jsonify(DataLoader.get_stats())

@app.route("/api/search")
def global_search():
    """全局搜索"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"error": "请提供搜索关键词"}), 400
    results = DataLoader.search(query)
    return jsonify(results)

@app.route("/api/seasonal")
def get_seasonal():
    """获取季节性推荐（默认当前月份）"""
    month = request.args.get('month', type=int)
    routes = DataLoader.get_seasonal_routes(month)
    return jsonify({
        "month": month,
        "routes": routes,
        "count": len(routes)
    })


'''

# 插入新代码
new_content = content[:insert_pos] + new_routes + content[insert_pos:]

# 写回文件
with open(APP_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ 已添加 8 个新 API 端点")
