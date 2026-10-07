import json, re, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('paea-entreprises.html', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'const DATA = (\[.*?\]);', content, re.DOTALL)
if not m:
    print("DATA non trouvé")
    sys.exit(1)

data = json.loads(m.group(1))

societes = [x for x in data if x.get('form') in ('SARL', 'SAS', 'SNC', 'SELARL', 'SCP', 'COOP', 'EURL', 'SCI', 'SA')]
pphy = [x for x in data if x.get('form') == 'PPHY']
institutions = [x for x in data if x.get('form') == 'Institution']

print(f"Total: {len(data)}")
print(f"Sociétés: {len(societes)} (avec contact: {sum(1 for x in societes if x.get('contact'))})")
print(f"Patentés (PPHY): {len(pphy)} (avec contact: {sum(1 for x in pphy if x.get('contact'))})")
print(f"Institutions: {len(institutions)} (avec contact: {sum(1 for x in institutions if x.get('contact'))})")

with open('societes.json', 'w', encoding='utf-8') as f:
    json.dump(societes, f, ensure_ascii=False, indent=2)

with open('pphy.json', 'w', encoding='utf-8') as f:
    json.dump(pphy, f, ensure_ascii=False, indent=2)

print("Exporté dans societes.json et pphy.json")
