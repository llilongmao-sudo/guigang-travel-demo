# -*- coding: utf-8 -*-
path = 'templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('const spots')
chunk = html[idx:idx+3000]
with open('spots_full.txt', 'w', encoding='utf-8') as out:
    out.write(chunk)
print(f'Written {len(chunk)} bytes from offset {idx}')
