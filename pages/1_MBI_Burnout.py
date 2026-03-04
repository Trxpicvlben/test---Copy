# ============================================================
# YODAN ANALYTICS — 1_MBI_Burnout.py
# ============================================================
import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from io import BytesIO

st.set_page_config(
    page_title="MBI Burnout - YODAN Analytics",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
    '<style>'
    'html,body,[class*="css"]{font-family:Inter,sans-serif!important}'
    '.main{background:#f1f4f9!important}'
    '.block-container{padding:1.5rem 2rem!important;max-width:1300px!important}'
    '#MainMenu,footer,header{visibility:hidden}'
    '.stTabs [data-baseweb="tab-list"]{gap:8px;background:transparent;padding:4px 0 12px 0;border-bottom:none!important}'
    '.stTabs [data-baseweb="tab"]{height:44px;padding:0 24px;background:#f8fafc!important;border-radius:9px;'
    'border:1.5px solid #e2e8f0!important;color:#475569!important;font-weight:600;font-size:13px;'
    'box-shadow:none;transition:all 0.2s}'
    '.stTabs [data-baseweb="tab"] p{color:#475569!important}'
    '.stTabs [data-baseweb="tab"]:hover{border-color:#3b82f6!important;color:#1e40af!important}'
    '.stTabs [data-baseweb="tab"]:hover p{color:#1e40af!important}'
    '.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#1e40af,#3b82f6)!important;'
    'color:white!important;border-color:#1e40af!important;box-shadow:0 3px 10px rgba(30,64,175,0.25)!important}'
    '.stTabs [aria-selected="true"] p{color:white!important}'
    '.stTabs [data-baseweb="tab-highlight"]{display:none!important}'
    '.stTabs [data-baseweb="tab-border"]{display:none!important}'
    '.stButton>button{background:white!important;color:#1e40af!important;'
    'border:1.5px solid #bfdbfe!important;border-radius:10px!important;'
    'font-weight:600!important;font-size:13px!important;height:42px!important;transition:all 0.2s!important}'
    '.stButton>button:hover{background:#1e40af!important;color:white!important;border-color:#1e40af!important}'
    '.stDownloadButton>button{background:white!important;color:#1e40af!important;'
    'border:1.5px solid #bfdbfe!important;border-radius:10px!important;'
    'font-weight:600!important;font-size:13px!important;transition:all 0.2s!important}'
    '.stDownloadButton>button:hover{background:#1e40af!important;color:white!important}'
    'div[data-baseweb="select"]>div{background:white!important;border:1.5px solid #cbd5e1!important;'
    'border-radius:9px!important;color:#1e293b!important}'
    'div[data-baseweb="select"] span{color:#1e293b!important}'
    'div[data-baseweb="select"] input{color:#1e293b!important}'
    'div[data-baseweb="select"] *{color:#1e293b!important}'
    '.stSelectbox label{color:#1e293b!important;font-weight:600!important;font-size:13px!important}'
    '.stSelectbox p{color:#1e293b!important}'
    '[data-baseweb="select"] [data-testid="stMarkdownContainer"] p{color:#1e293b!important}'
    'div[data-baseweb="select"] div{color:#1e293b!important}'
    'ul[role="listbox"]{background:white!important;border:1px solid #e2e8f0!important;'
    'border-radius:10px!important;box-shadow:0 8px 24px rgba(0,0,0,0.11)!important}'
    'li[role="option"]{background:white!important;color:#1e293b!important;font-size:13px!important}'
    'li[role="option"] *{color:#1e293b!important}'
    'li[role="option"]:hover{background:#eff6ff!important;color:#1e40af!important}'
    'li[role="option"]:hover *{color:#1e40af!important}'
    'li[role="option"][aria-selected="true"]{background:#1e40af!important;color:white!important}'
    'li[role="option"][aria-selected="true"] *{color:white!important}'
    '[data-testid="collapsedControl"]{background:#1e40af!important;border-radius:0 8px 8px 0!important}'
    '[data-testid="collapsedControl"] svg{fill:white!important}'
    '.stTextInput>div>div>input{border:1.5px solid #cbd5e1!important;border-radius:9px!important;'
    'font-size:14px!important;color:#1e293b!important;background:white!important;padding:10px 14px!important}'
    '.stTextInput>div>div>input:focus{border-color:#3b82f6!important;background:white!important;'
    'box-shadow:0 0 0 3px rgba(59,130,246,0.15)!important}'
    '.stTextInput label{color:#1e293b!important;font-weight:600!important;font-size:13px!important}'
    '.stNumberInput>div>div>input{border:1.5px solid #cbd5e1!important;border-radius:9px!important;'
    'font-size:14px!important;color:#1e293b!important;background:white!important}'
    '.stNumberInput>div>div>input:focus{border-color:#3b82f6!important;background:white!important;'
    'box-shadow:0 0 0 3px rgba(59,130,246,0.15)!important}'
    '.stNumberInput label{color:#1e293b!important;font-weight:600!important;font-size:13px!important}'
    '.stNumberInput button{background:white!important;border-color:#cbd5e1!important;color:#1e40af!important}'
    '</style>',
    unsafe_allow_html=True
)

# ════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════
if 'mbi_df'           not in st.session_state: st.session_state['mbi_df']           = None
if 'mbi_nom'          not in st.session_state: st.session_state['mbi_nom']          = ''
if 'mbi_effectif'     not in st.session_state: st.session_state['mbi_effectif']     = None
if 'mbi_clean_log'    not in st.session_state: st.session_state['mbi_clean_log']    = ''
if 'mbi_matched_q'    not in st.session_state: st.session_state['mbi_matched_q']    = 0
if 'mbi_sidebar_bytes' not in st.session_state: st.session_state['mbi_sidebar_bytes'] = None
if 'mbi_sidebar_name'  not in st.session_state: st.session_state['mbi_sidebar_name']  = ''

MBI_COLS = ['mbi_q1','mbi_q2','mbi_q3','mbi_q4','mbi_q5','mbi_q6','mbi_q7',
            'mbi_q8','mbi_q9','mbi_q10','mbi_q11','mbi_q12','mbi_q13','mbi_q14',
            'mbi_q15','mbi_q16','mbi_q17','mbi_q18','mbi_q19','mbi_q20','mbi_q21','mbi_q22']

SEUIL_PCT = 5.0

# ════════════════════════════════════════════════════════════
# DICTIONNAIRE FUZZY — textes officiels des 22 questions MBI
# (utilisé pour renommer automatiquement des colonnes dont
#  l'intitulé ressemble à la question officielle)
# ════════════════════════════════════════════════════════════
MBI_QUESTION_TEXTS = {
    'mbi_q1':  "je me sens emotionnellement vide par mon travail",
    'mbi_q2':  "je me sens a bout a la fin de ma journee de travail",
    'mbi_q3':  "je me sens fatigue lorsque je me leve le matin et que j ai a affronter une autre journee de travail",
    'mbi_q4':  "je peux comprendre facilement ce que mes collaborateurs collegues ou clients ressentent",
    'mbi_q5':  "je sens que je m occupe de certains collaborateurs collegues ou clients de facon impersonnelle comme s ils etaient des objets",
    'mbi_q6':  "travailler avec des gens tout au long de la journee me demande beaucoup d efforts",
    'mbi_q7':  "je m occupe tres efficacement des problemes de mes collaborateurs collegues ou clients",
    'mbi_q8':  "je sens que je craque a cause de mon travail",
    'mbi_q9':  "j ai l impression a travers mon travail d avoir une influence positive sur les gens",
    'mbi_q10': "je suis devenue plus insensible aux gens depuis que j ai ce travail",
    'mbi_q11': "je crains que ce travail ne m endurcisse emotionnellement",
    'mbi_q12': "je me sens plein d energie",
    'mbi_q13': "je me sens frustre par mon travail",
    'mbi_q14': "je sens que je travaille trop dur dans mon boulot",
    'mbi_q15': "je ne me soucie pas vraiment de ce qui arrive a certains de mes collaborateurs collegues ou clients",
    'mbi_q16': "travailler en contact direct avec les gens me stresse trop",
    'mbi_q17': "j arrive facilement a creer une atmosphere detendue avec mes collaborateurs collegues ou clients",
    'mbi_q18': "je me sens ragaillardi lorsque dans mon travail j ai ete proche de collaborateurs collegues ou clients",
    'mbi_q19': "j ai accompli beaucoup de choses qui en valent la peine dans ce travail",
    'mbi_q20': "je me sens au bout du rouleau",
    'mbi_q21': "dans mon travail je traite les problemes emotionnels tres calmement",
    'mbi_q22': "j ai l impression que certains de mes collaborateurs collegues ou clients me rendent responsable de certains de leurs problemes",
}

