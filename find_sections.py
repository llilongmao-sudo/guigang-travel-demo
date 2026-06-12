# -*- coding: utf-8 -*-
path = 'templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find chat-area or messages div
for marker in ['<div class="chat-area"', '<div id="messages"', 'class="messages"']:
    pos = html.find(marker)
    if pos > 0:
        chunk = html[pos:pos+100]
        print(f'Found "{marker}" at {pos}: {chunk[:80]}')
        break

# Find the welcome-card section (hero section)
pos = html.find('class="hero-section"')
if pos > 0:
    # Go back to find parent
    start = html.rfind('<div', 0, pos)
    print(f'\nhero-section div starts around {start}')
