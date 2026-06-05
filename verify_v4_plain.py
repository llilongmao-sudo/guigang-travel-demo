#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证知识库 v4.0（纯英文输出，避免编码问题）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from knowledge_base_v4 import SCENIC_SPOTS, TRAVEL_TIPS, CATEGORY_INDEX, DISTRICT_STATS
    
    print("=" * 60)
    print("Guigang Travel Knowledge Base v4.0 Verification")
    print("=" * 60)
    
    # Statistics
    print(f"\n>> Total spots: {len(SCENIC_SPOTS)}")
    print(f">> Total tips: {len(TRAVEL_TIPS)}")
    print(f">> Category indexes: {len(CATEGORY_INDEX)}")
    print(f">> Districts: {len(DISTRICT_STATS)}")
    
    # By district
    print("\n>> Distribution by district:")
    district_count = {}
    for spot in SCENIC_SPOTS:
        district = spot.get("district", "Unknown")
        district_count[district] = district_count.get(district, 0) + 1
    
    for district, count in sorted(district_count.items(), key=lambda x: -x[1]):
        print(f"   - {district}: {count} spots")
    
    # By category
    print("\n>> Distribution by category:")
    category_count = {}
    for spot in SCENIC_SPOTS:
        category = spot.get("category", "Unknown")
        category_count[category] = category_count.get(category, 0) + 1
    
    for category, count in sorted(category_count.items(), key=lambda x: -x[1]):
        print(f"   - {category}: {count} spots")
    
    # Check coordinates
    print("\n>> Coordinate check:")
    has_coords = 0
    no_coords = []
    for spot in SCENIC_SPOTS:
        if spot.get("lat") and spot.get("lng"):
            has_coords += 1
        else:
            no_coords.append(spot["name"])
    
    print(f"   - With coordinates: {has_coords}")
    if no_coords:
        print(f"   - Without coordinates: {len(no_coords)}")
        for name in no_coords[:5]:  # Show only first 5
            print(f"      {name}")
        if len(no_coords) > 5:
            print(f"      ... and {len(no_coords) - 5} more")
    else:
        print(f"   - Without coordinates: 0")
    
    # Check images
    print("\n>> Image check:")
    has_image = 0
    no_image = []
    for spot in SCENIC_SPOTS:
        if spot.get("image_url"):
            has_image += 1
        else:
            no_image.append(spot["name"])
    
    print(f"   - With images: {has_image}")
    if no_image:
        print(f"   - Without images: {len(no_image)}")
    else:
        print(f"   - Without images: 0")
    
    # Check key tips
    print("\n>> Key tips check:")
    key_tips = ["Best travel season", "Transportation", "Accommodation", "Local food", "One-day itinerary", "Notes"]
    # Map English keys to Chinese keys
    tip_mapping = {
        "Best travel season": "最佳旅游季节",
        "Transportation": "交通方式",
        "Accommodation": "住宿推荐",
        "Local food": "特色美食",
        "One-day itinerary": "行程建议（一日游）",
        "Notes": "注意事项"
    }
    
    for eng_key, chn_key in tip_mapping.items():
        if chn_key in TRAVEL_TIPS:
            print(f"   [OK] {eng_key} ({chn_key})")
        else:
            print(f"   [MISSING] {eng_key} ({chn_key})")
    
    # Check new content
    print("\n>> New content check:")
    new_spots = ["马草江生态公园", "贵港市图书馆", "覃塘莲藕产业示范区", "桂平东塔", "桂平湿地公园", "北回归线标志公园"]
    for spot_name in new_spots:
        found = False
        for spot in SCENIC_SPOTS:
            if spot["name"] == spot_name:
                found = True
                break
        if found:
            print(f"   [OK] {spot_name}")
        else:
            print(f"   [MISSING] {spot_name}")
    
    new_tips = ["春季活动（3-5月）", "夏季活动（6-8月）", "秋季活动（9-11月）", "冬季活动（12-2月）", "壮族三月三", "摄影之旅", "美食之旅"]
    for tip_name in new_tips:
        if tip_name in TRAVEL_TIPS:
            print(f"   [OK] {tip_name}")
        else:
            print(f"   [MISSING] {tip_name}")
    
    print("\n" + "=" * 60)
    print(">> Verification completed! Knowledge base v4.0 is ready.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n>> Verification failed: {e}")
    import traceback
    traceback.print_exc()