# ════════════════════════════════════════════════════════════
# NORMALISATION TEXTE (pour le fuzzy match)
# ════════════════════════════════════════════════════════════
import re
import unicodedata

def _normalize_text(text: str) -> str:
    """Minuscule, sans accents, ponctuation → espace, espaces multiples fusionnés."""
    text = str(text).lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def _token_overlap_ratio(a: str, b: str) -> float:
    """Ratio de Jaccard sur les tokens (mots) entre deux textes normalisés."""
    sa = set(a.split())
    sb = set(b.split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

# ════════════════════════════════════════════════════════════
# FUZZY MATCH — renommage automatique des colonnes MBI
# ════════════════════════════════════════════════════════════
def fuzzy_rename_mbi_columns(df: pd.DataFrame,
                              threshold: float = 0.40) -> tuple:
    """
    Tente de renommer les colonnes d'un DataFrame vers les noms canoniques
    mbi_q1…mbi_q22 par similarité textuelle avec les questions officielles.

    Retourne (df_renamed, log_lines, matched_count).
    - threshold : ratio de Jaccard minimum pour accepter un match (0.40 = 40 % de tokens communs)
    """
    df       = df.copy()
    logs     = []
    renamed  = {}   # {ancien_nom: nouveau_nom}
    used_targets = set()   # évite qu'une même cible soit assignée deux fois

    # Colonnes déjà correctement nommées
    already_ok = [c for c in MBI_COLS if c in df.columns]
    for c in already_ok:
        used_targets.add(c)
        logs.append(f"✅ '{c}' déjà présente — aucun renommage nécessaire.")

    # Pour chaque colonne du fichier non encore mappée
    for col in df.columns:
        if col in used_targets or col in MBI_COLS:
            continue
        col_norm = _normalize_text(col)
        best_target = None
        best_score  = 0.0
        for target, ref_text in MBI_QUESTION_TEXTS.items():
            if target in used_targets:
                continue
            score = _token_overlap_ratio(col_norm, ref_text)
            if score > best_score:
                best_score  = score
                best_target = target
        if best_target and best_score >= threshold:
            renamed[col]   = best_target
            used_targets.add(best_target)
            logs.append(
                f"🔄 Fuzzy match '{col}' → '{best_target}' "
                f"(similarité Jaccard : {best_score:.2f})"
            )

    if renamed:
        df = df.rename(columns=renamed)

    # Compter les colonnes MBI trouvées après renommage
    matched = [c for c in MBI_COLS if c in df.columns]
    missing = [c for c in MBI_COLS if c not in df.columns]
    if missing:
        logs.append(f"⚠️  Questions MBI non détectées ({len(missing)}) : {', '.join(missing)}")
    logs.append(f"📊 Questions MBI détectées : {len(matched)}/22")

    return df, logs, len(matched)

# ════════════════════════════════════════════════════════════
# NETTOYAGE COMMUN — standardisation + fillna
# ════════════════════════════════════════════════════════════
# Colonnes socio-démographiques et modes de vie attendues dans MBI
_SOCIO_COLS_MBI = [
    'genre', 'age', 'anciennete', 'poids', 'taille',
    'situation_matrimoniale', 'pratique_sport', 'consommation_alcool',
    'tabagisme', 'maladie_chronique', 'handicap_physique', 'suivi_psychologique',
]

# Alias fréquents pour les colonnes clés (fuzzy renommage socio)
_SOCIO_ALIASES = {
    'genre':                   ['sexe', 'sex', 'gender', 'genre'],
    'age':                     ['age', 'âge', 'annee_naissance'],
    'anciennete':              ['anciennete', 'ancienneté', 'seniority', 'years_in_company'],
    'situation_matrimoniale':  ['situation_matrimoniale', 'situation matrimoniale',
                                'statut_marital', 'etat_civil'],
    'pratique_sport':          ['pratique_sport', 'pratique reguliere du sport',
                                'sport', 'activite_physique'],
    'consommation_alcool':     ['consommation_alcool', 'consommation reguliere d alcool',
                                'alcool', 'alcohol'],
    'tabagisme':               ['tabagisme', 'tabac', 'fumeur', 'smoking'],
    'maladie_chronique':       ['maladie_chronique', 'avez-vous une maladie chronique',
                                'maladie chronique', 'chronic'],
    'handicap_physique':       ['handicap_physique', 'avez-vous un handicap physique',
                                'handicap'],
    'suivi_psychologique':     ['suivi_psychologique',
                                'avez-vous ete suivi pour un probleme psychologique',
                                'psy', 'suivi_psy'],
}

# Valeurs binaires Oui/Non reconnues
_OUI_VALS = {'oui', 'yes', 'o', '1', 'true', 'vrai', 'y'}
_NON_VALS = {'non', 'no', 'n', '0', 'false', 'faux'}
# Valeurs genre reconnues
_HOMME_VALS = {'homme', 'h', 'm', 'male', 'masculin'}
_FEMME_VALS = {'femme', 'f', 'female', 'féminin', 'feminin'}


def clean_common_variables(df: pd.DataFrame) -> tuple:
    """
    Nettoyage et standardisation des variables communes (socio-démo + modes de vie).

    Étapes :
    1. Fuzzy renommage des colonnes socio vers les noms canoniques
    2. Standardisation genre → 'Homme' / 'Femme'
    3. Conversion numérique age / ancienneté / poids / taille
    4. Standardisation binaires (Oui/Non)
    5. fillna 'Non renseigné' sur toutes les colonnes non-MBI avec des NA restants

    Retourne (df_cleaned, log_lines).
    """
    df   = df.copy()
    logs = []

    # ── 1. Fuzzy renommage des colonnes socio ──────────────────
    col_norm_map = {_normalize_text(c): c for c in df.columns}
    for canonical, aliases in _SOCIO_ALIASES.items():
        if canonical in df.columns:
            continue  # déjà là
        for alias in aliases:
            alias_n = _normalize_text(alias)
            if alias_n in col_norm_map:
                old = col_norm_map[alias_n]
                if old != canonical:
                    df  = df.rename(columns={old: canonical})
                    logs.append(f"🔄 Colonne socio '{old}' → '{canonical}'")
                break

    # ── 2. Genre ───────────────────────────────────────────────
    if 'genre' in df.columns:
        before_na = df['genre'].isna().sum()
        def _std_genre(v):
            if pd.isna(v): return np.nan
            vl = _normalize_text(str(v))
            if vl in _HOMME_VALS: return 'Homme'
            if vl in _FEMME_VALS: return 'Femme'
            return np.nan
        df['genre'] = df['genre'].apply(_std_genre)
        after_na = df['genre'].isna().sum()
        converted = before_na - after_na  if after_na < before_na else 0
        logs.append(f"✅ Genre standardisé (Homme/Femme) — {after_na} valeurs non reconnues.")
        if converted:
            logs.append(f"   ↳ {converted} valeur(s) NaN récupérées.")

    # ── 3. Numériques ──────────────────────────────────────────
    for col in ['age', 'anciennete', 'poids', 'taille']:
        if col in df.columns:
            before = df[col].isna().sum()
            df[col] = pd.to_numeric(df[col], errors='coerce')
            after   = df[col].isna().sum()
            if after > before:
                logs.append(f"⚠️  '{col}' : {after-before} valeur(s) non numérique(s) → NaN.")
            else:
                logs.append(f"✅ '{col}' converti en numérique ({before} NaN initiaux).")

    # ── 4. Variables binaires Oui/Non ─────────────────────────
    bin_cols = ['pratique_sport', 'consommation_alcool', 'tabagisme',
                'maladie_chronique', 'handicap_physique', 'suivi_psychologique']
    for col in bin_cols:
        if col not in df.columns:
            continue
        def _std_bin(v):
            if pd.isna(v): return np.nan
            vl = _normalize_text(str(v))
            if vl in _OUI_VALS: return 'Oui'
            if vl in _NON_VALS: return 'Non'
            return np.nan
        df[col] = df[col].apply(_std_bin)
        na_count = df[col].isna().sum()
        logs.append(f"✅ '{col}' standardisé (Oui/Non) — {na_count} non reconnu(s).")

    # ── 5. fillna 'Non renseigné' sur toutes les colonnes ─────
    #    (sauf colonnes MBI numériques et colonnes purement numériques)
    numeric_protected = set(MBI_COLS) | {'age', 'anciennete', 'poids', 'taille', 'imc',
                                          'ee_score', 'dp_score', 'pa_score'}
    filled_cols = []
    for col in df.columns:
        if col in numeric_protected:
            continue
        na_count = df[col].isna().sum()
        if na_count > 0:
            df[col] = df[col].fillna('Non renseigné')
            filled_cols.append(f"'{col}' ({na_count} valeur(s))")
    if filled_cols:
        logs.append(f"🔲 fillna 'Non renseigné' appliqué sur : {', '.join(filled_cols)}")
    else:
        logs.append("✅ Aucun NA restant à remplir sur les colonnes catégorielles.")

    return df, logs

# ════════════════════════════════════════════════════════════
# TRANCHES INTELLIGENTES
# ════════════════════════════════════════════════════════════
def compute_tranche_age(df):
    n         = len(df)
    threshold = n * SEUIL_PCT / 100
    fuse_low  = (df['age'] <= 20).sum() < threshold
    fuse_high = (df['age'] >= 61).sum() < threshold

    def assign(age):
        if fuse_low and fuse_high:
            if age <= 30: return '16-30 ans'
            elif age <= 40: return '31-40 ans'
            elif age <= 50: return '41-50 ans'
            else:           return '51-70 ans'
        elif fuse_low:
            if age <= 30: return '16-30 ans'
            elif age <= 40: return '31-40 ans'
            elif age <= 50: return '41-50 ans'
            elif age <= 60: return '51-60 ans'
            else:           return '61 ans et plus'
        elif fuse_high:
            if age <= 20: return '20 ans et moins'
            elif age <= 30: return '21-30 ans'
            elif age <= 40: return '31-40 ans'
            elif age <= 50: return '41-50 ans'
            else:           return '51-70 ans'
        else:
            if age <= 20: return '20 ans et moins'
            elif age <= 30: return '21-30 ans'
            elif age <= 40: return '31-40 ans'
            elif age <= 50: return '41-50 ans'
            elif age <= 60: return '51-60 ans'
            else:           return '61 ans et plus'

    if   fuse_low and fuse_high: cats = ['16-30 ans','31-40 ans','41-50 ans','51-70 ans']
    elif fuse_low:                cats = ['16-30 ans','31-40 ans','41-50 ans','51-60 ans','61 ans et plus']
    elif fuse_high:               cats = ['20 ans et moins','21-30 ans','31-40 ans','41-50 ans','51-70 ans']
    else:                         cats = ['20 ans et moins','21-30 ans','31-40 ans','41-50 ans','51-60 ans','61 ans et plus']

    df['tranche_age'] = pd.Categorical(df['age'].apply(assign), categories=cats, ordered=True)
    return df

def compute_tranche_anciennete(df):
    n         = len(df)
    threshold = n * SEUIL_PCT / 100
    fuse_high = (df['anciennete'] >= 21).sum() < threshold

    def assign(anc):
        if fuse_high:
            if anc <= 2:  return '0-2 ans'
            elif anc <= 5:  return '3-5 ans'
            elif anc <= 10: return '6-10 ans'
            else:           return '11 ans et plus'
        else:
            if anc <= 2:  return '0-2 ans'
            elif anc <= 5:  return '3-5 ans'
            elif anc <= 10: return '6-10 ans'
            elif anc <= 20: return '11-20 ans'
            else:           return '21 ans et plus'

    cats = ['0-2 ans','3-5 ans','6-10 ans','11 ans et plus'] if fuse_high \
           else ['0-2 ans','3-5 ans','6-10 ans','11-20 ans','21 ans et plus']

    df['tranche_anciennete'] = pd.Categorical(df['anciennete'].apply(assign), categories=cats, ordered=True)
    return df

# ════════════════════════════════════════════════════════════
# TRAITEMENT DU DATAFRAME
# ════════════════════════════════════════════════════════════
def process_df(raw):
    df   = raw.copy()
    q_ee = ['mbi_q1','mbi_q2','mbi_q3','mbi_q6','mbi_q8','mbi_q13','mbi_q14','mbi_q16','mbi_q20']
    q_dp = ['mbi_q5','mbi_q10','mbi_q11','mbi_q15','mbi_q22']
    q_pa = ['mbi_q4','mbi_q7','mbi_q9','mbi_q12','mbi_q17','mbi_q18','mbi_q19','mbi_q21']
    df['ee_score'] = df[q_ee].sum(axis=1)
    df['dp_score'] = df[q_dp].sum(axis=1)
    df['pa_score'] = df[q_pa].sum(axis=1)

    def cat_ee(s): return 'Faible' if s<=16 else ('Modéré' if s<=26 else 'Élevé')
    def cat_dp(s): return 'Faible' if s<=6  else ('Modéré' if s<=12 else 'Élevé')
    def cat_pa(s): return 'Élevé'  if s>=39 else ('Modéré' if s>=32 else 'Faible')
    df['ee_categorie'] = df['ee_score'].apply(cat_ee)
    df['dp_categorie'] = df['dp_score'].apply(cat_dp)
    df['pa_categorie'] = df['pa_score'].apply(cat_pa)

    def cls_burnout(r):
        ee, dp, pa = r['ee_categorie'], r['dp_categorie'], r['pa_categorie']
        if ee=='Faible' and dp=='Faible' and pa=='Élevé': return 'Pas de burnout'
        if (ee=='Élevé' and dp=='Élevé') or (ee=='Élevé' and pa=='Faible'): return 'Burnout avéré'
        return 'Pré-burnout'
    df['niveau_burnout'] = df.apply(cls_burnout, axis=1)

    if 'age' in df.columns:
        df = compute_tranche_age(df)
    if 'anciennete' in df.columns:
        df = compute_tranche_anciennete(df)
    if 'poids' in df.columns and 'taille' in df.columns:
        df['imc'] = (df['poids'] / ((df['taille']/100)**2)).round(1)
        def cat_imc(v):
            if v<18.5: return 'Maigreur'
            if v<25:   return 'Normal'
            if v<30:   return 'Surpoids'
            return 'Obésité'
        df['imc_categorie'] = df['imc'].apply(cat_imc)
    return df

# ════════════════════════════════════════════════════════════
# HELPERS UI
# ════════════════════════════════════════════════════════════
def sec(label):
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:22px 0 14px;">'
        f'<div style="width:4px;height:20px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
        f'<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.3px;text-transform:uppercase;">{label}</span>'
        f'</div>', unsafe_allow_html=True)

