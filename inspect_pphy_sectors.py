import json, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('pphy.json', 'r', encoding='utf-8') as f:
    pphy = json.load(f)

def show_group(title, filter_fn):
    items = [p for p in pphy if filter_fn(p)]
    print(f"\n=== {title} ({len(items)}) ===")
    for p in items[:25]:
        print(f"- {p['name']} | {p.get('naf','')} | {p.get('address','')}")

show_group("HÉBERGEMENT TOURISTIQUE (5520Z)", lambda p: '5520Z' in p.get('naf',''))
show_group("RESTAURATION RAPIDE / SNACK (5610C)", lambda p: '5610C' in p.get('naf',''))
show_group("SANTÉ / SOINS", lambda p: any(c in p.get('naf','') for c in ['8621', '8622', '8623', '8690']))
show_group("COIFFURE / BEAUTÉ (9602)", lambda p: '9602' in p.get('naf',''))
show_group("GARAGES / AUTO (4520)", lambda p: '4520' in p.get('naf',''))
