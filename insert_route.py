"""
在 app.py 的 if __name__ == "__main__": 前插入行程页路由
"""
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

route_code = '''

# ── V8 行程管理页面 ────────────────────────────────────────
@app.route("/my-itineraries")
def my_itineraries():
    """我的行程页面（查看已保存的行程）"""
    return render_template("itinerary_detail.html")
'''

# 在 if __name__ == "__main__": 前插入
marker = 'if __name__ == "__main__":'
if marker in content:
    content = content.replace(marker, route_code + '\n' + marker)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ 路由 /my-itineraries 已添加')
else:
    print('❌ 未找到', marker)
