import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Charger et mettre à jour all_direct_contacts.json
with open('all_direct_contacts.json', 'r', encoding='utf-8') as f:
    direct_contacts = json.load(f)

new_verified_contacts = {
    "MOBYDICK TAHITI": "☎ 87 20 72 14 · ✉ mobydicktahiti@gmail.com · 🌐 mobydicktahiti.com · 🌐 facebook.com/MobydickTahiti",
    "SARL MOBYDICK TAHITI": "☎ 87 20 72 14 · ✉ mobydicktahiti@gmail.com · 🌐 mobydicktahiti.com · 🌐 facebook.com/MobydickTahiti",
    "PENSION TE MITI": "☎ 40 58 48 61 · ✉ pensiontemiti@mail.pf · 🌐 pensiontemiti.com · 🌐 facebook.com/pensiontemiti",
    "SARL PENSION TE MITI": "☎ 40 58 48 61 · ✉ pensiontemiti@mail.pf · 🌐 pensiontemiti.com · 🌐 facebook.com/pensiontemiti",
    "RESTAURANT CECILE PAEA": "☎ 40 82 82 86 · 🌐 smartmaptahiti.com",
    "RESTAURANT CECILE": "☎ 40 82 82 86 · 🌐 smartmaptahiti.com",
    "HAPPY LUNCH": "🌐 facebook.com/HappyLunchPaea",
    "FENUAFLOWAI": "☎ 87 38 51 47 · ✉ contact@fenuaflowai.com · 🌐 fenuaflowai.com · 🌐 facebook.com/Fenuaflowai",
    "APIJOB": "✉ contact@apijob.pf · 🌐 apijob.pf · 🌐 facebook.com/apijobpf",
    "HOHONU": "🌐 hohonuworld.store · 🌐 facebook.com/HohonuTahiti",
    "VILLA TIAITI": "☎ 89 70 07 10 · 🌐 booking.com",
    "SCI KAORIKI": "☎ 89 70 07 10 · 🌐 booking.com",
    "SCI KAORIKI (VILLA TIAITI)": "☎ 89 70 07 10 · 🌐 booking.com",
    "ANN SIMON TAHITI": "🌐 annsimontahiti.com · 🌐 facebook.com/annsimontahiti",
    "BLACKSTONE PRODUCTIONS": "☎ 87 27 69 31 / 89 36 47 66 · 🌐 blackstoneprod.com · 🌐 facebook.com/blackstoneprod",
    "TAHITI DETOX CENTER": "☎ 89 48 87 18 · 🌐 facebook.com/TahitiDetoxCenter",
    "BLUE PARADISE TOURS": "☎ 87 77 65 10 / 40 43 27 09 · 🌐 tahititourisme.fr/equipement/blue-paradise-tours",
    "SARL GARAGE DE PAEA API": "☎ 40 85 00 07",
    "GARAGE DE PAEA API": "☎ 40 85 00 07",
    "GARAGE DE PAEA": "☎ 40 85 00 07",
    "VT ELEC": "☎ 89 56 60 01 · ✉ vtelec@outlook.com",
    "SARL HERERAGI": "☎ 87 32 30 81 / 87 70 28 96 · ✉ sarlhereragi@yahoo.fr",
    "HERERAGI": "☎ 87 32 30 81 / 87 70 28 96 · ✉ sarlhereragi@yahoo.fr",
    "SAFE TAHITI": "🌐 facebook.com/SafeTahiti",
    "SELARL PHARMACIE OPUHI": "☎ 40 50 30 05 / 40 53 31 53 · 🌐 pharmacieopuhi-pf.fr · 🌐 facebook.com/pharmacieopuhi",
    "PHARMACIE OPUHI": "☎ 40 50 30 05 / 40 53 31 53 · 🌐 pharmacieopuhi-pf.fr · 🌐 facebook.com/pharmacieopuhi",
    "Michel Bourez": "🌐 facebook.com/michelbourez · 🌐 instagram.com/bourezmichel · 🌐 michelbourez.com"
}

direct_contacts.update(new_verified_contacts)

with open('all_direct_contacts.json', 'w', encoding='utf-8') as f:
    json.dump(direct_contacts, f, ensure_ascii=False, indent=2)

