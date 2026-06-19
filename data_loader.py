# -*- coding: utf-8 -*-
"""
统一数据加载器 - 整合 attractions.json, routes.json, categories.json
"""
import json
import os
from typing import Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

class DataLoader:
    """景点、路线、分类数据加载器"""
    _attractions = None
    _routes = None
    _categories = None
    
    @classmethod
    def _load_json(cls, filename: str) -> dict:
        """加载JSON文件"""
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @classmethod
    def get_attractions(cls, reload: bool = False) -> List[Dict]:
        """获取所有景点数据"""
        if cls._attractions is None or reload:
            data = cls._load_json('attractions.json')
            cls._attractions = data.get('attractions', [])
        return cls._attractions
    
    @classmethod
    def get_attraction_by_id(cls, attraction_id: str) -> Optional[Dict]:
        """根据ID获取景点"""
        attractions = cls.get_attractions()
        for a in attractions:
            if a.get('id') == attraction_id:
                return a
        return None
    
    @classmethod
    def get_attractions_by_category(cls, category_id: str) -> List[Dict]:
        """根据分类获取景点"""
        attractions = cls.get_attractions()
        return [a for a in attractions if category_id in a.get('category_ids', [])]
    
    @classmethod
    def get_categories(cls, reload: bool = False) -> List[Dict]:
        """获取所有分类数据"""
        if cls._categories is None or reload:
            data = cls._load_json('categories.json')
            cls._categories = data.get('categories', [])
        return cls._categories
    
    @classmethod
    def get_category_by_id(cls, category_id: str) -> Optional[Dict]:
        """根据ID获取分类"""
        categories = cls.get_categories()
        for c in categories:
            if c.get('id') == category_id:
                return c
        return None
    
    @classmethod
    def get_routes(cls, reload: bool = False) -> List[Dict]:
        """获取所有路线数据（优先加载 V2）"""
        if cls._routes is None or reload:
            # 优先加载 V2 版本
            data = cls._load_json('routes_v2.json')
            if not data or not data.get('routes'):
                data = cls._load_json('routes.json')
            cls._routes = data.get('routes', [])
        return cls._routes
    
    @classmethod
    def get_route_by_id(cls, route_id: str) -> Optional[Dict]:
        """根据ID获取路线"""
        routes = cls.get_routes()
        for r in routes:
            if r.get('id') == route_id:
                return r
        return None
    
    @classmethod
    def get_routes_by_tag(cls, tag: str) -> List[Dict]:
        """根据标签获取路线"""
        routes = cls.get_routes()
        return [r for r in routes if tag in r.get('tags', [])]
    
    @classmethod
    def search(cls, query: str) -> Dict[str, List]:
        """全局搜索"""
        query = query.lower()
        results = {
            'attractions': [],
            'routes': [],
            'categories': []
        }
        
        # 搜索景点
        for a in cls.get_attractions():
            if query in a.get('name', '').lower():
                results['attractions'].append(a)
            elif query in ' '.join(a.get('tags', [])).lower():
                results['attractions'].append(a)
        
        # 搜索路线
        for r in cls.get_routes():
            if query in r.get('name', '').lower():
                results['routes'].append(r)
            elif query in r.get('short_name', '').lower():
                results['routes'].append(r)
        
        return results
    
    @classmethod
    def get_seasonal_routes(cls, month: int = None) -> List[Dict]:
        """获取季节性路线"""
        if month is None:
            from datetime import datetime
            month = datetime.now().month
        
        routes = cls.get_routes()
        results = []
        
        for r in routes:
            best_season = r.get('best_season', '')
            if not best_season:
                continue
            
            # 解析月份范围（如"6-8月"、"5-9月"）
            import re
            match = re.search(r'(\d+)-(\d+)月?', best_season)
            if match:
                start, end = int(match.group(1)), int(match.group(2))
                if start <= month <= end:
                    results.append(r)
        
        return results
    
    @classmethod
    

    @classmethod
    def get_foods(cls, reload: bool = False) -> List[Dict]:
        """获取所有美食数据（优先加载 V2）"""
        if not hasattr(cls, '_foods') or cls._foods is None or reload:
            # 优先加载 V2 版本
            data = cls._load_json('food_v2.json')
            if not data or not data.get('foods'):
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

    @classmethod
    def get_stats(cls) -> Dict:
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
        }


# 便捷函数
def get_attractions():
    return DataLoader.get_attractions()

def get_routes():
    return DataLoader.get_routes()

def get_categories():
    return DataLoader.get_categories()

def get_stats():
    return DataLoader.get_stats()


if __name__ == '__main__':
    # 测试数据加载
    stats = get_stats()
    print(f"数据加载成功：")
    print(f"  景点: {stats['attractions']} 个")
    print(f"  分类: {stats['categories']} 个")
    print(f"  路线: {stats['routes']} 条")
    
    # 测试季节性路线
    seasonal = DataLoader.get_seasonal_routes(6)
    print(f"\n6月推荐路线: {[r['short_name'] for r in seasonal]}")
