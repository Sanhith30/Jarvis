with open('Jarvis_prompts.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all problematic special characters
content = content.replace('—', '-')  # Em dash
content = content.replace('–', '-')  # En dash
content = content.replace('…', '...')  # Ellipsis
content = content.replace(''', "'")  # Smart single quote
content = content.replace(''', "'")  # Smart single quote
content = content.replace('"', '"')  # Smart double quote
content = content.replace('"', '"')  # Smart double quote

with open('Jarvis_prompts.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all special characters!")
