# -*- coding: utf-8 -*-
path = 'templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Get the category grid HTML section (around 56700-58600)
start = 56700
end = 58800
chunk = html[start:end]
with open('cat_grid_html.txt', 'w', encoding='utf-8') as out:
    out.write(chunk)
print(f'Written {end-start} bytes')
