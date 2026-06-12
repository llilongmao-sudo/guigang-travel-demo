# -*- coding: utf-8 -*-
path = 'templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

import re
# Find remaining 主题乐园
for m in re.finditer(r'.{40}主题乐园.{40}', html):
    start = max(0, m.start())
    end = min(len(html), m.end())
    chunk = html[start:end]
    print(f'At {m.start()}:')
    print(chunk)
    print('---')
