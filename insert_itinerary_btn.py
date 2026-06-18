"""
在 index.html 的 AI 规划按钮后插入"我的行程"按钮
"""
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 在 AI 按钮的 </div> 后插入新按钮
old = '''<button class="hero-ai-btn" onclick="openPlanningModal()">🤖 AI 帮我规划旅行</button>
            </div>'''

new = '''<button class="hero-ai-btn" onclick="openPlanningModal()">🤖 AI 帮我规划旅行</button>
                <button class="hero-itinerary-btn" onclick="location.href='/my-itineraries'">📋 我的行程</button>
            </div>'''

if old in content:
    content = content.replace(old, new)
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: 我的行程按钮已添加')
else:
    print('WARN: 未找到目标字符串')
