import json, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('societes.json', 'r', encoding='utf-8') as f:
    socs = json.load(f)

print(f"Total sociétés : {len(socs)}")
for i, s in enumerate(socs):
    print(f"{i+1:3d}. {s['name']} | Forme: {s['form']} | NAF: {s.get('naf','')} | Rep: {s.get('rep','')} | Addr: {s.get('address','')} | Contact: {s.get('contact','')}")
