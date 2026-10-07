import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Charger les données enrichies
with open('data_enriched.json', 'r', encoding='utf-8') as f:
    enriched_data = json.load(f)

total_entries = len(enriched_data)
total_entries_fr = f'{total_entries:,}'.replace(',', ' ')
with_contact = sum(1 for d in enriched_data if d.get('contact') and d['contact'].strip())
without_contact = total_entries - with_contact

print(f"Données chargées : {total_entries} entrées")
print(f"Avec contact direct : {with_contact}")
print(f"Sans contact (vide) : {without_contact}")

# 2. Charger le template HTML original
with open('paea-entreprises.html.bak', 'r', encoding='utf-8') as f:
    html = f.read()

# 3. CSS additionnel pour les contacts et badges réseaux sociaux
additional_css = """
  .contact-cell{display:flex;flex-direction:column;gap:5px;font-size:12.5px;line-height:1.4}
  .contact-badge{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;width:fit-content;letter-spacing:.2px}
  .contact-badge.direct{background:#dcfce7;color:#166534;border:1px solid #bbf7d0}
  .contact-badge.alert{background:#fee2e2;color:#991b1b;border:1px solid #fecaca}
  .contact-desc{color:#334155;font-size:12px;margin-top:2px;display:flex;flex-wrap:wrap;gap:5px;align-items:center}
  .contact-link{display:inline-flex;align-items:center;gap:4px;text-decoration:none;font-weight:600;font-size:12px;padding:3px 8px;border-radius:6px;transition:.15s;white-space:nowrap}
  .contact-link.tel{color:#0369a1;background:#f0f9ff;border:1px solid #bae6fd}
  .contact-link.tel:hover{background:#e0f2fe;color:#0284c7}
  .contact-link.mail{color:#6d28d9;background:#f5f3ff;border:1px solid #ddd6fe}
  .contact-link.mail:hover{background:#ede9fe;color:#7c3aed}
  .contact-link.web{color:#047857;background:#ecfdf5;border:1px solid #a7f3d0}
  .contact-link.web:hover{background:#d1fae5;color:#059669}
  .contact-link.fb{color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe}
  .contact-link.fb:hover{background:#dbeafe;color:#1e40af}
  .contact-link.insta{color:#be185d;background:#fdf2f8;border:1px solid #fbcfe8}
  .contact-link.insta:hover{background:#fce7f3;color:#9d174d}
  .contact-link.linkedin{color:#0369a1;background:#f0f9ff;border:1px solid #bae6fd}
  .contact-link.linkedin:hover{background:#e0f2fe;color:#075985}
"""

html = html.replace('</style>', additional_css + '\n</style>')

# 4. Mettre à jour la carte KPI 4 (Avec contact direct)
old_stat_c4 = """    <div class="stat c4">
      <div class="label">Avec contact renseigné</div>
      <div class="val" id="statContact">—</div>
      <div class="hint">tél. / e-mail / site</div>
    </div>"""

new_stat_c4 = f"""    <div class="stat c4">
      <div class="label">Avec contact direct</div>
      <div class="val" id="statContact">{with_contact}</div>
      <div class="hint" id="statContactHint">tél. · e-mail · site · réseaux</div>
    </div>"""

html = html.replace(old_stat_c4, new_stat_c4)

# 5. Mettre à jour le sélecteur filterContact et ajouter filterQuartier
old_filter_contact = """    <select id="filterContact">
      <option value="">Tous</option>
      <option value="with">Avec contact</option>
      <option value="without">Sans contact</option>
    </select>"""

new_filter_contact = f"""    <select id="filterContact">
      <option value="">Tous les contacts ({total_entries_fr})</option>
      <option value="with">⭐ Avec contact direct ({with_contact})</option>
      <option value="without">Sans contact ({without_contact})</option>
      <option value="tel">📞 Avec ligne téléphonique</option>
      <option value="web_mail">🌐 Avec e-mail, site ou réseaux</option>
    </select>
    <select id="filterQuartier">
      <option value="">Tous les quartiers</option>
      <option value="Maraa">Maraa</option>
      <option value="Orofero">Orofero</option>
      <option value="Papehue">Papehue</option>
      <option value="Tiapa">Tiapa</option>
      <option value="Vaiterupe">Vaiterupe</option>
      <option value="Vaiatu">Vaiatu</option>
      <option value="Aoua">Aoua</option>
      <option value="Tefana / Vaitupa">Tefana &amp; Vaitupa</option>
      <option value="AUTRE">Autres / non précisé</option>
    </select>"""

