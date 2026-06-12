# -*- coding: utf-8 -*-
path = 'templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find spots data - search for spot entries with category field
import re
# Look for pattern: {name:'...', category:'...'}
for m in re.finditer(r"\{name:'[^']+',\s*category:'[^']+'}", html):
    print(f"Spot at {m.start()}: {m.group()[:80]}")
    
# Also look for SCENIC_SPOTS or spots definition
for pat in ['SCENIC_SPOTS', 'const spots', 'let spots', 'spotList']:
    idx = html.find(pat)
    if idx >= 0:
        print(f'\nFound "{pat}" at {idx}')
