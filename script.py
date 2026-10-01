import re

data = open('vercel_index.js', 'r', encoding='utf-16').read()
for match in re.findall(r'(https?://[^\s\"\'\>\;]+|ws://[^\s\"\'\>\;]+)', data):
    if 'onrender' in match or 'localhost' in match:
        print(match)
