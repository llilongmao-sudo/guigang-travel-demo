# -*- coding: utf-8 -*-
"""Fix indentation - get_stats got pushed outside class"""
path = 'data_loader.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The issue: food_methods were inserted before get_stats but the indentation 
# might have broken. Let's check
import re
# Find get_stats position and check if it's inside class
idx = content.find('def get_stats(')
if idx > 0:
    # Check preceding lines for class context
    chunk = content[max(0,idx-100):idx+50]
    with open('debug_stats.txt', 'w', encoding='utf-8') as out:
        out.write(chunk)
    print(f'get_stats at {idx}')
else:
    print('get_stats not found!')
