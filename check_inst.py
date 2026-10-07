import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('paea-entreprises.html', 'r', encoding='utf-8') as f:
    m = re.search(r'const DATA = (\[.*?\]);', f.read(), re.DOTALL)
    data = json.loads(m.group(1))

insts = [x for x in data if x.get('form') == 'Institution']
for i, inst in enumerate(insts):
    print(f"{i+1}. {inst['name']} -> {inst.get('contact', '')}")
