import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Charger les données enrichies
with open('data_enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total_entries = len(data)
with_contact = sum(1 for d in data if d.get('contact') and d['contact'].strip() and not d['contact'].strip().startswith('⚠️'))
alert_status = sum(1 for d in data if d.get('contact') and d['contact'].strip().startswith('⚠️'))
societes_count = sum(1 for d in data if d.get('form') not in ('PPHY', 'Institution'))
pphy_count = sum(1 for d in data if d.get('form') == 'PPHY')
for idx, d in enumerate(data):
    d['idx'] = idx

data_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

print(f"Compilation de paea-entreprises.html avec {total_entries} entités...")
print(f"- Sociétés : {societes_count}")
print(f"- Patentés (PPHY) : {pphy_count}")
print(f"- Contacts directs vérifiés : {with_contact}")
print(f"- Statuts légaux spécifiques : {alert_status}")

html_content = f'''<!DOCTYPE html>
<html lang="fr" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Observatoire Économique de Paea – Répertoire consolidé des Entreprises &amp; Patentés</title>
<meta name="description" content="Annuaire officiel et observatoire économique consolidé des entreprises et patentés de la commune de Paea (Tahiti, Polynésie française). Mission PIAC 2026.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">

<style>
/* ==========================================================================
   DESIGN SYSTEM "POLYNÉSIE MODERNE" - TOKENS & THÈMES
   ========================================================================== */
:root {{
  --font-title: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  /* Thème Clair "Lagon & Nacre" */
  --bg-app: #f8fafc;
  --bg-card: rgba(255, 255, 255, 0.88);
  --bg-card-solid: #ffffff;
  --bg-hover: #f1f5f9;
  --border: #e2e8f0;
  --border-subtle: #cbd5e1;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --text-dim: #94a3b8;

  --lagoon-900: #082f49;
  --lagoon-700: #0369a1;
  --lagoon-600: #0284c7;
  --lagoon-500: #0ea5e9;
  --lagoon-100: #e0f2fe;
  --lagoon-50: #f0f9ff;

  --emerald-700: #047857;
  --emerald-600: #059669;
  --emerald-500: #10b981;
  --emerald-100: #d1fae5;
  --emerald-50: #ecfdf5;

  --amber-600: #d97706;
  --amber-500: #f59e0b;
  --amber-100: #fef3c7;
  --amber-50: #fffbeb;

  --coral-600: #e11d48;
  --coral-100: #ffe4e6;

  --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.05);
  --shadow-md: 0 4px 20px -2px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 12px 32px -4px rgba(15, 23, 42, 0.12);
  --glass-blur: blur(16px);
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-full: 9999px;
  --transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}}

[data-theme="dark"] {{
  --bg-app: #080d1a;
  --bg-card: rgba(15, 23, 42, 0.78);
  --bg-card-solid: #0f172a;
  --bg-hover: #1e293b;
  --border: #1e293b;
  --border-subtle: #334155;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --text-dim: #64748b;

  --lagoon-900: #e0f2fe;
  --lagoon-700: #38bdf8;
  --lagoon-600: #0ea5e9;
  --lagoon-100: #082f49;
  --lagoon-50: #0c1e36;

  --emerald-700: #34d399;
  --emerald-600: #10b981;
  --emerald-100: #064e3b;
  --emerald-50: #062e24;

  --amber-600: #fbbf24;
  --amber-100: #451a03;
  --amber-50: #291503;

  --coral-600: #fb7185;
  --coral-100: #4c0519;

  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 12px 32px -4px rgba(0, 0, 0, 0.6);
}}

/* ==========================================================================
   RESET & BASE
   ========================================================================== */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ font-size: 15px; scroll-behavior: smooth; -webkit-tap-highlight-color: transparent; }}
body {{
  font-family: var(--font-body);
  background-color: var(--bg-app);
  color: var(--text-main);
  min-height: 100vh;
  line-height: 1.5;
  transition: background-color 0.3s ease, color 0.3s ease;
  overflow-x: hidden;
  padding-bottom: 80px; /* Espace pour la bottom bar mobile */
}}

/* ==========================================================================
   HEADER HERO IMMERSIF
   ========================================================================== */
.hero {{
  position: relative;
  background: linear-gradient(135deg, #063156 0%, #0c4a6e 50%, #047857 100%);
  color: #ffffff;
  padding: 20px 20px 38px;
  overflow: hidden;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}}
.hero::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 80% 20%, rgba(56, 189, 248, 0.25) 0%, transparent 60%),
              radial-gradient(circle at 10% 90%, rgba(16, 185, 129, 0.2) 0%, transparent 50%);
  pointer-events: none;
}}
.hero-content {{
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}}
.hero-top {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}}
.hero-badge {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(12px);
  padding: 5px 12px;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}}
.pulse-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #34d399;
  box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7);
  animation: pulse 2s infinite;
}}
@keyframes pulse {{
  0% {{ box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }}
  70% {{ box-shadow: 0 0 0 8px rgba(52, 211, 153, 0); }}
  100% {{ box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }}
}}
.hero-controls {{
  display: flex;
  align-items: center;
  gap: 10px;
}}
.icon-btn {{
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
}}
.icon-btn:hover {{
  background: rgba(255, 255, 255, 0.22);
  transform: translateY(-2px);
}}
.hero h1 {{
  font-family: var(--font-title);
  font-size: clamp(1.4rem, 2.5vw, 1.95rem);
  font-weight: 800;
  line-height: 1.2;
  margin: 4px 0 0;
  letter-spacing: -0.4px;
}}

/* ==========================================================================
   CONTAINER PRINCIPAL
   ========================================================================== */
.main-wrapper {{
  max-width: 1400px;
  margin: -22px auto 0;
  padding: 0 20px;
  position: relative;
  z-index: 10;
}}

/* ==========================================================================
   RUBAN STATISTIQUES COMPACT (INTERACTIF)
   ========================================================================== */
.stats-strip {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}}
@media (max-width: 960px) {{
  .stats-strip {{ grid-template-columns: repeat(2, 1fr); gap: 8px; }}
}}
@media (max-width: 480px) {{
  .stats-strip {{ grid-template-columns: 1fr; gap: 6px; }}
}}
.stat-pill {{
  background: var(--bg-card);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
  outline: none;
  font-family: inherit;
  width: 100%;
}}
.stat-pill:hover {{
  border-color: var(--lagoon-500);
  background: var(--bg-card-solid);
  transform: translateY(-1px);
}}
.stat-pill.active {{
  border-color: var(--lagoon-600);
  background: var(--bg-card-solid);
  box-shadow: 0 0 0 2px var(--lagoon-500);
}}
.stat-icon {{
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: var(--lagoon-50);
  color: var(--lagoon-700);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}}
.stat-meta {{
  display: flex;
  flex-direction: column;
  min-width: 0;
}}
.stat-num {{
  font-family: var(--font-title);
  font-size: 1.15rem;
  font-weight: 800;
  line-height: 1.1;
  color: var(--text-main);
}}
.stat-txt {{
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}

/* ==========================================================================
   TOOLBAR, RECHERCHE & RUBAN PK (STICKY SANS PERTE DE REPÈRE)
   ========================================================================== */
.control-panel {{
  background: var(--bg-card);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  box-shadow: var(--shadow-md);
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: sticky;
  top: 10px;
  z-index: 40;
}}
.search-row {{
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}}
.search-box {{
  flex: 1;
  min-width: 280px;
  position: relative;
}}
.search-box svg {{
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}}
.search-input {{
  width: 100%;
  height: 46px;
  padding: 0 44px 0 42px;
  background: var(--bg-card-solid);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-main);
  font-family: var(--font-body);
  font-size: 0.95rem;
  outline: none;
  transition: var(--transition);
}}
.search-input:focus {{
  border-color: var(--lagoon-600);
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
}}
.kbd-hint {{
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 7px;
  border-radius: 6px;
  background: var(--bg-hover);
  color: var(--text-muted);
  border: 1px solid var(--border);
  pointer-events: none;
}}
.view-switch {{
  display: flex;
  background: var(--bg-hover);
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}}
.view-btn {{
  border: none;
  background: transparent;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: var(--transition);
}}
.view-btn.active {{
  background: var(--bg-card-solid);
  color: var(--text-main);
  box-shadow: var(--shadow-sm);
}}
.filters-row {{
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}}
.custom-select {{
  height: 40px;
  padding: 0 32px 0 12px;
  background: var(--bg-card-solid);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-main);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  outline: none;
  transition: var(--transition);
}}
.custom-select:focus {{
  border-color: var(--lagoon-600);
}}
.reset-btn {{
  height: 40px;
  padding: 0 14px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: var(--transition);
}}
.reset-btn:hover {{
  background: var(--bg-hover);
  color: var(--coral-600);
}}
.toolbar-actions {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}}
.csv-btn, .print-btn {{
  height: 40px;
  padding: 0 14px;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
}}
.csv-btn {{
  background: var(--lagoon-50);
  border: 1px solid var(--lagoon-100);
  color: var(--lagoon-700);
}}
.csv-btn:hover {{
  background: var(--lagoon-600);
  color: #fff;
  border-color: var(--lagoon-600);
}}
.print-btn {{
  background: var(--emerald-50);
  border: 1px solid var(--emerald-100);
  color: var(--emerald-700);
}}
.print-btn:hover {{
  background: var(--emerald-600);
  color: #fff;
  border-color: var(--emerald-600);
}}
@media (max-width: 768px) {{
  .toolbar-actions {{
    width: 100%;
    margin-left: 0;
  }}
  .csv-btn, .print-btn {{
    flex: 1;
    justify-content: center;
  }}
}}

/* Ruban Kilométrique RT1 (Paea PK 18 -> PK 28.3) */
.pk-ribbon {{
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: thin;
}}
.pk-ribbon::-webkit-scrollbar {{ height: 4px; }}
.pk-ribbon::-webkit-scrollbar-thumb {{ background: var(--border-subtle); border-radius: 4px; }}
.pk-pill {{
  white-space: nowrap;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
}}
.pk-pill:hover {{
  border-color: var(--lagoon-500);
  color: var(--lagoon-700);
}}
.pk-pill.active {{
  background: var(--lagoon-600);
  color: #fff;
  border-color: var(--lagoon-600);
}}

/* ==========================================================================
   VUE TABLEAU PRO (DESKTOP)
   ========================================================================== */
.table-panel {{
  background: var(--bg-card);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}}
.table-scroll {{
  overflow-x: auto;
}}
table {{
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.88rem;
  text-align: left;
}}
thead {{
  position: sticky;
  top: 76px;
  z-index: 20;
  background: var(--bg-card-solid);
  border-bottom: 2px solid var(--border);
}}
th {{
  padding: 12px 14px;
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
  transition: var(--transition);
}}
th:hover {{
  color: var(--lagoon-600);
}}
th.sorted {{
  color: var(--lagoon-600);
}}
th.sorted::after {{
  content: ' ↑';
}}
th.sorted.desc::after {{
  content: ' ↓';
}}
tbody tr {{
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background-color 0.15s ease;
}}
tbody tr:hover {{
  background-color: var(--bg-hover);
}}
td {{
  padding: 12px 14px;
  vertical-align: middle;
  border-bottom: 1px solid var(--border);
}}
td.td-name {{
  font-weight: 600;
  color: var(--text-main);
  max-width: 260px;
}}
td.td-rep {{
  color: var(--text-muted);
  max-width: 220px;
}}
td.td-addr {{
  color: var(--text-muted);
  max-width: 240px;
  font-size: 0.84rem;
}}

/* Badges & Pills */
.pill-form {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.2px;
}}
.pill-form.sarl {{ background: #e0f2fe; color: #0369a1; }}
.pill-form.sas {{ background: #f3e8ff; color: #7e22ce; }}
.pill-form.sci {{ background: #fef3c7; color: #b45309; }}
.pill-form.pphy {{ background: #f1f5f9; color: #475569; }}
.pill-form.inst {{ background: #ecfdf5; color: #047857; }}

.pill-cat {{
  display: inline-block;
  padding: 2px 7px;
  border-radius: var(--radius-full);
  font-size: 0.72rem;
  font-weight: 600;
}}
.pill-cat.COMMERCE {{ background: #e0f2fe; color: #0284c7; }}
.pill-cat.INDUSTRIE {{ background: #fee2e2; color: #b91c1c; }}
.pill-cat.MÉTIER {{ background: #fef3c7; color: #d97706; }}
.pill-cat.SERVICE {{ background: #dcfce7; color: #15803d; }}
.pill-cat.INSTITUTION {{ background: #f1f5f9; color: #475569; }}

/* ==========================================================================
   BADGES D'IDENTIFIANTS OFFICIELS (HAUTE VISIBILITÉ ISPF / RCS)
   ========================================================================== */
.id-badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 8px;
  border-radius: 6px;
  font-family: 'SF Mono', Monaco, Inconsolata, 'Fira Mono', Consolas, monospace;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  line-height: 1.25;
  margin: 2px 4px 2px 0;
  vertical-align: middle;
  white-space: nowrap;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
  transition: var(--transition);
}}
.id-badge:hover {{
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.14);
}}

/* Badge N° TAHITI (Territoire / ISPF / DICP) */
.id-badge.id-tahiti, .id-badge:not(.id-rcs) {{
  background: #e0f2fe;
  color: #0369a1;
  border: 1.5px solid #0284c7;
}}
.id-badge.id-tahiti .id-prefix {{
  background: #0284c7;
  color: #ffffff;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}}
.id-badge.id-tahiti .id-val {{
  font-weight: 800;
  color: #0c4a6e;
}}

/* Badge RCS (Registre du Commerce et des Sociétés) */
.id-badge.id-rcs {{
  background: #f3e8ff;
  color: #6b21a8;
  border: 1.5px solid #9333ea;
}}
.id-badge.id-rcs .id-prefix {{
  background: #9333ea;
  color: #ffffff;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}}
.id-badge.id-rcs .id-val {{
  font-weight: 800;
  color: #581c87;
}}

/* Dark Mode pour les badges officiels */
[data-theme="dark"] .id-badge.id-tahiti,
[data-theme="dark"] .id-badge:not(.id-rcs) {{
  background: rgba(2, 132, 199, 0.2);
  color: #38bdf8;
  border-color: #38bdf8;
}}
[data-theme="dark"] .id-badge.id-tahiti .id-prefix {{
  background: #0284c7;
  color: #ffffff;
}}
[data-theme="dark"] .id-badge.id-tahiti .id-val {{
  color: #f0f9ff;
}}

[data-theme="dark"] .id-badge.id-rcs {{
  background: rgba(147, 51, 234, 0.2);
  color: #c084fc;
  border-color: #c084fc;
}}
[data-theme="dark"] .id-badge.id-rcs .id-prefix {{
  background: #9333ea;
  color: #ffffff;
}}
[data-theme="dark"] .id-badge.id-rcs .id-val {{
  color: #faf5ff;
}}

.biz-ids-row {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  padding: 6px 10px;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-left: 3px solid var(--lagoon-600);
  border-radius: var(--radius-sm);
}}

/* ==========================================================================
   VUE CARTES BENTO (GRID VIEW - DESKTOP & MOBILE)
   ========================================================================== */
.cards-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
  gap: 16px;
}}
.biz-card {{
  background: var(--bg-card);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 18px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 14px;
  transition: var(--transition);
  cursor: pointer;
  position: relative;
}}
.biz-card:hover {{
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: var(--lagoon-500);
}}
.biz-top {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}}
.biz-title {{
  font-family: var(--font-title);
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.25;
  color: var(--text-main);
}}
.biz-badges {{
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}}
.biz-info {{
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.84rem;
}}
.biz-row {{
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: var(--text-muted);
}}
.biz-row svg {{
  flex-shrink: 0;
  margin-top: 2px;
}}
.biz-actions {{
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding-top: 10px;
  border-top: 1px dashed var(--border);
}}

/* Contact Links & Action Buttons */
.action-chip {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  font-weight: 600;
  text-decoration: none;
  transition: var(--transition);
}}
.action-chip.tel {{ background: var(--lagoon-50); color: var(--lagoon-700); border: 1px solid var(--lagoon-100); }}
.action-chip.tel:hover {{ background: var(--lagoon-600); color: #fff; }}
.action-chip.wa {{ background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }}
.action-chip.wa:hover {{ background: #059669; color: #fff; }}
.action-chip.web {{ background: var(--bg-hover); color: var(--text-main); border: 1px solid var(--border); }}
.action-chip.web:hover {{ background: var(--lagoon-50); color: var(--lagoon-600); }}
.action-chip.status-warn {{ background: var(--amber-50); color: var(--amber-600); border: 1px solid var(--amber-100); font-size: 0.75rem; }}

/* Contact Cell in Table */
.contact-cell {{ display: flex; flex-direction: column; gap: 4px; font-size: 0.82rem; }}
.contact-tag-direct {{ display: inline-flex; align-items: center; gap: 4px; padding: 2px 7px; border-radius: var(--radius-full); font-size: 0.72rem; font-weight: 700; background: var(--emerald-50); color: var(--emerald-700); border: 1px solid var(--emerald-100); width: fit-content; }}
.contact-tag-alert {{ display: inline-flex; align-items: center; gap: 4px; padding: 2px 7px; border-radius: var(--radius-full); font-size: 0.72rem; font-weight: 700; background: var(--coral-100); color: var(--coral-600); border: 1px solid var(--coral-100); width: fit-content; }}

/* ==========================================================================
   FICHE DÉTAIL GLISSANTE : SLIDE-OVER DRAWER (PC) & BOTTOM SHEET (MOBILE)
   ========================================================================== */
.drawer-backdrop {{
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(4px);
  z-index: 1000;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
}}
.drawer-backdrop.open {{
  opacity: 1;
  pointer-events: auto;
}}
.drawer {{
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: min(520px, 100%);
  background: var(--bg-card-solid);
  box-shadow: var(--shadow-lg);
  z-index: 1001;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
}}
.drawer.open {{
  transform: translateX(0);
}}
@media (max-width: 640px) {{
  .drawer {{
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    max-height: 85vh;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    transform: translateY(100%);
  }}
  .drawer.open {{
    transform: translateY(0);
  }}
}}
.drawer-handle {{
  display: none;
  width: 44px;
  height: 5px;
  background: var(--border-subtle);
  border-radius: 4px;
  margin: 12px auto 4px;
}}
@media (max-width: 640px) {{
  .drawer-handle {{ display: block; }}
}}
.drawer-head {{
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}}
.drawer-title {{
  font-family: var(--font-title);
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1.2;
}}
.drawer-close {{
  background: var(--bg-hover);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}}
.drawer-close:hover {{
  color: var(--text-main);
  background: var(--border);
}}
.drawer-body {{
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}}
.detail-section {{
  display: flex;
  flex-direction: column;
  gap: 8px;
}}
.detail-label {{
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}}
.detail-value {{
  font-size: 0.95rem;
  color: var(--text-main);
  font-weight: 500;
}}
.drawer-quick-actions {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin: 10px 0;
}}
.btn-action-big {{
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-weight: 700;
  font-size: 0.88rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-decoration: none;
  cursor: pointer;
  transition: var(--transition);
  border: none;
}}
.btn-action-big.call {{ background: var(--lagoon-600); color: #fff; }}
.btn-action-big.call:hover {{ background: var(--lagoon-700); }}
.btn-action-big.maps {{ background: var(--bg-hover); color: var(--text-main); border: 1px solid var(--border); }}
.btn-action-big.maps:hover {{ border-color: var(--lagoon-600); }}
.btn-action-big.vcard {{ grid-column: span 2; background: var(--emerald-50); color: var(--emerald-700); border: 1px solid var(--emerald-100); }}
.btn-action-big.vcard:hover {{ background: var(--emerald-600); color: #fff; }}

/* ==========================================================================
   BOTTOM NAVIGATION BAR FIXE (MOBILE ONLY)
   ========================================================================== */
.bottom-bar {{
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--bg-card-solid);
  border-top: 1px solid var(--border);
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.08);
  z-index: 100;
  justify-content: space-around;
  align-items: center;
}}
@media (max-width: 768px) {{
  .bottom-bar {{ display: flex; }}
}}
.b-tab {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 600;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: var(--transition);
  padding: 6px 12px;
}}
.b-tab.active {{
  color: var(--lagoon-600);
}}

/* ==========================================================================
   FEEDBACK VIDE & PAGINATION INFINIE
   ========================================================================== */
.empty-feedback {{
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
  display: none;
}}
.empty-feedback svg {{
  margin: 0 auto 12px;
  color: var(--text-dim);
}}
.loading-more {{
  text-align: center;
  padding: 24px;
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 600;
}}

/* Animations */
@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(6px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
/* Print-only / Screen-only helpers */
.print-only-header,
.print-only-footer,
.biz-print-contact,
.biz-row-label,
.print-contact-line {{
  display: none;
}}

/* ==========================================================================
   MODALE D'IMPRESSION PRO
   ========================================================================== */
.print-modal-backdrop {{
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(6px);
  z-index: 1100;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}}
.print-modal-backdrop.open {{
  opacity: 1;
  pointer-events: auto;
}}
.print-modal {{
  width: min(580px, 100%);
  background: var(--bg-card-solid);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transform: translateY(12px) scale(0.98);
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}}
.print-modal-backdrop.open .print-modal {{
  transform: translateY(0) scale(1);
}}
.print-modal-header {{
  padding: 18px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.print-modal-icon {{
  font-size: 1.5rem;
  width: 42px;
  height: 42px;
  border-radius: var(--radius-md);
  background: var(--emerald-50);
  display: flex;
  align-items: center;
  justify-content: center;
}}
.print-modal-title {{
  font-family: var(--font-title);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1.2;
}}
.print-modal-sub {{
  font-size: 0.82rem;
  color: var(--text-muted);
}}
.print-modal-body {{
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: calc(85vh - 140px);
  overflow-y: auto;
}}
.print-summary-box {{
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}}
.print-summary-count {{
  display: flex;
  align-items: baseline;
  gap: 8px;
}}
.count-number {{
  font-family: var(--font-title);
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--lagoon-600);
}}
.count-label {{
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-main);
}}
.print-summary-detail {{
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.4;
}}
.print-format-section {{
  display: flex;
  flex-direction: column;
  gap: 8px;
}}
.print-section-label {{
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted);
}}
.print-options-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}}
@media (max-width: 520px) {{
  .print-options-grid {{ grid-template-columns: 1fr; }}
}}
.print-option-card {{
  border: 2px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px;
  cursor: pointer;
  background: var(--bg-card-solid);
  transition: var(--transition);
  display: flex;
  gap: 10px;
  position: relative;
}}
.print-option-card:hover {{
  border-color: var(--lagoon-500);
  background: var(--bg-hover);
}}
.print-option-card.selected {{
  border-color: var(--lagoon-600);
  background: var(--lagoon-50);
}}
.print-option-card input[type="radio"] {{
  margin-top: 3px;
  accent-color: var(--lagoon-600);
}}
.option-content {{
  display: flex;
  flex-direction: column;
  gap: 4px;
}}
.option-header {{
  display: flex;
  align-items: center;
  gap: 6px;
}}
.option-title {{
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
}}
.option-badge {{
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  background: var(--lagoon-600);
  color: #fff;
  padding: 1px 5px;
  border-radius: 4px;
}}
.option-desc {{
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.35;
}}
.print-tip-box {{
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 14px;
  background: var(--amber-50);
  border: 1px solid var(--amber-100);
  border-radius: var(--radius-md);
  color: var(--amber-600);
  font-size: 0.78rem;
  line-height: 1.4;
}}
.print-tip-box svg {{
  flex-shrink: 0;
  margin-top: 1px;
}}
.print-modal-footer {{
  padding: 16px 24px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 10px;
  background: var(--bg-hover);
}}
.btn-cancel {{
  padding: 10px 18px;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.88rem;
  background: var(--bg-card-solid);
  border: 1px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  transition: var(--transition);
}}
.btn-cancel:hover {{
  color: var(--text-main);
  border-color: var(--border-subtle);
}}

/* ==========================================================================
   STYLES D'IMPRESSION PROFESSIONNELS (MISE EN PAGE PAPIER & EXPORT PDF)
   ========================================================================== */
@media print {{
  @page {{
    size: A4 portrait;
    margin: 8mm 8mm 10mm 8mm;
  }}

  /* Forcer la préservation des couleurs et contrastes */
  *, *::before, *::after {{
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}

  /* Masquer tous les éléments visuels de l'interface web */
  header.hero,
  .hero,
  .stats-strip,
  .control-panel,
  .search-row,
  .pk-ribbon,
  .filters-row,
  .bottom-bar,
  .drawer-backdrop,
  .drawer,
  .print-modal-backdrop,
  .loading-more,
  .empty-feedback,
  #themeToggle,
  .kbd-hint,
  .biz-actions,
  #bTabSearch,
  #bTabContact,
  #bTabPk,
  #bTabStats,
  .view-switch,
  .toolbar-actions {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }}

  /* Assurer que le conteneur masqué reste masqué */
  #tableContainer[style*="display: none"],
  #cardsContainer[style*="display: none"] {{
    display: none !important;
  }}

  /* Reset document pour papier */
  html, body {{
    background: #ffffff !important;
    color: #0f172a !important;
    font-size: 8pt !important;
    line-height: 1.3 !important;
    padding: 0 !important;
    margin: 0 !important;
    min-height: auto !important;
    overflow: visible !important;
  }}

  .main-wrapper {{
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    position: static !important;
  }}

  /* En-tête officiel imprimé */
  .print-only-header {{
    display: block !important;
    margin-bottom: 10px !important;
    padding-bottom: 8px !important;
    border-bottom: 2px solid #0f172a !important;
  }}
  .print-header-top {{
    display: flex !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    margin-bottom: 4px !important;
  }}
  .print-logo-emblem {{
    font-family: var(--font-title) !important;
    font-size: 11pt !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    letter-spacing: 0.5px !important;
  }}
  .print-logo-sub {{
    font-size: 7.2pt !important;
    color: #475569 !important;
    font-weight: 500 !important;
  }}
  .print-meta-right {{
    text-align: right !important;
    font-size: 7.2pt !important;
    color: #475569 !important;
  }}
  .print-count-badge {{
    font-weight: 700 !important;
    color: #0f172a !important;
    font-size: 8pt !important;
    margin-top: 2px !important;
  }}
  .print-header-title {{
    font-family: var(--font-title) !important;
    font-size: 12pt !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    margin: 4px 0 3px !important;
  }}
  .print-filter-line {{
    font-size: 7.5pt !important;
    color: #1e293b !important;
    background: #f1f5f9 !important;
    padding: 3px 8px !important;
    border-radius: 4px !important;
    display: inline-block !important;
    border: 1px solid #cbd5e1 !important;
  }}
  .print-filter-label {{
    font-weight: 700 !important;
    color: #0f172a !important;
    margin-right: 4px !important;
  }}

  /* Pied de page officiel imprimé */
  .print-only-footer {{
    display: flex !important;
    justify-content: space-between !important;
    margin-top: 14px !important;
    padding-top: 6px !important;
    border-top: 1px solid #cbd5e1 !important;
    font-size: 6.8pt !important;
    color: #64748b !important;
  }}

  /* -------------------------------------------------------------------------
     MISE EN PAGE 1 : TABLEAU PRO IMPRIMÉ
     ------------------------------------------------------------------------- */
  .table-panel {{
    background: #ffffff !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    overflow: visible !important;
  }}
  .table-scroll {{
    overflow: visible !important;
  }}
  table {{
    width: 100% !important;
    border-collapse: collapse !important;
    font-size: 7.5pt !important;
  }}
  thead {{
    position: static !important;
    display: table-header-group !important;
    background: #f1f5f9 !important;
  }}
  th {{
    border: 1px solid #cbd5e1 !important;
    background: #f8fafc !important;
    color: #0f172a !important;
    padding: 5px 6px !important;
    font-size: 7pt !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.3px !important;
  }}
  th.sorted::after, th.sorted.desc::after {{
    display: none !important;
  }}
  tbody tr {{
    border: 1px solid #cbd5e1 !important;
    page-break-inside: avoid !important;
    break-inside: avoid !important;
  }}
  tbody tr:nth-child(even) {{
    background-color: #f8fafc !important;
  }}
  td {{
    border: 1px solid #cbd5e1 !important;
    padding: 5px 6px !important;
    vertical-align: top !important;
    font-size: 7.2pt !important;
    color: #1e293b !important;
  }}
  td.td-name {{
    font-weight: 700 !important;
    color: #000000 !important;
    max-width: none !important;
    font-size: 7.8pt !important;
  }}
  td.td-rep {{
    max-width: none !important;
    color: #334155 !important;
  }}
  td.td-addr {{
    max-width: none !important;
    color: #334155 !important;
    font-size: 7pt !important;
  }}

  /* Badges dans le tableau imprimé */
  .pill-form, .pill-cat {{
    border: 1px solid #94a3b8 !important;
    background: #f1f5f9 !important;
    color: #0f172a !important;
    padding: 1px 4px !important;
    font-size: 6.5pt !important;
    font-weight: 700 !important;
    border-radius: 3px !important;
    display: inline-block !important;
  }}
  /* Badges d'identifiants officiels à l'impression (Haute visibilité) */
  .id-badge {{
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
    border: 1.5px solid #0f172a !important;
    background: #f8fafc !important;
    color: #0f172a !important;
    font-size: 7.2pt !important;
    font-weight: 800 !important;
    padding: 2px 6px !important;
    margin: 1px 4px 1px 0 !important;
    border-radius: 4px !important;
    font-family: monospace !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}
  .id-badge.id-tahiti {{
    border-color: #0284c7 !important;
    background: #f0f9ff !important;
  }}
  .id-badge.id-tahiti .id-prefix {{
    background: #0284c7 !important;
    color: #ffffff !important;
    padding: 1px 4px !important;
    border-radius: 3px !important;
    font-size: 6.2pt !important;
    font-weight: 800 !important;
  }}
  .id-badge.id-tahiti .id-val {{
    font-weight: 800 !important;
    color: #0369a1 !important;
  }}
  .id-badge.id-rcs {{
    border-color: #7c3aed !important;
    background: #faf5ff !important;
  }}
  .id-badge.id-rcs .id-prefix {{
    background: #7c3aed !important;
    color: #ffffff !important;
    padding: 1px 4px !important;
    border-radius: 3px !important;
    font-size: 6.2pt !important;
    font-weight: 800 !important;
  }}
  .id-badge.id-rcs .id-val {{
    font-weight: 800 !important;
    color: #581c87 !important;
  }}
  .contact-cell {{
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
    font-size: 7pt !important;
  }}
  .contact-tag-direct, .contact-tag-alert {{
    display: none !important;
  }}
  .print-contact-line {{
    display: block !important;
    line-height: 1.25 !important;
    color: #0f172a !important;
  }}
  .action-chip {{
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
    font-size: 7pt !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    text-decoration: none !important;
  }}

  /* -------------------------------------------------------------------------
     MISE EN PAGE 2 : CARTES PRO IMPRIMÉES (GRILLE 2 COLONNES PAPIER)
     ------------------------------------------------------------------------- */
  .cards-grid {{
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 8px !important;
  }}
  .biz-card {{
    background: #ffffff !important;
    border: 1px solid #94a3b8 !important;
    border-radius: 6px !important;
    padding: 8px 10px !important;
    box-shadow: none !important;
    transform: none !important;
    page-break-inside: avoid !important;
    break-inside: avoid !important;
    gap: 6px !important;
  }}
  .biz-card:hover {{
    transform: none !important;
    border-color: #94a3b8 !important;
  }}
  .biz-top {{
    display: flex !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    gap: 6px !important;
  }}
  .biz-title {{
    font-size: 8.8pt !important;
    font-weight: 700 !important;
    color: #000000 !important;
    line-height: 1.2 !important;
  }}
  .biz-badges {{
    display: flex !important;
    gap: 4px !important;
    flex-shrink: 0 !important;
  }}
  .biz-info {{
    display: flex !important;
    flex-direction: column !important;
    gap: 3px !important;
    font-size: 7.2pt !important;
    margin-top: 4px !important;
  }}
  .biz-row {{
    display: flex !important;
    align-items: flex-start !important;
    gap: 4px !important;
    color: #334155 !important;
  }}
  .biz-row svg {{
    display: none !important;
  }}
  .biz-row-label {{
    display: inline !important;
    font-weight: 700 !important;
    color: #0f172a !important;
  }}
  .biz-ids-row {{
    display: flex !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    gap: 4px !important;
    margin-top: 4px !important;
    padding: 3px 6px !important;
    background: #f8fafc !important;
    border: 1px solid #cbd5e1 !important;
    border-left: 3px solid #0284c7 !important;
    border-radius: 4px !important;
  }}
  .biz-actions {{
    display: none !important;
  }}
  .biz-print-contact {{
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
    margin-top: 5px !important;
    padding-top: 4px !important;
    border-top: 1px dashed #cbd5e1 !important;
    font-size: 7pt !important;
    color: #0f172a !important;
  }}
  .bpc-row {{
    line-height: 1.25 !important;
  }}
}}
</style>
</head>
<body>

<!-- HERO HEADER IMMERSIF -->
<header class="hero">
  <div class="hero-content">
    <div class="hero-top">
      <div class="hero-badge">
        <span class="pulse-dot"></span>
        <span>Observatoire Économique de Paea</span>
      </div>
      <button class="icon-btn" id="themeToggle" title="Changer de thème (Clair / Nuit)">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/></svg>
      </button>
    </div>
    <h1>Répertoire des entreprises et patentés</h1>
  </div>
</header>

<!-- MAIN WRAPPER -->
<main class="main-wrapper">

  <!-- RUBAN STATISTIQUES COMPACT (INTERACTIF) -->
  <section class="stats-strip" aria-label="Statistiques clés">
    <button type="button" class="stat-pill active" id="cardTotal" data-filter="all" title="Afficher toutes les entités">
      <span class="stat-icon">🏢</span>
      <div class="stat-meta">
        <span class="stat-num" id="statTotalVal">{total_entries}</span>
        <span class="stat-txt">Total entités</span>
      </div>
    </button>

    <button type="button" class="stat-pill" id="cardSocietes" data-filter="societes" title="Filtrer uniquement les Sociétés">
      <span class="stat-icon" style="background:rgba(126, 34, 206, 0.1);color:#7e22ce;">⚖️</span>
      <div class="stat-meta">
        <span class="stat-num" id="statSocietesVal">{societes_count}</span>
        <span class="stat-txt">Sociétés</span>
      </div>
    </button>

    <button type="button" class="stat-pill" id="cardPphy" data-filter="pphy" title="Filtrer uniquement les Patentés">
      <span class="stat-icon" style="background:rgba(217, 119, 6, 0.1);color:#d97706;">👤</span>
      <div class="stat-meta">
        <span class="stat-num" id="statPphyVal">{pphy_count}</span>
        <span class="stat-txt">Patentés individuels</span>
      </div>
    </button>

    <button type="button" class="stat-pill" id="cardDigital" data-filter="direct" title="Filtrer avec contacts directs vérifiés">
      <span class="stat-icon" style="background:rgba(5, 150, 105, 0.1);color:#059669;">⭐</span>
      <div class="stat-meta">
        <span class="stat-num" id="statDirectVal">{with_contact} <small style="font-size:0.75rem;font-weight:600;opacity:0.85;">({round((with_contact/total_entries)*100)}%)</small></span>
        <span class="stat-txt">Contacts directs vérifiés</span>
      </div>
    </button>
  </section>

  <!-- CONTROL PANEL : RECHERCHE UNIVERSELLE & FILTRES -->
  <section class="control-panel">
    <div class="search-row">
      <div class="search-box">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input type="text" id="searchInput" class="search-input" placeholder="Rechercher une entreprise, un gérant, un PK, une activité, n° TAHITI…">
        <span class="kbd-hint">Ctrl K</span>
      </div>

      <div class="view-switch" id="viewSwitcher">
        <button class="view-btn active" id="btnViewTable" title="Affichage tableau">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18M3 15h18M9 9v12M15 9v12"/></svg>
          <span>Tableau</span>
        </button>
        <button class="view-btn" id="btnViewCards" title="Affichage cartes">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>
          <span>Cartes</span>
        </button>
      </div>

      <div class="toolbar-actions">
        <button class="csv-btn" id="btnExportCsv" title="Exporter la sélection courante en CSV (Excel)">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
          <span>Export CSV</span>
        </button>
        <button class="print-btn" id="btnPrintList" title="Imprimer la sélection filtrée (Tableau ou Cartes)">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg>
          <span>Imprimer</span>
        </button>
      </div>
    </div>

    <!-- RUBAN PK INTERACTIF (AXE RT1) -->
    <div class="pk-ribbon" id="pkRibbon">
      <span class="pk-pill active" data-pk="">Tout Paea (PK 18 à 28)</span>
      <span class="pk-pill" data-pk="18">PK 18 – 19 (Papehue)</span>
      <span class="pk-pill" data-pk="20">PK 20 – 21 (Tiapa / Mairie)</span>
      <span class="pk-pill" data-pk="22">PK 22 – 23 (Orofero / Arahurahu)</span>
      <span class="pk-pill" data-pk="24">PK 24 – 25 (Vaiterupe)</span>
      <span class="pk-pill" data-pk="26">PK 26 – 28 (Mara'a / Pahiarepo)</span>
    </div>

    <!-- FILTRES SECONDAIRES -->
    <div class="filters-row">
      <select id="filterCat" class="custom-select">
        <option value="">Tous les collèges (4)</option>
        <option value="COMMERCE">Commerce</option>
        <option value="INDUSTRIE">Industrie</option>
        <option value="MÉTIER">Métier</option>
        <option value="SERVICE">Service</option>
        <option value="INSTITUTION">Institutions</option>
      </select>

      <select id="filterForm" class="custom-select">
        <option value="">Toutes les formes</option>
        <option value="PPHY">Patentés (PPHY)</option>
        <option value="SARL">SARL</option>
        <option value="SAS">SAS / SASU</option>
        <option value="SCI">SCI</option>
        <option value="EURL">EURL</option>
        <option value="SCP">SCP</option>
      </select>

      <select id="filterContact" class="custom-select">
        <option value="">Tous les contacts ({total_entries})</option>
        <option value="with">⭐ Avec contact direct ({with_contact})</option>
        <option value="tel">📞 Avec ligne téléphonique</option>
        <option value="web_mail">🌐 Avec e-mail, site ou réseaux</option>
        <option value="alert">⚠️ Avec statut particulier ({alert_status})</option>
        <option value="without">Sans contact</option>
      </select>

      <button id="btnResetFilters" class="reset-btn" title="Réinitialiser les filtres">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
        <span>Effacer</span>
      </button>

      <span id="activeCountBadge" style="font-size:0.85rem;font-weight:600;color:var(--text-muted);margin-left:auto;">
        <span id="resultCount">{total_entries}</span> résultats affichés
      </span>
    </div>
  </section>

  <!-- EN-TÊTE OFFICIEL DE DOCUMENT POUR IMPRESSION (VISIBLE UNIQUEMENT À L'IMPRESSION) -->
  <header class="print-only-header" id="printDocumentHeader">
    <div class="print-header-top">
      <div class="print-brand">
        <div class="print-logo-emblem">COMMUNE DE PAEA – OBSERVATOIRE ÉCONOMIQUE</div>
        <div class="print-logo-sub">Mission PIAC 2026 • Répertoire consolidé officiel des Entreprises et Patentés</div>
      </div>
      <div class="print-meta-right">
        <div class="print-date" id="printHeaderDate">Date d'édition</div>
        <div class="print-count-badge" id="printHeaderCount">0 entités répertoriées</div>
      </div>
    </div>
    <div class="print-header-banner">
      <h1 class="print-header-title" id="printHeaderTitle">Répertoire officiel des Entreprises &amp; Patentés</h1>
      <div class="print-filter-line">
        <span class="print-filter-label">Sélection / Filtres :</span>
        <span class="print-filter-value" id="printHeaderFilters">Toutes les entités</span>
        <span style="margin: 0 4px; opacity: 0.6;">•</span>
        <span class="print-header-mode" id="printHeaderMode">Format Tableau</span>
      </div>
    </div>
  </header>

  <!-- VUE 1 : TABLEAU PRO (DESKTOP) -->
  <section class="table-panel" id="tableContainer">
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th data-key="name" class="sorted">Dénomination / Nom</th>
            <th data-key="form">Forme</th>
            <th data-key="cat">Collège</th>
            <th data-key="rep">Dirigeant / Mandataire</th>
            <th data-key="naf">Activité / NAF</th>
            <th data-key="ids">Identifiants</th>
            <th data-key="address">Adresse / PK</th>
            <th>Contact Direct</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
  </section>

  <!-- VUE 2 : CARTES BENTO (GRID VIEW) -->
  <section class="cards-grid" id="cardsContainer" style="display:none;"></section>

  <!-- FEEDBACK SI AUCUN RÉSULTAT -->
  <div class="empty-feedback" id="emptyFeedback">
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/><path d="M8 11h6"/></svg>
    <h3>Aucune entreprise ne correspond à ces critères</h3>
    <p>Modifiez vos termes de recherche ou cliquez sur "Effacer" pour réinitialiser la vue.</p>
  </div>

  <div class="loading-more" id="loadingMore" style="display:none;">Chargement de résultats supplémentaires…</div>

  <!-- PIED DE PAGE OFFICIEL POUR IMPRESSION (VISIBLE UNIQUEMENT À L'IMPRESSION) -->
  <footer class="print-only-footer" id="printDocumentFooter">
    <span>Observatoire Économique de Paea — Répertoire consolidé (Données publiques CCISM • DICP • Lexpol)</span>
    <span>Document d'information économique — Paea, Tahiti</span>
  </footer>

</main>

<!-- BOTTOM NAVIGATION BAR (MOBILE ONLY) -->
<nav class="bottom-bar">
  <button class="b-tab active" id="bTabSearch">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
    <span>Rechercher</span>
  </button>
  <button class="b-tab" id="bTabContact">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
    <span>Contacts</span>
  </button>
  <button class="b-tab" id="bTabPk">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
    <span>Par PK</span>
  </button>
  <button class="b-tab" id="bTabStats">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M12 8v8M8 12v4M16 10v6"/></svg>
    <span>Chiffres</span>
  </button>
</nav>

<!-- FICHE DÉTAIL GLISSANTE (DRAWER / BOTTOM SHEET) -->
<div class="drawer-backdrop" id="drawerBackdrop"></div>
<aside class="drawer" id="drawerSheet" aria-hidden="true">
  <div class="drawer-handle"></div>
  <div class="drawer-head">
    <div>
      <div id="drawerBadges" style="margin-bottom:6px;"></div>
      <h2 class="drawer-title" id="drawerTitle">—</h2>
    </div>
    <button class="drawer-close" id="drawerClose" title="Fermer la fiche">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
    </button>
  </div>
  <div class="drawer-body">
    <!-- BOUTONS D'ACTION 1-TAP IMMÉDIATS -->
    <div class="drawer-quick-actions" id="drawerQuickActions"></div>

    <div class="detail-section">
      <span class="detail-label">Dirigeant / Mandataire officiel</span>
      <div class="detail-value" id="drawerRep">—</div>
    </div>

    <div class="detail-section">
      <span class="detail-label">Activité &amp; Code NAF</span>
      <div class="detail-value" id="drawerNaf">—</div>
    </div>

    <div class="detail-section">
      <span class="detail-label">Localisation &amp; Repère Kilométrique</span>
      <div class="detail-value" id="drawerAddress">—</div>
    </div>

    <div class="detail-section">
      <span class="detail-label">Identifiants Officiels (ISPF / RCS)</span>
      <div class="detail-value" id="drawerIds">—</div>
    </div>

    <div class="detail-section">
      <span class="detail-label">Coordonnées &amp; Présence Web</span>
      <div class="detail-value" id="drawerContactText">—</div>
    </div>

    <!-- BOUTON VCARD DIRECT -->
    <button class="btn-action-big vcard" id="btnDownloadVcard">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/><path d="M16 11h6M19 8v6"/></svg>
      <span>Ajouter au carnet d'adresses (vCard)</span>
    </button>
  </div>
</aside>

<!-- MODALE D'IMPRESSION PROFESSIONNELLE -->
<div class="print-modal-backdrop" id="printModalBackdrop">
  <div class="print-modal" id="printModal" role="dialog" aria-modal="true" aria-labelledby="printModalTitle">
    <div class="print-modal-header">
      <div style="display:flex;align-items:center;gap:12px;">
        <div class="print-modal-icon">🖨️</div>
        <div>
          <h2 class="print-modal-title" id="printModalTitle">Imprimer la sélection</h2>
          <p class="print-modal-sub">Mise en page papier et export PDF haute fidélité</p>
        </div>
      </div>
      <button class="drawer-close" id="btnPrintModalClose" title="Fermer" type="button">✕</button>
    </div>

    <div class="print-modal-body">
      <!-- Synthèse des filtres et volumétrie -->
      <div class="print-summary-box">
        <div class="print-summary-count">
          <span class="count-number" id="printModalCount">0</span>
          <span class="count-label">entités correspondent à vos filtres</span>
        </div>
        <div class="print-summary-detail">
          <strong>Critères actuels :</strong> <span id="printModalFilters">Toutes les entités</span>
        </div>
      </div>

      <!-- Choix de la présentation -->
      <div class="print-format-section">
        <label class="print-section-label">Format de mise en page</label>
        <div class="print-options-grid">
          <label class="print-option-card selected" id="optCardTable">
            <input type="radio" name="printFormat" value="table" id="radioPrintTable" checked>
            <div class="option-content">
              <div class="option-header">
                <span class="option-title">📋 Tableau de synthèse</span>
                <span class="option-badge">Officiel</span>
              </div>
              <p class="option-desc">Listing compact structuré avec en-têtes récurrents sur chaque page. Idéal pour dossiers administratifs et économie de papier.</p>
            </div>
          </label>

          <label class="print-option-card" id="optCardCards">
            <input type="radio" name="printFormat" value="cards" id="radioPrintCards">
            <div class="option-content">
              <div class="option-header">
                <span class="option-title">🗂️ Fiches / Cartes</span>
                <span class="option-badge" style="background:var(--emerald-600);">Détaillé</span>
              </div>
              <p class="option-desc">Grille 2 colonnes avec encadrés individuels et coordonnées de contact en texte clair. Idéal pour prospection et tournées de terrain.</p>
            </div>
          </label>
        </div>
      </div>

      <!-- Conseils d'impression -->
      <div class="print-tip-box">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
        <div>
          <strong>Rendu propre et sans éléments web :</strong>
          <div style="margin-top:2px;">Les barres de recherche, boutons, filtres et menus sont automatiquement masqués. Pour préserver les nuances de couleurs des badges, activez <em>« Graphiques d'arrière-plan »</em> dans la fenêtre d'impression.</div>
        </div>
      </div>
    </div>

    <div class="print-modal-footer">
      <button type="button" class="btn-cancel" id="btnPrintModalCancel">Annuler</button>
      <button type="button" class="btn-action-big call" id="btnPrintModalConfirm" style="flex:1;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg>
        <span id="btnPrintConfirmLabel">Lancer l'impression</span>
      </button>
    </div>
  </div>
</div>

<!-- ==========================================================================
   DONNÉES ENRICHIES ET SCRIPT INTERACTIF
   ========================================================================== -->
<script>
const DATA = {data_json_str};

// UTILITAIRES
const $ = id => document.getElementById(id);
const norm = s => (s||'').toString().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');

function escapeHtml(s){{
  if(!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}}

// RENDU DES IDENTIFIANTS OFFICIELS (HAUTE VISIBILITÉ TAHITI / RCS)
function renderIdBadge(id) {{
  if(!id) return '';
  const s = id.toString().trim();
  const upper = s.toUpperCase();
  if(upper.startsWith('TAHITI')) {{
    const val = s.replace(/^TAHITI\s*/i, '');
    return `<span class="id-badge id-tahiti" title="Numéro TAHITI (Identifiant officiel ISPF / DICP)"><span class="id-prefix">TAHITI</span> <span class="id-val">${{escapeHtml(val)}}</span></span>`;
  }} else if(upper.startsWith('RCS')) {{
    const val = s.replace(/^RCS\s*/i, '');
    return `<span class="id-badge id-rcs" title="Registre du Commerce et des Sociétés"><span class="id-prefix">RCS</span> <span class="id-val">${{escapeHtml(val)}}</span></span>`;
  }}
  return `<span class="id-badge id-generic"><span class="id-prefix">ID</span> <span class="id-val">${{escapeHtml(s)}}</span></span>`;
}}

// ANIMATION COUNT-UP FLUIDE
function countUp(el, target, duration = 500) {{
  if(!el) return;
  const start = 0;
  const startTime = performance.now();
  function update(time) {{
    const elapsed = time - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(start + (target - start) * ease);
    el.textContent = current.toLocaleString('fr-FR');
    if(progress < 1) requestAnimationFrame(update);
  }}
  requestAnimationFrame(update);
}}

// PARSING DU CONTACT PROPREMENT AVEC ISOLATION
function parseContactData(raw) {{
  if(!raw || !raw.trim()) return {{ hasContact: false, phones: [], mails: [], urls: [], isAlert: false, text: '' }};
  const str = raw.trim();
  if(str.startsWith('⚠️')) {{
    return {{ hasContact: true, phones: [], mails: [], urls: [], isAlert: true, text: str.replace(/^⚠️\s*/, '') }};
  }}

  const phones = [];
  const mails = [];
  const urls = [];

  // Découpage par composant ' · ' ou parsing multi-formats
  const parts = str.split(' · ').map(p => p.trim());
  parts.forEach(p => {{
    if(p.startsWith('☎')) {{
      const num = p.replace(/^☎\s*/, '').trim();
      if(num) phones.push(num);
    }} else if(p.startsWith('✉')) {{
      const em = p.replace(/^✉\s*/, '').trim();
      if(em) mails.push(em);
    }} else if(p.startsWith('🌐')) {{
      const u = p.replace(/^🌐\s*/, '').trim();
      if(u) urls.push(u);
    }} else if(p.includes('@')) {{
      mails.push(p);
    }} else if(/(?:40|87|88|89)\s*\d{{2}}\s*\d{{2}}\s*\d{{2}}/.test(p)) {{
      phones.push(p.replace(/[^\d\s]/g, '').trim());
    }} else if(p.includes('.com') || p.includes('.pf') || p.includes('.fr')) {{
      urls.push(p);
    }}
  }});

  return {{
    hasContact: phones.length > 0 || mails.length > 0 || urls.length > 0,
    phones, mails, urls, isAlert: false, text: str
  }};
}}

// RENDU CELLULE TABLE
function renderContactCell(r, forPrint = false) {{
  const c = parseContactData(r.contact);
  if(!c.hasContact && !c.isAlert) return '<span style="color:var(--text-dim)">—</span>';
  if(c.isAlert) {{
    return `<div class="contact-cell"><span class="contact-tag-alert">⚠️ Statut</span><span style="font-size:0.75rem;color:var(--text-muted);">${{escapeHtml(c.text)}}</span></div>`;
  }}
  if(forPrint) {{
    let items = [];
    c.phones.forEach(num => {{
      items.push(`<div class="print-contact-line">📞 <strong>${{escapeHtml(num)}}</strong></div>`);
    }});
    c.mails.forEach(em => {{
      items.push(`<div class="print-contact-line">✉ ${{escapeHtml(em)}}</div>`);
    }});
    c.urls.forEach(url => {{
      const clean = url.replace(/^https?:\\/\\//, '');
      items.push(`<div class="print-contact-line">🌐 ${{escapeHtml(clean)}}</div>`);
    }});
    return `<div class="contact-cell">${{items.join('')}}</div>`;
  }}
  let links = [];
  c.phones.forEach(num => {{
    const clean = num.replace(/\\s+/g, '');
    const href = clean.length === 8 ? `+689${{clean}}` : clean;
    links.push(`<a href="tel:${{href}}" class="action-chip tel">📞 ${{escapeHtml(num)}}</a>`);
  }});
  c.mails.forEach(em => {{
    links.push(`<a href="mailto:${{escapeHtml(em)}}" class="action-chip web">✉ ${{escapeHtml(em)}}</a>`);
  }});
  c.urls.forEach(url => {{
    const href = url.startsWith('http') ? url : 'https://' + url;
    const clean = url.replace(/^https?:\\/\\//, '');
    let label = `🌐 ${{clean}}`;
    if(url.includes('facebook.com')) label = `📘 FB`;
    links.push(`<a href="${{escapeHtml(href)}}" target="_blank" rel="noopener noreferrer" class="action-chip web">${{escapeHtml(label)}}</a>`);
  }});
  return `<div class="contact-cell"><span class="contact-tag-direct">⭐ Contact direct</span><div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:2px;">${{links.join('')}}</div></div>`;
}}

// RENDU CARTE BENTO
function renderBizCard(r) {{
  const c = parseContactData(r.contact);
  let formCls = (r.form||'').toLowerCase();
  if(!['sarl','sas','sci','pphy'].includes(formCls)) formCls = 'inst';
  
  let actionsHtml = '';
  if(c.isAlert) {{
    actionsHtml = `<span class="action-chip status-warn">⚠️ ${{escapeHtml(c.text)}}</span>`;
  }} else {{
    const chips = [];
    if(c.phones.length > 0) {{
      const p = c.phones[0];
      const clean = p.replace(/\\s+/g, '');
      chips.push(`<a href="tel:+689${{clean}}" class="action-chip tel">📞 Appeler</a>`);
      if(clean.startsWith('87') || clean.startsWith('89')) {{
        chips.push(`<a href="https://wa.me/689${{clean}}" target="_blank" rel="noopener noreferrer" class="action-chip wa">💬 WhatsApp</a>`);
      }}
    }}
    if(c.urls.length > 0) {{
      const u = c.urls[0];
      const href = u.startsWith('http') ? u : 'https://' + u;
      chips.push(`<a href="${{escapeHtml(href)}}" target="_blank" rel="noopener noreferrer" class="action-chip web">${{u.includes('facebook')?'📘 Facebook':'🌐 Web'}}</a>`);
    }}
    if(r.address && r.address !== 'Commune de Paea') {{
      chips.push(`<a href="https://www.google.com/maps/search/?api=1&query=${{encodeURIComponent(r.address + ', Paea, Tahiti')}}" target="_blank" rel="noopener noreferrer" class="action-chip web">📍 Itinéraire</a>`);
    }}
    actionsHtml = chips.join('');
  }}

  const idsHtml = (r.ids && r.ids.length > 0) 
    ? `<div class="biz-ids-row">${{r.ids.map(id => renderIdBadge(id)).join('')}}</div>`
    : '';

  const printContactRows = [];
  if(c.phones.length > 0) {{
    printContactRows.push(`<div class="bpc-row"><strong>📞 Tél :</strong> ${{c.phones.map(p => escapeHtml(p)).join(' / ')}}</div>`);
  }}
  if(c.mails.length > 0) {{
    printContactRows.push(`<div class="bpc-row"><strong>✉ Email :</strong> ${{c.mails.map(m => escapeHtml(m)).join(' / ')}}</div>`);
  }}
  if(c.urls.length > 0) {{
    printContactRows.push(`<div class="bpc-row"><strong>🌐 Web/FB :</strong> ${{c.urls.map(u => escapeHtml(u.replace(/^https?:\\/\\//,''))).join(' / ')}}</div>`);
  }}
  if(c.isAlert) {{
    printContactRows.push(`<div class="bpc-row" style="color:#b91c1c;"><strong>⚠️ Statut :</strong> ${{escapeHtml(c.text)}}</div>`);
  }}
  if(!c.hasContact && !c.isAlert) {{
    printContactRows.push(`<div class="bpc-row" style="color:#64748b;"><em>Aucun contact direct enregistré</em></div>`);
  }}

  return `
  <article class="biz-card anim-fade" data-idx="${{r.idx}}">
    <div>
      <div class="biz-top">
        <h3 class="biz-title">${{escapeHtml(r.name)}}</h3>
        <div class="biz-badges">
          <span class="pill-form ${{formCls}}">${{escapeHtml(r.form)}}</span>
          <span class="pill-cat ${{escapeHtml(r.cat)}}">${{escapeHtml(r.cat)}}</span>
        </div>
      </div>
      <div class="biz-info" style="margin-top:8px;">
        <div class="biz-row">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
          <span class="biz-row-label">Dirigeant : </span>
          <span>${{escapeHtml(r.rep||'—')}}</span>
        </div>
        <div class="biz-row">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
          <span class="biz-row-label">Adresse : </span>
          <span>${{escapeHtml(r.address||'Commune de Paea')}}</span>
        </div>
        ${{r.naf ? `<div class="biz-row"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="14" x="2" y="7" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg><span class="biz-row-label">Activité : </span><span style="font-size:0.78rem;">${{escapeHtml(r.naf)}}</span></div>` : ''}}
        ${{idsHtml}}
      </div>
    </div>
    ${{actionsHtml ? `<div class="biz-actions">${{actionsHtml}}</div>` : ''}}
    <div class="biz-print-contact">
      ${{printContactRows.join('')}}
    </div>
  </article>`;
}}

// GESTION DU RENDU ET DE LA PAGINATION INFINIE
let filtered = [...DATA];
let sortKey = 'name';
let sortDir = 1;
let currentView = 'table';
let pageIndex = 1;
const PAGE_SIZE = 40;

function sortData() {{
  filtered.sort((a,b) => {{
    let va = (sortKey === 'ids' ? (a.ids||[]).join(' ') : (a[sortKey]||'')).toString();
    let vb = (sortKey === 'ids' ? (b.ids||[]).join(' ') : (b[sortKey]||'')).toString();
    va = norm(va); vb = norm(vb);
    if(va < vb) return -1 * sortDir;
    if(va > vb) return 1 * sortDir;
    return 0;
  }});
}}

function render(keepCount = false) {{
  if(!keepCount) {{
    pageIndex = 1;
  }}
  const total = filtered.length;
  $('resultCount').textContent = total.toLocaleString('fr-FR');
  
  if(total === 0) {{
    $('tableBody').innerHTML = '';
    $('cardsContainer').innerHTML = '';
    $('emptyFeedback').style.display = 'block';
    $('loadingMore').style.display = 'none';
    return;
  }}
  $('emptyFeedback').style.display = 'none';

  const visibleItems = filtered.slice(0, pageIndex * PAGE_SIZE);

  if(currentView === 'table') {{
    $('tableContainer').style.display = 'block';
    $('cardsContainer').style.display = 'none';
    const rowsHtml = visibleItems.map(r => `
      <tr data-idx="${{r.idx}}">
        <td class="td-name">${{escapeHtml(r.name)}}</td>
        <td><span class="pill-form ${{['sarl','sas','sci','pphy'].includes((r.form||'').toLowerCase())?(r.form||'').toLowerCase():'inst'}}">${{escapeHtml(r.form)}}</span></td>
        <td><span class="pill-cat ${{escapeHtml(r.cat)}}">${{escapeHtml(r.cat)}}</span></td>
        <td class="td-rep">${{escapeHtml(r.rep||'—')}}</td>
        <td>${{r.naf ? `<span style="font-size:0.75rem;background:var(--bg-hover);padding:2px 6px;border-radius:4px;">${{escapeHtml(r.naf)}}</span>` : '—'}}</td>
        <td>${{(r.ids||[]).map(id => renderIdBadge(id)).join('')}}</td>
        <td class="td-addr">${{escapeHtml(r.address||'—')}}</td>
        <td>${{renderContactCell(r)}}</td>
      </tr>
    `).join('');
    $('tableBody').innerHTML = rowsHtml;
  }} else {{
    $('tableContainer').style.display = 'none';
    $('cardsContainer').style.display = 'grid';
    const cardsHtml = visibleItems.map(r => renderBizCard(r)).join('');
    $('cardsContainer').innerHTML = cardsHtml;
  }}

  $('loadingMore').style.display = visibleItems.length < total ? 'block' : 'none';
}}

// SCROLL INFINI
window.addEventListener('scroll', () => {{
  if(pageIndex * PAGE_SIZE >= filtered.length) return;
  if(window.innerHeight + window.scrollY >= document.body.offsetHeight - 400) {{
    pageIndex++;
    render(true);
  }}
}});

// FILTRAGE AVANCÉ
function applyFilters() {{
  const q = norm($('searchInput').value);
  const cat = $('filterCat').value;
  const form = $('filterForm').value;
  const contact = $('filterContact').value;
  const pkSelected = document.querySelector('.pk-pill.active')?.dataset.pk || '';

  filtered = DATA.filter(item => {{
    if(cat && item.cat !== cat) return false;
    if(form) {{
      if(form === 'SAS' && !['SAS','SASU'].includes(item.form)) return false;
      if(form !== 'SAS' && item.form !== form) return false;
    }}
    const parsed = parseContactData(item.contact);
    if(contact === 'with' && !parsed.hasContact) return false;
    if(contact === 'without' && parsed.hasContact) return false;
    if(contact === 'tel' && parsed.phones.length === 0) return false;
    if(contact === 'web_mail' && parsed.mails.length === 0 && parsed.urls.length === 0) return false;
    if(contact === 'alert' && !parsed.isAlert) return false;

    if(pkSelected) {{
      const addrNorm = norm(item.address);
      const pkNum = parseInt(pkSelected, 10);
      const matchesPk = addrNorm.includes(`pk ${{pkNum}}`) || addrNorm.includes(`pk ${{pkNum + 1}}`);
      if(!matchesPk) return false;
    }}

    if(q) {{
      const blob = norm([item.name, item.rep, item.address, item.naf, (item.ids||[]).join(' '), item.contact].join(' '));
      if(!blob.includes(q)) return false;
    }}
    return true;
  }});

  sortData();
  render(false);
}}

// DÉTAILS MODAL / DRAWER
let activeItem = null;

function openDetails(target) {{
  let item = null;
  if(typeof target === 'number') {{
    item = DATA[target];
  }} else if(typeof target === 'string') {{
    item = DATA.find(d => d.name === target);
  }}
  if(!item) return;
  activeItem = item;

  $('drawerTitle').textContent = item.name;
  $('drawerBadges').innerHTML = `
    <span class="pill-form ${{['sarl','sas','sci','pphy'].includes((item.form||'').toLowerCase())?(item.form||'').toLowerCase():'inst'}}">${{escapeHtml(item.form)}}</span>
    <span class="pill-cat ${{escapeHtml(item.cat)}}">${{escapeHtml(item.cat)}}</span>
  `;
  $('drawerRep').textContent = item.rep || 'Non précisé';
  $('drawerNaf').textContent = item.naf || 'Non renseigné';
  $('drawerAddress').textContent = item.address || 'Commune de Paea';
  $('drawerIds').innerHTML = (item.ids||[]).length ? (item.ids||[]).map(id => renderIdBadge(id)).join('') : '<span style="color:var(--text-dim)">Non renseigné</span>';

  const c = parseContactData(item.contact);
  const actionsContainer = $('drawerQuickActions');
  actionsContainer.innerHTML = '';

  if(c.isAlert) {{
    $('drawerContactText').innerHTML = `<span style="color:var(--coral-600);font-weight:700;">⚠️ ${{escapeHtml(c.text)}}</span>`;
  }} else if(c.hasContact) {{
    let contactInfo = [];
    if(c.phones.length > 0) {{
      const p = c.phones[0];
      const clean = p.replace(/\\s+/g, '');
      actionsContainer.innerHTML += `<a href="tel:+689${{clean}}" class="btn-action-big call">📞 Appeler ${{escapeHtml(p)}}</a>`;
      if(clean.startsWith('87') || clean.startsWith('89')) {{
        actionsContainer.innerHTML += `<a href="https://wa.me/689${{clean}}" target="_blank" rel="noopener" class="btn-action-big" style="background:#059669;color:#fff;">💬 WhatsApp</a>`;
      }}
      contactInfo.push(`Téléphone : ${{c.phones.join(' / ')}}`);
    }}
    if(item.address && item.address !== 'Commune de Paea') {{
      actionsContainer.innerHTML += `<a href="https://www.google.com/maps/search/?api=1&query=${{encodeURIComponent(item.address + ', Paea, Tahiti')}}" target="_blank" rel="noopener" class="btn-action-big maps">📍 Itinéraire GPS</a>`;
    }}
    c.mails.forEach(em => {{
      actionsContainer.innerHTML += `<a href="mailto:${{escapeHtml(em)}}" class="btn-action-big" style="background:#0284c7;color:#fff;">✉ Écrire e-mail</a>`;
      contactInfo.push(`E-mail : <a href="mailto:${{escapeHtml(em)}}" style="color:var(--lagoon-600);font-weight:600;">${{escapeHtml(em)}}</a>`);
    }});
    c.urls.forEach(url => {{
      const href = url.startsWith('http') ? url : 'https://' + url;
      actionsContainer.innerHTML += `<a href="${{escapeHtml(href)}}" target="_blank" rel="noopener" class="btn-action-big" style="background:#0369a1;color:#fff;">${{url.includes('facebook') ? '📘 Page Facebook' : '🌐 Site Internet'}}</a>`;
      contactInfo.push(`Site/Réseaux : <a href="${{escapeHtml(href)}}" target="_blank" rel="noopener" style="color:var(--lagoon-600);font-weight:600;">${{escapeHtml(url)}}</a>`);
    }});
    $('drawerContactText').innerHTML = contactInfo.join('<br>') || '—';
  }} else {{
    $('drawerContactText').innerHTML = '<span style="color:var(--text-muted)">Aucun contact public direct répertorié.</span>';
    if(item.address && item.address !== 'Commune de Paea') {{
      actionsContainer.innerHTML += `<a href="https://www.google.com/maps/search/?api=1&query=${{encodeURIComponent(item.address + ', Paea, Tahiti')}}" target="_blank" rel="noopener" class="btn-action-big maps" style="grid-column:span 2;">📍 Itinéraire GPS vers l'adresse</a>`;
    }}
  }}

  $('drawerBackdrop').classList.add('open');
  $('drawerSheet').classList.add('open');
  $('drawerSheet').setAttribute('aria-hidden', 'false');
}}

function closeDetails() {{
  $('drawerBackdrop').classList.remove('open');
  $('drawerSheet').classList.remove('open');
  $('drawerSheet').setAttribute('aria-hidden', 'true');
  activeItem = null;
}}

$('drawerClose').addEventListener('click', closeDetails);
$('drawerBackdrop').addEventListener('click', closeDetails);

// GÉNÉRATION VCARD DIRECTE
$('btnDownloadVcard').addEventListener('click', () => {{
  if(!activeItem) return;
  const c = parseContactData(activeItem.contact);
  const tel = c.phones.length > 0 ? `+689${{c.phones[0].replace(/\\s+/g, '')}}` : '';
  const email = c.mails.length > 0 ? c.mails[0] : '';
  const org = activeItem.name;
  
  const vcard = [
    'BEGIN:VCARD',
    'VERSION:3.0',
    `FN:${{org}}`,
    `ORG:${{org}}`,
    activeItem.rep ? `TITLE:${{activeItem.rep}}` : '',
    tel ? `TEL;TYPE=WORK,VOICE:${{tel}}` : '',
    email ? `EMAIL;TYPE=PREF,INTERNET:${{email}}` : '',
    `ADR;TYPE=WORK:;;${{activeItem.address||'Paea'}};;;98711;Polynésie française`,
    `NOTE:Observatoire Économique de Paea - NAF: ${{activeItem.naf||''}} - Identifiants: ${{(activeItem.ids||[]).join(' ')}}`,
    'END:VCARD'
  ].filter(Boolean).join('\\n');

  const blob = new Blob([vcard], {{ type: 'text/vcard;charset=utf-8;' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${{activeItem.name.replace(/[^a-zA-Z0-9]/g, '_')}}.vcf`;
  a.click();
  URL.revokeObjectURL(url);
}});

// SWITCH DE VUES TABLEAU / CARTES (SANS SAUT DE DÉFILEMENT)
function switchView(newView) {{
  if(currentView === newView) return;
  currentView = newView;
  $('btnViewTable').classList.toggle('active', newView === 'table');
  $('btnViewCards').classList.toggle('active', newView === 'cards');
  // Conserver le nombre d'éléments chargés et la position de défilement actuelle (zéro saut d'écran)
  render(true);
}}

$('btnViewTable').addEventListener('click', () => switchView('table'));
$('btnViewCards').addEventListener('click', () => switchView('cards'));

// DÉLÉGATION DE CLIC (SANS ONCLICK INLINE, 100% SÉCURISÉ CONTRE LES GUILLEMETS)
$('tableBody').addEventListener('click', e => {{
  if(e.target.closest('a, button')) return;
  const tr = e.target.closest('tr[data-idx]');
  if(tr) openDetails(parseInt(tr.dataset.idx, 10));
}});

$('cardsContainer').addEventListener('click', e => {{
  if(e.target.closest('a, button')) return;
  const card = e.target.closest('.biz-card[data-idx]');
  if(card) openDetails(parseInt(card.dataset.idx, 10));
}});

// CLIC PILL STAT POUR FILTRER RAPIDEMENT
document.querySelectorAll('.stat-pill').forEach(pill => {{
  pill.addEventListener('click', () => {{
    document.querySelectorAll('.stat-pill').forEach(c => c.classList.remove('active'));
    pill.classList.add('active');
    const f = pill.dataset.filter;
    if(f === 'all') {{ $('filterForm').value = ''; $('filterContact').value = ''; }}
    else if(f === 'direct') {{ $('filterContact').value = 'with'; }}
    else if(f === 'societes') {{ $('filterForm').value = 'SARL'; }}
    else if(f === 'pphy') {{ $('filterForm').value = 'PPHY'; }}
    applyFilters();
  }});
}});

// CLIC RUBAN PK
document.querySelectorAll('.pk-pill').forEach(pill => {{
  pill.addEventListener('click', () => {{
    document.querySelectorAll('.pk-pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    applyFilters();
  }});
}});

// ÉVÉNEMENTS RECHERCHE & SÉLECTEURS
$('searchInput').addEventListener('input', applyFilters);
$('filterCat').addEventListener('change', applyFilters);
$('filterForm').addEventListener('change', applyFilters);
$('filterContact').addEventListener('change', applyFilters);

$('btnResetFilters').addEventListener('click', () => {{
  $('searchInput').value = '';
  $('filterCat').value = '';
  $('filterForm').value = '';
  $('filterContact').value = '';
  document.querySelectorAll('.pk-pill').forEach((p, idx) => p.classList.toggle('active', idx === 0));
  document.querySelectorAll('.stat-pill').forEach((c, idx) => c.classList.toggle('active', idx === 0));
  sortKey = 'name';
  sortDir = 1;
  applyFilters();
}});

// TRI DES COLONNES
document.querySelectorAll('thead th').forEach(th => {{
  th.addEventListener('click', () => {{
    const key = th.dataset.key;
    if(sortKey === key) {{ sortDir *= -1; }}
    else {{ sortKey = key; sortDir = 1; }}
    document.querySelectorAll('thead th').forEach(t => t.classList.remove('sorted', 'desc'));
    th.classList.add('sorted');
    if(sortDir === -1) th.classList.add('desc');
    sortData();
    render(false);
  }});
}});

// RACCOURCI CLAVIER CTRL+K & ECHAP
window.addEventListener('keydown', e => {{
  if((e.ctrlKey || e.metaKey) && e.key === 'k') {{
    e.preventDefault();
    $('searchInput').focus();
    $('searchInput').select();
  }}
  if(e.key === 'Escape') {{
    closeDetails();
    closePrintModal();
  }}
}});

// THÈME CLAIR / NUIT (LOCALSTORAGE)
const themeToggle = $('themeToggle');
const savedTheme = localStorage.getItem('paea_theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);

themeToggle.addEventListener('click', () => {{
  const cur = document.documentElement.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('paea_theme', next);
}});

// EXPORT CSV
$('btnExportCsv').addEventListener('click', () => {{
  const sep = ';';
  const headers = ['Dénomination / Nom','Forme','Catégorie','Dirigeant / Mandataire','NAF / Activité','Identifiants','Adresse','Contact'];
  const lines = [headers.join(sep)];
  filtered.forEach(r => {{
    const row = [r.name, r.form, r.cat, r.rep||'', r.naf||'', (r.ids||[]).join(' | '), r.address||'', r.contact||'']
      .map(v => `"${{(v||'').toString().replace(/"/g,'""')}}"`);
    lines.push(row.join(sep));
  }});
  const csv = '\\uFEFF' + lines.join('\\n');
  const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `paea_entreprises_${{new Date().toISOString().slice(0,10)}}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}});

// ==========================================================================
// GESTION DE L'IMPRESSION PRO (FILTRES, TABLEAU / CARTES, MASQUAGE WEB)
// ==========================================================================

function getFilterSummary() {{
  const parts = [];
  const q = $('searchInput').value.trim();
  const cat = $('filterCat').value;
  const form = $('filterForm').value;
  const contact = $('filterContact').value;
  const pkPill = document.querySelector('.pk-pill.active');
  const pk = pkPill ? pkPill.dataset.pk : '';

  if(form) {{
    if(form === 'PPHY') parts.push('Patentés (PPHY)');
    else parts.push('Forme ' + form);
  }}
  if(cat) {{
    parts.push('Collège ' + cat.charAt(0) + cat.slice(1).toLowerCase());
  }}
  if(pk) {{
    parts.push(pkPill.textContent.trim());
  }}
  if(contact) {{
    if(contact === 'with') parts.push('Avec contact direct vérifié');
    else if(contact === 'tel') parts.push('Avec ligne téléphonique');
    else if(contact === 'web_mail') parts.push('Avec e-mail / web');
    else if(contact === 'alert') parts.push('Statut particulier');
    else if(contact === 'without') parts.push('Sans contact');
  }}
  if(q) {{
    parts.push('Recherche : « ' + q + ' »');
  }}

  if(parts.length === 0) {{
    return 'Répertoire complet (Toutes formes, Tous collèges, Tout Paea)';
  }}
  return parts.join(' • ');
}}

function updatePrintHeader(formatToPrint) {{
  const now = new Date();
  const dateStr = now.toLocaleDateString('fr-FR', {{ day: '2-digit', month: '2-digit', year: 'numeric' }});
  const timeStr = now.toLocaleTimeString('fr-FR', {{ hour: '2-digit', minute: '2-digit' }});
  
  $('printHeaderDate').textContent = `Édité le ${{dateStr}} à ${{timeStr}}`;
  $('printHeaderCount').textContent = `${{filtered.length.toLocaleString('fr-FR')}} entité${{filtered.length > 1 ? 's' : ''}} répertoriée${{filtered.length > 1 ? 's' : ''}}`;
  $('printHeaderFilters').textContent = getFilterSummary();
  $('printHeaderMode').textContent = formatToPrint === 'cards' ? 'Présentation : Fiches / Cartes' : 'Présentation : Tableau officiel';
}}

let isPrinting = false;
let prePrintViewState = null;

function preparePrint(formatToPrint) {{
  isPrinting = true;
  prePrintViewState = {{
    view: currentView,
    pageIndex: pageIndex
  }};

  updatePrintHeader(formatToPrint);

  if(formatToPrint === 'table') {{
    $('tableContainer').style.display = 'block';
    $('cardsContainer').style.display = 'none';
    const allRowsHtml = filtered.map(r => `
      <tr data-idx="${{r.idx}}">
        <td class="td-name">${{escapeHtml(r.name)}}</td>
        <td><span class="pill-form ${{['sarl','sas','sci','pphy'].includes((r.form||'').toLowerCase())?(r.form||'').toLowerCase():'inst'}}">${{escapeHtml(r.form)}}</span></td>
        <td><span class="pill-cat ${{escapeHtml(r.cat)}}">${{escapeHtml(r.cat)}}</span></td>
        <td class="td-rep">${{escapeHtml(r.rep||'—')}}</td>
        <td>${{r.naf ? `<span style="font-size:0.75rem;">${{escapeHtml(r.naf)}}</span>` : '—'}}</td>
        <td>${{(r.ids||[]).map(id => renderIdBadge(id)).join('')}}</td>
        <td class="td-addr">${{escapeHtml(r.address||'—')}}</td>
        <td>${{renderContactCell(r, true)}}</td>
      </tr>
    `).join('');
    $('tableBody').innerHTML = allRowsHtml;
  }} else {{
    $('tableContainer').style.display = 'none';
    $('cardsContainer').style.display = 'grid';
    const allCardsHtml = filtered.map(r => renderBizCard(r)).join('');
    $('cardsContainer').innerHTML = allCardsHtml;
  }}
}}

function restoreAfterPrint() {{
  if(!isPrinting) return;
  isPrinting = false;
  if(prePrintViewState) {{
    currentView = prePrintViewState.view;
    pageIndex = prePrintViewState.pageIndex;
    prePrintViewState = null;
  }}
  $('btnViewTable').classList.toggle('active', currentView === 'table');
  $('btnViewCards').classList.toggle('active', currentView === 'cards');
  render(true);
}}

function openPrintModal() {{
  if(filtered.length === 0) {{
    alert("Aucune entreprise ou patenté ne correspond à votre sélection actuelle pour l'impression.");
    return;
  }}
  closeDetails();
  $('printModalCount').textContent = filtered.length.toLocaleString('fr-FR');
  $('printModalFilters').textContent = getFilterSummary();
  $('btnPrintConfirmLabel').textContent = `Lancer l'impression (${{filtered.length.toLocaleString('fr-FR')}} entités)`;

  if(currentView === 'cards') {{
    $('radioPrintCards').checked = true;
    $('optCardCards').classList.add('selected');
    $('optCardTable').classList.remove('selected');
  }} else {{
    $('radioPrintTable').checked = true;
    $('optCardTable').classList.add('selected');
    $('optCardCards').classList.remove('selected');
  }}

  $('printModalBackdrop').classList.add('open');
}}

function closePrintModal() {{
  $('printModalBackdrop').classList.remove('open');
}}

$('optCardTable').addEventListener('click', () => {{
  $('radioPrintTable').checked = true;
  $('optCardTable').classList.add('selected');
  $('optCardCards').classList.remove('selected');
}});
$('optCardCards').addEventListener('click', () => {{
  $('radioPrintCards').checked = true;
  $('optCardCards').classList.add('selected');
  $('optCardTable').classList.remove('selected');
}});

$('btnPrintList').addEventListener('click', openPrintModal);
$('btnPrintModalClose').addEventListener('click', closePrintModal);
$('btnPrintModalCancel').addEventListener('click', closePrintModal);
$('printModalBackdrop').addEventListener('click', e => {{
  if(e.target === $('printModalBackdrop')) closePrintModal();
}});

$('btnPrintModalConfirm').addEventListener('click', () => {{
  const chosenFormat = $('radioPrintCards').checked ? 'cards' : 'table';
  closePrintModal();
  preparePrint(chosenFormat);
  setTimeout(() => {{
    window.print();
  }}, 80);
}});

window.addEventListener('beforeprint', () => {{
  if(!isPrinting) {{
    preparePrint(currentView);
  }}
}});

window.addEventListener('afterprint', () => {{
  restoreAfterPrint();
}});

// BOTTOM NAVIGATION BAR MOBILE
$('bTabSearch').addEventListener('click', () => {{
  $('searchInput').focus();
  window.scrollTo({{ top: $('searchInput').offsetTop - 60, behavior: 'smooth' }});
}});
$('bTabContact').addEventListener('click', () => {{
  $('filterContact').value = 'with';
  applyFilters();
}});
$('bTabPk').addEventListener('click', () => {{
  $('pkRibbon').scrollIntoView({{ behavior: 'smooth' }});
}});
$('bTabStats').addEventListener('click', () => {{
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}});

// DÉMARRAGE INITIAL
sortData();
render(false);
</script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# Garder également une copie paea-entreprises.html pour compatibilité des raccourcis existants
with open('paea-entreprises.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"index.html & paea-entreprises.html générés avec succès ! Taille : {len(html_content):,} caractères.")
