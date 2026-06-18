"""
V9.5 数据升级：给 attractions_v2.json 添加 parking/opening_hours_detail/ticket_info 字段
"""
import json

# 读取现有数据
with open('data/attractions_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 定义新增字段的默认值（按景点 ID 定制）
parking_info = {
    "pingtianshan": {"has_parking": True, "parking_fee": "免费", "spaces": 200, "notes": "山脚下有停车场，旺季需早到"},
    "jiulinghu": {"has_parking": True, "parking_fee": "10元/次", "spaces": 150, "notes": "景区入口处"},
    "xishan": {"has_parking": True, "parking_fee": "15元/次", "spaces": 300, "notes": "西山脚下大型停车场"},
    "datengxia": {"has_parking": True, "parking_fee": "10元/次", "spaces": 100, "notes": "游客中心停车场"},
    "longtansi": {"has_parking": True, "parking_fee": "5元/次", "spaces": 80, "notes": "寺庙前空地"},
    "nanshansi": {"has_parking": False, "notes": "周边可停路边，建议打车"},
    "donghu": {"has_parking": False, "notes": "周边有收费停车场（5元/小时）"},
    "yuanboyuan": {"has_parking": True, "parking_fee": "免费", "spaces": 500, "notes": "园博园东/南门均有停车场"},
    "museum": {"has_parking": True, "parking_fee": "免费", "spaces": 50, "notes": "博物馆院内"},
    "xiongsen-animal": {"has_parking": True, "parking_fee": "10元/次", "spaces": 200, "notes": "景区大门前"},
    "danan-guzhen": {"has_parking": False, "notes": "古镇内不准停车，需停镇外"},
    "shigongsi": {"has_parking": True, "parking_fee": "免费", "spaces": 30, "notes": "寺前有空地"},
    "baishishan": {"has_parking": True, "parking_fee": "5元/次", "spaces": 100, "notes": "山门停车场"},
    "beidishan": {"has_parking": True, "parking_fee": "10元/次", "spaces": 150, "notes": "景区入口"},
    "hemeitantang": {"has_parking": False, "notes": "荷塘周边可临时停车"},
    "qinnangongyuan": {"has_parking": True, "parking_fee": "免费", "spaces": 100},
    "longhuagongyuan": {"has_parking": False, "notes": "周边道路可临停"},
    "zhoujiang": {"has_parking": False, "notes": "郁江边无专用停车场"},
    "macaojiang": {"has_parking": False, "notes": "沿江路可临时停车"},
    "tongguwan": {"has_parking": True, "parking_fee": "10元/次", "spaces": 80},
    "dakaihu": {"has_parking": False, "notes": "大开挖景区建议打车"},
    "guipin-laostreet": {"has_parking": False, "notes": "老街内不准通车"},
    "guipingguijizhi": {"has_parking": False, "notes": "建议停西山停车场后步行"},
    "pingnanxianbowuguan": {"has_parking": True, "parking_fee": "免费", "spaces": 30},
    "shanzhongcu": {"has_parking": False, "notes": "山中无停车场，需停村口"},
    "wuyuan": {"has_parking": False, "notes": "五原景区建议包车前往"},
    "xishanquan": {"has_parking": True, "parking_fee": "20元/次", "spaces": 100, "notes": "温泉酒店停车场"},
    "yuanboyuan-hehua": {"has_parking": True, "parking_fee": "免费", "spaces": 300, "notes": "夏季荷花节期间车位紧张"},
    "nature-museum": {"has_parking": True, "parking_fee": "免费", "spaces": 50},
    "jintian": {"has_parking": True, "parking_fee": "免费", "spaces": 80, "notes": "起义遗址停车场"},
}

# 营业时间详细信息
opening_hours_detail = {
    "pingtianshan": {"open": "全天", "best_time": "6:00-18:00", "notes": "山顶日出时段需夜爬"},
    "jiulinghu": {"open": "8:00-18:00", "closed_days": [], "notes": "夏季荷花节延长至20:00"},
    "xishan": {"open": "8:00-17:30", "ticket_stop": "16:30", "notes": "节假日可能延长"},
    "datengxia": {"open": "8:30-17:00", "notes": "游船班次：9:00/11:00/14:00/16:00"},
    "longtansi": {"open": "8:00-17:00", "notes": "初一/十五香火旺盛"},
    "nanshansi": {"open": "7:00-18:00", "notes": "常年开放"},
    "donghu": {"open": "6:00-22:00", "notes": "免费开放，夜间有灯光"},
    "yuanboyuan": {"open": "9:00-17:00", "closed_days": ["周一"], "notes": "法定节假日周一照常开放"},
    "museum": {"open": "9:00-17:00", "closed_days": ["周一"], "notes": "16:30停止入场"},
    "xiongsen-animal": {"open": "9:00-17:30", "notes": "16:00停止入场"},
    "danan-guzhen": {"open": "全天", "notes": "古镇街道全天开放，店铺营业时间8:00-18:00"},
    "shigongsi": {"open": "8:00-17:30", "notes": "香火最旺时段：农历初一/十五"},
    "baishishan": {"open": "8:00-17:00", "notes": "白石山攀岩需预约"},
    "beidishan": {"open": "8:30-17:00", "notes": "漂流季节（6-9月）延长至18:00"},
    "hemeitantang": {"open": "全天", "best_time": "6:00-19:00", "notes": "夏季荷花最佳观赏期6-8月"},
    "qinnangongyuan": {"open": "6:00-22:00", "notes": "免费开放"},
    "longhuagongyuan": {"open": "6:00-22:00", "notes": "免费开放"},
    "zhoujiang": {"open": "全天", "notes": "沿江步道全天开放"},
    "macaojiang": {"open": "全天", "notes": "沿江绿道全天开放"},
    "tongguwan": {"open": "9:00-21:00", "notes": "夜间灯光秀19:30-21:00"},
    "dakaihu": {"open": "8:00-17:00", "notes": "大开挖景区正在建设中"},
    "guipin-laostreet": {"open": "全天", "notes": "老街全天开放，店铺8:00-20:00"},
    "guipingguijizhi": {"open": "9:00-21:00", "notes": "骑楼夜景最佳时段19:00-22:00"},
    "pingnanxianbowuguan": {"open": "9:00-17:00", "closed_days": ["周一"], "notes": "16:30停止入场"},
    "shanzhongcu": {"open": "8:00-18:00", "notes": "山中无照明，建议白天前往"},
    "wuyuan": {"open": "8:00-17:00", "notes": "五原景区需包车前往"},
    "xishanquan": {"open": "9:00-23:00", "notes": "温泉开放至深夜，建议预约"},
    "yuanboyuan-hehua": {"open": "9:00-17:00", "closed_days": ["周一"], "notes": "荷花节期间（6-8月）延长至20:00"},
    "nature-museum": {"open": "9:00-17:00", "closed_days": ["周一"], "notes": "16:30停止入场"},
    "jintian": {"open": "9:00-17:00", "closed_days": ["周一"], "notes": "金田起义遗址，免费参观"},
}

# 门票详细信息
ticket_info = {
    "pingtianshan": {"price": 0, "type": "免费", "notes": "无需预约"},
    "jiulinghu": {"price": 30, "type": "门票", "discount": "学生半价", "notes": "含荷花节期间"},
    "xishan": {"price": 90, "type": "门票", "discount": "学生/老人半价", "notes": "索道另收费（上行40/下行30）"},
    "datengxia": {"price": 50, "type": "门票+游船", "notes": "游船为必选项"},
    "longtansi": {"price": 0, "type": "免费", "notes": "香火自愿"},
    "nanshansi": {"price": 0, "type": "免费", "notes": "常年免费"},
    "donghu": {"price": 0, "type": "免费", "notes": "免费开放"},
    "yuanboyuan": {"price": 0, "type": "免费", "notes": "园博园免费，部分展馆收费"},
    "museum": {"price": 0, "type": "免费", "notes": "需身份证登记"},
    "xiongsen-animal": {"price": 120, "type": "门票", "discount": "儿童/老人优惠", "notes": "含动物表演"},
    "danan-guzhen": {"price": 0, "type": "免费", "notes": "古镇免费，部分景点收费"},
    "shigongsi": {"price": 0, "type": "免费", "notes": "寺内自愿捐赠"},
    "baishishan": {"price": 60, "type": "门票", "notes": "攀岩项目另收费"},
    "beidishan": {"price": 80, "type": "门票+漂流", "notes": "漂流季节6-9月"},
    "hemeitantang": {"price": 0, "type": "免费", "notes": "荷塘免费，游船30元/人"},
    "qinnangongyuan": {"price": 0, "type": "免费", "notes": "免费开放"},
    "longhuagongyuan": {"price": 0, "type": "免费", "notes": "免费开放"},
    "zhoujiang": {"price": 0, "type": "免费", "notes": "沿江步道免费"},
    "macaojiang": {"price": 0, "type": "免费", "notes": "沿江绿道免费"},
    "tongguwan": {"price": 0, "type": "免费", "notes": "景区免费，游乐项目另收费"},
    "dakaihu": {"price": 0, "type": "免费（在建）", "notes": "景区建设中"},
    "guipin-laostreet": {"price": 0, "type": "免费", "notes": "老街免费"},
    "guipingguijizhi": {"price": 0, "type": "免费", "notes": "骑楼免费，部分店铺消费"},
    "pingnanxianbowuguan": {"price": 0, "type": "免费", "notes": "需身份证登记"},
    "shanzhongcu": {"price": 0, "type": "免费", "notes": "山中免费"},
    "wuyuan": {"price": 0, "type": "免费", "notes": "五原景区免费"},
    "xishanquan": {"price": 138, "type": "温泉门票", "discount": "住店客人优惠", "notes": "需预约"},
    "yuanboyuan-hehua": {"price": 0, "type": "免费", "notes": "园博园免费，荷花节期间可能收费"},
    "nature-museum": {"price": 0, "type": "免费", "notes": "需身份证登记"},
    "jintian": {"price": 0, "type": "免费", "notes": "金田起义遗址免费参观"},
}

# 更新每个景点
for attr in data['attractions']:
    aid = attr['id']
    
    # 添加 parking 字段
    if aid in parking_info:
        attr['parking'] = parking_info[aid]
    else:
        attr['parking'] = {"has_parking": False, "notes": "暂无停车信息"}
    
    # 添加 opening_hours_detail 字段
    if aid in opening_hours_detail:
        attr['opening_hours_detail'] = opening_hours_detail[aid]
    else:
        attr['opening_hours_detail'] = {"open": attr.get('open_hours', '未知'), "notes": ""}
    
    # 添加 ticket_info 字段
    if aid in ticket_info:
        attr['ticket_info'] = ticket_info[aid]
    else:
        attr['ticket_info'] = {"price": 0, "type": "未知", "notes": ""}

# 写回文件
with open('data/attractions_v2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 已更新 {len(data['attractions'])} 个景点的数据")
print("新增字段：parking / opening_hours_detail / ticket_info")
