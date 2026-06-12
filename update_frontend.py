# -*- coding: utf-8 -*-
"""更新前端以使用新数据 API"""
import os
import re

HTML_PATH = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 更新分类图标（基于 categories.json）
category_updates = {
    '自然风光': {'emoji': '🏔️', 'color': '#2D5F3F'},
    '古郡探幽': {'emoji': '🏯', 'color': '#8B4513'},  # 原"人文历史"
    '公园休闲': {'emoji': '🌳', 'color': '#4A7C59'},
    '荷塘泛舟': {'emoji': '🪷', 'color': '#D44C7C'},  # 原"主题乐园"
    '科普教育': {'emoji': '🔬', 'color': '#3B7A8C'},
}

# 2. 更新 categoryEmoji 和 categoryColors
emoji_block = html[html.find('const categoryEmoji = {'):html.find('};', html.find('const categoryEmoji = {'))+2]
colors_block = html[html.find('const categoryColors = {'):html.find('};', html.find('const categoryColors = {'))+2]

new_emoji = '''const categoryEmoji = {
        '自然风光': '🏔️',
        '古郡探幽': '🏯',
        '公园休闲': '🌳',
        '荷塘泛舟': '🪷',
        '科普教育': '🔬'
    };'''

new_colors = '''const categoryColors = {
        '自然风光': ['#66bb6a','#388e3c'],
        '古郡探幽': ['#8d6e63','#5d4037'],
        '公园休闲': ['#66bb6a','#2e7d32'],
        '荷塘泛舟': ['#e91e63','#c2185b'],
        '科普教育': ['#29b6f6','#0288d1']
    };'''

html = html.replace(emoji_block, new_emoji)
html = html.replace(colors_block, new_colors)

# 3. 添加函数：从新 API 加载分类数据
load_categories_js = '''
    // 从新 API 加载分类数据
    async function loadCategories() {
        try {
            const resp = await fetch('/api/categories');
            const data = await resp.json();
            window.CATEGORIES_DATA = data.categories || [];
            return window.CATEGORIES_DATA;
        } catch (e) {
            console.error('加载分类数据失败:', e);
            return [];
        }
    }
    
    // 从新 API 加载路线数据
    async function loadRoutes() {
        try {
            const resp = await fetch('/api/routes');
            const data = await resp.json();
            window.ROUTES_DATA = data.routes || [];
            return window.ROUTES_DATA;
        } catch (e) {
            console.error('加载路线数据失败:', e);
            return [];
        }
    }
'''

# 在 initDistricts 之前插入
html = html.replace('function initDistricts()', load_categories_js + '\n    function initDistricts()')

# 4. 在 DOMContentLoaded 中调用
html = html.replace(
    'initDistricts();',
    'loadCategories(); loadRoutes(); initDistricts();'
)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ 前端已更新，集成新数据 API')