print(f"all_direct_contacts.json mis à jour : {len(direct_contacts)} entrées de contact direct.")

# 2. Charger les données actuelles
with open('data_enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Créer un dictionnaire pour accès rapide par nom majuscule
data_by_name = {d['name'].strip().upper(): d for d in data}

# 3. Mises à jour d'entreprises existantes avec données précises LexPol / JOPF
updates_existing = {
    "SARL IRON GUARD": {
        "address": "PK 20 côté montagne, BP 20140 Papeete, Paea",
        "rep": "M. Moehau Ruben Darrouzes (Gérant)",
        "ids": ["TAHITI B43203", "RCS 15 28 B"]
    },
    "SARL PACIFIC BUSINESS OVERSEAS": {
        "address": "PK 25,500, côté montagne, Paea",
        "rep": "M. Kevin Puaita Robson (Gérant)"
    },
    "MATAIVA": {
        "name": "SCP MATAIVA",
        "address": "PK 18,500, côté mer, quartier Papehue, Paea",
        "ids": ["TAHITI D14945", "RCS 20 208 D"]
    },
    "SERVICES ET TRAVAUX ELECTRIQUES DE POLYNESIE": {
        "address": "PK 19,200, servitude Avia, Paea",
        "rep": "M. Yves Teheipuarii (Gérant)"
    },
    "L'ART DU TAPOI ROI": {
        "address": "PK 20,200 côté montagne, Paea",
        "rep": "M. Patrick Maurice Juif (Gérant)"
    },
    "CONCEPT PEINTURE": {
        "address": "PK 18,900, lotissement Papehue 1, Paea"
    },
    "M.V SERVICES": {
        "address": "PK 20,600, lotissement CPS N°17, Paea",
        "rep": "M. Emile Ré Teraivetea Anihia (Gérant)"
    },
    "TKT PANDA PAEA": {
        "rep": "M. Aldo Teiva Sangue & Mme Rava Moerau Marama (Gérants)"
    },
    "PARC AUTO PAEA SERVICES": {
        "rep": "Mme Johanna Taata (Gérante) & M. Jean-Marc Lycurgue"
    },
    "MANA CATERING": {
        "address": "PK 22,700 côté montagne, Paea",
        "ids": ["TAHITI C88420", "RCS 21 112 B"]
    },
    "SARL GARAGE DE PAEA API": {
        "address": "PK 20,200 côté montagne, Paea",
        "contact": "☎ 40 85 00 07"
    },
    "SELARL PHARMACIE OPUHI": {
        "address": "PK 23,7 côté mer, Immeuble Totoe Beach, Paea",
        "contact": "☎ 40 50 30 05 / 40 53 31 53 · 🌐 pharmacieopuhi-pf.fr · 🌐 facebook.com/pharmacieopuhi"
    },
    "TAHITI DETOX CENTER": {
        "address": "PK 18,8, Servitude Frogier, Paea",
        "contact": "☎ 89 48 87 18 · 🌐 facebook.com/TahitiDetoxCenter"
    },
    "VT ELEC": {
        "address": "Derrière le magasin Apuarii, Paea",
        "contact": "☎ 89 56 60 01 · ✉ vtelec@outlook.com"
    },
    "SARL HERERAGI": {
        "address": "PK 20 côté montagne, Servitude Taputuarai, Paea",
        "contact": "☎ 87 32 30 81 / 87 70 28 96 · ✉ sarlhereragi@yahoo.fr"
    },
    "SAFE TAHITI": {
        "address": "Route Lotissement Bourne, Lot 17, Paea",
        "contact": "🌐 facebook.com/SafeTahiti"
    },
    "BLUE PARADISE TOURS": {
        "address": "Route vallée Orofero, Paea",
        "contact": "☎ 87 77 65 10 / 40 43 27 09 · 🌐 tahititourisme.fr/equipement/blue-paradise-tours"
    },
    "BLACKSTONE PRODUCTIONS": {
        "address": "Résidence Les Bougainvilliers N°13, Paea",
        "contact": "☎ 87 27 69 31 / 89 36 47 66 · 🌐 blackstoneprod.com · 🌐 facebook.com/blackstoneprod"
    },
    "GLOBAL SERVICES ET LOGISTIQUES": {
        "address": "PK 21,100, côté montagne, servitude Lehartel, Paea",
        "ids": ["TAHITI D95951", "RCS Papeete"],
        "rep": "Mme Mereani Hélène Erika Leblanc & M. Bertrand Leblanc"
    },
    "TAHITIAN SPIRIT": {
        "address": "PK 19,200, côté mer, Fare N°14, Paea",
        "ids": ["TAHITI D11347", "RCS Papeete"],
        "rep": "M. Nicolas Boussereau (Gérant)"
    },
    "BATI FENUA": {
        "address": "PK 22,500, N°8 Servitude Taurua, Paea"
    },
    "DIGITAL EXPERTS TAHITI (OCEAN4CLIMATE)": {
        "address": "PK 22 côté mer, Paea"
    },
    "SARL TAHITI COV CUSTOM": {
        "address": "PK 22,100 côté mer, Servitude Badot Lot N°8, Paea"
    }
}

updated_count = 0
for name_key, patch in updates_existing.items():
    target = None
    for k, v in data_by_name.items():
        if k == name_key or name_key in k:
            target = v
            break
    if target:
        for pk, pv in patch.items():
            target[pk] = pv
        updated_count += 1
        print(f"Mise à jour réussie : {target['name']}")

print(f"{updated_count} entreprises existantes enrichies avec succès.")

# 4. Nouvelles entités découvertes sur LexPol / JOPF et JuriPacific
new_entities = [
    {
        "name": "OAOA WEB",
        "form": "EURL",
        "cat": "SERVICES",
        "rep": "Mme Nathalie Cinquin (Gérante)",
        "naf": "6201Z – Programmation informatique",
        "ids": ["TAHITI F90833", "RCS Papeete"],
        "address": "10, servitude Teioatua, Paea",
        "contact": ""
    },
    {
        "name": "O PAIN DES ILES",
        "form": "SARL",
        "cat": "MÉTIER",
        "rep": "M. Axel Delaporte (Gérant)",
        "naf": "1071C – Industries alimentaires (Boulangerie)",
        "ids": ["TAHITI E47611", "RCS Papeete"],
        "address": "PK 22,200, côté montagne, servitude Brillant 1 lot 6, Paea",
        "contact": "⚠️ Statut : Clôture pour insuffisance d'actif enregistrée"
    },
    {
        "name": "FILMIN’ TAHITI",
        "form": "SARL",
        "cat": "SERVICES",
        "rep": "M. Denis Pinson (Gérant)",
        "naf": "5911A – Production audiovisuelle et cinéma",
        "ids": ["TAHITI B71584", "RCS Papeete"],
        "address": "PK 29 C/Montagne, Paea",
        "contact": ""
    },
    {
        "name": "MOBYDICK TAHITI",
        "form": "EURL",
        "cat": "SERVICES",
        "rep": "Direction Mobydick",
        "naf": "5010Z – Transports maritimes, observation baleines et plongée",
        "ids": ["TAHITI B68440", "RCS Papeete"],
        "address": "Port de pêche de Pahiarepo, PK 26.7, Paea",
        "contact": "☎ 87 20 72 14 · ✉ mobydicktahiti@gmail.com · 🌐 mobydicktahiti.com · 🌐 facebook.com/MobydickTahiti"
    },
    {
        "name": "SARL TE VAKA CRUISE",
        "form": "SARL",
        "cat": "SERVICES",
        "rep": "M. Rehia Samg-Mouit & M. Karl Chang (Gérants)",
        "naf": "5010Z – Transport maritime et côtier de passagers",
        "ids": ["TAHITI B18874", "RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "SARL PENSION TE MITI",
        "form": "SARL",
        "cat": "SERVICES",
        "rep": "Direction Pension Te Miti",
        "naf": "5520Z – Hébergement touristique et pension de famille",
        "ids": ["TAHITI 847255", "RCS Papeete"],
        "address": "PK 18,500 côté montagne, lotissement Papehue, Paea",
        "contact": "☎ 40 58 48 61 · ✉ pensiontemiti@mail.pf · 🌐 pensiontemiti.com · 🌐 facebook.com/pensiontemiti"
    },
    {
        "name": "FENUAFLOWAI",
        "form": "PPHY",
        "cat": "SERVICES",
        "rep": "Direction FenuaFlowAI",
        "naf": "6201Z – Solutions d'IA, automatisation et workflows",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": "☎ 87 38 51 47 · ✉ contact@fenuaflowai.com · 🌐 fenuaflowai.com · 🌐 facebook.com/Fenuaflowai"
    },
    {
        "name": "APIJOB",
        "form": "PPHY",
        "cat": "SERVICES",
        "rep": "Direction APIJOB",
        "naf": "6201Z – Plateforme de mise en relation de services",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": "✉ contact@apijob.pf · 🌐 apijob.pf · 🌐 facebook.com/apijobpf"
    },
    {
        "name": "HOHONU",
        "form": "SARL",
        "cat": "COMMERCE",
        "rep": "M. Todd Fagneaux (Gérant)",
        "naf": "1399Z – Impression textile, prêt-à-porter océanien et sérigraphie",
        "ids": ["TAHITI D74820", "RCS Papeete"],
        "address": "Boutique Hohonu, Paea",
        "contact": "🌐 hohonuworld.store · 🌐 facebook.com/HohonuTahiti"
    },
    {
        "name": "RESTAURANT CECILE PAEA",
        "form": "PPHY",
        "cat": "RESTAURATION",
        "rep": "Direction Restaurant Cécile",
        "naf": "5610A – Restauration traditionnelle et chinoise",
        "ids": ["Patenté Paea"],
        "address": "PK 22,300 côté montagne, Servitude 113, Résidence Tarevareva, Paea",
        "contact": "☎ 40 82 82 86 · 🌐 smartmaptahiti.com"
    },
    {
        "name": "HAPPY LUNCH",
        "form": "PPHY",
        "cat": "RESTAURATION",
        "rep": "Direction Happy Lunch",
        "naf": "5610C – Restauration rapide, snack et plats à emporter",
        "ids": ["Patenté Paea"],
        "address": "Centre médical Tiapa, Paea",
        "contact": "🌐 facebook.com/HappyLunchPaea"
    },
    {
        "name": "CHEZ VATEA",
        "form": "PPHY",
        "cat": "RESTAURATION",
        "rep": "M. Vatea Brodien",
        "naf": "5610C – Restauration rapide et snack à emporter",
        "ids": ["Patenté Paea"],
        "address": "PK 19,500 côté mer, Paea",
        "contact": ""
    },
    {
        "name": "SCI KAORIKI (VILLA TIAITI)",
        "form": "SCI",
        "cat": "SERVICES",
        "rep": "Gérance Kaoriki",
        "naf": "5520Z – Hébergement touristique et meublé de tourisme",
        "ids": ["TAHITI D55210", "RCS Papeete"],
        "address": "PK 20,500 côté mer, quartier Tiapa (face au temple Mormon), Paea",
        "contact": "☎ 89 70 07 10 · 🌐 booking.com"
    },
    {
        "name": "ANN SIMON TAHITI",
        "form": "PPHY",
        "cat": "MÉTIER",
        "rep": "Mme Anne Denise Simon",
        "naf": "3212Z – Bijouterie de luxe et perles de Tahiti",
        "ids": ["Patenté Paea"],
        "address": "PK 22, vallée Orofero, Paea",
        "contact": "🌐 annsimontahiti.com · 🌐 facebook.com/annsimontahiti"
    },
    {
        "name": "SAS PNEU FACTORY",
        "form": "SAS",
        "cat": "MÉTIER",
        "rep": "Direction Pneu Factory",
        "naf": "4520A – Pneumatiques et entretien automobile",
        "ids": ["RCS Papeete"],
        "address": "PK 22,100 côté mer, servitude Badot, Paea",
        "contact": ""
    },
    {
        "name": "SCI TIAPA",
        "form": "SCI",
        "cat": "SERVICES",
        "rep": "Gérance SCI Tiapa",
        "naf": "6820B – Administration et location d'immeubles",
        "ids": ["RCS Papeete"],
        "address": "PK 20,500 côté montagne, Immeuble Tiapa, Paea",
        "contact": ""
    },
    {
        "name": "SCI MANU 3",
        "form": "SCI",
        "cat": "SERVICES",
        "rep": "Gérance SCI Manu 3",
        "naf": "6820B – Administration et location d'immeubles",
        "ids": ["RCS Papeete"],
        "address": "PK 20,500 côté montagne, Paea",
        "contact": ""
    },
    {
        "name": "SCI TAHATAI 202 (EX-NUUTEA)",
        "form": "SCI",
        "cat": "SERVICES",
        "rep": "Gérance Tahatai",
        "naf": "6820B – Administration d'immeubles",
        "ids": ["RCS Papeete"],
        "address": "PK 19,100, servitude Sarciaux, Paea",
        "contact": ""
    },
    {
        "name": "SCI TE URA",
        "form": "SCI",
        "cat": "SERVICES",
        "rep": "Gérance Te Ura",
        "naf": "5520Z – Hébergement touristique de courte durée",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "SARL MATA'IREA LODGE",
        "form": "SARL",
        "cat": "SERVICES",
        "rep": "Direction Mata'irea Lodge",
        "naf": "5520Z – Hébergement touristique et lodge",
        "ids": ["RCS Papeete"],
        "address": "PK 18,500 côté montagne, quartier Papehue, Paea",
        "contact": ""
    },
    {
        "name": "ARGANCE II (FARE MITI)",
        "form": "SARL",
        "cat": "SERVICES",
        "rep": "Direction Fare Miti",
        "naf": "5520Z – Hébergement touristique de courte durée",
        "ids": ["RCS Papeete"],
        "address": "PK 20,400, Paea",
        "contact": ""
    },
    {
        "name": "SARL HISTOIRE DE GOUT",
        "form": "SARL",
        "cat": "RESTAURATION",
        "rep": "M. Guillaume Harlall (Gérant)",
        "naf": "5610A – Restauration et traiteur",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "ENORA",
        "form": "SARL",
        "cat": "COMMERCE",
        "rep": "M. Raufea Ariipeu (Gérant)",
        "naf": "4711D – Commerce et distribution",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "ONOIAU",
        "form": "SARL",
        "cat": "SERVICES",
        "rep": "M. Tepunavai Jouen (Gérant)",
        "naf": "0311Z – Pêche en mer et palangre",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "MATAMARAMA",
        "form": "SARL",
        "cat": "COMMERCE",
        "rep": "M. Allan Likafia & Mme Noéline Mauore (Gérants)",
        "naf": "4711D – Commerce et services",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "KIA MANUIA",
        "form": "SARL",
        "cat": "COMMERCE",
        "rep": "Mme Vaihere Tuataa (Gérante)",
        "naf": "4711D – Commerce et services",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "SARL HAPPINESS",
        "form": "SARL",
        "cat": "COMMERCE",
        "rep": "Mme Jeannine Taae épouse Chavez (Gérante)",
        "naf": "4711D – Commerce et services",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "NIKAEA",
        "form": "SARL",
        "cat": "SERVICES",
        "rep": "M. Michel Bourez (Gérant)",
        "naf": "9319Z – Activités sportives, surf et coaching",
        "ids": ["RCS Papeete"],
        "address": "PK 20,500 côté mer (face au temple Mormon), Paea",
        "contact": "🌐 facebook.com/michelbourez · 🌐 instagram.com/bourezmichel · 🌐 michelbourez.com"
    },
    {
        "name": "ALIIKAI",
        "form": "SARL",
        "cat": "SERVICES",
        "rep": "M. Michel Bourez (Gérant)",
        "naf": "9319Z – Activités nautiques et sportives",
        "ids": ["RCS Papeete"],
        "address": "PK 20,500 côté mer (face au temple Mormon), Paea",
        "contact": "🌐 facebook.com/michelbourez · 🌐 instagram.com/bourezmichel · 🌐 michelbourez.com"
    },
    {
        "name": "SARL PRO FLUIDE (EX-ATRIA PRO FLUIDE)",
        "form": "SARL",
        "cat": "MÉTIER",
        "rep": "Direction Pro Fluide",
        "naf": "4322B – Plomberie sanitaire, climatisation et ventilation",
        "ids": ["RCS Papeete"],
        "address": "PK 19,800, servitude Teriitua, Paea",
        "contact": ""
    },
    {
        "name": "SARL HAMANI CONCEPT",
        "form": "SARL",
        "cat": "MÉTIER",
        "rep": "Direction Hamani Concept",
        "naf": "4332A – Menuiserie intérieure, électricité et second œuvre",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "VSM TERRASSEMENT",
        "form": "SARL",
        "cat": "MÉTIER",
        "rep": "Direction VSM",
        "naf": "4312A – Travaux de terrassement et BTP",
        "ids": ["RCS Papeete"],
        "address": "PK 20,500 côté montagne, lotissement Tepuhapa, Paea",
        "contact": ""
    },
    {
        "name": "RENOV' TOIT TAHITI",
        "form": "SARL",
        "cat": "MÉTIER",
        "rep": "Direction Renov Toit",
        "naf": "4391A – Travaux de couverture, toiture et maçonnerie",
        "ids": ["RCS Papeete"],
        "address": "PK 28,500, Paea",
        "contact": ""
    },
    {
        "name": "TAHITI DIGITAL SERVICES",
        "form": "SARL",
        "cat": "SERVICES",
        "rep": "Direction TDS",
        "naf": "6202A – Informatique et télésurveillance",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "H&N",
        "form": "SARL",
        "cat": "COMMERCE",
        "rep": "Direction H&N",
        "naf": "4771Z – Vente de prêt-à-porter, accessoires et chaussures",
        "ids": ["RCS Papeete"],
        "address": "Vallée Orofero, Paea",
        "contact": ""
    },
    {
        "name": "SARL MAITAI NETTOYAGE",
        "form": "SARL",
        "cat": "SERVICES",
        "rep": "Direction Maitai Nettoyage",
        "naf": "8121Z – Nettoyage courant des bâtiments",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "KAHIWAI CREATION",
        "form": "SARL",
        "cat": "MÉTIER",
        "rep": "Direction Kahiwai Creation",
        "naf": "3213Z – Artisanat d'art et bijoux",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "PACIFIC NOMAD",
        "form": "SARL",
        "cat": "SERVICES",
        "rep": "Direction Pacific Nomad",
        "naf": "7721Z – Location d'articles de sport et loisirs",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "R.H.F.C.",
        "form": "SARL",
        "cat": "MÉTIER",
        "rep": "Direction RHFC",
        "naf": "4120A – Travaux du bâtiment",
        "ids": ["RCS Papeete"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "OK ENTREPRISE",
        "form": "PPHY",
        "cat": "MÉTIER",
        "rep": "Direction OK Entreprise",
        "naf": "4399Z – Travaux de construction et services",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "POLY-USINAGE",
        "form": "PPHY",
        "cat": "MÉTIER",
        "rep": "Direction Poly-Usinage",
        "naf": "2562B – Usinage et mécanique de précision",
        "ids": ["Patenté Paea"],
        "address": "PK 21,500 derrière le stade Manu Ura, Paea",
        "contact": "⚠️ Statut : Radiation enregistrée au RCS en décembre 2025"
    },
    {
        "name": "ART'S TILE TAHITI",
        "form": "PPHY",
        "cat": "MÉTIER",
        "rep": "M. Yannick Samy Schweizer",
        "naf": "4333Z – Travaux de carrelage et dallage",
        "ids": ["Patenté Paea"],
        "address": "PK 19,500 côté mer, Servitude Vihiaura Lot 1, Paea",
        "contact": "⚠️ Statut : Cessation d'activité enregistrée"
    },
    {
        "name": "AML",
        "form": "PPHY",
        "cat": "SERVICES",
        "rep": "Direction AML",
        "naf": "5320Z – Coursier, trading et prestations de services",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "TH CREATION",
        "form": "PPHY",
        "cat": "MÉTIER",
        "rep": "Direction TH Creation",
        "naf": "8130Z – Travaux en tous genres et jardinage",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "CHEF PASCAL",
        "form": "PPHY",
        "cat": "RESTAURATION",
        "rep": "M. Pascal (Chef)",
        "naf": "5621Z – Traiteur et chef à domicile",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "COCO BELLI",
        "form": "PPHY",
        "cat": "COMMERCE",
        "rep": "Direction Coco Belli",
        "naf": "4791A – Vente à distance et commerce",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": "⚠️ Statut : Radiation enregistrée en avril 2026"
    },
    {
        "name": "TEHEI ORA",
        "form": "PPHY",
        "cat": "SERVICES",
        "rep": "Direction Tehei Ora",
        "naf": "9604Z – Bien-être et soins",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "MANA TAMAU",
        "form": "PPHY",
        "cat": "MÉTIER",
        "rep": "Direction Mana Tamau",
        "naf": "9003B – Création artistique et artisanat",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "MOANA BOIS",
        "form": "PPHY",
        "cat": "MÉTIER",
        "rep": "Direction Moana Bois",
        "naf": "1629Z – Travail du bois et artisanat",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "T-KEN CHIC",
        "form": "PPHY",
        "cat": "MÉTIER",
        "rep": "Direction T-Ken Chic",
        "naf": "3213Z – Bijouterie fantaisie et artisanat",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "MAITI JOSEPH TETOHU",
        "form": "PPHY",
        "cat": "MÉTIER",
        "rep": "M. Joseph Tetohu Maiti",
        "naf": "4332A – Travaux de menuiserie bois et PVC",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "ATAIKI PRO SERVICE",
        "form": "PPHY",
        "cat": "MÉTIER",
        "rep": "Direction Ataiki Pro Service",
        "naf": "4322A – Plomberie, entretien et services",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "MANUURA JARDIN",
        "form": "PPHY",
        "cat": "SERVICES",
        "rep": "M. Franck Monire Richmond",
        "naf": "8130Z – Entretien d'espaces verts et jardinage",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "TUARANI JARDINAGE",
        "form": "PPHY",
        "cat": "SERVICES",
        "rep": "M. Yans Faaitoito Maitui",
        "naf": "8130Z – Entretien d'espaces verts et jardinage",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "LIGTHART SYLVIANE HEIPUA",
        "form": "PPHY",
        "cat": "SERVICES",
        "rep": "Mme Sylviane Heipua Ligthart",
        "naf": "8121Z – Nettoyage de locaux et jardinage",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "MINOUCHKA NETTOYAGE",
        "form": "PPHY",
        "cat": "SERVICES",
        "rep": "Direction Minouchka Nettoyage",
        "naf": "8121Z – Nettoyage de locaux et vitres",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "MARAMA CLEANING",
        "form": "PPHY",
        "cat": "SERVICES",
        "rep": "Direction Marama Cleaning",
        "naf": "8121Z – Entretien et nettoyage",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "WAHINE NANI ESTHETIQUE",
        "form": "PPHY",
        "cat": "SERVICES",
        "rep": "Direction Wahine Nani",
        "naf": "9602B – Esthétique itinérante et formation",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "MANUTAHI APICULTURE",
        "form": "PPHY",
        "cat": "COMMERCE",
        "rep": "Direction Manutahi",
        "naf": "0149Z – Apiculture et vente de miel",
        "ids": ["Patenté Paea"],
        "address": "Commune de Paea",
        "contact": ""
    },
    {
        "name": "GAYA FROM TAHITI",
        "form": "PPHY",
        "cat": "COMMERCE",
        "rep": "Mme Anitta Farah",
        "naf": "4791A – Commerce et créations",
        "ids": ["Patenté Paea"],
        "address": "Derrière garderie Chouna, Paea",
        "contact": ""
    }
]

added_count = 0
for ne in new_entities:
    name_up = ne['name'].strip().upper()
    if name_up not in data_by_name:
        data.append(ne)
        data_by_name[name_up] = ne
        added_count += 1
        print(f"Ajout nouvelle entité : {ne['name']} ({ne['form']})")

print(f"\n{added_count} nouvelles entités ajoutées à la base.")
print(f"Total nouveau dans data_enriched.json : {len(data)}")

# Sauvegarde dans data_enriched.json
with open('data_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("data_enriched.json sauvegardé avec succès.")
