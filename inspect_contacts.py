import json, re, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('paea-entreprises.html', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'const DATA = (\[.*?\]);', content, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    contacts = [x for x in data if x.get('contact')]
    print(f"Total contacts remplis : {len(contacts)} / {len(data)}")
    for c in contacts:
        print(f"- {c['name']} [{c.get('form')}] : {c['contact']}")
else:
    print("DATA non trouvé")
