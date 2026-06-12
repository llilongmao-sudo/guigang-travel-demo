# -*- coding: utf-8 -*-
path = 'templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find the category buttons in HTML (the grid of category cards)
import re
# Look for the category grid section - search for 自然风光 near emoji or button
patterns = [
    '人文历史',
    '主题乐园',
    'category-grid',
    'category-btn',
    'cat-card',
]

for pat in patterns:
    idx = html.find(pat)
    if idx > 0:
        start = max(0, idx-100)
        end = min(len(html), idx+200)
        chunk = html[start:end]
        with open(f'cat_check_{pat}.txt', 'w', encoding='utf-8') as out:
            out.write(f'=== Found "{pat}" at {idx} ===\n')
            out.write(chunk)
        print(f'Found "{pat}" at {idx}')

# Also find where categories are rendered as HTML buttons/cards
for m in re.finditer(r'(自然风光|人文历史|主题乐园)[^<]{0,50}', html):
    start = max(0, m.start()-50)
    end = min(len(html), m.end()+100)
    chunk = html[start:end]
    with open(f'cat_html_{m.start()}.txt', 'w', encoding='utf-8') as out:
        out.write(chunk)
    print(f'HTML occurrence of "{m.group(1)}" at {m.start()}')