def kpi(icon, icon_color, icon_bg, bar_color, value, unit, sub, label):
    sub_html = f'<div style="font-size:11px;color:#94a3b8;margin-top:2px;">{sub}</div>' if sub else ''
    return (
        f'<div style="background:white;border-radius:12px;padding:16px 14px 12px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.05),0 4px 12px rgba(0,0,0,0.06);'
        f'border:1px solid #e8edf5;border-top:3px solid {bar_color};height:140px;">'
        f'<div style="width:32px;height:32px;background:{icon_bg};border-radius:8px;'
        f'display:flex;align-items:center;justify-content:center;margin-bottom:8px;">'
        f'<i class="{icon}" style="color:{icon_color};font-size:13px;"></i></div>'
        f'<div style="font-size:28px;font-weight:700;color:#1e293b;line-height:1;letter-spacing:-0.5px;">'
        f'{value}<span style="font-size:13px;font-weight:400;color:#64748b;">{unit}</span></div>'
        f'{sub_html}'
        f'<div style="font-size:10px;font-weight:600;color:#64748b;letter-spacing:0.7px;'
        f'text-transform:uppercase;margin-top:6px;">{label}</div>'
        f'</div>'
    )

# ════════════════════════════════════════════════════════════
# TOPBAR YODAN
# ════════════════════════════════════════════════════════════
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)
_col_top, _col_back = st.columns([9, 1])
with _col_top:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;background:white;border-radius:12px;'
        'padding:14px 24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06),'
        '0 4px 12px rgba(30,64,175,0.08);border:1px solid #e8edf5;">'
        '<div style="width:38px;height:38px;background:linear-gradient(135deg,#dc2626,#ef4444);'
        'border-radius:10px;display:flex;align-items:center;justify-content:center;">'
        '<i class="fas fa-fire" style="color:white;font-size:15px;"></i></div>'
        '<div>'
        '<div style="font-size:16px;font-weight:700;color:#1e293b;">MBI — Maslach Burnout Inventory</div>'
        '<div style="font-size:11px;color:#64748b;margin-top:1px;">Analyse du burnout professionnel · YODAN Analytics</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
with _col_back:
    st.write("")
    st.write("")
    if st.button("← Accueil", key="back_home_mbi", use_container_width=True):
        st.switch_page("app.py")

