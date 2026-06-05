#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证知识库 v4.0（简化版，无 emoji）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from knowledge_base_v4 import SCENIC_SPOTS, TRAVEL_TIPS, CATEGORY_INDEX, DISTRICT_STATS
    
    print("=" * 60)
    print("贵港旅游知识库 v4.0 验证")
    print("=" * 60)
    
    # 统计
    print(f"\n>> 景点总数：{len(SCENIC_SPOTS)} 个")
    print(f">> 旅游贴士：{len(TRAVEL_TIPS)} 条")
    print(f">> 分类索引：{len(CATEGORY_INDEX)} 个分类")
    print(f">> 行政区划：{len(DISTRICT_STATS)} 个区域")
    
    # 按行政区划统计
    print("\n>> 按行政区划分布：")
    district_count = {}
    for spot in SCENIC_SPOTS:
        district = spot.get("district", "未知")
        district_count[district] = district_count.get(district, 0) + 1
    
    for district, count in sorted(district_count.items(), key=lambda x: -x[1]):
        print(f"  • {district}：{count} 个景点")
    
    # 按分类统计
    print("\n>> 按分类统计：")
    category_count = {}
    for spot in SCENIC_SPOTS:
        category = spot.get("category", "未知")
        category_count[category] = category_count.get(category, 0) + 1
    
    for category, count in sorted(category_count.items(), key=lambda x: -x[1]):
        print(f"  • {category}：{count} 个景点")
    
    # 检查坐标
    print("\n>> 坐标检查：")
    has_coords = 0
    no_coords = []
    for spot in SCENIC_SPOTS:
        if spot.get("lat") and spot.get("lng"):
            has_coords += 1
        else:
            no_coords.append(spot["name"])
    
    print(f"  • 有坐标：{has_coords} 个")
    if no_coords:
        print(f"  • 无坐标：{len(no_coords)} 个")
        for name in no_coords:
            print(f"    - {name}")
    else:
        print(f"  • 无坐标：0 个")
    
    # 检查图片
    print("\n>> 图片检查：")
    has_image = 0
    no_image = []
    for spot in SCENIC_SPOTS:
        if spot.get("image_url"):
            has_image += 1
        else:
            no_image.append(spot["name"])
    
    print(f"  • 有图片：{has_image} 个")
    if no_image:
        print(f"  • 无图片：{len(no_image)} 个")
        for name in no_image:
            print(f"    - {name}")
    else:
        print(f"  • 无图片：0 个")
    
    # 检查贴士内容
    print("\n>> 贴士内容检查：")
    key_tips = ["最佳旅游季节", "交通方式", "住宿推荐", "特色美食", "行程建议（一日游）", "注意事项"]
    for tip in key_tips:
        if tip in TRAVEL_TIPS:
            print(f"  [OK] {tip}")
        else:
            print(f"  [缺失] {tip}（缺失）")
    
    # 新增内容检查
    print("\n>> 新增内容检查：")
    new_spots = ["马草江生态公园", "贵港市图书馆", "覃塘莲藕产业示范区", "桂平东塔", "桂平湿地公园", "北回归线标志公园"]
    for spot_name in new_spots:
        found = False
        for spot in SCENIC_SPOTS:
            if spot["name"] == spot_name:
                found = True
                break
        if found:
            print(f"  [OK] {spot_name}")
        else:
            print(f"  [缺失] {spot_name}（缺失）")
    
    new_tips = ["春季活动（3-5月）", "夏季活动（6-8月）", "秋季活动（9-11月）", "冬季活动（12-2月）", "壮族三月三", "摄影之旅", "美食之旅"]
    for tip_name in new_tips:
        if tip_name in TRAVEL_TIPS:
            print(f"  [OK] {tip_name}")
        else:
            print(f"  [缺失] {tip_name}（缺失）")
    
    print("\n" + "=" * 60)
    print(">> 验证完成！知识库 v4.0 已准备就绪")
    print("=" * 60)
    
except Exception as e:
    print(f"\n>> 验证失败：{e}")
    import traceback
    traceback.print_exc()
