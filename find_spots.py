# -*- coding: utf-8 -*-
path = 'templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find where spots array is defined
idx = html.find('const spots = [')
if idx > 0:
    chunk = html[idx:idx+200]
    with open('spots_array.txt', 'w', encoding='utf-8') as out:
        out.write(chunk)
    print(f'Found spots at {idx}')
else:
    # Try other patterns
    for pat in ['let spots = ', 'var spots = ', 'spots = [']:
        idx = html.find(pat)
        if idx > 0:
            chunk = html[idx:idx+200]
            with open('spots_array.txt', 'w', encoding='utf-8') as out:
                out.write(chunk)
            print(f'Found spots with "{pat}" at {idx}')
            break
