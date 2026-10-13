"""
Intègre dans data_enriched.json les résultats VÉRIFIÉS de la recherche web (octobre 2026) :
  1. contacts publics professionnels trouvés pour les sociétés / patentés qui n'avaient pas de téléphone ;
  2. associations loi 1901 dont le siège est à Paea (RNA, via assoce.fr), avec adresse et contacts vérifiés.

Seules les valeurs confirmées par un second agent vérificateur indépendant sont retenues.
La provenance (URL sources, verdict, motif) est conservée dans web_research_sources.json.

Usage : python integrate_web_research.py <journal.jsonl du workflow> [associations_paea_rna.json]
"""
import json
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

DATA_FILE = 'data_enriched.json'
SOURCES_FILE = 'web_research_sources.json'
RNA_FILE = 'associations_paea_rna.json'

PHONE_RE = re.compile(r'(?:\+?689[\s.]*)?((?:40|87|88|89)(?:[\s.]?\d{2}){3})')
GENERIC_PHONES = {'40548510', '40532053', '40472700', '40548500'}  # mairie, fax mairie, CCISM
ALERT_WORDS = ('radi', 'liquid', 'cess', 'dissou', 'dissol', 'clôtur', 'clotur', 'ferm')

# Catégories administratives RNA (libellés assoce.fr) -> domaine lisible pour le filtre « Domaine associatif »
DOMAINES = {
    'Sport': [
        'Sports, activités de plein air', 'Football (football, futsal)',
        'Sports de combat (boxe, kick box, boxe thaï, lutte)', "Tir (tir à l'arc, tir à balle, ball trap), javelot",
        "activités de plein air (dont saut à l'élastique)", 'associations multisports locales',
        'associations pour la promotion du sport, médailles, mérite sportif',
    ],
    'Culture & arts': [
        "culture, pratiques d'activités artistiques, culturelles", "promotion de l'art et des artistes",
        'danse', 'folklore', 'artisanat, travaux manuels, bricolage, expositions', 'sociétés, clubs de généalogie',
    ],
    'Patrimoine & foncier': ['préservation du patrimoine', 'comités de défense du patrimoine'],
    'Environnement & cadre de vie': [
        'Environnement, cadre de vie', 'protection de sites naturels', 'défense et amélioration du cadre de vie',
        "actions de sensibilisation et d'éducation à l'environnement et au développement durable",
        'ressources naturelles', 'jardins ouvriers, floralies',
    ],
    'Économie & emploi': [
        "représentation, promotion et défense d'intérêts économiques", 'association à but commercial, développement économique',
        "aide à l'emploi, développement local, promotion de solidarités économiques, vie locale",
        "conduite d'activités économiques", "aide à la création d'activités économiques individuelles",
        "associations pour la représentation d'artisans, de commerçants",
    ],
    'Agriculture & pêche': [
        "associations d'exploitants agricoles, élevage, horticulture, aviculture, apiculture, viticulture, viniculture",
        'chasse pêche',
    ],
    'Famille & solidarité': [
        'associations familiales, services sociaux pour les familles', 'aide et conseils aux familles',
        'services familiaux, services aux personnes âgées',
        'associations caritatives, humanitaires, aide au développement, développement du bénévolat',
        "groupements d'entraide et de solidarité",
        "amicales, groupements affinitaires, groupements d'entraide (hors défense de droits fondamentaux",
        'interventions sociales', 'amicale de sapeurs pompiers',
    ],
    'Éducation & jeunesse': [
        'éducation formation', "centre d'enseignement et de formation", "aide à l'insertion des jeunes",
        "mouvements éducatifs de jeunesse et d'éducation populaire", "parents d'élèves",
        "associations périscolaires, coopération, aide à l'enseignement",
    ],
    'Loisirs & vie locale': [
        'clubs de loisirs, relations', 'centres de loisirs, clubs de loisirs multiples', 'comités des fêtes',
        "comités de défense et d'animation de quartier, association locale ou municipale",
        'clubs, cercles de réflexion', 'action socio-culturelle',
    ],
    'Citoyenneté & droits': [
        'défense de droits fondamentaux, activités civiques', 'activités civiques, information civique', 'activités politiques',
    ],
    'Santé': ['santé', 'éducation sanitaire, prévention générale', 'organisation de professions médicales ou paramédicales'],
    'Religion & spiritualité': ['activités religieuses, spirituelles ou philosophiques'],
}
CAT_TO_DOMAINE = {c: dom for dom, cats in DOMAINES.items() for c in cats}


