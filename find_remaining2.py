# -*- coding: utf-8 -*-
path = 'templates/index.html'
with open(path, 'rb') as f:
    data = f.read()

# Find all occurrences of 主题乐园 (UTF-8 bytes)
target = '主题乐园'.encode('utf-8')
pos = 0
while True:
    idx = data.find(target, pos)
    if idx < 0:
        break
    # Get surrounding context
    start = max(0, idx - 50)
    end = min(len(data), idx + 80)
    chunk = data[start:end].decode('utf-8', errors='replace')
    with open(f'remaining_{idx}.txt', 'w', encoding='utf-8') as out:
        out.write(f'At byte {idx}:\n{chunk}\n')
    print(f'Found at byte {idx}')
    pos = idx + 1
