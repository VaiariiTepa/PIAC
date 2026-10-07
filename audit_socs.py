import json, sys

sys.stdout.reconfigure(encoding='utf-8')

# Dictionnaire des contacts trouvés pour les sociétés
KNOWN_CONTACTS = {
    # 1. Grande distribution / Alimentation
    "SOCIETE COMMERCIALE DE PAEA": "☎ 40 52 30 03 · 🌐 championtahiti.com",
    "HAPPY MARKET PAEA": "☎ 40 82 89 89",
    "STE DE DISTRIBUTION DE PAEA": "☎ 40 53 32 19 / 89 46 66 66 · 🌐 magasins-u.pf",
    "MARCHE FRAICHEUR PAEA": "☎ 40 53 32 19 / 87 72 47 15 · 🌐 magasins-u.pf",
    "SOCIETE DE GESTION D'APPROVISIONNEMENT ET DE MARKETING": "☎ 40 82 89 89",
    "ATLAS PARTS IMPORT": "☎ 88 88 23 73 · ✉ atlaspartsimport@icloud.com",
    "ATRIA (ATRIATEITIEI 1 ET TEURUFARAPA)": "☎ 87 37 37 09 · ✉ direction.proenergie@gmail.com · 🌐 pro-energie-987.com",
    "SARL PRO ENERGIE": "☎ 87 37 37 09 · ✉ direction.proenergie@gmail.com · 🌐 pro-energie-987.com",
    "BIBI CASSE AUTO": "☎ 40 48 20 11 / 40 53 20 11",
    "BIBI RECYCLAGE": "☎ 40 48 20 11 / 40 53 20 11",
    "CAISHEN-TEMANA": "☎ 40 43 15 41",
    "MAMITA AND CO": "☎ 40 43 15 41",
    "CHEZ DONDON GRILL": "☎ 89 46 14 61 / 89 79 35 85 · 🌐 facebook.com/ChezDondonGrill",
    "COOPERATIVE PAHIAREPO NUI RAVA'AI": "☎ 87 79 65 85 · Port de pêche de Pahiaripo",
    "RAITIREA": "☎ 87 79 65 85 · Port de pêche de Pahiaripo",
    "HIGH PROTECT SYSTEMS": "☎ 87 77 62 22 · ✉ hps-agrizap@mail.pf",
    "HM IMPORT": "☎ 89 53 04 85",
    "HOTU MAHANA": "☎ 40 45 22 88 / 87 38 87 10 · ✉ hotumahana@gmail.com",
    "MAHANA PARK CENTER": "☎ 40 45 22 88 / 87 38 87 10 · ✉ hotumahana@gmail.com",
    "INNOVATION TRADING": "☎ 87 00 39 00 · 1er ét. Imm. Totoe Beach",
    "LE TAKI": "☎ 87 22 16 49",
    "TROPICAL BURGER": "☎ 87 22 16 49 (Tropical Grill Paea)",
    "SELARL PHARMACIE OPUHI": "☎ 40 50 30 05 / 40 53 31 53 · 🌐 pharmacieopuhi-pf.fr",
    "SNACK FUKU": "☎ 87 26 29 29 · ✉ chisaka@mail.pf",
    "TAHITI FENG SHUI": "☎ 40 82 78 78 (World of Feng Shui PK 22.3)",
    "TAHITI HARDWARE STORE": "☎ 40 85 60 43 (Quincaillerie Montaron PK 19.1)",
    "TAHITI LITERIE EURL": "☎ 40 82 48 24",
    "LA SAVONNERIE DE TAHITI (Tahitian Soap / Heiva Cosmétiques)": "☎ 40 42 31 31 · ✉ tahitiansoap@mail.pf · ✉ contact@heivacosmetics.com · 🌐 savonneriedetahiti.com",
    "LE COMPTOIR DES PLANTES POLYNESIENNES": "☎ 89 77 80 53 · 🌐 comptoir-plantes-polynesiennes.fr",
    "AVA TEA DISTILLATION": "☎ 89 40 14 14 · ✉ contact@manao.pf · 🌐 manao.pf",
    "VDM (VDM CHARPENTE)": "☎ 40 45 28 41 / 87 28 58 99 · ✉ vdm.charpente@yahoo.fr · 🌐 vdm-charpente.com",
    "SCIERIE DE TUBUAI": "☎ 40 45 28 41 / 87 28 58 99 · ✉ vdm.charpente@yahoo.fr · 🌐 vdm-charpente.com",
    "AITO COMPOSITES": "☎ 87 77 87 25 · 🌐 faivaa.com",
    "ALARME SCORPION": "☎ 40 43 78 18 / 87 77 78 05 · ✉ alarmescorpion@mail.pf · 🌐 videosurveillance-tahiti.com",
    "ANGELINA'S CROCHET TAHITI": "☎ 89 49 85 13 · ✉ angelinascrochettahiti@gmail.com · 🌐 angelinascrochettahiti.com",
    "ASSISTANCE AMBULANCE": "☎ 40 42 06 05 / 40 94 52 79 (Urgence SAMU : 15)",
    "DELICES DE TAHITI": "☎ 40 47 22 41 (PK 21.800 c/mont)",
    "HIVAI": "✉ hitivai.secretariat@gmail.com",
    "HOLOPUNI CANOES TAHITI": "☎ 87 78 01 01 · 🌐 holopunicanoes.com",
    "MBB": "☎ 40 67 10 24 / 87 67 10 24 (PK 19.900 c/mont)",
    "PHEBUS POLYNESIE": "☎ 87 73 95 07 / 87 77 59 50 · 🌐 phebus-polynesie.com",
    "WES ELEC": "☎ 89 72 78 31 / 87 75 08 15 · ✉ b.weselec@gmail.com",
    "ALOMA CL 28": "☎ 40 54 83 80 (Résidence White Plage / Poerava)",
    "'ATA 'ATA": "☎ 40 53 35 01 · 🌐 dr-chambaud-virginie.chirurgiens-dentistes.fr",
    "BLACKSTONE PRODUCTIONS": "☎ 89 36 47 66 / 87 27 69 31 · ✉ moana@blackstoneprod.com · 🌐 blackstoneprod.com",
    "BLUE PARADISE TOURS": "☎ 40 43 27 09 / 87 77 65 10",
    "CAP INGENIERIE": "☎ 40 54 41 25 · ✉ cap.contact@mail.pf",
    "DOUDOU CREPES & GAUFFRES": "☎ 87 24 23 18",
    "LES DELICES DE MERCURE": "☎ 87 24 23 18",
    "FILMIN TAHITI": "🌐 filmin-tahiti.com · Unifrance",
    "FUNERAIRE MARAETEFAU": "☎ 89 50 15 02 / 87 73 80 97 (24h/24)",
    "ICEBERG ASSISTANCE": "☎ 40 45 31 39 / 87 71 77 73 · ✉ iceberg.assistance@mail.pf",
    "JC A.G.I PEST CONTROL": "☎ 40 45 31 81 / 87 72 15 04 · ✉ direction@jcpestcontrol.pf · 🌐 jcpestcontrol.pf",
    "LES SAPINS": "☎ 40 53 33 87 / 87 74 29 42 (PK 18.5 c/mont)",
    "MARAMA LOCATION": "☎ 87 74 72 59 · ✉ marama.location@gmail.com · 🌐 marama-location.com",
    "RS CONCEPTION": "⚠️ Société dissoute / radiée (clôture 03/10/2025)",
    "SALT ADVENTURES": "☎ 87 05 20 20 / 87 75 14 33",
    "SARL PENSION TE MITI": "☎ 40 58 48 61 · ✉ pensiontemiti@mail.pf · 🌐 pensiontemiti.com",
    "SOLUTIONS SECURITE INCENDIE": "☎ 87 21 41 19 · ✉ solutionsecuriteincendie@gmail.com · 🌐 solutionsecuriteincendie.pf",
    "STORIES&CO PRODUCTIONS": "☎ 87 32 14 14 · ✉ corinne.pouplard@gmail.com · 🌐 stories-tahiti.com",
    "TAHITI AUTO CENTER": "☎ 40 82 33 33 / 89 52 62 89 · ✉ info@tahitiautocenter.com · 🌐 tahitiautocenter.com",
    "TAHITIAN SPIRIT": "☎ 87 27 79 07 · 🌐 osteopathie-tahiti.com",
    "TAKTIK.NET": "🌐 taktik.net",
    "TI AI MOANA": "☎ 40 42 75 87 / 89 78 44 73 · ✉ tiaimoana@mail.pf · 🌐 tiaimoana.fr",
    "TEK IT EZE": "☎ 40 42 75 87 / 89 78 44 73 · ✉ tiaimoana@mail.pf · 🌐 tiaimoana.fr",
    "VT ELEC": "☎ 89 56 60 01 · ✉ vtelec@outlook.com",
    "PACIFIC MOBILE TELECOM SAS": "☎ 89 89 (Vodafone Polynésie) · 🌐 vodafone.pf",
    "MANUVAI SHOP": "☎ 87 96 87 68 (Quartier Mahutatua)",
    "MARLON'S GASTRONOMY": "☎ 87 47 83 62 (PK 26.4 c/mont)",
    "MOON RAY": "☎ 40 82 89 89 · ✉ moonray@live.fr",
    "RVRP": "☎ 89 46 14 61 (Centre commercial Manuura Centre)",
    "TENTATIONS": "🌐 facebook.com/TentationsTahiti",
    "VISSAYAS DISTRIBUTION": "⚠️ Société radiée / clôture de liquidation",
    "KH BAT": "☎ 87 22 51 97 (Face école Vaiatu)",
    "M.V SERVICES": "☎ 87 79 89 70 (Lotissement CPS)",
    "PARC AUTO PAEA SERVICES": "☎ 89 49 00 51",
    "SOCIETE IA ORA CLEAN": "⚠️ En procédure de liquidation / dissolution",
}

with open('societes.json', 'r', encoding='utf-8') as f:
    socs = json.load(f)

matched = 0
unmatched = []
for s in socs:
    name = s['name']
    if name in KNOWN_CONTACTS or s.get('contact'):
        matched += 1
    else:
        unmatched.append(s)

print(f"Sociétés couvertes directement : {matched} / {len(socs)} ({matched/len(socs)*100:.1f}%)")
print(f"Sociétés restantes sans contact direct spécifique : {len(unmatched)}")
for u in unmatched:
    print(f"- {u['name']} | Rep: {u.get('rep','')} | NAF: {u.get('naf','')}")