def norm_phone(p):
    m = PHONE_RE.search(p or '')
    if not m:
        return None
    digits = re.sub(r'\D', '', m.group(1))
    if len(digits) != 8 or digits in GENERIC_PHONES:
        return None
    return ' '.join(digits[i:i + 2] for i in range(0, 8, 2))


def norm_url(u):
    u = re.sub(r'\s*\(.*?\)\s*', ' ', (u or '')).strip().split(' ')[0]
    u = re.sub(r'^https?://', '', u, flags=re.I)
    u = re.sub(r'^(www\.|m\.|web\.|fr-fr\.|fr\.)', '', u, flags=re.I)
    u = u.split('?')[0].split('#')[0].rstrip('/')
    if not u or '.' not in u or u.lower() in ('facebook.com', 'instagram.com'):
        return None
    if re.match(r'(?i)linkedin\.com/in/', u):  # profil LinkedIn d'une personne : donnée personnelle, écartée
        return None
    return u


def clean_rep(rep):
    """Garde « Prénom NOM (président) » ; écarte les dirigeants dont le nom ne vient que d'une adresse « chez … »."""
    rep = (rep or '').strip()
    if not rep or re.search(r'(?i)as written|seat address|adresse', rep):
        return ''
    m = re.match(r'^(.*?)\s*\(([^)]*)\)', rep)
    if m:
        role = 'présidente' if re.search(r'(?i)pr[ée]sidente', m.group(2)) else 'président' if re.search(r'(?i)pr[ée]sident', m.group(2)) else ''
        return f'{m.group(1).strip()} ({role})' if role else m.group(1).strip()
    return rep


def clean_enseigne(e):
    return re.sub(r'\s*\(.*?\)', '', (e or '')).strip()


def norm_mail(m):
    m = (m or '').strip().strip('<>').lower()
    return m if re.fullmatch(r'[^@\s]+@[^@\s]+\.[a-z]{2,}', m) else None


def parse_contact(raw):
    """Découpe une chaîne de contact existante en (téléphones, mails, urls, autres segments)."""
    phones, mails, urls, other = [], [], [], []
    for part in [p.strip() for p in (raw or '').split(' · ') if p.strip()]:
        if part.startswith('☎'):
            for seg in part[1:].split('/'):
                n = norm_phone(seg)
                if n:
                    phones.append(n)
        elif part.startswith('✉'):
            mails.append(part[1:].strip())
        elif part.startswith('🌐'):
            urls.append(re.sub(r'\s*\(.*?\)', '', part[1:]).strip())
        else:
            other.append(part)
    return phones, mails, urls, other


def build_contact(phones, mails, urls, other=()):
    def uniq(seq, key=lambda x: x.lower()):
        seen, out = set(), []
        for x in seq:
            if x and key(x) not in seen:
                seen.add(key(x))
                out.append(x)
        return out
    parts = []
    phones = uniq(phones, key=lambda x: x)
    if phones:
        parts.append('☎ ' + ' / '.join(phones))
    parts += ['✉ ' + m for m in uniq(mails)]
    parts += ['🌐 ' + u for u in uniq(urls)]
    parts += list(other)
    return ' · '.join(parts)


