with open('Jarvis_prompts.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('—', '-')

with open('Jarvis_prompts.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all em dashes!")
