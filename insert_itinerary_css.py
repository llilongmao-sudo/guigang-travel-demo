"""
在 .hero-ai-btn:active CSS 后插入 .hero-itinerary-btn 样式
"""
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 在 .hero-ai-btn:active 块后插入新样式
old_marker = """.hero-ai-btn:active {
            transform: scale(0.97);
            box-shadow: 0 2px 8px rgba(16,185,129,0.25);
        }"""

new_css = """.hero-ai-btn:active {
            transform: scale(0.97);
            box-shadow: 0 2px 8px rgba(16,185,129,0.25);
        }
        /* 我的行程 第二入口 */
        .hero-itinerary-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            margin: 6px 0 12px;
            padding: clamp(10px, 2.5vw, 14px) clamp(16px, 4vw, 24px);
            background: #fff;
            border: 2px solid #10b981;
            border-radius: 14px;
            color: #10b981;
            font-size: clamp(14px, 3.5vw, 17px);
            font-weight: 700;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
            position: relative;
            z-index: 2;
        }
        .hero-itinerary-btn:active {
            transform: scale(0.97);
            background: #f0fdf4;
        }"""

if old_marker in content:
    content = content.replace(old_marker, new_css, 1)
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: CSS 已插入')
else:
    print('ERROR: 未找到标记')
    # 调试：找 hero-ai-btn:active
    idx = content.find('hero-ai-btn:active')
    print(f'位置: {idx}')
    if idx > 0:
        print(repr(content[idx:idx+200]))