def sanitize_address(a):
    """Retire de l'adresse de siège les noms de particuliers (« chez M. X », « c/o … », « au domicile de … »)."""
    a = re.sub(r'\s+', ' ', (a or '').strip())
    a = re.sub(r'(?i)\s*\([^)]*\b(?:domicile|chez|c/o)\b[^)]*\)', '', a)
    a = re.sub(r'(?i)\b(?:chez|c/o)\b.*?\s(?=pk\b)', '', a)
    a = re.sub(r"(?i)\b(?:au\s+)?domicile\s+d(?:e|u|e\s+la|e\s+l')?\s*[^,]*?(?=\s*(?:,|\bpk\b|$))", '', a)
    a = re.sub(r'(?i)[\s,\-–]*\b(?:chez|c/o)\b[^,]*', '', a)
    a = re.sub(r'^[\s,.\-–]+|[\s,\-–]+$', '', a)
    a = re.sub(r'(?i)\bpk\b', 'PK', a)
    a = a.rstrip('.').strip()
    if a and 'paea' not in a.lower():
        a += ', Paea'
    return a


def clean_name(name):
    """Normalise les guillemets parasites de certains intitulés RNA : « " TRIO 219 " » -> « TRIO 219 »."""
    n = re.sub(r'\s+', ' ', (name or '').strip())
    m = re.fullmatch(r'["“”«»]\s*(.+?)\s*["“”«»]', n)
    if m and not re.search(r'["“”«»]', m.group(1)):
        n = m.group(1)
    n = re.sub(r'"\s*([^"]+?)\s*"', r'« \1 »', n)
    return n.strip() or (name or '').strip()


def clean_objet(desc):
    d = re.sub(r'[\s\-–_;.,]+$', '', (desc or '').strip())
    d = re.sub(r'\s+', ' ', d)
    d = re.sub(r"(\w)' (\w)", r"\1'\2", d)
    if not d or d.lower() in ('a saisir', 'à saisir'):
        return ''
    d = d[0].upper() + d[1:]
    return d if len(d) <= 240 else d[:237].rsplit(' ', 1)[0] + '…'


DOMAINE_KEYWORDS = [
    ('Sport', ('sport', 'football', 'futsal', "va'a", 'vaa', 'pirogue', 'boxe', 'boxing', 'taekwondo', 'judo', 'karat', 'surf',
               'rugby', 'basket', 'volley', 'handball', 'athl', 'pétanque', 'petanque', 'cycl', 'aïkido', 'aikido', 'tir ')),
    ('Culture & arts', ('cultur', 'danse', 'heiva', 'arts', 'artist', 'musique', 'chant', 'himene', 'orero', 'langue', 'artisan')),
    ('Religion & spiritualité', ('paroisse', 'église', 'eglise', 'religi', 'spirituel', 'culte')),
    ('Éducation & jeunesse', ('école', 'ecole', 'élèves', 'eleves', 'scolaire', 'collège', 'college', 'jeunes', 'jeunesse', 'éducati', 'educati')),
    ('Famille & solidarité', ('famil', 'solidar', 'entraide', 'social', 'caritati', 'âgées', 'agees', 'handicap')),
    ('Santé', ('santé', 'sante', 'médic', 'medic', 'prévention', 'prevention')),
    ('Environnement & cadre de vie', ('environnement', 'nature', 'rivière', 'riviere', 'lagon', 'déchets', 'dechets')),
    ('Agriculture & pêche', ('agric', 'pêche', 'peche', 'élevage', 'elevage', 'horticult', 'faapu')),
    ('Économie & emploi', ('économ', 'econom', 'emploi', 'commer', 'entrepr', 'professionn')),
    ('Patrimoine & foncier', ('patrimoine', 'foncier', 'terres', 'généalog', 'genealog')),
    ('Loisirs & vie locale', ('quartier', 'comité', 'comite', 'loisir', 'fêtes', 'fetes', 'amicale')),
    ('Citoyenneté & droits', ('droit', 'citoyen', 'civique', 'consommateur')),
]


