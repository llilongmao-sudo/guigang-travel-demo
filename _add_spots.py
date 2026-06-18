import json

with open('data/attractions_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

gongzhou = {
    'id': 'gongzhou-park',
    'name': '龚州公园',
    'area': '平南县',
    'category_ids': ['park'],
    'level': '市级',
    'highlights': ['状元阁', '湖心亭', '正觉寺', '古建园林'],
    'best_season': '全年',
    'ticket': '免费',
    'open_hours': '全天',
    'duration_recommended': '1-2小时',
    'tags': ['公园', '古建', '免费', '出片'],
    'description': '平南县城中心综合性公园，有状元阁、湖心亭、正觉寺等标志性建筑，是市民休闲和摄影的好去处。',
    'tips': ['傍晚光线最佳', '可结合周边美食街游览'],
    'image': '/static/images/spots/gongzhou-park/1.jpg',
    'parking': {'has_parking': True, 'parking_fee': '免费', 'spaces': 50, 'notes': '公园门口路边停车'},
    'opening_hours_detail': {'open': '全天', 'notes': '免费开放'},
    'ticket_info': {'price': 0, 'type': '免费', 'notes': '免费开放'}
}

daan = {
    'id': 'daan-ancient',
    'name': '大安古建筑群',
    'area': '平南县大安镇',
    'category_ids': ['ancient'],
    'level': '全国重点文物保护单位',
    'highlights': ['岭南骑楼', '粤东会馆', '石拱桥', '明清古建'],
    'best_season': '全年',
    'ticket': '免费',
    'open_hours': '全天',
    'duration_recommended': '2-3小时',
    'tags': ['古建', '免费', '摄影', '平南县'],
    'description': '保存完好的明清古建筑群落，包括大骑楼、粤东会馆、石拱桥、古码头等，是研究两广古代商贸文化的重要实物资料。全国重点文保单位。',
    'tips': ['可结合平南南线旅游', '古镇老街小吃值得尝试'],
    'image': '/static/images/spots/daan-ancient/1.png',
    'parking': {'has_parking': False, 'notes': '古镇内不便停车，需停镇外'},
    'opening_hours_detail': {'open': '全天', 'notes': '古镇街道全天开放，店铺营业时间8:00-18:00'},
    'ticket_info': {'price': 0, 'type': '免费', 'notes': '古镇免费，部分景点收费'}
}

data['attractions'].append(gongzhou)
data['attractions'].append(daan)

with open('data/attractions_v2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

count = len(data['attractions'])
print(f"Done! Total spots: {count}")
print("Added: gongzhou-park, daan-ancient")
