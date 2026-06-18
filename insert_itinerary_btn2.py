"""
在 index.html Hero 区域的 AI 规划按钮后插入"我的行程"按钮
"""
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 AI 按钮的位置，在其后插入新按钮
# 兼容各种空格/换行情况：用正则
import re

# 匹配 AI 按钮的整个 tag（兼容各种写法）
pattern = r'(<button[^>]*hero-ai-btn[^>]*>.*?AI 帮我规划旅行.*?</button>)'

match = re.search(pattern, content, re.DOTALL)
if not match:
    print("ERROR: 未找到 AI 规划按钮")
    # 调试：查找包含 hero-ai-btn 的位置
    idx = content.find('hero-ai-btn')
    print(f"hero-ai-btn 位置: {idx}")
    if idx > 0:
        print("上下文:", repr(content[max(0,idx-50):idx+100]))
else:
    old_tag = match.group(1)
    # 新按钮
    new_btns = old_tag + '\n                <button class="hero-itinerary-btn" onclick="location.href=\'/my-itineraries\'">📋 我的行程</button>'
    
    content = content.replace(old_tag, new_btns, 1)
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK: 我的行程按钮已插入")
