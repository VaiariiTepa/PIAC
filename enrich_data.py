import json, sys

sys.stdout.reconfigure(encoding='utf-8')

# Charger uniquement les contacts directs vérifiés épurés de guichets
with open('all_direct_contacts.json', 'r', encoding='utf-8') as f:
    DIRECT_CONTACTS = json.load(f)

def determine_contact(item):
    name = item.get('name', '').strip()
    rep = item.get('rep', '').strip()
    cur_contact = item.get('contact', '').strip()

    # Si un statut particulier / alerte légale (ex: radiation, cessation) est présent, le conserver
    if cur_contact.startswith('⚠️'):
        return cur_contact

    # 1. Correspondance exacte par nom d'entité
    if name in DIRECT_CONTACTS:
        return DIRECT_CONTACTS[name]

    # 2. Correspondance par dirigeant / mandataire
    for k, v in DIRECT_CONTACTS.items():
        if k and (k in rep or (rep and rep in k)):
            return v

    # 3. Si l'entité a déjà un contact direct valide
    if cur_contact and not any(bad in cur_contact for bad in ['40 47 27 00', '40 54 85 10', 'Guichet de référence']):
        return cur_contact

    # 4. Si aucun contact direct n'est trouvé, laisser VIDE comme demandé par l'utilisateur
    return ""

if __name__ == '__main__':
    with open('data_enriched.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    with_contact = 0
    without_contact = 0

    for item in data:
        c = determine_contact(item)
        item['contact'] = c
        if c:
            with_contact += 1
        else:
            without_contact += 1

    with open('data_enriched.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Synchroniser le backup
    with open('data_enriched.backup.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"data_enriched.json et data_enriched.backup.json mis à jour avec succès :")
    print(f"- Total : {len(data)}")
    print(f"- Avec contact direct vérifié : {with_contact}")
    print(f"- Sans contact (laissé vide) : {without_contact}")
