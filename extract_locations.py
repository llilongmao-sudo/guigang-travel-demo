"""
提取 routes.json 中所有 location，去重，输出映射表
"""
import json

with open('data/routes.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

locations = set()
for route in data['routes']:
    for step in route.get('itinerary', []):
        loc = step.get('location', '')
        if loc:
            locations.add(loc)

# 同时提取所有 title 中的景点名
titles = set()
for route in data['routes']:
    for step in route.get('itinerary', []):
        t = step.get('title', '')
        if t:
            titles.add(t)

print("=== 所有 location（去重后）===")
for l in sorted(locations):
    print(l)

print("\n=== 所有 title（去重后）===")
for t in sorted(titles):
    print(t)