html = html.replace(old_filter_contact, new_filter_contact)

# 6. Remplacement des données DATA
data_json_str = json.dumps(enriched_data, ensure_ascii=False, separators=(',', ':'))
data_regex = r'const DATA = \[.*?\];'
html = re.sub(data_regex, lambda m: f'const DATA = {data_json_str};', html, count=1, flags=re.DOTALL)

# 7. Nouveau code Javascript sécurisé sans guichets de référence
new_js_logic = """const $ = id => document.getElementById(id);
const tbody = $('tbody'), empty = $('empty');
let filtered = [...DATA];
let sortKey = 'name', sortDir = 1;

const FORM_CLASS = {SARL:'sarl',SAS:'sas',SASU:'sas',SNC:'snc',EURL:'eurl',SELARL:'selarl',SCP:'scp',COOP:'coop',PPHY:'pphy',Institution:'contact-inst'};

function norm(s){return (s||'').toString().toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}
function escapeHtml(s){if(s==null) return '';return s.toString().replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function formTag(form){const cls = FORM_CLASS[form]||'sarl';return `<span class="tag ${cls}">${escapeHtml(form)}</span>`;}
function hasContact(item){return item.contact && item.contact.trim().length>0;}

function hasPhone(item){
  return /\\b(?:40|87|88|89)\\s*\\d{2}\\s*\\d{2}\\s*\\d{2}\\b|\\b89\\s*89\\b/.test(item.contact||'');
}

function hasWebOrMail(item){
  return /@|www\\.|\\.pf|\\.com|\\.fr|facebook\\.com|instagram\\.com|linkedin\\.com/.test(item.contact||'');
}

const QUARTIER_KEYWORDS = {
  'Maraa':['maraa'],
  'Orofero':['orofero'],
  'Papehue':['papehu'],
  'Tiapa':['tiapa'],
  'Vaiterupe':['vaiterupe'],
  'Vaiatu':['vaiatu'],
  'Aoua':['aoua'],
  'Tefana / Vaitupa':['tefana','vaitupa']
};
function hasQuartier(item,key){
  const a = norm(item.address||'');
  if(key==='AUTRE'){
    return !Object.keys(QUARTIER_KEYWORDS).some(k=>hasQuartier(item,k));
  }
  const kws = QUARTIER_KEYWORDS[key]||[];
  return kws.some(k=>a.includes(k));
}

// RENDU SÉCURISÉ DES CONTACTS SANS AUCUNE FUITE HTML
function renderContact(r){
  const c = (r.contact || '').trim();
  if(!c) return '—';

  if(c.startsWith('⚠️')){
    return `<div class="contact-cell"><span class="contact-badge alert">⚠️ Statut</span><span class="contact-desc">${escapeHtml(c.replace('⚠️','').trim())}</span></div>`;
  }

  // Tokenisation isolée pour empêcher les regex croisées et les fuites HTML
  const tokens = {};
  let tokId = 0;
  const addTok = html => {
    const k = `___TOK_${tokId++}___`;
    tokens[k] = html;
    return k;
  };

  let text = c;

  // 1. Extraire les emails
  text = text.replace(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})/g, (m, em) => {
    return addTok(`<a href="mailto:${escapeHtml(em)}" class="contact-link mail" title="Envoyer un e-mail">✉ ${escapeHtml(em)}</a>`);
  });

  // 2. Extraire les sites web et réseaux sociaux
  text = text.replace(/(?:🌐\\s*)?((?:https?:\\/\\/)?(?:[a-zA-Z0-9-]+\\.)+(?:com|pf|fr|org|net)(?:\\/[^\\s·<]*)?)/g, (m, url) => {
    const href = url.startsWith('http') ? url : 'https://' + url;
    const clean = url.replace(/^https?:\\/\\//, '');
    const low = url.toLowerCase();
    let cls = 'contact-link web', label = `🌐 ${clean}`, title = 'Site web';
    if(low.includes('facebook.com')) {
      cls = 'contact-link fb';
      label = `📘 ${clean.replace(/^(?:www\\.)?facebook\\.com\\/?/, 'fb/')}`;
      title = 'Page Facebook';
    } else if(low.includes('instagram.com')) {
      cls = 'contact-link insta';
      label = `📷 ${clean.replace(/^(?:www\\.)?instagram\\.com\\/?/, 'ig/')}`;
      title = 'Page Instagram';
    } else if(low.includes('linkedin.com')) {
      cls = 'contact-link linkedin';
      label = `💼 ${clean.replace(/^(?:www\\.)?linkedin\\.com\\/in\\/?/, 'in/')}`;
      title = 'Profil LinkedIn';
    }
    return addTok(`<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer" class="${cls}" title="${title}">${escapeHtml(label)}</a>`);
  });

  // 3. Extraire les téléphones
  text = text.replace(/(?:☎\\s*)?(\\b(?:40|87|88|89)\\s*\\d{2}\\s*\\d{2}\\s*\\d{2}\\b|\\b89\\s*89\\b)/g, (m, num) => {
    const clean = num.replace(/\\s+/g, '');
    const telHref = clean.length === 8 ? `+689${clean}` : clean;
    return addTok(`<a href="tel:${telHref}" class="contact-link tel" title="Appeler">☎ ${escapeHtml(num)}</a>`);
  });

  // 4. Échapper tout le reste du texte
  text = escapeHtml(text);

  // Nettoyer les emojis orphelins
  text = text.replace(/✉\\s*___TOK_/g, '___TOK_');
  text = text.replace(/🌐\\s*___TOK_/g, '___TOK_');
  text = text.replace(/☎\\s*___TOK_/g, '___TOK_');

  // 5. Réinsérer les tokens HTML propres
  for(const k in tokens){
    text = text.replace(k, tokens[k]);
  }

  return `<div class="contact-cell"><span class="contact-badge direct">⭐ Contact direct</span><div class="contact-desc">${text}</div></div>`;
}

function render(){
  const rows = filtered;
  $('resultCount').textContent = rows.length;
  if(rows.length===0){tbody.innerHTML='';empty.style.display='block';return;}
  empty.style.display='none';
  tbody.innerHTML = rows.map(r=>`
    <tr>
      <td class="name">${escapeHtml(r.name)}</td>
      <td>${formTag(r.form)}</td>
      <td>${escapeHtml(r.cat)}</td>
      <td>${escapeHtml(r.rep||'—')}</td>
      <td>${r.naf?`<span class="naf-pill">${escapeHtml(r.naf)}</span>`:'—'}</td>
      <td><div class="ids">${(r.ids||[]).map(id=>`<span class="id-pill">${escapeHtml(id)}</span>`).join('')}</div></td>
      <td>${escapeHtml(r.address||'—')}</td>
      <td>${renderContact(r)}</td>
    </tr>`).join('');
}

function applyFilters(){
  const q = norm($('search').value);
  const cat = $('filterCat').value, form = $('filterForm').value, contact = $('filterContact').value;
  const quartier = $('filterQuartier') ? $('filterQuartier').value : '';
  filtered = DATA.filter(item=>{
    if(cat && item.cat !== cat) return false;
    if(form){
      if(form==='SAS' && !['SAS','SASU'].includes(item.form)) return false;
      if(form!=='SAS' && item.form !== form) return false;
    }
    if(contact==='with' && !hasContact(item)) return false;
    if(contact==='without' && hasContact(item)) return false;
    if(contact==='tel' && !hasPhone(item)) return false;
    if(contact==='web_mail' && !hasWebOrMail(item)) return false;
    if(quartier && !hasQuartier(item, quartier)) return false;
    if(q){
      const blob = norm([item.name,item.rep,item.address,item.naf,(item.ids||[]).join(' '),item.contact].join(' '));
      if(!blob.includes(q)) return false;
    }
    return true;
  });
  sortData(); render(); updateStats();
}

function sortData(){
  filtered.sort((a,b)=>{
    let va,vb;
    if(sortKey==='ids'){va=(a.ids||[]).join(' ');vb=(b.ids||[]).join(' ');}
    else {va=a[sortKey]||'';vb=b[sortKey]||'';}
    va=norm(va);vb=norm(vb);
    if(va<vb) return -1*sortDir;
    if(va>vb) return 1*sortDir;
    return 0;
  });
}

function updateStats(){
  const total = DATA.length;
  const societes = DATA.filter(d=>d.form!=='PPHY'&&d.form!=='Institution').length;
  const pphy = DATA.filter(d=>d.form==='PPHY').length;
  const withContact = DATA.filter(hasContact).length;
  $('statTotal').textContent = total.toLocaleString('fr-FR');
  $('statSocietes').textContent = societes.toLocaleString('fr-FR');
  $('statPphy').textContent = pphy.toLocaleString('fr-FR');
  $('statContact').textContent = withContact.toLocaleString('fr-FR');
  if($('statContactHint')) $('statContactHint').textContent = `${Math.round((withContact/total)*100)} % des entreprises · vérifiés`;
  $('cntAll').textContent = DATA.length;
  $('cntCOMMERCE').textContent = DATA.filter(d=>d.cat==='COMMERCE').length;
  $('cntINDUSTRIE').textContent = DATA.filter(d=>d.cat==='INDUSTRIE').length;
  $('cntMETIER').textContent = DATA.filter(d=>d.cat==='MÉTIER').length;
  $('cntSERVICE').textContent = DATA.filter(d=>d.cat==='SERVICE').length;
  $('cntINSTITUTION').textContent = DATA.filter(d=>d.cat==='INSTITUTION').length;
}

$('search').addEventListener('input', applyFilters);
$('filterCat').addEventListener('change', ()=>{
  const v = $('filterCat').value;
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active', t.dataset.cat===v));
  applyFilters();
});
$('filterForm').addEventListener('change', applyFilters);
$('filterContact').addEventListener('change', applyFilters);
$('filterQuartier').addEventListener('change', applyFilters);
document.querySelectorAll('.tab').forEach(tab=>{
  tab.addEventListener('click', ()=>{
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
    tab.classList.add('active');
    $('filterCat').value = tab.dataset.cat;
    applyFilters();
  });
});
document.querySelectorAll('thead th').forEach(th=>{
  th.addEventListener('click', ()=>{
    const key = th.dataset.key;
    if(sortKey===key){sortDir*=-1;} else {sortKey=key;sortDir=1;}
    document.querySelectorAll('thead th').forEach(t=>t.classList.remove('sorted'));
    th.classList.add('sorted');sortData();render();
  });
});
$('resetBtn').addEventListener('click', ()=>{
  $('search').value='';$('filterCat').value='';$('filterForm').value='';$('filterContact').value='';$('filterQuartier').value='';
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active', t.dataset.cat===''));
  sortKey='name';sortDir=1;applyFilters();
});
$('exportCsv').addEventListener('click', ()=>{
  const sep = ';';
  const headers = ['Dénomination / Nom','Forme','Catégorie','Dirigeant / Mandataire','NAF / Activité','Identifiants','Adresse','Contact'];
  const lines = [headers.join(sep)];
  filtered.forEach(r=>{
    const row = [r.name,r.form,r.cat,r.rep||'',r.naf||'',(r.ids||[]).join(' | '),r.address||'',r.contact||'']
      .map(v=>`"${(v||'').toString().replace(/"/g,'""')}"`);
    lines.push(row.join(sep));
  });
  const csv = '\\uFEFF'+lines.join('\\n');
  const blob = new Blob([csv],{type:'text/csv;charset=utf-8;'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');a.href=url;
  a.download=`paea_entreprises_${new Date().toISOString().slice(0,10)}.csv`;
  a.click();URL.revokeObjectURL(url);
});
document.querySelector('thead th[data-key="name"]').classList.add('sorted');
applyFilters();
"""

# Remplacer le code JS original après const DATA = [...]
js_pattern = r'const \$ = id => document\.getElementById\(id\);.*?</script>'
html = re.sub(js_pattern, lambda m: new_js_logic + '\n</script>', html, flags=re.DOTALL)

# 8. Sauvegarder dans paea-entreprises.html
with open('paea-entreprises.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("paea-entreprises.html reconstruit avec succès !")
print(f"Taille finale : {len(html):,} octets")
