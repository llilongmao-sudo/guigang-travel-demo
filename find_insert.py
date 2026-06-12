# -*- coding: utf-8 -*-
path = 'templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find where to insert food section - after quick-actions-bar
pos = html.find('quick-actions-bar')
if pos > 0:
    # Find end of quick-actions-bar div
    end = html.find('</div>', pos)
    # Count nested divs
    depth = 1
    search = end + 1
    while depth > 0:
        next_open = html.find('<div', search)
        next_close = html.find('</div>', search)
        if next_close < next_open or next_open < 0:
            depth -= 1
            end = next_close
            search = next_close + 6
        else:
            depth += 1
            search = next_open + 4
    
    print(f'quick-actions-bar ends at {end}')
    # Show what comes after
    chunk = html[end+6:end+200]
    print(f'After: {chunk[:100]}')
else:
    print('NOT FOUND')
