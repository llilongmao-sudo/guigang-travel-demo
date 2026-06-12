# -*- coding: utf-8 -*-
import os, re

path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find all badge.textContent assignments
for m in re.finditer(r'badge\.textContent\s*=\s*[\'\"](.+?)[\'\"]', html):
    start = max(0, m.start()-30)
    end = min(len(html), m.end()+30)
    context = html[start:end].replace('\n',' ')
    print(f'[{m.start()}] "{m.group(1)}" | ...{context}...')