def guess_domaine(*texts):
    blob = ' '.join(t or '' for t in texts).lower()
    for dom, words in DOMAINE_KEYWORDS:
        if dom.lower() in blob or any(w in blob for w in words):
            return dom
    return 'Autres domaines'


def load_journal(path):
    """Retourne {label: résultat} pour chaque agent terminé du workflow."""
    labels, results = {}, {}
    for line in open(path, encoding='utf-8'):
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get('type') == 'started':
            labels[o.get('key')] = o.get('label')
        elif o.get('type') == 'result':
            lab = o.get('label') or labels.get(o.get('key'))
            res = o.get('result', o.get('value'))
            if isinstance(res, str):
                try:
                    res = json.loads(res)
                except json.JSONDecodeError:
                    pass
            if lab:
                results[lab] = res
    return results


def main(journal_path, assoc_path=RNA_FILE):
    data = json.load(open(DATA_FILE, encoding='utf-8'))
    journal = load_journal(journal_path)
    provenance = {'contacts': [], 'associations': [], 'associations_hors_rna': []}

    # Normalisation : « SERVICES » est une variante orthographique du collège « SERVICE »
    for item in data:
        if item.get('cat') == 'SERVICES':
            item['cat'] = 'SERVICE'

    # ---------- 1. Contacts des sociétés / patentés ----------
    verdicts = defaultdict(list)
    for lab, res in journal.items():
        if lab.startswith(('verif-contacts:', 'verif-deep-soc:')) and isinstance(res, dict):
            for v in res.get('verdicts', []):
                if v.get('verdict') in ('confirmed', 'partial'):
                    verdicts[v['idx']].append(v)

    stats = Counter()
    for idx, vs in sorted(verdicts.items()):
        if not (0 <= idx < len(data)):
            continue
        item = data[idx]
        cur = (item.get('contact') or '').strip()
        if cur.startswith('⚠️'):
            continue
        phones, mails, urls, other = parse_contact(cur)
        new_p = [p for v in vs for p in map(norm_phone, v.get('phones') or []) if p]
        new_m = [m for v in vs for m in map(norm_mail, v.get('emails') or []) if m]
        new_u = [u for v in vs for u in map(norm_url, v.get('urls') or []) if u]
        alert = next((v['status_alert'].strip() for v in vs
                      if (v.get('status_alert') or '').strip() and any(w in v['status_alert'].lower() for w in ALERT_WORDS)), '')
        enseigne = next((clean_enseigne(v['enseigne']) for v in vs if clean_enseigne(v.get('enseigne'))), '')
        if not (new_p or new_m or new_u or alert or enseigne):
            continue
        before = cur
        if alert:
            item['contact'] = '⚠️ ' + alert
            stats['alertes'] += 1
        else:
            item['contact'] = build_contact(phones + new_p, mails + new_m, urls + new_u, other)
        if enseigne and enseigne.upper() != item['name'].upper():
            item['enseigne'] = enseigne
        stats['entités enrichies'] += item['contact'] != before or bool(enseigne)
        stats['avec nouveau téléphone'] += bool(new_p) and not alert
        provenance['contacts'].append({
            'idx': idx, 'name': item['name'], 'form': item['form'], 'avant': before, 'apres': item['contact'],
            'enseigne': item.get('enseigne', ''),
            'verifications': [{k: v.get(k) for k in ('verdict', 'phones', 'emails', 'urls', 'status_alert', 'sources', 'reason')} for v in vs],
        })

    # ---------- 2. Associations (RNA, siège à Paea) ----------
    assocs = json.load(open(assoc_path, encoding='utf-8'))['associations']
    a_verdicts = {}
    for lab, res in journal.items():
        if lab.startswith('verif-assoc:') and isinstance(res, dict):
            for v in res.get('verdicts', []):
                if v.get('verdict') in ('confirmed', 'partial'):
                    a_verdicts[v['aid']] = v

    existing_rna = {i for d in data for i in d.get('ids', []) if i.startswith('RNA ')}
    domaines = Counter()
    for a in assocs:
        rid = 'RNA ' + a['rna']
        if rid in existing_rna:
            continue
        v = a_verdicts.get(a['aid'], {})
        if v.get('rna') and v['rna'] != a['rna']:
            v = {}
        dom = CAT_TO_DOMAINE.get(a['categorie_rna'], 'Autres domaines')
        domaines[dom] += 1
        # Adresse de siège : celle du RNA en priorité, sinon celle confirmée par le vérificateur
        address = sanitize_address(a.get('adresse_rna')) or sanitize_address(v.get('address'))
        inactive = (v.get('inactive_evidence') or '').strip()
        contact = build_contact(
            [p for p in map(norm_phone, v.get('phones') or []) if p],
            [m for m in map(norm_mail, v.get('emails') or []) if m],
            [u for u in map(norm_url, v.get('urls') or []) if u],
        )
        if inactive and any(w in inactive.lower() for w in ALERT_WORDS):
            contact = '⚠️ ' + inactive
        data.append({
            'name': clean_name(a['name']),
            'form': 'Association',
            'cat': 'ASSOCIATION',
            'rep': clean_rep(v.get('rep')),
            'naf': clean_objet(a.get('objet')),
            'domaine': dom,
            'ids': [rid],
            'address': address or 'Paea (98711)',
            'contact': contact,
            'created': a.get('date', ''),
        })
        stats['associations ajoutées'] += 1
        stats['associations avec adresse'] += bool(address)
        stats['associations avec contact'] += bool(contact) and not contact.startswith('⚠️')
        if v:
            provenance['associations'].append({'rna': a['rna'], 'name': a['name'], **{k: v.get(k) for k in ('verdict', 'address', 'rep', 'phones', 'emails', 'urls', 'inactive_evidence', 'sources', 'reason')}})

    # ---------- 3. Associations repérées hors liste RNA (vérifiées) ----------
    known_names = {re.sub(r'\W', '', d['name'].upper()) for d in data if d.get('form') == 'Association'}
    for lab, res in journal.items():
        if not lab.startswith('verif-completude:') or not isinstance(res, dict):
            continue
        for c in res.get('candidates', []):
            key = re.sub(r'\W', '', (c.get('name') or '').upper())
            rna = (c.get('rna') or '').strip().upper()
            if not key or key in known_names or (rna and 'RNA ' + rna in existing_rna):
                continue
            known_names.add(key)
            address = sanitize_address(c.get('address'))
            dom = (c.get('domaine') or '').strip()
            dom = dom if dom in DOMAINES else guess_domaine(dom, c.get('objet'), c.get('name'))
            domaines[dom] += 1
            data.append({
                'name': clean_name(c['name']).upper(),
                'form': 'Association',
                'cat': 'ASSOCIATION',
                'rep': clean_rep(c.get('rep')),
                'naf': clean_objet(c.get('objet')),
                'domaine': dom,
                'ids': ['RNA ' + rna] if re.fullmatch(r'W9P\d{7}', rna) else ['Association déclarée'],
                'address': address or 'Paea (98711)',
                'contact': build_contact(
                    [p for p in map(norm_phone, c.get('phones') or []) if p],
                    [m for m in map(norm_mail, c.get('emails') or []) if m],
                    [u for u in map(norm_url, c.get('urls') or []) if u],
                ),
                'created': '',
            })
            stats['associations hors liste RNA ajoutées'] += 1
            provenance['associations_hors_rna'].append(c)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(SOURCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(provenance, f, ensure_ascii=False, indent=2)

    print(f'{DATA_FILE} mis à jour : {len(data)} entités')
    for k, n in stats.items():
        print(f'- {k} : {n}')
    print('- domaines associatifs :', dict(domaines.most_common()))
    print(f'Provenance détaillée : {SOURCES_FILE}')


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
