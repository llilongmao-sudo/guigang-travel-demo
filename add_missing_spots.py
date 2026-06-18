"""
在 knowledge_base_v4.py 的 SCENIC_SPOTS 列表末尾（] 前）插入 4 个缺失景点：
1. 荷美覃塘 (qintang_hetang)
2. 九凌湖 (jiulinghu)
3. 龙头山 (longtoushan)
4. 北帝山 (beidishan)
"""
import re

with open('knowledge_base_v4.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 新景点数据（按现有格式）
new_spots = '''    # === 以下为路线数据补全新增景点 (2026-06-18) ===
    {
        "id": "qintang_hetang",
        "name": "荷美覃塘",
        "alias": ["覃塘荷塘", "荷花景区", "龙凤村荷田"],
        "category": "自然风光",
        "location": "覃塘区龙凤村",
        "district": "覃塘区",
        "lat": 23.08,
        "lng": 109.45,
        "rating": "免费",
        "ticket_price": "免费",
        "open_time": "全天开放",
        "image_url": "https://images.unsplash.com/photo-1471696035574180-96c066d5a59b?w=800&q=80",
        "description": "荷美覃塘是贵港市覃塘区的千亩荷田观光区，每年6-8月荷花盛开，是摄影和亲近自然的好去处。景区内有竹筏、环湖骑行等项目。",
        "highlights": ["千亩荷田", "竹筏体验", "环湖骑行", "莲藕宴"],
        "recommended_route": "入口→荷田观景区→竹筏码头→莲藕文化馆，全程约2小时",
        "tips": "6-8月为最佳观赏期；晨雾中的荷田最出片；建议自驾或包车前往",
        "near_by_spots": ["九凌湖", "覃塘莲藕产业示范区"],
        "near_by_hotels": []
    },
    {
        "id": "jiulinghu",
        "name": "九凌湖",
        "alias": ["九凌湖景区", "九凌湖旅游区"],
        "category": "自然风光",
        "location": "覃塘区石卡镇",
        "district": "覃塘区",
        "lat": 23.18,
        "lng": 109.52,
        "rating": "4A",
        "ticket_price": "免费（划船另收费）",
        "open_time": "全天开放",
        "image_url": "https://images.unsplash.com/photo-1501788507822-eb9b57b1067d?w=800&q=80",
        "description": "九凌湖是贵港市覃塘区的一处自然湖泊景区，湖水清澈，周围绿树成荫。游客可划船游湖、环湖骑行，是家庭出游的好去处。",
        "highlights": ["湖光山色", "划船", "环湖骑行", "地下泉眼"],
        "recommended_route": "入口→湖边步道→划船码头→环湖骑行道，全程约3小时",
        "tips": "划船约30元/小时；夏季注意防晒；可与大藤峡联游",
        "near_by_spots": ["荷美覃塘", "大藤峡"],
        "near_by_hotels": []
    },
    {
        "id": "longtoushan",
        "name": "龙头山",
        "alias": ["龙头山景区", "龙头山草原", "贵港草原"],
        "category": "自然风光",
        "location": "港北区奇石乡",
        "district": "港北区",
        "lat": 23.15,
        "lng": 109.58,
        "rating": "免费",
        "ticket_price": "免费（栈道免费）",
        "open_time": "全天开放",
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
        "description": "龙头山位于贵港市港北区，海拔1158米，拥有5000余亩高山草甸，被誉为贵港版「云端阿勒泰」。山上有悬崖栈道，是徒步、摄影、观星空的好去处。",
        "highlights": ["海拔1158米", "5000余亩草甸", "云海日出", "悬崖栈道", "星空露营"],
        "recommended_route": "山脚→爱情天梯→悬崖栈道→高山草甸→山顶，全程约4-5小时",
        "tips": "海拔较高，山顶风大，必带外套；看日出需凌晨4点出发；目前免大门票",
        "near_by_spots": ["东湖公园", "贵港市区"],
        "near_by_hotels": []
    },
    {
        "id": "beidishan",
        "name": "北帝山",
        "alias": ["北帝山旅游区", "平南北帝山"],
        "category": "自然风光",
        "location": "平南县大鹏镇",
        "district": "平南县",
        "lat": 23.55,
        "lng": 110.15,
        "rating": "4A",
        "ticket_price": "约100元（以景区公示为准）",
        "open_time": "08:00-18:00",
        "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80",
        "description": "北帝山旅游区位于贵港市平南县，是国家4A级旅游景区。景区内有玻璃栈道、祈福台等景点，是徒步和观景的好去处。夏季开放漂流项目。",
        "highlights": ["玻璃栈道", "祈福台", "北帝山漂流", "星空露营"],
        "recommended_route": "山门→玻璃栈道→祈福台→主峰，全程约4-5小时",
        "tips": "漂流仅5-9月开放；山上早晚凉，必带薄外套；民宿需提前1-2周预订",
        "near_by_spots": ["平南雄森动物大世界", "平南县城"],
        "near_by_hotels": []
    }'''

# 在最后一个 ] 前插入（SCENIC_SPOTS 列表的结尾）
# 找到列表结尾的 ]（前面有换行和空格）
old_tail = '\n]'
new_tail = ',\n' + new_spots + '\n]'

if old_tail in content:
    content = content.replace(old_tail, new_tail, 1)
    with open('knowledge_base_v4.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: 4 个缺失景点已插入 knowledge_base_v4.py')
else:
    print('ERROR: 未找到列表结尾 ]')
    # 调试：找最后 100 个字符
    idx = content.rfind(']')
    print(f'] 最后出现位置: {idx}')
    print('上下文:', repr(content[max(0,idx-50):idx+10]))
