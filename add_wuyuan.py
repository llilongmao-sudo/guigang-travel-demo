"""
在 knowledge_base_v4.py 的 century_square 条目前插入「吾园」景点
"""
with open('knowledge_base_v4.py', 'r', encoding='utf-8') as f:
    content = f.read()

wuyuan_spot = '''    {
        "id": "wuyuan",
        "name": "吾园",
        "alias": ["吾园景区", "苏式园林吾园"],
        "category": "城市公园",
        "location": "港北区荷城路",
        "district": "港北区",
        "lat": 23.12,
        "lng": 109.60,
        "rating": "免费",
        "ticket_price": "免费",
        "open_time": "08:00-18:00",
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
        "description": "吾园是贵港市区内的一座苏式园林，园内亭台楼阁、曲径通幽，是拍照、喂鱼、休闲散步的好去处。",
        "highlights": ["苏式园林", "亭台楼阁", "喂鱼", "拍照打卡"],
        "recommended_route": "南门→主殿→曲廊→荷塘→北门，全程约1.5小时",
        "tips": "免费开放；适合带老人小孩；晨练时段人较多",
        "near_by_spots": ["东湖公园", "世纪广场", "贵港博物馆"],
        "near_by_hotels": []
    },
'''

# 在 century_square 条目之前插入
marker = '    {\n        "id": "century_square"'
if marker in content:
    content = content.replace(marker, wuyuan_spot + '    {\n        "id": "century_square"', 1)
    with open('knowledge_base_v4.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: 吾园景点已插入')
else:
    print('ERROR: 未找到 century_square 标记')
