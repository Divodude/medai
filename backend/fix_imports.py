import os
import glob

files = glob.glob('**/*.py', recursive=True)
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if 'from backend.' in content:
        print(f"Updating {f}")
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content.replace('from backend.', 'from '))