# ════════════════════════════════════════════════════════════
# IMPORT SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("📂 Données")
    _mbi_sidebar_up = st.file_uploader(
        "Charger un fichier Excel ou CSV",
        type=["xlsx", "xls", "csv"],
        help="Glissez-déposez ou cliquez pour sélectionner votre fichier MBI.",
        key="mbi_sidebar_uploader",
    )

if _mbi_sidebar_up is not None:
    _b = _mbi_sidebar_up.read()
    if _b:
        st.session_state["mbi_sidebar_bytes"] = _b
        st.session_state["mbi_sidebar_name"]  = _mbi_sidebar_up.name

# ════════════════════════════════════════════════════════════
# SECTION IMPORT
# ════════════════════════════════════════════════════════════
_data_loaded = st.session_state['mbi_df'] is not None and st.session_state['mbi_nom']

if not _data_loaded:
    # Si un fichier a été chargé depuis la sidebar, pré-remplir l'uploader central
    _sidebar_preload = st.session_state.get('mbi_sidebar_bytes') is not None

    sec("Configuration de l'analyse")
    st.markdown(
        '<div style="background:white;border-radius:12px;padding:20px 24px 16px;'
        'box-shadow:0 1px 4px rgba(0,0,0,0.06);border:1px solid #e8edf5;margin-bottom:12px;">'
        '<div style="font-size:13px;font-weight:700;color:#1e293b;margin-bottom:14px;">'
        '<i class="fas fa-upload" style="color:#1e40af;margin-right:8px;"></i>'
        'Renseignez les informations ci-dessous pour démarrer l\'analyse</div>'
        '</div>',
        unsafe_allow_html=True
    )
    col_nom, col_eff, col_file, col_btn = st.columns([1.6, 1, 2, 0.9])
    with col_nom:
        nom_input = st.text_input("Nom de l'entreprise", value=st.session_state['mbi_nom'],
                                   placeholder="Ex : Pahaliah & Fils", key="input_nom")
    with col_eff:
        eff_input = st.number_input("Effectif total", min_value=1, value=100,
                                    step=1, key="input_effectif")
    with col_file:
        uploaded = st.file_uploader("Base de données MBI (CSV / Excel)", type=['csv','xlsx','xls'], key="upload_mbi")
        if uploaded is None and _sidebar_preload:
            st.caption(f"📎 Fichier sidebar prêt : **{st.session_state['mbi_sidebar_name']}**")
    with col_btn:
        st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
        lancer = st.button("🚀  Lancer", use_container_width=True, key="btn_lancer")

    if lancer:
        errors = []
        if not nom_input.strip(): errors.append("Veuillez saisir le nom de l'entreprise.")
        # Accepter soit l'uploader central, soit le fichier sidebar
        has_file = uploaded is not None or _sidebar_preload
        if not has_file: errors.append("Veuillez importer un fichier CSV ou Excel.")
        if errors:
            for e in errors: st.error(f"❌ {e}")
        else:
            try:
                # ── Lecture brute (priorité uploader central, sinon sidebar) ──
                if uploaded is not None:
                    ext = uploaded.name.rsplit('.', 1)[-1].lower()
                    if ext in ('xlsx', 'xls'):
                        raw = pd.read_excel(uploaded)
                    else:
                        try:
                            raw = pd.read_csv(uploaded, encoding='utf-8-sig')
                        except Exception:
                            uploaded.seek(0)
                            raw = pd.read_csv(uploaded, encoding='latin-1')
                else:
                    # Fichier depuis sidebar
                    _buf = io.BytesIO(st.session_state['mbi_sidebar_bytes'])
                    _fn  = st.session_state['mbi_sidebar_name'].lower()
                    if _fn.endswith(('.xlsx', '.xls')):
                        raw = pd.read_excel(_buf)
                    else:
                        for _enc in ('utf-8-sig', 'latin-1', 'cp1252'):
                            try:
                                _buf.seek(0)
                                raw = pd.read_csv(_buf, encoding=_enc)
                                break
                            except UnicodeDecodeError:
                                continue

                all_logs = []
                all_logs.append("═══ ÉTAPE 1 : Fuzzy match des questions MBI ═══")

                # ── Fuzzy match colonnes MBI ───────────────────────────
                raw, fuzzy_logs, matched_q_count = fuzzy_rename_mbi_columns(raw)
                all_logs.extend(fuzzy_logs)

                # ── Vérification des 22 questions après fuzzy ──────────
                manquantes = [c for c in MBI_COLS if c not in raw.columns]
                if manquantes:
                    cleaning_log = "\n".join(all_logs)
                    with st.expander("📋 Journal de nettoyage automatique", expanded=True):
                        st.text(cleaning_log)
                        st.write(f"Questions MBI détectées automatiquement : {matched_q_count}/22")
                    st.error(
                        f"❌ {len(manquantes)} question(s) MBI introuvable(s) après fuzzy match : "
                        f"`{'`, `'.join(manquantes)}`\n\n"
                        f"Vérifiez que les intitulés de colonnes correspondent aux 22 questions MBI."
                    )
                else:
                    # ── Nettoyage commun ───────────────────────────────
                    all_logs.append("")
                    all_logs.append("═══ ÉTAPE 2 : Nettoyage & standardisation des variables ═══")
                    raw, clean_logs = clean_common_variables(raw)
                    all_logs.extend(clean_logs)

                    # ── Traitement MBI (scores + catégories) ───────────
                    all_logs.append("")
                    all_logs.append("═══ ÉTAPE 3 : Calcul des scores MBI ═══")
                    processed = process_df(raw)
                    all_logs.append(f"✅ Scores EE / DP / PA calculés sur {len(processed)} répondants.")
                    all_logs.append(f"✅ Classification burnout appliquée (Pas de burnout / Pré-burnout / Burnout avéré).")

                    # ── Stockage en session ────────────────────────────
                    st.session_state['mbi_df']        = processed
                    st.session_state['mbi_nom']       = nom_input.strip()
                    st.session_state['mbi_effectif']  = int(eff_input)
                    st.session_state['mbi_clean_log'] = "\n".join(all_logs)
                    st.session_state['mbi_matched_q'] = matched_q_count
                    st.rerun()

            except Exception as ex:
                st.error(f"❌ Erreur lors de la lecture du fichier : {ex}")
    st.stop()

# ── Données chargées : badge compact + bouton reset ───────────
df  = st.session_state['mbi_df']
nom = st.session_state['mbi_nom']
total_entreprise = st.session_state['mbi_effectif'] or len(df)

col_badge, col_reset = st.columns([6, 1])
with col_badge:
    nd = nom.replace('&','&amp;')
    st.markdown(
        f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;'
        f'padding:9px 16px;margin-bottom:12px;display:flex;align-items:center;gap:10px;">'
        f'<i class="fas fa-check-circle" style="color:#16a34a;font-size:14px;"></i>'
        f'<span style="font-size:13px;color:#15803d;font-weight:600;">'
        f'Base chargée · {len(df)} analysés / {total_entreprise} employés · {nd}</span>'
        f'</div>',
        unsafe_allow_html=True
    )
with col_reset:
    if st.button("↺ Changer", key="btn_reset", use_container_width=True):
        st.session_state['mbi_df']            = None
        st.session_state['mbi_nom']           = ''
        st.session_state['mbi_effectif']      = None
        st.session_state['mbi_clean_log']     = ''
        st.session_state['mbi_matched_q']     = 0
        st.session_state['mbi_sidebar_bytes'] = None
        st.session_state['mbi_sidebar_name']  = ''
        st.rerun()

