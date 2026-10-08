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
<html lang="fr" data-theme="light" data-palette="lagoon">
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
   DESIGN SYSTEM "POLYNÉSIE MODERNE" - 6 PALETTES ASSORTIES & MODES CLAIR / NUIT
   ========================================================================== */
:root {{
  --font-title: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

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

/* --------------------------------------------------------------------------
   1. PALETTE LAGON DE PAEA (Bleu Océan & Cyan Lagon) - DÉFAUT
   -------------------------------------------------------------------------- */
html, html[data-palette="lagoon"] {{
  --hero-gradient: linear-gradient(135deg, #063156 0%, #0c4a6e 50%, #047857 100%);
  --palette-accent: #0284c7;
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
}}
html[data-palette="lagoon"][data-theme="dark"], html:not([data-palette])[data-theme="dark"] {{
  --hero-gradient: linear-gradient(135deg, #031b2e 0%, #082f49 50%, #064e3b 100%);
  --palette-accent: #38bdf8;
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
  --lagoon-500: #38bdf8;
  --lagoon-100: #082f49;
  --lagoon-50: #0c1e36;
}}

/* --------------------------------------------------------------------------
   2. PALETTE ÉMERAUDE TIARE (Vert Tropical & Menthe Exotique)
   -------------------------------------------------------------------------- */
html[data-palette="emerald"] {{
  --hero-gradient: linear-gradient(135deg, #064e3b 0%, #047857 50%, #0d9488 100%);
  --palette-accent: #059669;
  --bg-app: #f6fbf8;
  --bg-card: rgba(255, 255, 255, 0.88);
  --bg-card-solid: #ffffff;
  --bg-hover: #eef7f2;
  --border: #d2e7db;
  --border-subtle: #bcdbc8;
  --text-main: #062b1e;
  --text-muted: #4b6b5d;
  --text-dim: #7f9f91;

  --lagoon-900: #022c22;
  --lagoon-700: #047857;
  --lagoon-600: #059669;
  --lagoon-500: #10b981;
  --lagoon-100: #d1fae5;
  --lagoon-50: #ecfdf5;
}}
html[data-palette="emerald"][data-theme="dark"] {{
  --hero-gradient: linear-gradient(135deg, #022c22 0%, #064e3b 50%, #134e4a 100%);
  --palette-accent: #34d399;
  --bg-app: #04140e;
  --bg-card: rgba(6, 35, 25, 0.82);
  --bg-card-solid: #08281d;
  --bg-hover: #0e3d2e;
  --border: #124334;
  --border-subtle: #1c5946;
  --text-main: #f0fdf4;
  --text-muted: #86efac;
  --text-dim: #4ade80;

  --lagoon-900: #d1fae5;
  --lagoon-700: #34d399;
  --lagoon-600: #10b981;
  --lagoon-500: #34d399;
  --lagoon-100: #064e3b;
  --lagoon-50: #032e22;
}}

/* --------------------------------------------------------------------------
   3. PALETTE SUNSET MARA'A (Ambre Flamboyant & Cuivre Chaud)
   -------------------------------------------------------------------------- */
html[data-palette="sunset"] {{
  --hero-gradient: linear-gradient(135deg, #7c2d12 0%, #c2410c 50%, #d97706 100%);
  --palette-accent: #ea580c;
  --bg-app: #fdfaf6;
  --bg-card: rgba(255, 255, 255, 0.88);
  --bg-card-solid: #ffffff;
  --bg-hover: #fceddf;
  --border: #fae0cd;
  --border-subtle: #f4cbb0;
  --text-main: #331505;
  --text-muted: #784c2f;
  --text-dim: #ab7f62;

  --lagoon-900: #431407;
  --lagoon-700: #c2410c;
  --lagoon-600: #ea580c;
  --lagoon-500: #f97316;
  --lagoon-100: #ffedd5;
  --lagoon-50: #fff7ed;
}}
html[data-palette="sunset"][data-theme="dark"] {{
  --hero-gradient: linear-gradient(135deg, #431407 0%, #7c2d12 50%, #78350f 100%);
  --palette-accent: #fb923c;
  --bg-app: #150904;
  --bg-card: rgba(38, 18, 10, 0.82);
  --bg-card-solid: #2a140a;
  --bg-hover: #3d1f11;
  --border: #452416;
  --border-subtle: #63321f;
  --text-main: #fff7ed;
  --text-muted: #fdba74;
  --text-dim: #fb923c;

  --lagoon-900: #ffedd5;
  --lagoon-700: #fb923c;
  --lagoon-600: #f97316;
  --lagoon-500: #fb923c;
  --lagoon-100: #431407;
  --lagoon-50: #290e05;
}}

/* --------------------------------------------------------------------------
   4. PALETTE PERLE ROYALE (Pourpre & Nacre Améthyste)
   -------------------------------------------------------------------------- */
html[data-palette="amethyst"] {{
  --hero-gradient: linear-gradient(135deg, #3b0764 0%, #6b21a8 50%, #9333ea 100%);
  --palette-accent: #7c3aed;
  --bg-app: #faf8fd;
  --bg-card: rgba(255, 255, 255, 0.88);
  --bg-card-solid: #ffffff;
  --bg-hover: #f3ebfa;
  --border: #e8d7f7;
  --border-subtle: #d6bdf0;
  --text-main: #1f0b35;
  --text-muted: #64467c;
  --text-dim: #997bab;

  --lagoon-900: #2e1065;
  --lagoon-700: #6d28d9;
  --lagoon-600: #7c3aed;
  --lagoon-500: #8b5cf6;
  --lagoon-100: #ede9fe;
  --lagoon-50: #f5f3ff;
}}
html[data-palette="amethyst"][data-theme="dark"] {{
  --hero-gradient: linear-gradient(135deg, #24053e 0%, #3b0764 50%, #4a044e 100%);
  --palette-accent: #c084fc;
  --bg-app: #100618;
  --bg-card: rgba(30, 14, 46, 0.82);
  --bg-card-solid: #210f33;
  --bg-hover: #341850;
  --border: #3c1c5c;
  --border-subtle: #552783;
  --text-main: #faf5ff;
  --text-muted: #d8b4fe;
  --text-dim: #c084fc;

  --lagoon-900: #ede9fe;
  --lagoon-700: #c084fc;
  --lagoon-600: #a855f7;
  --lagoon-500: #c084fc;
  --lagoon-100: #2e1065;
  --lagoon-50: #1b073e;
}}

/* --------------------------------------------------------------------------
   5. PALETTE CORAIL TUAMOTU (Rose Corallien & Rubis Ensoleillé)
   -------------------------------------------------------------------------- */
html[data-palette="coral"] {{
  --hero-gradient: linear-gradient(135deg, #4c0519 0%, #be123c 50%, #e11d48 100%);
  --palette-accent: #e11d48;
  --bg-app: #fdf7f8;
  --bg-card: rgba(255, 255, 255, 0.88);
  --bg-card-solid: #ffffff;
  --bg-hover: #fde8eb;
  --border: #fcd0d7;
  --border-subtle: #f9afbc;
  --text-main: #370614;
  --text-muted: #7f3e4e;
  --text-dim: #b26c7e;

  --lagoon-900: #4c0519;
  --lagoon-700: #be123c;
  --lagoon-600: #e11d48;
  --lagoon-500: #f43f5e;
  --lagoon-100: #ffe4e6;
  --lagoon-50: #fff1f2;
}}
html[data-palette="coral"][data-theme="dark"] {{
  --hero-gradient: linear-gradient(135deg, #2d020d 0%, #4c0519 50%, #700a25 100%);
  --palette-accent: #fb7185;
  --bg-app: #140408;
  --bg-card: rgba(38, 10, 20, 0.82);
  --bg-card-solid: #280a15;
  --bg-hover: #3e1222;
  --border: #471527;
  --border-subtle: #681f3a;
  --text-main: #fff1f2;
  --text-muted: #fda4af;
  --text-dim: #fb7185;

  --lagoon-900: #ffe4e6;
  --lagoon-700: #fb7185;
  --lagoon-600: #f43f5e;
  --lagoon-500: #fb7185;
  --lagoon-100: #4c0519;
  --lagoon-50: #2a030d;
}}

/* --------------------------------------------------------------------------
   6. PALETTE OCÉAN SAPHIR (Bleu Cobalt & Outremer Pacifique)
   -------------------------------------------------------------------------- */
html[data-palette="sapphire"] {{
  --hero-gradient: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
  --palette-accent: #2563eb;
  --bg-app: #f6f8fd;
  --bg-card: rgba(255, 255, 255, 0.88);
  --bg-card-solid: #ffffff;
  --bg-hover: #ebf1fd;
  --border: #d4e0fa;
  --border-subtle: #b6ccf7;
  --text-main: #0c1a3b;
  --text-muted: #42588c;
  --text-dim: #748bc2;

  --lagoon-900: #172554;
  --lagoon-700: #1d4ed8;
  --lagoon-600: #2563eb;
  --lagoon-500: #3b82f6;
  --lagoon-100: #dbeafe;
  --lagoon-50: #eff6ff;
}}
html[data-palette="sapphire"][data-theme="dark"] {{
  --hero-gradient: linear-gradient(135deg, #090e1c 0%, #0f2452 50%, #17387a 100%);
  --palette-accent: #60a5fa;
  --bg-app: #080e1e;
  --bg-card: rgba(14, 25, 48, 0.82);
  --bg-card-solid: #101c38;
  --bg-hover: #192a54;
  --border: #1d3366;
  --border-subtle: #29478e;
  --text-main: #eff6ff;
  --text-muted: #93c5fd;
  --text-dim: #60a5fa;

  --lagoon-900: #dbeafe;
  --lagoon-700: #60a5fa;
  --lagoon-600: #3b82f6;
  --lagoon-500: #60a5fa;
  --lagoon-100: #172554;
  --lagoon-50: #0d1733;
}}

/* Ombrages en mode sombre */
[data-theme="dark"] {{
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
  background: var(--hero-gradient);
  color: #ffffff;
  padding: 20px 20px 22px;
  overflow: visible;
  z-index: 50;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  transition: background 0.35s ease;
}}
@media (max-width: 680px) {{
  .hero {{
    padding: 16px 14px 18px;
  }}
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
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.22);
  color: #fff;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
  position: relative;
}}
.icon-btn:hover {{
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}}

/* ==========================================================================
   SÉLECTEUR DE PALETTE & THÈMES GÉNÉRAUX ASSORTIS
   ========================================================================== */
.palette-picker-wrapper {{
  position: relative;
  display: inline-block;
}}
.palette-btn {{
  position: relative;
}}
.active-palette-dot {{
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--palette-accent, #0284c7);
  border: 1.5px solid #ffffff;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.45);
  transition: background 0.25s ease;
}}
.palette-dropdown {{
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 250px;
  max-width: calc(100vw - 32px);
  background: var(--bg-card-solid);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
  padding: 8px;
  display: none;
  flex-direction: column;
  gap: 4px;
  z-index: 3000;
  backdrop-filter: var(--glass-blur);
  animation: fadeIn 0.18s ease-out;
}}
.palette-dropdown.open {{
  display: flex;
}}
.palette-dropdown-header {{
  padding: 8px 10px 6px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 4px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}}
.palette-dropdown-title {{
  font-family: var(--font-title);
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-main);
}}
.palette-dropdown-sub {{
  font-size: 0.72rem;
  color: var(--text-muted);
}}
.palette-options-list {{
  display: flex;
  flex-direction: column;
  gap: 3px;
}}
.palette-option {{
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 7px 10px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-main);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: 0.82rem;
  font-weight: 600;
  text-align: left;
  transition: var(--transition);
}}
.palette-option:hover {{
  background: var(--bg-hover);
  border-color: var(--border);
}}
.palette-option.active {{
  background: var(--lagoon-50);
  border-color: var(--lagoon-500);
  color: var(--lagoon-700);
}}
.palette-swatch {{
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
  flex-shrink: 0;
}}
.swatch-lagoon {{ background: linear-gradient(135deg, #0284c7 0%, #047857 100%); }}
.swatch-emerald {{ background: linear-gradient(135deg, #059669 0%, #10b981 100%); }}
.swatch-sunset {{ background: linear-gradient(135deg, #ea580c 0%, #f59e0b 100%); }}
.swatch-amethyst {{ background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); }}
.swatch-coral {{ background: linear-gradient(135deg, #e11d48 0%, #fb7185 100%); }}
.swatch-sapphire {{ background: linear-gradient(135deg, #2563eb 0%, #38bdf8 100%); }}

.palette-name {{
  flex: 1;
}}
.palette-check {{
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--lagoon-600);
  opacity: 0;
  transition: opacity 0.2s ease;
}}
.palette-option.active .palette-check {{
  opacity: 1;
}}

/* Icônes dynamiques bouton Dark / Light */
[data-theme="dark"] #themeToggle .sun-icon {{ display: none !important; }}
[data-theme="dark"] #themeToggle .moon-icon {{ display: block !important; }}
#themeToggle .sun-icon {{ display: block; }}
#themeToggle .moon-icon {{ display: none; }}

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
  margin: 16px auto 0;
  padding: 0 20px;
  position: relative;
  z-index: 10;
}}
@media (max-width: 680px) {{
  .main-wrapper {{
    margin: 12px auto 0;
    padding: 0 12px;
  }}
}}

/* ==========================================================================
   RUBAN STATISTIQUES COMPACT (INTERACTIF - ALIGNÉ SUR 1 LIGNE MOBILE)
   ========================================================================== */
.stats-strip {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}}
.stat-label-long {{ display: inline; }}
.stat-label-short {{ display: none; }}

@media (max-width: 960px) {{
  .stats-strip {{ gap: 8px; }}
  .stat-pill {{ padding: 7px 9px; gap: 8px; }}
  .stat-num {{ font-size: 1.05rem; }}
}}

/* Forcer l'alignement strict des 4 statistiques sur la même ligne horizontale sur mobile */
@media (max-width: 680px) {{
  .stats-strip {{
    grid-template-columns: repeat(4, 1fr) !important;
    gap: 5px !important;
  }}
  .stat-pill {{
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    padding: 6px 2px !important;
    gap: 3px !important;
    min-width: 0 !important;
  }}
  .stat-icon {{
    width: 24px !important;
    height: 24px !important;
    font-size: 0.8rem !important;
    margin-bottom: 1px !important;
  }}
  .stat-meta {{
    align-items: center !important;
    text-align: center !important;
    width: 100% !important;
  }}
  .stat-num {{
    font-size: 0.92rem !important;
    font-weight: 800 !important;
    line-height: 1.1 !important;
    white-space: nowrap !important;
  }}
  .stat-pct {{
    display: none !important;
  }}
  .stat-txt {{
    font-size: 0.62rem !important;
    line-height: 1.05 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 100% !important;
  }}
  .stat-label-long {{
    display: none !important;
  }}
  .stat-label-short {{
    display: inline !important;
  }}
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
.search-box {{
  width: 100%;
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

/* LIGNE DES ACTIONS & VUES (TABLEAU, CARTES, FILTRES, IMPRIMER - 100% FLUIDE ET SANS ASCENSEUR) */
.actions-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  box-sizing: border-box;
}}
.view-switch {{
  display: flex;
  background: var(--bg-hover);
  padding: 3px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  box-sizing: border-box;
}}
.view-btn {{
  border: none;
  background: transparent;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
  box-sizing: border-box;
}}
.view-btn svg {{
  flex-shrink: 0;
}}
.view-btn.active {{
  background: var(--bg-card-solid);
  color: var(--text-main);
  box-shadow: var(--shadow-sm);
}}
.toolbar-actions {{
  display: flex;
  align-items: center;
  gap: 8px;
  box-sizing: border-box;
}}
.filter-btn, .print-btn {{
  height: 40px;
  padding: 0 12px;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
  box-sizing: border-box;
}}
.filter-btn svg, .print-btn svg {{
  flex-shrink: 0;
}}
.filter-btn {{
  background: var(--lagoon-50);
  border: 1px solid var(--lagoon-100);
  color: var(--lagoon-700);
  position: relative;
}}
.filter-btn:hover {{
  background: var(--lagoon-600);
  color: #fff;
  border-color: var(--lagoon-600);
}}
.filter-btn.has-active-filters {{
  background: var(--lagoon-600);
  color: #fff;
  border-color: var(--lagoon-700);
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
}}
.filter-count-badge {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--coral-600);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9999px;
  line-height: 1;
  flex-shrink: 0;
}}
.filter-btn.has-active-filters .filter-count-badge {{
  background: #fff;
  color: var(--lagoon-700);
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

/* ADAPTATION MOBILE FLUIDE SANS ASCENSEUR HORIZONTAL */
@media (max-width: 768px) {{
  .control-panel {{
    padding: 10px 10px;
    gap: 8px;
  }}
  .actions-row {{
    display: flex;
    gap: 6px;
    width: 100%;
    overflow: hidden; /* Aucun ascenseur */
  }}
  .view-switch {{
    flex: 1 1 0;
    min-width: 0;
    display: flex;
    padding: 2px;
  }}
  .view-btn {{
    flex: 1 1 0;
    min-width: 0;
    justify-content: center;
    padding: 6px 4px;
    font-size: 0.78rem;
    gap: 4px;
  }}
  .view-btn span {{
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  .toolbar-actions {{
    flex: 1 1 0;
    min-width: 0;
    display: flex;
    gap: 6px;
  }}
  .filter-btn, .print-btn {{
    flex: 1 1 0;
    min-width: 0;
    justify-content: center;
    height: 36px;
    padding: 0 4px;
    font-size: 0.78rem;
    gap: 4px;
  }}
  .filter-btn span, .print-btn span {{
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  .filter-count-badge {{
    min-width: 16px;
    height: 16px;
    font-size: 0.65rem;
    padding: 0 3px;
  }}
}}

@media (max-width: 380px) {{
  .control-panel {{
    padding: 8px 6px;
  }}
  .actions-row {{
    gap: 4px;
  }}
  .view-btn, .filter-btn, .print-btn {{
    font-size: 0.72rem;
    padding: 0 2px;
    gap: 3px;
  }}
}}

/* Barre d'état des résultats sous les actions */
.results-meta-bar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 2px 0 2px;
  font-size: 0.85rem;
  color: var(--text-muted);
  flex-wrap: wrap;
  gap: 8px;
}}
.results-count-text {{
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}}
.results-count-text strong {{
  color: var(--text-main);
  font-weight: 700;
}}
.filter-summary-chip {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--lagoon-50);
  border: 1px solid var(--lagoon-100);
  color: var(--lagoon-700);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
}}
.filter-summary-chip button {{
  background: none;
  border: none;
  color: var(--lagoon-700);
  font-size: 0.95rem;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  line-height: 1;
}}

/* Grille PK intégrée au tiroir de filtres */
.pk-drawer-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}}
.pk-drawer-grid .pk-pill:first-child {{
  grid-column: span 2;
}}
.pk-pill {{
  padding: 9px 12px;
  border-radius: var(--radius-md);
  background: var(--bg-app);
  border: 1.5px solid var(--border);
  color: var(--text-main);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.pk-pill:hover {{
  border-color: var(--lagoon-500);
  background: var(--lagoon-50);
  color: var(--lagoon-700);
}}
.pk-pill.active {{
  background: var(--lagoon-600);
  color: #fff;
  border-color: var(--lagoon-600);
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);
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
  cursor: grab;
  touch-action: none;
}}
@media (max-width: 640px) {{
  .drawer-handle {{ display: block; }}
  .drawer-head {{ touch-action: none; }}
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
  min-width: 36px;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
  flex-shrink: 0;
  pointer-events: auto;
  z-index: 2;
  touch-action: manipulation;
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
   TIROIR DE FILTRES GLISSANT (DRAWER / FLYOUT)
   ========================================================================== */
.filter-drawer-backdrop {{
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(4px);
  z-index: 1040;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
}}
.filter-drawer-backdrop.open {{
  opacity: 1;
  pointer-events: auto;
}}
.filter-drawer {{
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: min(420px, 100vw);
  background: var(--bg-card-solid);
  box-shadow: var(--shadow-lg);
  z-index: 1050;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
}}
.filter-drawer.open {{
  transform: translateX(0);
}}
@media (max-width: 640px) {{
  .filter-drawer {{
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    max-height: 85vh;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    transform: translateY(100%);
  }}
  .filter-drawer.open {{
    transform: translateY(0);
  }}
}}
.filter-drawer-head {{
  padding: 18px 22px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background: var(--bg-card);
}}
.filter-drawer-title-group {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
.filter-drawer-icon {{
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  background: var(--lagoon-50);
  color: var(--lagoon-600);
  border: 1px solid var(--lagoon-100);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}}
.filter-drawer-title {{
  font-family: var(--font-title);
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-main);
  margin: 0;
  line-height: 1.2;
}}
.filter-drawer-sub {{
  font-size: 0.76rem;
  color: var(--text-muted);
  margin: 2px 0 0;
}}
.filter-drawer-close {{
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
.filter-drawer-close:hover {{
  color: var(--text-main);
  background: var(--border);
}}
.filter-drawer-body {{
  padding: 22px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
  flex: 1;
}}
.filter-group {{
  display: flex;
  flex-direction: column;
  gap: 8px;
}}
.filter-label {{
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-main);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}}
.filter-label svg {{
  color: var(--lagoon-600);
}}
.filter-drawer-select {{
  width: 100%;
  height: 44px;
  padding: 0 36px 0 14px;
  background: var(--bg-app);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-main);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%230284c7' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  outline: none;
  transition: var(--transition);
}}
.filter-drawer-select:focus {{
  border-color: var(--lagoon-600);
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
}}
.filter-drawer-status-box {{
  padding: 12px 14px;
  background: var(--lagoon-50);
  border: 1px solid var(--lagoon-100);
  border-radius: var(--radius-md);
  margin-top: 4px;
}}
.filter-status-count {{
  display: flex;
  align-items: baseline;
  gap: 8px;
}}
.count-highlight {{
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--lagoon-700);
  font-family: var(--font-title);
}}
.count-subtext {{
  font-size: 0.82rem;
  color: var(--lagoon-700);
  font-weight: 600;
}}
.filter-drawer-footer {{
  padding: 16px 22px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 10px;
  background: var(--bg-hover);
}}
.btn-drawer-reset {{
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: var(--bg-card-solid);
  border: 1px solid var(--border);
  color: var(--text-muted);
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: var(--transition);
}}
.btn-drawer-reset:hover {{
  color: var(--coral-600);
  border-color: var(--coral-100);
  background: var(--coral-100);
}}
.btn-drawer-apply {{
  flex: 1;
  padding: 12px 18px;
  border-radius: var(--radius-md);
  background: var(--lagoon-600);
  border: none;
  color: #fff;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);
  transition: var(--transition);
}}
.btn-drawer-apply:hover {{
  background: var(--lagoon-700);
}}

/* ==========================================================================
   BOTTOM NAVIGATION BAR FIXE (MOBILE ONLY : RECHERCHER & FILTRES)
   ========================================================================== */
.bottom-bar {{
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: var(--bg-card-solid);
  border-top: 1px solid var(--border);
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.08);
  z-index: 100;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 0 16px;
}}
@media (max-width: 768px) {{
  .bottom-bar {{ display: flex; }}
}}
.b-tab {{
  display: flex;
  flex: 1;
  max-width: 180px;
  height: 42px;
  border-radius: var(--radius-md);
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 0.88rem;
  font-weight: 700;
  border: 1px solid transparent;
  background: var(--bg-hover);
  cursor: pointer;
  transition: var(--transition);
  padding: 0 14px;
}}
.b-tab:hover {{
  color: var(--text-main);
}}
.b-tab.active, .b-tab:active {{
  color: var(--lagoon-600);
  background: var(--lagoon-50);
  border-color: var(--lagoon-100);
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
  .results-meta-bar,
  .bottom-bar,
  .drawer-backdrop,
  .drawer,
  .filter-drawer-backdrop,
  .filter-drawer,
  .print-modal-backdrop,
  .loading-more,
  .empty-feedback,
  #themeToggle,
  .kbd-hint,
  .biz-actions,
  #bTabSearch,
  #bTabContact,
  #bTabFilters,
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
      <div class="hero-controls">
        <!-- SÉLECTEUR DE THÈMES & PALETTES ASSORTIES -->
        <div class="palette-picker-wrapper" id="palettePickerWrapper">
          <button class="icon-btn palette-btn" id="paletteToggle" type="button" title="Changer l'ambiance et les couleurs" aria-expanded="false" aria-haspopup="true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/>
              <circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/>
              <circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/>
              <circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/>
              <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>
            </svg>
            <span class="active-palette-dot" id="activePaletteDot"></span>
          </button>
          <div class="palette-dropdown" id="paletteDropdown" role="menu">
            <div class="palette-dropdown-header">
              <span class="palette-dropdown-title">Thèmes &amp; Couleurs</span>
              <span class="palette-dropdown-sub">6 palettes assorties</span>
            </div>
            <div class="palette-options-list">
              <button type="button" class="palette-option active" data-palette-val="lagoon">
                <span class="palette-swatch swatch-lagoon"></span>
                <span class="palette-name">Lagon de Paea</span>
                <span class="palette-check">✓</span>
              </button>
              <button type="button" class="palette-option" data-palette-val="emerald">
                <span class="palette-swatch swatch-emerald"></span>
                <span class="palette-name">Émeraude Tiare</span>
                <span class="palette-check">✓</span>
              </button>
              <button type="button" class="palette-option" data-palette-val="sunset">
                <span class="palette-swatch swatch-sunset"></span>
                <span class="palette-name">Sunset Mara'a</span>
                <span class="palette-check">✓</span>
              </button>
              <button type="button" class="palette-option" data-palette-val="amethyst">
                <span class="palette-swatch swatch-amethyst"></span>
                <span class="palette-name">Perle Royale</span>
                <span class="palette-check">✓</span>
              </button>
              <button type="button" class="palette-option" data-palette-val="coral">
                <span class="palette-swatch swatch-coral"></span>
                <span class="palette-name">Corail Tuamotu</span>
                <span class="palette-check">✓</span>
              </button>
              <button type="button" class="palette-option" data-palette-val="sapphire">
                <span class="palette-swatch swatch-sapphire"></span>
                <span class="palette-name">Océan Saphir</span>
                <span class="palette-check">✓</span>
              </button>
            </div>
          </div>
        </div>

        <!-- BOUTON BASCULE CLAIR / SOMBRE -->
        <button class="icon-btn" id="themeToggle" type="button" title="Changer de mode (Clair / Nuit)">
          <svg class="sun-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/></svg>
          <svg class="moon-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="display:none;"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>
      </div>
    </div>
    <h1>Répertoire des entreprises et patentés</h1>
  </div>
</header>

<!-- MAIN WRAPPER -->
<main class="main-wrapper">

  <!-- RUBAN STATISTIQUES COMPACT (INTERACTIF - ALIGNÉ SUR 1 LIGNE HORIZONTALE MOBILE) -->
  <section class="stats-strip" aria-label="Statistiques clés">
    <button type="button" class="stat-pill active" id="cardTotal" data-filter="all" title="Afficher toutes les entités">
      <span class="stat-icon">🏢</span>
      <div class="stat-meta">
        <span class="stat-num" id="statTotalVal">{total_entries}</span>
        <span class="stat-txt">
          <span class="stat-label-long">Total entités</span>
          <span class="stat-label-short">Total</span>
        </span>
      </div>
    </button>

    <button type="button" class="stat-pill" id="cardSocietes" data-filter="societes" title="Filtrer uniquement les Sociétés">
      <span class="stat-icon" style="background:rgba(126, 34, 206, 0.1);color:#7e22ce;">⚖️</span>
      <div class="stat-meta">
        <span class="stat-num" id="statSocietesVal">{societes_count}</span>
        <span class="stat-txt">
          <span class="stat-label-long">Sociétés</span>
          <span class="stat-label-short">Sociétés</span>
        </span>
      </div>
    </button>

    <button type="button" class="stat-pill" id="cardPphy" data-filter="pphy" title="Filtrer uniquement les Patentés">
      <span class="stat-icon" style="background:rgba(217, 119, 6, 0.1);color:#d97706;">👤</span>
      <div class="stat-meta">
        <span class="stat-num" id="statPphyVal">{pphy_count}</span>
        <span class="stat-txt">
          <span class="stat-label-long">Patentés individuels</span>
          <span class="stat-label-short">Patentés</span>
        </span>
      </div>
    </button>

    <button type="button" class="stat-pill" id="cardDigital" data-filter="direct" title="Filtrer avec contacts directs vérifiés">
      <span class="stat-icon" style="background:rgba(5, 150, 105, 0.1);color:#059669;">⭐</span>
      <div class="stat-meta">
        <span class="stat-num" id="statDirectVal">{with_contact} <small class="stat-pct" style="font-size:0.75rem;font-weight:600;opacity:0.85;">({round((with_contact/total_entries)*100)}%)</small></span>
        <span class="stat-txt">
          <span class="stat-label-long">Contacts vérifiés</span>
          <span class="stat-label-short">Contacts</span>
        </span>
      </div>
    </button>
  </section>

  <!-- CONTROL PANEL : RECHERCHE UNIVERSELLE & ACTIONS -->
  <section class="control-panel">
    <div class="search-box">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      <input type="text" id="searchInput" class="search-input" placeholder="Rechercher une entreprise, un gérant, un PK, une activité, n° TAHITI…">
      <span class="kbd-hint">Ctrl K</span>
    </div>

    <!-- LIGNE DES 4 BOUTONS ALIGNÉS SUR LA MÊME LIGNE : TABLEAU, CARTES, FILTRES, IMPRIMER -->
    <div class="actions-row">
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
        <button class="filter-btn" id="btnToggleFilters" title="Filtrer par collège, forme juridique, PK, contact...">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
          <span>Filtres</span>
          <span class="filter-count-badge" id="filterActiveBadge" style="display:none;">0</span>
        </button>
        <button class="print-btn" id="btnPrintList" title="Imprimer la sélection filtrée (Tableau ou Cartes)">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg>
          <span>Imprimer</span>
        </button>
      </div>
    </div>

    <!-- RÉSULTATS & STATUT DE SÉLECTION -->
    <div class="results-meta-bar">
      <div class="results-count-text">
        <span><strong id="resultCount">{total_entries}</strong> résultats affichés</span>
        <span id="activeFiltersSummaryChip" class="filter-summary-chip" style="display:none;">
          <span id="activeFiltersSummaryText">0 filtre</span>
          <button type="button" id="btnClearQuickFilters" title="Effacer tous les filtres">✕</button>
        </span>
      </div>
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

<!-- BOTTOM NAVIGATION BAR (MOBILE ONLY - RECHERCHER & FILTRES UNIQUEMENT) -->
<nav class="bottom-bar">
  <button class="b-tab active" id="bTabSearch">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
    <span>Rechercher</span>
  </button>
  <button class="b-tab" id="bTabFilters">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
    <span>Filtres</span>
  </button>
</nav>

<!-- TIROIR DE FILTRES GLISSANT (DRAWER / FLYOUT) -->
<div class="filter-drawer-backdrop" id="filterDrawerBackdrop"></div>
<aside class="filter-drawer" id="filterDrawer" aria-hidden="true" role="dialog" aria-label="Filtres de sélection">
  <div class="filter-drawer-head">
    <div class="filter-drawer-title-group">
      <div class="filter-drawer-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
      </div>
      <div>
        <h2 class="filter-drawer-title">Filtres de sélection</h2>
        <p class="filter-drawer-sub">Affinez selon vos besoins</p>
      </div>
    </div>
    <button class="filter-drawer-close" id="filterDrawerClose" title="Fermer le tiroir de filtres">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
    </button>
  </div>

  <div class="filter-drawer-body">
    <!-- Groupe 1 : Collège d'activité -->
    <div class="filter-group">
      <label class="filter-label" for="filterCat">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="14" x="2" y="7" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
        <span>Collège d'activité</span>
      </label>
      <select id="filterCat" class="filter-drawer-select">
        <option value="">Tous les collèges (4)</option>
        <option value="COMMERCE">Commerce</option>
        <option value="INDUSTRIE">Industrie</option>
        <option value="MÉTIER">Métier</option>
        <option value="SERVICE">Service</option>
        <option value="INSTITUTION">Institutions</option>
      </select>
    </div>

    <!-- Groupe 2 : Forme juridique -->
    <div class="filter-group">
      <label class="filter-label" for="filterForm">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        <span>Forme juridique</span>
      </label>
      <select id="filterForm" class="filter-drawer-select">
        <option value="">Toutes les formes</option>
        <option value="PPHY">Patentés (PPHY)</option>
        <option value="SARL">SARL</option>
        <option value="SAS">SAS / SASU</option>
        <option value="SCI">SCI</option>
        <option value="EURL">EURL</option>
        <option value="SCP">SCP</option>
      </select>
    </div>

    <!-- Groupe 3 : Secteur / Repère Kilométrique (PK) -->
    <div class="filter-group">
      <label class="filter-label">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
        <span>Secteur / Repère Kilométrique (PK)</span>
      </label>
      <div class="pk-drawer-grid" id="pkRibbon">
        <button type="button" class="pk-pill active" data-pk="">Tout Paea (PK 18 à 28)</button>
        <button type="button" class="pk-pill" data-pk="18">PK 18 – 19 (Papehue)</button>
        <button type="button" class="pk-pill" data-pk="20">PK 20 – 21 (Tiapa / Mairie)</button>
        <button type="button" class="pk-pill" data-pk="22">PK 22 – 23 (Orofero / Arahurahu)</button>
        <button type="button" class="pk-pill" data-pk="24">PK 24 – 25 (Vaiterupe)</button>
        <button type="button" class="pk-pill" data-pk="26">PK 26 – 28 (Mara'a / Pahiarepo)</button>
      </div>
    </div>

    <!-- Groupe 4 : Canaux de contact public -->
    <div class="filter-group">
      <label class="filter-label" for="filterContact">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
        <span>Disponibilité contact</span>
      </label>
      <select id="filterContact" class="filter-drawer-select">
        <option value="">Tous les contacts ({total_entries})</option>
        <option value="with">⭐ Avec contact direct vérifié ({with_contact})</option>
        <option value="tel">📞 Avec ligne téléphonique</option>
        <option value="web_mail">🌐 Avec e-mail, site ou réseaux</option>
        <option value="alert">⚠️ Avec statut particulier ({alert_status})</option>
        <option value="without">Sans contact</option>
      </select>
    </div>

    <!-- Statut en direct dans le tiroir -->
    <div class="filter-drawer-status-box">
      <div class="filter-status-count">
        <span id="filterDrawerCount" class="count-highlight">{total_entries}</span>
        <span class="count-subtext">entités correspondent à ces filtres</span>
      </div>
    </div>
  </div>

  <div class="filter-drawer-footer">
    <button type="button" id="btnResetFilters" class="btn-drawer-reset" title="Réinitialiser tous les filtres">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
      <span>Effacer</span>
    </button>
    <button type="button" id="btnApplyFilters" class="btn-drawer-apply">
      <span>Appliquer (<span id="filterDrawerApplyCount">{total_entries}</span>)</span>
    </button>
  </div>
</aside>

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
  updateFilterActiveIndicators();
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

  resetDrawerTransform();
  const dBody = $('drawerSheet').querySelector('.drawer-body');
  if(dBody) dBody.scrollTop = 0;

  $('drawerBackdrop').classList.add('open');
  $('drawerSheet').classList.add('open');
  $('drawerSheet').setAttribute('aria-hidden', 'false');
}}

function resetDrawerTransform() {{
  const sheet = $('drawerSheet');
  const backdrop = $('drawerBackdrop');
  if(sheet) {{
    sheet.style.transform = '';
    sheet.style.transition = '';
  }}
  if(backdrop) {{
    backdrop.style.opacity = '';
    backdrop.style.transition = '';
  }}
}}

function closeDetails() {{
  resetDrawerTransform();
  $('drawerBackdrop').classList.remove('open');
  $('drawerSheet').classList.remove('open');
  $('drawerSheet').setAttribute('aria-hidden', 'true');
  activeItem = null;
}}

// Bouton fermer (croix) toujours visible et actif
$('drawerClose').addEventListener('click', closeDetails);
$('drawerBackdrop').addEventListener('click', closeDetails);

// ==========================================================================
// FERMETURE PAR GLISSEMENT / SLIDE VERS LE BAS SUR MOBILE (SWIPE TO DISMISS)
// ==========================================================================
const drawerSheetEl = $('drawerSheet');
const drawerBackdropEl = $('drawerBackdrop');
let dTouchStartY = 0;
let dTouchStartX = 0;
let dTouchCurrentY = 0;
let isDraggingDrawerSheet = false;
let canDragDrawerSheet = false;

drawerSheetEl.addEventListener('touchstart', (e) => {{
  if (window.innerWidth > 640) return; // Uniquement en affichage mobile
  if (e.touches.length !== 1) return;

  const target = e.target;
  const bodyEl = drawerSheetEl.querySelector('.drawer-body');
  
  // Autoriser le slide si on touche la poignée, l'en-tête, ou si le scroll interne est tout en haut
  const isTopArea = target.closest('.drawer-handle, .drawer-head') !== null;
  const isBodyAtTop = bodyEl ? bodyEl.scrollTop <= 2 : true;

  if (isTopArea || isBodyAtTop) {{
    canDragDrawerSheet = true;
    isDraggingDrawerSheet = false;
    dTouchStartY = e.touches[0].clientY;
    dTouchStartX = e.touches[0].clientX;
    dTouchCurrentY = dTouchStartY;
  }} else {{
    canDragDrawerSheet = false;
  }}
}}, {{ passive: true }});

drawerSheetEl.addEventListener('touchmove', (e) => {{
  if (!canDragDrawerSheet || window.innerWidth > 640) return;
  if (e.touches.length !== 1) return;

  const curY = e.touches[0].clientY;
  const curX = e.touches[0].clientX;
  const diffY = curY - dTouchStartY;
  const diffX = curX - dTouchStartX;

  // Si l'utilisateur glisse vers le bas et que le mouvement est vertical
  if (diffY > 8 && Math.abs(diffY) > Math.abs(diffX) * 1.1) {{
    isDraggingDrawerSheet = true;
    dTouchCurrentY = curY;

    // Déplacement immédiat du modal vers le bas au doigt
    drawerSheetEl.style.transition = 'none';
    drawerSheetEl.style.transform = `translateY(${{diffY}}px)`;

    // Atténuation fluide de l'arrière-plan
    const progress = Math.min(diffY / 280, 1);
    drawerBackdropEl.style.transition = 'none';
    drawerBackdropEl.style.opacity = (1 - progress * 0.75).toString();

    // Empêcher le défilement parasite de la page
    if (e.cancelable) e.preventDefault();
  }}
}}, {{ passive: false }});

function finishDrawerDrag() {{
  if (!canDragDrawerSheet) return;
  canDragDrawerSheet = false;

  if (isDraggingDrawerSheet) {{
    isDraggingDrawerSheet = false;
    const totalDiffY = dTouchCurrentY - dTouchStartY;

    // Seuil de fermeture : si glissé vers le bas de plus de 80px
    if (totalDiffY > 80) {{
      drawerSheetEl.style.transition = 'transform 0.22s cubic-bezier(0.16, 1, 0.3, 1)';
      drawerBackdropEl.style.transition = 'opacity 0.22s ease';
      drawerSheetEl.style.transform = 'translateY(100%)';
      drawerBackdropEl.style.opacity = '0';
      setTimeout(() => {{
        closeDetails();
        resetDrawerTransform();
      }}, 220);
    }} else {{
      // Rebond doux vers la position ouverte si le glissement est insuffisant
      drawerSheetEl.style.transition = 'transform 0.22s cubic-bezier(0.16, 1, 0.3, 1)';
      drawerBackdropEl.style.transition = 'opacity 0.22s ease';
      drawerSheetEl.style.transform = 'translateY(0)';
      drawerBackdropEl.style.opacity = '1';
      setTimeout(() => {{
        resetDrawerTransform();
      }}, 220);
    }}
  }}
}}

drawerSheetEl.addEventListener('touchend', finishDrawerDrag, {{ passive: true }});
drawerSheetEl.addEventListener('touchcancel', finishDrawerDrag, {{ passive: true }});

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

function resetAllFilters() {{
  $('searchInput').value = '';
  $('filterCat').value = '';
  $('filterForm').value = '';
  $('filterContact').value = '';
  document.querySelectorAll('.pk-pill').forEach((p, idx) => p.classList.toggle('active', idx === 0));
  document.querySelectorAll('.stat-pill').forEach((c, idx) => c.classList.toggle('active', idx === 0));
  sortKey = 'name';
  sortDir = 1;
  applyFilters();
}}

$('btnResetFilters').addEventListener('click', resetAllFilters);
const btnClearChip = $('btnClearQuickFilters');
if(btnClearChip) {{
  btnClearChip.addEventListener('click', resetAllFilters);
}}

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

// ==========================================================================
// GESTION DU TIROIR DE FILTRES LATÉRAL (DRAWER & FERMETURE CLIC EXTÉRIEUR)
// ==========================================================================
let isFilterDrawerOpen = false;

function openFilterDrawer() {{
  isFilterDrawerOpen = true;
  closeDetails();
  closePrintModal();
  $('filterDrawerBackdrop').classList.add('open');
  $('filterDrawer').classList.add('open');
  $('filterDrawer').setAttribute('aria-hidden', 'false');
  updateFilterDrawerCounts();
}}

function closeFilterDrawer() {{
  if(!isFilterDrawerOpen) return;
  isFilterDrawerOpen = false;
  $('filterDrawerBackdrop').classList.remove('open');
  $('filterDrawer').classList.remove('open');
  $('filterDrawer').setAttribute('aria-hidden', 'true');
}}

function updateFilterDrawerCounts() {{
  const c = filtered.length.toLocaleString('fr-FR');
  const countEl = $('filterDrawerCount');
  const applyCountEl = $('filterDrawerApplyCount');
  if(countEl) countEl.textContent = c;
  if(applyCountEl) applyCountEl.textContent = c;
}}

function updateFilterActiveIndicators() {{
  let activeCount = 0;
  const cat = $('filterCat').value;
  const form = $('filterForm').value;
  const contact = $('filterContact').value;
  const pkSelected = document.querySelector('.pk-pill.active')?.dataset.pk || '';

  if(cat) activeCount++;
  if(form) activeCount++;
  if(contact) activeCount++;
  if(pkSelected) activeCount++;

  const badge = $('filterActiveBadge');
  const btnToggle = $('btnToggleFilters');
  const summaryChip = $('activeFiltersSummaryChip');
  const summaryText = $('activeFiltersSummaryText');

  if(activeCount > 0) {{
    badge.textContent = activeCount;
    badge.style.display = 'inline-flex';
    btnToggle.classList.add('has-active-filters');
    if(summaryChip && summaryText) {{
      summaryText.textContent = `${{activeCount}} filtre${{activeCount > 1 ? 's' : ''}} actif${{activeCount > 1 ? 's' : ''}}`;
      summaryChip.style.display = 'inline-flex';
    }}
  }} else {{
    badge.style.display = 'none';
    btnToggle.classList.remove('has-active-filters');
    if(summaryChip) summaryChip.style.display = 'none';
  }}

  updateFilterDrawerCounts();
}}

// OUVERTURE PAR LES BOUTONS FILTRES
$('btnToggleFilters').addEventListener('click', (e) => {{
  e.stopPropagation();
  if(isFilterDrawerOpen) {{
    closeFilterDrawer();
  }} else {{
    openFilterDrawer();
  }}
}});

const btnCompact = $('btnOpenFiltersCompact');
if(btnCompact) {{
  btnCompact.addEventListener('click', (e) => {{
    e.stopPropagation();
    openFilterDrawer();
  }});
}}

// FERMETURE PAR CROIX, BOUTON APPLIQUER OU BACKDROP
$('filterDrawerClose').addEventListener('click', closeFilterDrawer);
$('btnApplyFilters').addEventListener('click', closeFilterDrawer);
$('filterDrawerBackdrop').addEventListener('click', closeFilterDrawer);

// FERMETURE AUTOMATIQUE DÈS QU'ON CLIQUE EN DEHORS DU TIROIR
document.addEventListener('click', (e) => {{
  if(!isFilterDrawerOpen) return;
  const drawer = $('filterDrawer');
  const btnToggle = $('btnToggleFilters');
  const btnCompactEl = $('btnOpenFiltersCompact');
  const bTab = $('bTabFilters');
  
  const clickedInsideDrawer = drawer && drawer.contains(e.target);
  const clickedOnTrigger = (btnToggle && btnToggle.contains(e.target)) || 
                           (btnCompactEl && btnCompactEl.contains(e.target)) ||
                           (bTab && bTab.contains(e.target));

  if(!clickedInsideDrawer && !clickedOnTrigger) {{
    closeFilterDrawer();
  }}
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
    closeFilterDrawer();
    closePaletteDropdown();
  }}
}});

// ==========================================================================
// GESTION DU SYSTÈME DE THÈMES & PALETTES DE COULEURS ASSORTIES
// ==========================================================================
let isPaletteOpen = false;

function openPaletteDropdown() {{
  isPaletteOpen = true;
  $('paletteDropdown').classList.add('open');
  $('paletteToggle').setAttribute('aria-expanded', 'true');
}}

function closePaletteDropdown() {{
  if(!isPaletteOpen) return;
  isPaletteOpen = false;
  $('paletteDropdown').classList.remove('open');
  $('paletteToggle').setAttribute('aria-expanded', 'false');
}}

const paletteAccentMap = {{
  lagoon: '#0284c7',
  emerald: '#059669',
  sunset: '#ea580c',
  amethyst: '#7c3aed',
  coral: '#e11d48',
  sapphire: '#2563eb'
}};

function applyPalette(palName) {{
  if(!paletteAccentMap[palName]) palName = 'lagoon';
  document.documentElement.setAttribute('data-palette', palName);
  localStorage.setItem('paea_palette', palName);

  document.querySelectorAll('.palette-option').forEach(opt => {{
    opt.classList.toggle('active', opt.dataset.paletteVal === palName);
  }});

  const dot = $('activePaletteDot');
  if(dot) {{
    dot.style.background = paletteAccentMap[palName] || '#0284c7';
  }}
}}

// Initialiser la palette sauvegardée
const savedPalette = localStorage.getItem('paea_palette') || 'lagoon';
applyPalette(savedPalette);

// Clic bouton d'ouverture dropdown palette
$('paletteToggle').addEventListener('click', (e) => {{
  e.stopPropagation();
  if(isPaletteOpen) closePaletteDropdown();
  else openPaletteDropdown();
}});

// Clic sur une des options de palette
document.querySelectorAll('.palette-option').forEach(opt => {{
  opt.addEventListener('click', (e) => {{
    e.stopPropagation();
    applyPalette(opt.dataset.paletteVal);
    closePaletteDropdown();
  }});
}});

// Fermeture automatique au clic en dehors du sélecteur de palette
document.addEventListener('click', (e) => {{
  if(!isPaletteOpen) return;
  const wrap = $('palettePickerWrapper');
  if(wrap && !wrap.contains(e.target)) {{
    closePaletteDropdown();
  }}
}});

// GESTION DU MODE CLAIR / SOMBRE (LOCALSTORAGE)
const themeToggle = $('themeToggle');
const savedTheme = localStorage.getItem('paea_theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);

themeToggle.addEventListener('click', () => {{
  const cur = document.documentElement.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('paea_theme', next);
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

// BOTTOM NAVIGATION BAR MOBILE (RECHERCHER ET FILTRES)
if($('bTabSearch')) {{
  $('bTabSearch').addEventListener('click', () => {{
    $('searchInput').focus();
    window.scrollTo({{ top: $('searchInput').offsetTop - 60, behavior: 'smooth' }});
  }});
}}
if($('bTabFilters')) {{
  $('bTabFilters').addEventListener('click', () => {{
    openFilterDrawer();
  }});
}}

// DÉMARRAGE INITIAL
sortData();
render(false);
updateFilterActiveIndicators();
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
