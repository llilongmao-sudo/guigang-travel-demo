# -*- coding: utf-8 -*-
"""将美食数据整合到 data_loader.py 和 app.py"""
import os

# 1. 更新 data_loader.py 添加美食加载
LOADER_PATH = os.path.join(os.path.dirname(__file__), 'data_loader.py')
with open(LOADER_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Add food methods to DataLoader class
food_methods = '''

    @classmethod
    def get_foods(cls, reload: bool = False) -> List[Dict]:
        """获取所有美食数据"""
        if not hasattr(cls, '_foods') or cls._foods is None or reload:
            data = cls._load_json('food.json')
            cls._foods = data.get('foods', [])
        return cls._foods

    @classmethod
    def get_food_by_id(cls, food_id: str) -> Optional[Dict]:
        """根据ID获取美食"""
        foods = cls.get_foods()
        for f in foods:
            if f.get('id') == food_id:
                return f
        return None

    @classmethod
    def get_foods_by_category(cls, category: str) -> List[Dict]:
        """根据分类获取美食"""
        foods = cls.get_foods()
        return [f for f in foods if f.get('category') == category]

    @classmethod
    def get_must_try_foods(cls) -> List[Dict]:
        """获取必吃美食"""
        foods = cls.get_foods()
        return [f for f in foods if f.get('must_try')]

    @classmethod
    def get_signature_foods(cls) -> List[Dict]:
        """获取招牌美食"""
        foods = cls.get_foods()
        return [f for f in foods if f.get('signature')]

    @classmethod
    def search_food(cls, query: str) -> List[Dict]:
        """搜索美食"""
        query = query.lower()
        foods = cls.get_foods()
        results = []
        for f in foods:
            if query in f.get('name', '').lower():
                results.append(f)
            elif query in ' '.join(f.get('tags', [])).lower():
                results.append(f)
            elif query in f.get('area', '').lower():
                results.append(f)
        return results

'''

# Insert before get_stats method
stats_pos = content.find('def get_stats(')
if stats_pos > 0:
    content = content[:stats_pos] + food_methods + content[stats_pos:]

# Update get_stats to include foods
old_stats = '''def get_stats(cls) -> Dict:
        """获取数据统计"""
        return {
            'attractions': len(cls.get_attractions()),
            'categories': len(cls.get_categories()),
            'routes': len(cls.get_routes()),
            'tags': len(set(
                tag 
                for a in cls.get_attractions() 
                for tag in a.get('tags', [])
            ))
        }'''

new_stats = '''def get_stats(cls) -> Dict:
        """获取数据统计"""
        all_tags = set()
        for a in cls.get_attractions():
            for tag in a.get('tags', []):
                all_tags.add(tag)
        for f in cls.get_foods():
            for tag in f.get('tags', []):
                all_tags.add(tag)
        return {
            'attractions': len(cls.get_attractions()),
            'foods': len(cls.get_foods()),
            'categories': len(cls.get_categories()),
            'routes': len(cls.get_routes()),
            'tags': len(all_tags),
            'must_try_foods': len(cls.get_must_try_foods())
        }'''

content = content.replace(old_stats, new_stats)

with open(LOADER_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print('OK: data_loader.py updated with food support')

# 2. 更新 app.py 添加美食 API
APP_PATH = os.path.join(os.path.dirname(__file__), 'app.py')
with open(APP_PATH, 'r', encoding='utf-8') as f:
    app_content = f.read()

# Find position before if __name__
main_pos = app_content.find("if __name__ == '__main__':" )

food_apis = '''

# ── 美食 API 端点 ────────────────────────────────────────

@app.route("/api/foods")
def get_foods_list():
    """获取所有美食"""
    return jsonify({
        "meta": DataLoader._load_json('food.json').get('meta', {}),
        "foods": DataLoader.get_foods()
    })

@app.route("/api/foods/<food_id>")
def get_food_detail(food_id):
    """获取单个美食详情"""
    food = DataLoader.get_food_by_id(food_id)
    if food:
        return jsonify(food)
    return jsonify({"error": "未找到该美食"}), 404

@app.route("/api/foods/category/<category>")
def get_foods_by_category(category):
    """按分类获取美食"""
    foods = DataLoader.get_foods_by_category(category)
    return jsonify({"category": category, "foods": foods, "count": len(foods)})

@app.route("/api/foods/must-try")
def get_must_try_foods():
    """获取必吃美食列表"""
    return jsonify(DataLoader.get_must_try_foods())

@app.route("/api/foods/signature")
def get_signature_foods():
    """获取招牌美食列表"""
    return jsonify(DataLoader.get_signature_foods())

@app.route("/api/foods/search")
def search_foods():
    """搜索美食"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"error": "请提供搜索关键词"}), 400
    results = DataLoader.search_food(query)
    return jsonify(results)


'''

app_content = app_content[:main_pos] + food_apis + app_content[main_pos:]
with open(APP_PATH, 'w', encoding='utf-8') as f:
    f.write(app_content)

print('OK: app.py updated with 6 food API endpoints')