# ── Journal de nettoyage automatique ─────────────────────────
_clean_log   = st.session_state.get('mbi_clean_log', '')
_matched_q   = st.session_state.get('mbi_matched_q', 0)
_log_ok      = _matched_q == 22
_expander_icon = "✅" if _log_ok else "⚠️"
with st.expander(
    f"{_expander_icon} Journal de nettoyage automatique "
    f"({'Questions MBI complètes' if _log_ok else f'{_matched_q}/22 questions détectées'})",
    expanded=not _log_ok,
):
    # Compteur mis en avant
    col_jl, col_jr = st.columns([3, 1])
    with col_jl:
        if _clean_log:
            st.markdown(
                '<div style="font-family:monospace;font-size:0.8rem;'
                'background:#f8fafc;border-radius:6px;padding:10px 14px;'
                'border:1px solid #e2e8f0;max-height:320px;overflow-y:auto;">'
                + "".join(
                    f'<div style="padding:1px 0;color:{"#16a34a" if l.startswith("✅") else "#d97706" if l.startswith("⚠️") else "#1e40af" if l.startswith("🔄") else "#475569" if l.startswith("═") else "#1e293b"}">{l}</div>'
                    for l in _clean_log.split("\n")
                )
                + '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("Aucun log disponible.")
    with col_jr:
        q_color = "#16a34a" if _matched_q == 22 else "#d97706" if _matched_q >= 18 else "#dc2626"
        st.markdown(
            f'<div style="background:white;border-radius:10px;padding:16px 12px;'
            f'text-align:center;border:1px solid #e2e8f0;'
            f'box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
            f'<div style="font-size:11px;font-weight:700;color:#64748b;'
            f'text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">'
            f'Questions MBI<br>détectées</div>'
            f'<div style="font-size:42px;font-weight:700;color:{q_color};line-height:1;">'
            f'{_matched_q}<span style="font-size:18px;color:#94a3b8;">/22</span></div>'
            f'<div style="margin-top:8px;font-size:11px;color:{q_color};font-weight:600;">'
            f'{"✅ Complet" if _matched_q == 22 else "⚠️ Incomplet"}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════
# CALCULS
# ════════════════════════════════════════════════════════════
total_analyses = len(df)
total_analyses = len(df)
nb_f   = (df['genre']=='Femme').sum()  if 'genre' in df.columns else 0
nb_h   = (df['genre']=='Homme').sum()  if 'genre' in df.columns else 0
pct_f  = nb_f / total_analyses * 100
pct_h  = nb_h / total_analyses * 100
age_moy = int(round(df['age'].mean())) if 'age' in df.columns else 0

bc = df['niveau_burnout'].value_counts()
nb_pas   = bc.get('Pas de burnout', 0); pct_pas   = nb_pas   / total_analyses * 100
nb_pre   = bc.get('Pré-burnout',    0); pct_pre   = nb_pre   / total_analyses * 100
nb_avere = bc.get('Burnout avéré',  0); pct_avere = nb_avere / total_analyses * 100

# ════════════════════════════════════════════════════════════
# ONGLETS
# ════════════════════════════════════════════════════════════
onglet1, onglet2 = st.tabs(["  Informations générales", "  Résultats MBI Burnout"])

# ╔══════════════════════════════════════════════════════════╗
# ║  ONGLET 1                                               ║
# ╚══════════════════════════════════════════════════════════╝
with onglet1:

    sec("Vue d'ensemble de la population analysée")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(kpi("fas fa-users","#1e40af","#eff6ff","#3b82f6",
            f"{total_analyses/total_entreprise*100:.1f}","%",f"{total_analyses} analysés sur {total_entreprise}","Population analysée"), unsafe_allow_html=True)
    with c2:
        if nb_f > nb_h:
            st.markdown(kpi("fas fa-female","#7c3aed","#f5f3ff","#a78bfa",
                f"{pct_f:.1f}","%",f"{nb_f} collaboratrices","Femmes"), unsafe_allow_html=True)
        else:
            st.markdown(kpi("fas fa-male","#0369a1","#f0f9ff","#38bdf8",
                f"{pct_h:.1f}","%",f"{nb_h} collaborateurs","Hommes"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("far fa-calendar-alt","#0f766e","#f0fdfa","#2dd4bf",
            age_moy," ans","","Âge moyen"), unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    sec("Facteurs de risque santé")
    RISQUES_DATA = []
    if 'poids' in df.columns and 'taille' in df.columns:
        if 'imc' not in df.columns:
            df['imc'] = df['poids'] / ((df['taille']/100)**2)
        RISQUES_DATA.append(('<i class="fas fa-weight"></i>', "Obésité/Surpoids",
                             int((df['imc'] >= 25).sum())))
    for col_r, lbl_r, vals_r in [
        ('pratique_sport',    "Sédentarité (pas sport)",  ['non','0','false']),
        ('consommation_alcool',"Consommation alcool",      ['oui','1','true']),
        ('tabagisme',          "Consommation tabac",       ['oui','1','true']),
        ('maladie_chronique',  "Maladie chronique",        ['oui','1','true']),
    ]:
        if col_r in df.columns:
            n = int((df[col_r].astype(str).str.lower().isin(vals_r)).sum())
            RISQUES_DATA.append((f'<i class="fas fa-circle"></i>', lbl_r, n))

    if RISQUES_DATA:
        col_risk, _ = st.columns([1.1, 1])
        with col_risk:
            for icon_r, lbl_r, n_risk in RISQUES_DATA:
                pct_r = n_risk / total_analyses * 100
                st.markdown(
                    f'<div style="background:white;padding:12px 15px;border-radius:8px;'
                    f'margin-bottom:6px;box-shadow:0 2px 5px rgba(0,0,0,0.08);">'
                    f'<div style="color:#1e293b;font-weight:600;font-size:14px;">'
                    f'{icon_r}&nbsp; {lbl_r} : <span style="color:#ef4444;">{pct_r:.1f}%</span>'
                    f' ({n_risk} pers.)</div></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div style="height:8px;border-radius:4px;background:#16a34a;margin:-2px 0 12px 0;">'
                    f'<div style="height:8px;border-radius:4px;background:#ef4444;'
                    f'width:{min(pct_r,100):.1f}%;"></div></div>', unsafe_allow_html=True)
    else:
        st.info("ℹ️ Aucune variable de risque santé trouvée dans le fichier.")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    sec("Analyses univariées")

    BINARY_VARS_UNI = ['pratique_sport','consommation_alcool','tabagisme',
                       'maladie_chronique','handicap_physique','suivi_psychologique']
    VAR_OPTIONS_BASE = {
        "Genre":                  "genre",
        "Tranche d'âge":          "tranche_age",
        "Ancienneté":             "tranche_anciennete",
        "Situation matrimoniale": "situation_matrimoniale",
        "Pratique de sport":      "pratique_sport",
        "Consommation alcool":    "consommation_alcool",
        "Tabagisme":              "tabagisme",
        "Catégorie IMC":          "imc_categorie",
        "Maladie chronique":      "maladie_chronique",
        "Handicap physique":      "handicap_physique",
        "Suivi psychologique":    "suivi_psychologique",
    }
    VAR_OPTIONS = {"Sélectionner une variable": None}
    VAR_OPTIONS.update({k: v for k, v in VAR_OPTIONS_BASE.items() if v in df.columns})

    sel_label = st.selectbox("Choisir une variable à visualiser :", list(VAR_OPTIONS.keys()), key="uni_tab1")
    sel_col   = VAR_OPTIONS[sel_label]

    if sel_col and sel_col in df.columns:
        from matplotlib.patches import Patch
        counts_u = df[sel_col].value_counts()
        total_u  = counts_u.sum()
        pcts_u   = (counts_u / total_u * 100).round(1)

        if sel_col == 'genre':
            fig, ax = plt.subplots(figsize=(3.8, 3.2))
            fig.patch.set_facecolor('#f1f4f9'); ax.set_facecolor('#f1f4f9')
            color_map  = {'Femme':'#a78bfa','femme':'#a78bfa','F':'#a78bfa',
                          'Homme':'#38bdf8','homme':'#38bdf8','H':'#38bdf8'}
            dominant_g = pcts_u.idxmax()
            colors_g2  = [color_map.get(str(k),'#1e40af') if k==dominant_g else '#f1f4f9'
                          for k in pcts_u.index]
            wedges, _  = ax.pie(pcts_u.values, labels=None, colors=colors_g2,
                                startangle=90, wedgeprops=dict(edgecolor='white', linewidth=2))
            for wedge, (k, v) in zip(wedges, pcts_u.items()):
                if k == dominant_g:
                    angle = (wedge.theta1 + wedge.theta2) / 2
                    x = 0.55 * np.cos(np.radians(angle))
                    y = 0.55 * np.sin(np.radians(angle))
                    ax.text(x, y, f"{k}\n{v:.1f}%\n({counts_u[k]})",
                            ha='center', va='center', color='white',
                            fontsize=8, fontweight='bold', linespacing=1.3)
            ax.set_title(f"Répartition des Employés\nde l'Entreprise {nom}\nselon : {sel_label}",
                         fontsize=11, fontweight='bold', color='#1e293b', pad=10)
            plt.tight_layout()
            _, cc, _ = st.columns([1,1,1])
            with cc: st.pyplot(fig, use_container_width=False)

        elif sel_col in BINARY_VARS_UNI:
            fig, ax = plt.subplots(figsize=(3.8, 3.0))
            fig.patch.set_facecolor('#f1f4f9'); ax.set_facecolor('#f1f4f9')
            dominant    = pcts_u.idxmax()
            sizes, colors_b, explode = [], [], []
            for k, v in pcts_u.items():
                sizes.append(v)
                colors_b.append('#1e40af' if k==dominant else '#e2e8f0')
                explode.append(0.03 if k==dominant else 0)
            wedges, _ = ax.pie(sizes, labels=None, colors=colors_b, explode=explode,
                               startangle=90, wedgeprops=dict(edgecolor='white', linewidth=2))
            for wedge, (k, v) in zip(wedges, pcts_u.items()):
                if k == dominant:
                    angle = (wedge.theta1 + wedge.theta2) / 2
                    x = 0.55 * np.cos(np.radians(angle))
                    y = 0.55 * np.sin(np.radians(angle))
                    ax.text(x, y, f"{k}\n{v:.1f}%\n({counts_u[k]})",
                            ha='center', va='center', color='white',
                            fontsize=8, fontweight='bold', linespacing=1.3)
            minority   = [k for k in pcts_u.index if k != dominant][0]
            legend_el  = [Patch(facecolor='#1e40af', edgecolor='white', label=f"{dominant}"),
                          Patch(facecolor='#e2e8f0', edgecolor='#ccc',  label=f"{minority}")]
            ax.legend(handles=legend_el, loc='lower center',
                      bbox_to_anchor=(0.5,-0.12), ncol=2, fontsize=8, frameon=False)
            ax.set_title(f"Répartition des Employés\nde l'Entreprise {nom}\nselon : {sel_label}",
                         fontsize=11, fontweight='bold', color='#1e293b', pad=10)
            plt.tight_layout()
            _, cc, _ = st.columns([1,1,1])
            with cc: st.pyplot(fig, use_container_width=False)

        else:
            if sel_col == 'tranche_age' and hasattr(df['tranche_age'], 'cat'):
                order    = list(df['tranche_age'].cat.categories)
                counts_u = df[sel_col].value_counts().reindex(order).dropna()
                pcts_u   = (counts_u / total_u * 100).round(1)
            elif sel_col == 'tranche_anciennete' and hasattr(df['tranche_anciennete'], 'cat'):
                order    = list(df['tranche_anciennete'].cat.categories)
                counts_u = df[sel_col].value_counts().reindex(order).dropna()
                pcts_u   = (counts_u / total_u * 100).round(1)

            fig, ax  = plt.subplots(figsize=(8, 4))
            fig.patch.set_facecolor('#f1f4f9'); ax.set_facecolor('#f1f4f9')
            n_bars   = len(counts_u)
            cmap     = plt.cm.get_cmap('tab10', n_bars)
            colors_bar = [cmap(i) for i in range(n_bars)]
            bars = ax.bar(range(n_bars), pcts_u.values, color=colors_bar,
                          edgecolor='white', linewidth=2.5, alpha=0.9, width=0.6)
            max_v = pcts_u.max()
            for bar, lbl, pv, cv in zip(bars, counts_u.index, pcts_u.values, counts_u.values):
                h    = bar.get_height()
                text = f"{pv:.1f}%\n({int(cv)})"
                if h > max_v * 0.25:
                    # Barre assez haute : texte blanc à l'intérieur
                    ax.text(bar.get_x()+bar.get_width()/2, h/2, text,
                            ha='center', va='center', color='white',
                            fontsize=11, fontweight='bold', linespacing=1.2)
                else:
                    # Barre petite : texte noir au-dessus, bien espacé
                    ax.text(bar.get_x()+bar.get_width()/2, h+max_v*0.03, text,
                            ha='center', va='bottom', color='#1e293b',
                            fontsize=11, fontweight='bold', linespacing=1.2)
            ax.set_xticks(range(n_bars))
            ax.set_xticklabels(counts_u.index.astype(str), fontsize=12,
                               rotation=0 if n_bars<=3 else 30,
                               ha='right' if n_bars>3 else 'center')
            ax.set_ylabel('Pourcentage (%)', fontsize=14, fontweight='bold', color='#1e293b')
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cbd5e1'); ax.spines['bottom'].set_color('#cbd5e1')
            ax.set_ylim(0, max_v * 1.40)
            ax.set_title(f"Répartition des Employés\nde l'Entreprise {nom}\nselon : {sel_label}",
                         fontsize=14, fontweight='bold', color='#1e293b', pad=16)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='#f1f4f9')
        buf.seek(0)
        st.download_button("⬇  Télécharger le graphique (PNG)", buf,
                           f"univarie_{sel_col}.png", "image/png", key="dl_uni")
        plt.close()

# ╔══════════════════════════════════════════════════════════╗
# ║  ONGLET 2                                               ║
# ╚══════════════════════════════════════════════════════════╝
with onglet2:

    sec("Résultats de l'évaluation MBI")
    r1, r2, r3 = st.columns(3)
    kpi_s = ("background:white;border-radius:12px;padding:22px 16px;"
             "box-shadow:0 1px 3px rgba(0,0,0,0.06),0 4px 12px rgba(0,0,0,0.07);"
             "border:1px solid #e8edf5;height:150px;"
             "display:flex;flex-direction:column;justify-content:center;align-items:center;gap:5px;text-align:center;")
    with r1:
        st.markdown(
            f'<div style="{kpi_s}border-top:4px solid #16a34a;">'
            f'<div style="width:36px;height:36px;background:#f0fdf4;border-radius:9px;'
            f'display:flex;align-items:center;justify-content:center;margin-bottom:2px;">'
            f'<i class="fas fa-smile" style="color:#16a34a;font-size:16px;"></i></div>'
            f'<div style="font-size:36px;font-weight:700;color:#16a34a;line-height:1;">{pct_pas:.1f}'
            f'<span style="font-size:14px;font-weight:400;color:#94a3b8;">%</span></div>'
            f'<div style="font-size:11px;color:#94a3b8;">({nb_pas} pers.)</div>'
            f'<div style="font-size:11px;font-weight:700;color:#475569;letter-spacing:0.6px;text-transform:uppercase;">Pas de burnout</div>'
            f'</div>', unsafe_allow_html=True)
    with r2:
        st.markdown(
            f'<div style="{kpi_s}border-top:4px solid #d97706;">'
            f'<div style="width:36px;height:36px;background:#fffbeb;border-radius:9px;'
            f'display:flex;align-items:center;justify-content:center;margin-bottom:2px;">'
            f'<i class="fas fa-meh" style="color:#d97706;font-size:16px;"></i></div>'
            f'<div style="font-size:36px;font-weight:700;color:#d97706;line-height:1;">{pct_pre:.1f}'
            f'<span style="font-size:14px;font-weight:400;color:#94a3b8;">%</span></div>'
            f'<div style="font-size:11px;color:#94a3b8;">({nb_pre} pers.)</div>'
            f'<div style="font-size:11px;font-weight:700;color:#475569;letter-spacing:0.6px;text-transform:uppercase;">Pré-burnout</div>'
            f'</div>', unsafe_allow_html=True)
    with r3:
        st.markdown(
            f'<div style="{kpi_s}border-top:4px solid #dc2626;">'
            f'<div style="width:36px;height:36px;background:#fef2f2;border-radius:9px;'
            f'display:flex;align-items:center;justify-content:center;margin-bottom:2px;">'
            f'<i class="fas fa-frown" style="color:#dc2626;font-size:16px;"></i></div>'
            f'<div style="font-size:36px;font-weight:700;color:#dc2626;line-height:1;">{pct_avere:.1f}'
            f'<span style="font-size:14px;font-weight:400;color:#94a3b8;">%</span></div>'
            f'<div style="font-size:11px;color:#94a3b8;">({nb_avere} pers.)</div>'
            f'<div style="font-size:11px;font-weight:700;color:#475569;letter-spacing:0.6px;text-transform:uppercase;">Burnout avéré</div>'
            f'</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    score_brut   = (0.5 * pct_avere) + (0.3 * pct_pre) + (0.2 * pct_pas)
    score_risque = round(100 - score_brut, 1)
    nd = nom.replace('&','&amp;')
    if   score_risque < 26: j_st,j_c,j_i,j_m = "Sain",     "#16a34a",'<i class="fas fa-check-circle"></i>',        f"L'entreprise {nd} se situe en zone saine. L'exposition au burnout est faible et la santé psychosociale est globalement préservée."
    elif score_risque < 75: j_st,j_c,j_i,j_m = "Vigilance","#d97706",'<i class="fas fa-exclamation-triangle"></i>',f"L'entreprise {nd} se situe en zone de vigilance. L'exposition au burnout est significative et nécessite un suivi actif."
    else:                   j_st,j_c,j_i,j_m = "Critique", "#dc2626",'<i class="fas fa-radiation-alt"></i>',       f"L'entreprise {nd} se situe en zone critique. L'exposition au burnout est élevée et requiert des actions immédiates."

    col_j, col_dim = st.columns([1, 1])

    with col_j:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;margin:0 0 14px;">'
            '<div style="width:4px;height:18px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
            '<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;">Score global d\'exposition</span>'
            '</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:white;padding:24px 20px;border-radius:12px;'
            f'box-shadow:0 2px 8px rgba(0,0,0,0.08);border:1px solid #e8edf5;">'
            f'<div style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;margin-bottom:10px;">'
            f'<span style="color:#16a34a;">SAIN</span><span style="color:#dc2626;">CRITIQUE</span></div>'
            f'<div style="position:relative;height:40px;width:100%;margin-bottom:5px;">'
            f'<div style="position:absolute;top:10px;left:0;width:100%;height:20px;'
            f'background:linear-gradient(90deg,#16a34a 0%,#16a34a 26%,#d97706 26%,'
            f'#d97706 75%,#dc2626 75%,#dc2626 100%);border-radius:10px;z-index:1;"></div>'
            f'<div style="position:absolute;left:{min(score_risque,99)}%;top:0;width:6px;height:40px;'
            f'background:#1e293b;border:1px solid white;border-radius:3px;'
            f'transform:translateX(-50%);z-index:10;box-shadow:0 0 5px rgba(0,0,0,0.3);"></div></div>'
            f'<div style="display:flex;justify-content:space-between;font-size:10px;color:#94a3b8;margin-bottom:20px;">'
            f'<span>0</span><span>25</span><span>50</span><span>75</span><span>100</span></div>'
            f'<div style="text-align:center;margin:12px 0;">'
            f'<div style="font-size:52px;font-weight:700;color:{j_c};">'
            f'{score_risque}<span style="font-size:22px;color:#94a3b8;">/100</span></div></div>'
            f'<div style="text-align:center;padding:8px;background:{j_c}20;'
            f'border-radius:8px;border-left:2px solid {j_c};margin-bottom:12px;">'
            f'<span style="font-size:16px;font-weight:700;color:{j_c};">{j_st}</span></div>'
            f'<div style="padding:10px 12px;background:#f8fafc;border-radius:8px;'
            f'border-left:4px solid {j_c};font-size:11px;color:#1e293b;line-height:1.5;">'
            f'<b>{j_i} {j_st.upper()} :</b> {j_m}</div>'
            f'</div>', unsafe_allow_html=True)

    with col_dim:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;margin:0 0 14px;">'
            '<div style="width:4px;height:18px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
            '<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;">Détails par dimension</span>'
            '</div>', unsafe_allow_html=True)

        def cat_ee_new(s): return 'Faible' if s<=16 else ('Modéré' if s<=26 else 'Élevé')
        def cat_dp_new(s): return 'Faible' if s<=6  else ('Modéré' if s<=12 else 'Élevé')
        def cat_pa_new(s): return 'Faible' if s<=31 else ('Modéré' if s<=38 else 'Élevé')

        df['ee_cat2'] = df['ee_score'].apply(cat_ee_new)
        df['dp_cat2'] = df['dp_score'].apply(cat_dp_new)
        df['pa_cat2'] = df['pa_score'].apply(cat_pa_new)

        def get_props(col):
            vc = df[col].value_counts(); n = len(df)
            f=vc.get('Faible',0); m=vc.get('Modéré',0); e=vc.get('Élevé',0)
            return (int(f),round(f/n*100,1)),(int(m),round(m/n*100,1)),(int(e),round(e/n*100,1))

        ee_f,ee_m2,ee_e = get_props('ee_cat2')
        dp_f,dp_m2,dp_e = get_props('dp_cat2')
        pa_f,pa_m2,pa_e = get_props('pa_cat2')
        ee_moy = df['ee_score'].mean()
        dp_moy = df['dp_score'].mean()
        pa_moy = df['pa_score'].mean()

        def get_niv_color(niv):
            return '#16a34a' if niv=='Faible' else '#d97706' if niv=='Modéré' else '#dc2626'

        def draw_dim_new(title, nf, pf, nm, pm, ne, pe, smoy, nmoy):
            nc = get_niv_color(nmoy)
            def seg(pct, bg, lbl, n):
                if pct < 3:
                    return f'<div style="width:{pct:.1f}%;background:{bg};min-height:36px;"></div>'
                return (
                    f'<div style="width:{pct:.1f}%;background:{bg};min-height:36px;'
                    f'display:flex;flex-direction:column;align-items:center;justify-content:center;">'
                    f'<span style="font-size:12px;font-weight:700;color:white;line-height:1.3;">{pct:.1f}%</span>'
                    f'<span style="font-size:10px;color:rgba(255,255,255,0.85);">{lbl} ({n})</span>'
                    f'</div>'
                )
            bar = (
                f'<div style="display:flex;border-radius:7px;overflow:hidden;margin:10px 0 14px;">'
                + seg(pf,'#16a34a','Faible',nf)
                + seg(pm,'#d97706','Modéré',nm)
                + seg(pe,'#dc2626','Élevé',ne)
                + '</div>'
            )
            msg = (
                f'<div style="font-size:12px;color:#64748b;padding:8px 10px;'
                f'background:#f8fafc;border-radius:6px;border:1px solid #e2e8f0;">'
                f'Score moyen de l\'entreprise : <b style="color:#1e293b;">{smoy:.1f}</b>'
                f' → niveau <b style="color:{nc};">{nmoy}</b></div>'
            )
            return (
                f'<div style="background:white;padding:14px 16px;border-radius:10px;'
                f'margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,0.06);border:1px solid #e8edf5;">'
                f'<div style="font-size:13px;font-weight:700;color:#1e293b;margin-bottom:4px;">{title}</div>'
                f'{bar}{msg}</div>'
            )

        st.markdown(draw_dim_new("Épuisement Émotionnel",
            ee_f[0],ee_f[1],ee_m2[0],ee_m2[1],ee_e[0],ee_e[1],ee_moy,cat_ee_new(ee_moy)), unsafe_allow_html=True)
        st.markdown(draw_dim_new("Dépersonnalisation",
            dp_f[0],dp_f[1],dp_m2[0],dp_m2[1],dp_e[0],dp_e[1],dp_moy,cat_dp_new(dp_moy)), unsafe_allow_html=True)
        st.markdown(draw_dim_new("Accomplissement Personnel",
            pa_f[0],pa_f[1],pa_m2[0],pa_m2[1],pa_e[0],pa_e[1],pa_moy,cat_pa_new(pa_moy)), unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    sec("Analyses bivariées détaillées")

    VAR_CROISE_BASE = {
        "Tranche d'âge":          "tranche_age",
        "Ancienneté":             "tranche_anciennete",
        "Catégorie IMC":          "imc_categorie",
        "Genre":                  "genre",
        "Situation matrimoniale": "situation_matrimoniale",
        "Pratique de sport":      "pratique_sport",
        "Maladie chronique":      "maladie_chronique",
        "Handicap physique":      "handicap_physique",
        "Suivi psychologique":    "suivi_psychologique",
    }
    VAR_CROISE = {"Sélectionner une variable": None}
    VAR_CROISE.update({k: v for k, v in VAR_CROISE_BASE.items() if v in df.columns})

    sel_c_label = st.selectbox("Sélectionnez une variable démographique à analyser :",
                               list(VAR_CROISE.keys()), key="croise_tab2")
    sel_c_col   = VAR_CROISE[sel_c_label]

    def render_table_mbi(df_t):
        html = ('<div style="overflow-x:auto;border-radius:8px;border:1px solid #dee2e6;">'
                '<table style="width:100%;border-collapse:collapse;background:white;font-size:13px;">'
                '<thead><tr style="background:#1e40af;color:white;">')
        html += f'<th style="padding:10px 12px;text-align:left;font-weight:600;border:1px solid #1e3a8a;">{df_t.index.name or ""}</th>'
        for c in df_t.columns:
            html += f'<th style="padding:10px 12px;text-align:center;font-weight:600;border:1px solid #1e3a8a;">{c}</th>'
        html += '</tr></thead><tbody>'
        for i,(idx,row) in enumerate(df_t.iterrows()):
            bg = "white" if i%2==0 else "#f8fafc"
            html += f'<tr style="background:{bg};"><td style="padding:9px 12px;font-weight:600;color:#1e293b;border:1px solid #e2e8f0;">{idx}</td>'
            for v in row:
                try:    fmt = f"{float(v):.1f}%"
                except: fmt = str(v)
                html += f'<td style="padding:9px 12px;text-align:center;color:#475569;border:1px solid #e2e8f0;">{fmt}</td>'
            html += '</tr>'
        html += '</tbody></table></div>'
        return html

    def msg_ligne(table, label_var):
        try:
            lignes = [idx for idx in table.index if str(idx) not in ('TOTAL','Total')]
            if len(lignes) < 2:
                return "Ce tableau montre la répartition du burnout au sein de chaque catégorie. La somme de chaque ligne fait 100%."
            l1, l2 = lignes[0], lignes[1]
            cols = [c for c in table.columns if c != 'TOTAL']
            if not cols:
                return "Ce tableau montre la répartition du burnout au sein de chaque catégorie."
            # Utilise la première colonne disponible pour la comparaison
            col_ref = 'Pas de burnout' if 'Pas de burnout' in table.columns else cols[0]
            def gv_l(row, col):
                try: return f"{table.loc[row, col]:.1f}%"
                except: return "N/A"
            return (f"Pour la catégorie <b>« {l1} »</b> : "
                    + ", ".join([f"<b>{gv_l(l1, c)}</b> {c}" for c in cols])
                    + f". Pour la catégorie <b>« {l2} »</b> : "
                    + ", ".join([f"<b>{gv_l(l2, c)}</b> {c}" for c in cols])
                    + f". Ce tableau compare la répartition du burnout par catégorie de {label_var}.")
        except Exception:
            return "Ce tableau montre la répartition du burnout au sein de chaque catégorie. La somme de chaque ligne fait 100%."

    def msg_colonne(table, label_var):
        try:
            lignes = [idx for idx in table.index if str(idx) not in ('TOTAL','Total')]
            if not lignes:
                return "Ce tableau montre la composition de chaque groupe de burnout. La somme de chaque colonne fait 100%."
            l1 = lignes[0]
            cols = [c for c in table.columns if c in ('Pas de burnout','Pré-burnout','Burnout avéré')]
            def gv(col):
                try: return f"{table.loc[l1, col]:.1f}%"
                except: return "N/A"
            parts = " — ".join([f"<b>{gv(c)}</b> appartiennent à <b>« {l1} »</b> parmi les <b>{c}</b>" for c in cols])
            return (parts + f". Ce tableau compare la composition de chaque groupe de burnout selon {label_var}.")
        except Exception:
            return "Ce tableau montre la composition de chaque groupe de burnout. La somme de chaque colonne fait 100%."

    if sel_c_col and sel_c_col in df.columns:
        ORDER    = ['Pas de burnout','Pré-burnout','Burnout avéré']
        t_ligne  = pd.crosstab(df[sel_c_col], df['niveau_burnout'], normalize='index')*100
        t_ligne  = t_ligne[[c for c in ORDER if c in t_ligne.columns]]
        t_ligne['TOTAL'] = t_ligne.sum(axis=1)
        t_colonne = pd.crosstab(df[sel_c_col], df['niveau_burnout'], normalize='columns')*100
        t_colonne = t_colonne[[c for c in ORDER if c in t_colonne.columns]]
        t_colonne.loc['TOTAL'] = t_colonne.sum(axis=0)

        viz_tab, lig_tab, col_tab = st.tabs([
            "  Visualisation Graphique","  Tableau Croisé % Ligne","  Tableau Croisé % Colonne"])

        with viz_tab:
            fig2, ax2 = plt.subplots(figsize=(12, 7))
            fig2.patch.set_facecolor('#f1f4f9'); ax2.set_facecolor('white')
            data_plot = t_ligne[[c for c in ORDER if c in t_ligne.columns]].copy()
            data_plot.plot(kind='barh', stacked=True, ax=ax2,
                           color=['#16a34a','#d97706','#dc2626'], edgecolor='none', linewidth=0)
            for i, idx in enumerate(data_plot.index):
                cumsum = 0
                for cat in data_plot.columns:
                    pv = data_plot.loc[idx, cat]
                    if pv > 5:
                        ax2.text(cumsum+pv/2, i, f'{pv:.1f}%',
                                 ha='center', va='center', color='white', fontsize=11, fontweight='bold')
                    cumsum += pv
            ax2.set_xlabel('Pourcentage (%)', fontsize=13, fontweight='bold', color='#1e293b')
            ax2.set_ylabel(sel_c_label, fontsize=13, fontweight='bold', color='#1e293b')
            ax2.set_title(f"Répartition du Burnout des Employés de l'Entreprise {nom}\nselon : {sel_c_label}",
                          fontsize=15, fontweight='bold', pad=20, color='#1e293b')
            ax2.legend(title='Niveau Burnout', loc='upper center',
                       bbox_to_anchor=(0.5,-0.12), ncol=3, frameon=False, fontsize=11)
            ax2.set_xlim(0, 100)
            ax2.grid(axis='x', alpha=0.3, linestyle='--')
            ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)
            ax2.spines['left'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig2)
            buf2 = BytesIO()
            fig2.savefig(buf2, format='png', dpi=300, bbox_inches='tight', facecolor='#f1f4f9')
            buf2.seek(0)
            st.download_button("⬇  Télécharger le graphique (PNG)", buf2,
                               f"burnout_{sel_c_col}.png", "image/png", key="dl_viz")
            plt.close()

        with lig_tab:
            st.markdown(f"<p style='font-size:13px;color:#1e293b;font-weight:600;'>Tableau croisé % ligne : {sel_c_label} vs Burnout</p>", unsafe_allow_html=True)
            st.markdown(render_table_mbi(t_ligne), unsafe_allow_html=True)
            st.markdown(
                f'<div style="margin-top:12px;background:#f8fafc;border-radius:8px;padding:12px 15px;border-left:4px solid #1e40af;">'
                f'<div style="font-size:11px;font-weight:700;color:#1e293b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">'
                f'<i class="fas fa-book-open" style="margin-right:6px;color:#1e40af;"></i>Comment lire ce tableau</div>'
                f'<p style="font-size:12px;color:#475569;margin:0;line-height:1.7;">{msg_ligne(t_ligne, sel_c_label)}</p></div>',
                unsafe_allow_html=True)
            csv = t_ligne.to_csv(index=True).encode('utf-8')
            st.download_button("⬇  Télécharger le tableau (CSV)", csv,
                               f"ligne_{sel_c_col}.csv", "text/csv", key="dl_lig")

        with col_tab:
            st.markdown(f"<p style='font-size:13px;color:#1e293b;font-weight:600;'>Tableau croisé % colonne : {sel_c_label} vs Burnout</p>", unsafe_allow_html=True)
            st.markdown(render_table_mbi(t_colonne), unsafe_allow_html=True)
            st.markdown(
                f'<div style="margin-top:12px;background:#f8fafc;border-radius:8px;padding:12px 15px;border-left:4px solid #1e40af;">'
                f'<div style="font-size:11px;font-weight:700;color:#1e293b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">'
                f'<i class="fas fa-book-open" style="margin-right:6px;color:#1e40af;"></i>Comment lire ce tableau</div>'
                f'<p style="font-size:12px;color:#475569;margin:0;line-height:1.7;">{msg_colonne(t_colonne, sel_c_label)}</p></div>',
                unsafe_allow_html=True)
            csv2 = t_colonne.to_csv(index=True).encode('utf-8')
            st.download_button("⬇  Télécharger le tableau (CSV)", csv2,
                               f"colonne_{sel_c_col}.csv", "text/csv", key="dl_col")
    elif sel_c_col:
        st.warning(f"⚠️ La colonne '{sel_c_col}' n'existe pas dans les données.")

# ── Footer ────────────────────────────────────────────────────
st.markdown(
    '<div style="margin-top:40px;padding:14px 0;border-top:1px solid #e2e8f0;'
    'display:flex;align-items:center;justify-content:space-between;">'
    '<div style="display:flex;align-items:center;gap:10px;">'
    '<div style="width:22px;height:22px;background:linear-gradient(135deg,#1e40af,#3b82f6);'
    'border-radius:6px;display:flex;align-items:center;justify-content:center;">'
    '<i class="fas fa-chart-line" style="color:white;font-size:9px;"></i></div>'
    '<span style="font-size:12px;font-weight:600;color:#374151;">YODAN Analytics</span>'
    '<span style="font-size:12px;color:#cbd5e1;">\u00b7</span>'
    '<span style="font-size:12px;color:#94a3b8;">MBI Burnout v2.0 \u00b7 2026</span>'
    '</div>'
    '<span style="font-size:11px;color:#cbd5e1;">Maslach Burnout Inventory</span>'
    '</div>',
    unsafe_allow_html=True
)