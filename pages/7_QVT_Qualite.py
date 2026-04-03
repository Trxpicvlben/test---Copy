# =============================================================================
# PAGE QVT — Qualité de Vie au Travail
# =============================================================================
# Cette page fait partie d'un projet multi-pages Streamlit.
# Elle est autonome : pas de dépendance à d'autres pages du projet.
#
# Structure du fichier :
#   1. Imports & constantes
#   2. CSS embarqué
#   3. Helpers Streamlit (query params, rerun)
#   4. Helpers de données (normalisation, recodage, dérivation)
#   5. Helpers UI (sec_title, kpi_card, jauge)
#   6. Helpers Plotly (graphiques)
#   7. Chargement & scoring des données
#   8. Fonction principale main()
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# 1. IMPORTS & CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────
import re
import textwrap
import unicodedata

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# --- Palette de couleurs principale ---
C = {
    "bg":        "#F0F7FF",
    "card":      "#FFFFFF",
    "text":      "#0F2633",
    "muted":     "#7F98A8",
    "border":    "#E6EEF6",
    "blue":      "#4A90E2",
    "orange":    "#F39C6B",
    "green":     "#66BB6A",
    "red":       "#E45757",
    "purple":    "#A78BFA",
    "gray":      "#D5DADE22",
    "dark_grn":  "#1B7A32",
}

# --- Deux classes de réponse (on fusionne les 4 modalités originales en 2) ---
# Satisfait  = modalités 3 et 4 (ou "Satisfait" / "Très satisfait")
# Insatisfait = modalités 1 et 2 (ou "Insatisfait" / "Très insatisfait")
RESPONSE_CLASSES = ["Insatisfait", "Satisfait"]

RESPONSE_COLORS = {
    "Insatisfait": C["red"],
    "Satisfait":   C["green"],
}

# --- Questions du questionnaire QVT ---
QUESTIONS = [
    "Je comprends clairement mes missions.",
    "Je dispose des moyens nécessaires pour faire mon travail.",
    "Je peux exprimer mon point de vue au travail.",
    "Je suis reconnu(e) pour le travail bien fait.",
    "Mon travail a du sens pour moi.",
    "Je suis écouté(e) par ma hiérarchie.",
    "J'ai un bon équilibre entre vie privée et professionnelle.",
    "J'ai des relations de qualité avec mes collègues.",
    "Je peux évoluer dans mon poste.",
    "Mon environnement de travail est sain et sécurisé.",
    "J'ai des pauses suffisantes pendant ma journée.",
    "Je reçois des informations utiles pour bien travailler.",
    "Je participe aux décisions qui concernent mon travail.",
    "Mon travail est compatible avec mes valeurs.",
    "Je ressens de la fierté dans ce que je fais.",
    "Mon travail est stimulant.",
    "Les horaires sont compatibles avec ma vie personnelle.",
    "Mon manager me soutient en cas de difficulté.",
    "Je me sens à l'aise dans mon équipe.",
    "Je me sens utile dans mon organisation.",
]
RENOMMED_QUESTIONS = {
    "Je comprends clairement mes missions.": "Clarté des missions",
    "Je dispose des moyens nécessaires pour faire mon travail.": "Disponibilité des moyens nécessaires",
    "Je peux exprimer mon point de vue au travail.": "Liberté d'expression",
    "Je suis reconnu(e) pour le travail bien fait.": "Reconnaissance du travail bienfait ",
    "Mon travail a du sens pour moi.": "Sens du travail personnel",
    "Je suis écouté(e) par ma hiérarchie.": "Écoute hiérarchique",
    "J'ai un bon équilibre entre vie privée et professionnelle.": "Équilibre de vie ",
    "J'ai des relations de qualité avec mes collègues.": "Bonnnes relations entre collègues",
    "Je peux évoluer dans mon poste.": "Évolution professionnelle",
    "Mon environnement de travail est sain et sécurisé.": "Environnement sain et sécurisé",
    "J'ai des pauses suffisantes pendant ma journée.": "Pauses suffisantes",
    "Je reçois des informations utiles pour bien travailler.": "Informations utiles",
    "Je participe aux décisions qui concernent mon travail.": "Participation aux décisions",
    "Mon travail est compatible avec mes valeurs.": "Reflète mes valeurs",
    "Je ressens de la fierté dans ce que je fais.": "Fierté au travail",
    "Mon travail est stimulant.": "Travail stimulant",
    "Les horaires sont compatibles avec ma vie personnelle.": "Horaires compatibles",
    "Mon manager me soutient en cas de difficulté.": "Soutien du manager",
    "Je me sens à l'aise dans mon équipe.": "Intégration dans l'équipe",
    "Je me sens utile dans mon organisation.": "Utilité dans l'organisation",
}
# --- Regroupement des questions par domaine ---
SCORE_GROUPS = {
    "Sens du Travail": [
        "Mon travail a du sens pour moi.",
        "Mon travail est compatible avec mes valeurs.",
        "Je ressens de la fierté dans ce que je fais.",
        "Mon travail est stimulant.",
        "Je me sens utile dans mon organisation.",
    ],
    "Relations Interpersonnelles": [
        "Je peux exprimer mon point de vue au travail.",
        "Je suis écouté(e) par ma hiérarchie.",
        "J'ai des relations de qualité avec mes collègues.",
        "Mon manager me soutient en cas de difficulté.",
        "Je me sens à l'aise dans mon équipe.",
    ],
    "Santé & Environnement": [
        "Je comprends clairement mes missions.",
        "Je dispose des moyens nécessaires pour faire mon travail.",
        "Mon environnement de travail est sain et sécurisé.",
        "Je reçois des informations utiles pour bien travailler.",
    ],
    "Reconnaissance & Évolution": [
        "Je suis reconnu(e) pour le travail bien fait.",
        "Je peux évoluer dans mon poste.",
        "Je participe aux décisions qui concernent mon travail.",
    ],
    "Équilibre de Vie": [
        "J'ai un bon équilibre entre vie privée et professionnelle.",
        "J'ai des pauses suffisantes pendant ma journée.",
        "Les horaires sont compatibles avec ma vie personnelle.",
    ],
}
def get_renamed_question(question_text: str) -> str:
    """Retourne le nom renommé d'une question si disponible, sinon le texte original."""
    return RENOMMED_QUESTIONS.get(question_text, question_text)
QUESTION_TO_GROUP = {
    question: group
    for group, questions in SCORE_GROUPS.items()
    for question in questions
}

SCORE_COLORS = {
    "Sens du Travail":             C["purple"],
    "Relations Interpersonnelles": C["blue"],
    "Santé & Environnement":       C["green"],
    "Reconnaissance & Évolution":  C["orange"],
    "Équilibre de Vie":            "#F59E0B",
}

# Colonnes sociodémographiques recherchées dans le fichier
SOCIO_CANDIDATES = [
    "Departement", "Département", "Direction",
    "Poste de travail", "Fonction",
    "Genre", "Service", "Situation_matrimoniale",
    "Categorie_IMC", "Classe_Anciennete", "TrancheAge",
]


# ─────────────────────────────────────────────────────────────────────────────
# 2. CSS EMBARQUÉ
# ─────────────────────────────────────────────────────────────────────────────

def _get_inline_css() -> str:
    """Retourne le CSS global de la page (inline dans <style>)."""
    return """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,400;1,9..144,600&display=swap');
:root{--bg-soft:#eef2f7;--card:#ffffff;--text:#2f3d55;--border:#dde5f2}
html,body,[class*="css"],.stApp{font-family:'Plus Jakarta Sans',sans-serif!important}
.stApp{background:linear-gradient(180deg,#f4f6fb 0%,var(--bg-soft) 100%);color:var(--text)}

/* Titre de section */
.section-title{display:flex;align-items:center;gap:0.7rem;font-family:'Fraunces',Georgia,serif!important;
font-style:italic!important;font-size:1.25rem!important;color:#0F2340!important;
margin:1.6rem 0 1rem!important;padding-bottom:0.65rem!important;border-bottom:2px solid #dde5f2!important}
.section-title::before{content:'';display:inline-block;width:4px;height:22px;
background:linear-gradient(180deg,#2f66b3 0%,#4f8be4 100%);border-radius:2px;flex-shrink:0}

/* KPI cards */
.kpi-card,.gauge-card{background:#fff;border:1px solid #dde5f2;border-radius:12px;padding:12px}
.kpi-label{font-size:0.72rem;color:#6B88A8;text-transform:uppercase;font-weight:700;margin-bottom:6px}
.kpi-value{font-family:'Fraunces',serif;font-size:1.6rem;font-weight:800}

/* Badges */
.badge{display:inline-block;font-size:0.64rem;font-weight:700;padding:0.18rem 0.65rem;border-radius:999px}
.badge-red{background:#FEE2E2;color:#B91C1C}
.badge-green{background:#DCFCE7;color:#15803D}
.badge-blue{background:rgba(56,163,232,0.1);color:#38A3E8}

/* Bouton retour */
.back-btn{display:inline-flex;align-items:center;gap:8px;padding:10px 16px;border-radius:14px;
background:linear-gradient(135deg,#2f66b3,#4f8be4);color:#ffffff!important;font-weight:700;
text-decoration:none!important;box-shadow:0 6px 18px rgba(47,102,179,0.12)}

/* Items risques / atouts */
.q-items{margin-top:20px}
.q-items .item-row{margin-bottom:22px;padding:12px 16px;border-radius:10px;
background:#fff;box-shadow:0 6px 18px rgba(16,24,40,0.03)}

/* Onglets */
[data-baseweb="tab-list"]{background:#FFFFFF!important;border-radius:12px!important;
padding:4px!important;gap:3px!important;border:1px solid #dde5f2!important;
box-shadow:0 2px 8px rgba(47,102,179,0.07)!important}
[data-baseweb="tab"]{font-family:'Plus Jakarta Sans',sans-serif!important;font-weight:600!important;
font-size:0.88rem!important;color:#6B88A8!important;border-radius:9px!important;
padding:0.5rem 1.4rem!important;transition:all 0.18s!important}
[aria-selected="true"][data-baseweb="tab"]{background:linear-gradient(135deg,#2f66b3,#4f8be4)!important;
color:#FFFFFF!important;font-weight:700!important;
box-shadow:0 3px 12px rgba(47,102,179,0.30)!important}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none!important}
"""


def load_css() -> None:
    st.markdown(f"<style>{_get_inline_css()}</style>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. HELPERS STREAMLIT (compatibilité multi-versions)
# ─────────────────────────────────────────────────────────────────────────────

def get_query_params_safe() -> dict:
    """Lecture des query params compatible toutes versions Streamlit."""
    try:
        if hasattr(st, "query_params"):
            return dict(st.query_params)
    except Exception:
        pass
    if hasattr(st, "get_query_params"):
        try:
            return st.get_query_params()
        except Exception:
            pass
    return {}


def set_query_params_safe(**params) -> None:
    """Écriture des query params compatible toutes versions Streamlit."""
    if hasattr(st, "set_query_params"):
        try:
            st.set_query_params(**params)
        except Exception:
            pass


def safe_rerun() -> None:
    """Rerun compatible toutes versions Streamlit."""
    if hasattr(st, "rerun"):
        try:
            st.rerun()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# 4. HELPERS DE DONNÉES
# ─────────────────────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Normalise un texte : minuscules, sans accents, sans caractères spéciaux."""
    t = str(text).strip().lower()
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", t)


def find_col(df: pd.DataFrame, target: str):
    """
    Trouve la colonne d'un DataFrame correspondant à `target`
    par correspondance normalisée (exacte → préfixe → contient → fuzzy).
    Retourne le nom original de la colonne ou None.
    """
    import difflib
    if df is None:
        return None
    nt = normalize(target)
    norm_map = {normalize(c): c for c in df.columns}
    if nt in norm_map:
        return norm_map[nt]
    for k, orig in norm_map.items():
        if k.startswith(nt) or nt.startswith(k):
            return orig
    for k, orig in norm_map.items():
        if nt in k or k in nt:
            return orig
    close = difflib.get_close_matches(nt, list(norm_map.keys()), n=1, cutoff=0.75)
    if close:
        return norm_map[close[0]]
    return None


def recode_to_2_classes(series: pd.Series) -> pd.Series:
    """
    Recode les réponses originales (1–4 ou textuelles) en 2 classes :
    - Insatisfait : modalités 1, 2 / "Très insatisfait" / "Insatisfait"
    - Satisfait   : modalités 3, 4 / "Satisfait" / "Très satisfait"
    Retourne une Series avec les valeurs "Insatisfait" ou "Satisfait" (ou NA).
    """
    out = pd.Series(pd.NA, index=series.index, dtype="object")
    # Recodage numérique
    num = pd.to_numeric(series, errors="coerce")
    out.loc[num.isin([1, 2])] = "Insatisfait"
    out.loc[num.isin([3, 4])] = "Satisfait"
    # Recodage textuel (labels déjà présents)
    text_map = {
        "tresinsatisfait": "Insatisfait",
        "insatisfait":     "Insatisfait",
        "satisfait":       "Satisfait",
        "tressatisfait":   "Satisfait",
    }
    normed = series.astype(str).map(normalize)
    for k, v in text_map.items():
        out.loc[normed == k] = v
    return out


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute des colonnes dérivées si elles n'existent pas déjà :
    - TrancheAge         (depuis Age)
    - Classe_Anciennete  (depuis Anciennete)
    - IMC                (depuis Poids + Taille)
    - Categorie_IMC      (depuis IMC)
    Copie aussi les variantes orthographiques sous un nom standard.
    """
    out = df.copy()
    age_col   = find_col(out, "Age")
    anc_col   = find_col(out, "Anciennete")
    poids_col = find_col(out, "Poids")
    taille_col = find_col(out, "Taille")
    imc_col   = find_col(out, "IMC")

    if age_col and "TrancheAge" not in out.columns:
        age = pd.to_numeric(out[age_col], errors="coerce")
        out["TrancheAge"] = pd.cut(
            age, bins=[0, 20, 30, 40, 50, 60, np.inf],
            labels=["<20", "20-30", "31-40", "41-50", "51-60", "60+"], right=False
        )

    if anc_col and "Classe_Anciennete" not in out.columns:
        anc = pd.to_numeric(out[anc_col], errors="coerce")
        out["Classe_Anciennete"] = pd.cut(
            anc, bins=[0, 2, 5, 10, 20, np.inf],
            labels=["0-2 ans", "3-5 ans", "6-10 ans", "11-20 ans", "21+ ans"],
            include_lowest=True
        )

    if poids_col and taille_col and "IMC" not in out.columns:
        p = pd.to_numeric(out[poids_col], errors="coerce")
        t = pd.to_numeric(out[taille_col], errors="coerce")
        out["IMC"] = np.round(p / (t / 100) ** 2, 1)

    imc_source = imc_col or ("IMC" if "IMC" in out.columns else None)
    if imc_source and "Categorie_IMC" not in out.columns:
        imc_vals = pd.to_numeric(out[imc_source], errors="coerce")
        out["Categorie_IMC"] = pd.cut(
            imc_vals, bins=[-np.inf, 18.5, 24.9, 29.9, np.inf],
            labels=["Sous-poids", "Normal", "Surpoids", "Obésité"]
        )

    # Harmonisation des noms de colonnes socio
    standard_socio = [
        "Taille", "Poids", "Departement", "Direction", "Anciennete",
        "Service", "Poste de travail", "Age", "Genre", "Fonction",
        "Situation_matrimoniale",
    ]
    for std in standard_socio:
        try:
            found = find_col(out, std)
            if found and std not in out.columns:
                out[std] = out[found]
        except Exception:
            continue

    return out


def resolve_questions(df: pd.DataFrame) -> dict:
    """
    Retourne un dict {question_label: nom_colonne_df}
    pour toutes les questions reconnues dans le fichier.
    """
    return {q: find_col(df, q) for q in QUESTIONS if find_col(df, q)}


@st.cache_data
def load_excel(file) -> pd.DataFrame:
    """Charge le fichier Excel (mis en cache par Streamlit)."""
    return pd.read_excel(file)


def compute_scores(df: pd.DataFrame, question_map: dict) -> pd.DataFrame:
    """
    Calcule les scores numériques (moyennes) par domaine et le Score_Global.
    Les scores sont sur l'échelle brute (1–4).
    """
    out = df.copy()
    for score_name, qs in SCORE_GROUPS.items():
        cols = [question_map[q] for q in qs if q in question_map]
        if cols:
            out[score_name] = out[cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    q_cols = list(question_map.values())
    if q_cols:
        out["Score_Global"] = out[q_cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    return out


def compute_pct_satisfait(df: pd.DataFrame, question_map: dict) -> dict:
    """
    Calcule le % de répondants "Satisfaits" pour chaque domaine et globalement.
    Retourne un dict {domaine: pct_satisfait} + {"Global": pct_global}.
    """
    result = {}
    # Par domaine
    for domain, qs in SCORE_GROUPS.items():
        cols = [question_map[q] for q in qs if q in question_map]
        if not cols:
            continue
        # On empile toutes les réponses de toutes les questions du domaine
        all_responses = pd.concat(
            [recode_to_2_classes(df[c]) for c in cols], ignore_index=True
        )
        n_total = all_responses.notna().sum()
        n_sat = (all_responses == "Satisfait").sum()
        result[domain] = (n_sat / n_total * 100) if n_total > 0 else 0.0

    # Score global : toutes les questions confondues
    all_cols = list(question_map.values())
    if all_cols:
        all_responses_global = pd.concat(
            [recode_to_2_classes(df[c]) for c in all_cols], ignore_index=True
        )
        n_total = all_responses_global.notna().sum()
        n_sat = (all_responses_global == "Satisfait").sum()
        result["Global"] = (n_sat / n_total * 100) if n_total > 0 else 0.0

    return result

def get_renamed_question(question_text: str) -> str:
    """Retourne le nom renommé d'une question si disponible, sinon le texte original."""
    return RENOMMED_QUESTIONS.get(question_text, question_text)
def question_stats(df: pd.DataFrame, question_map: dict) -> pd.DataFrame:
    """
    Calcule pour chaque question :
    - pct_insatisfait : % de répondants "Insatisfait"
    - pct_satisfait   : % de répondants "Satisfait"
    Retourne un DataFrame trié par pct_satisfait croissant.
    """
    rows = []
    for q, col in question_map.items():
        recoded = recode_to_2_classes(df[col])
        counts = recoded.value_counts()
        total = counts.sum()
        pct_sat = counts.get("Satisfait", 0) / total * 100 if total else 0
        pct_ins = counts.get("Insatisfait", 0) / total * 100 if total else 0
        rows.append({
            "question":    q,
            "col":         col,
            "pct_sat":     pct_sat,
            "pct_ins":     pct_ins,
            "n_valid":     int(total),
        })
    return pd.DataFrame(rows).sort_values("pct_sat")


# ─────────────────────────────────────────────────────────────────────────────
# 5. HELPERS UI
# ─────────────────────────────────────────────────────────────────────────────

def sec_title(text: str) -> None:
    """Affiche un titre de section stylé."""
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value, color: str = None, suffix: str = "", decimals: int = 0, sub: str = "") -> None:
    """
    Affiche une KPI card stylée.
    `value` peut être un nombre (formaté avec `decimals` décimales) ou une chaîne.
    """
    color = color or C["blue"]
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            disp = f"{value:.{decimals}f}{suffix}"
        else:
            disp = f"{value}{suffix}"
    except Exception:
        disp = str(value)
    sub_html = (
        f'<div style="font-size:0.72rem;color:#9AAFBF;margin-top:6px">{sub}</div>'
        if sub else ""
    )
    st.markdown(f"""
    <div class="kpi-card">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value" style="color:{color};">{disp}</div>
    {sub_html}
    </div>""", unsafe_allow_html=True)


def semi_gauge(pct: float, color: str, label: str, sublabel: str,
            key: str = "", badge_override: tuple = None) -> None:
    """
    Affiche une jauge semi-circulaire SVG.
    badge_override : tuple (bg, text_color, label_badge) pour forcer le badge.
    """
    pct = max(0.0, min(100.0, float(pct)))
    angle = pct / 100 * 180
    r, cx, cy = 68, 88, 78
    ex = cx + r * np.cos(np.radians(180 - angle))
    ey = cy - r * np.sin(np.radians(180 - angle))
    arc = f"M {cx-r} {cy} A {r} {r} 0 0 1 {ex:.2f} {ey:.2f}" if angle > 1 else ""

    if badge_override is not None:
        badge_bg, badge_c, badge_t = badge_override
    elif pct > 65:
        badge_bg, badge_c, badge_t = ("#DCFCE7", "#15803D", "Élevé")
    else:
        badge_bg, badge_c, badge_t = ("#FEE2E2", "#B91C1C", "Faible")

    stroke_color = C["green"] 
    st.markdown(f"""
    <div class="gauge-card">
    <svg width="176" height="96" style="display:block;margin:0 auto;">
        <path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}"
        fill="none" stroke="#EDF5FD" stroke-width="12" stroke-linecap="round"/>
        {"<path d='" + arc + "' fill='none' stroke='" + stroke_color + "' stroke-width='12' stroke-linecap='round'/>" if arc else ""}
        <text x="{cx}" y="76" text-anchor="middle" font-size="23" font-weight="800"
        fill="{stroke_color}" font-family="Fraunces, serif">{pct:.0f}%</text>
        <text x="{cx}" y="92" text-anchor="middle" font-size="10" fill="#6B88A8"
        font-family="Plus Jakarta Sans"></text>
    </svg>
    <div style="font-weight:700;font-size:0.82rem;color:{C['text']};line-height:1.35;
                text-align:center;margin-top:0.15rem;">{label}</div>
    <div style="font-size:0.7rem;color:{C['muted']};text-align:center;
                margin:0.15rem 0 0.45rem;line-height:1.4;">{sublabel}</div>
    <div style="text-align:center;">
        <span class="badge" style="background:{badge_bg};color:{badge_c};">{badge_t}</span>
    </div>
    </div>""", unsafe_allow_html=True)


def dual_status_bar(pct_ins, pct_sat, highlight="red"):
    gray = "#D5DADE4C"  # gris plein, pas de transparence
    
    red_color = "#FF4D4F" if highlight == "red" else gray
    green_color = "#00B400" if highlight == "green" else gray

    return f"""
    <div style="display:flex;width:100%;height:8px;border-radius:6px;overflow:hidden;">
        <div style="
            width:{pct_ins}%;
            background:{red_color};
        "></div>
        <div style="
            width:{pct_sat}%;
            background:{green_color};
        "></div>
    </div>
    """



# ─────────────────────────────────────────────────────────────────────────────
# 6. HELPERS PLOTLY
# ─────────────────────────────────────────────────────────────────────────────

LAYOUT_BASE = dict(
    plot_bgcolor="#FAFCFF",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color=C["text"], size=12),
    margin=dict(l=40, r=20, t=50, b=40),
)


def _apply_layout(fig: go.Figure, title: str = "", height: int = None) -> go.Figure:
    """Applique le style de base à une figure Plotly."""
    upd = dict(
        **LAYOUT_BASE,
        title=dict(
            text=title,
            font=dict(family="Fraunces, serif", size=14, color=C["text"]),
            x=0.02,
        )
    )
    if height:
        upd["height"] = height
    fig.update_layout(**upd)
    return fig


def chart_bar_univarie(series: pd.Series, var_label: str) -> go.Figure:
    """
    Graphique en barres horizontales pour la distribution d'une variable socio.
    Affiche % et effectif à l'intérieur de chaque barre.
    """
    counts = series.value_counts().reset_index()
    counts.columns = [var_label, "n"]
    total = counts["n"].sum()
    counts["pct"] = counts["n"] / total * 100
    palette = [C["blue"], C["orange"], C["purple"], C["green"],
            "#F2B86B", "#4EC0D9", "#FB9A6B", "#84CC6A"]
    fig = go.Figure()
    for i, row in counts.iterrows():
        fig.add_trace(go.Bar(
            y=[str(row[var_label])],
            x=[row["pct"]],
            orientation="h",
            marker_color=palette[i % len(palette)],
            opacity=0.88,
            text=f"{row['pct']:.1f}% ({int(row['n'])})",
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=12, family="Plus Jakarta Sans", weight="bold"),
            showlegend=False,
        ))
    height = max(260, len(counts) * 52 + 80)
    fig = _apply_layout(fig, f"Distribution — {var_label}", height)
    fig.update_xaxes(range=[0, 100], title_text="Pourcentage (%)", ticksuffix="%")
    fig.update_yaxes(title_text=var_label)
    return fig


def chart_stacked_2classes(crosstab: pd.DataFrame, title: str, y_axis_label: str) -> go.Figure:
    """
    Graphique en barres empilées à 100 % avec 2 classes (Insatisfait / Satisfait).
    `crosstab` doit avoir les colonnes 'Insatisfait' et/ou 'Satisfait'.
    L'index correspond aux catégories (ex. départements, questions...).
    """
    fig = go.Figure()
    for label in RESPONSE_CLASSES:
        if label not in crosstab.columns:
            continue
        fig.add_trace(go.Bar(
            x=crosstab[label],
            y=crosstab.index,
            orientation="h",
            name=label,
            marker_color=RESPONSE_COLORS[label],
            texttemplate="<b>%{x:.1f}%</b>",
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=11, family="Plus Jakarta Sans"),
            marker=dict(line=dict(color="white", width=0.8)),
        ))
    fig.update_layout(
        barmode="stack",
        title=dict(
            text=title,  # Le titre vient maintenant de chart_bivariate_question
            font=dict(family="Fraunces, serif", size=15, color=C["text"], weight="bold"),
            x=0.5,  # Centré
            xanchor="center",
        ),
        xaxis=dict(range=[0, 100], title="Pourcentage (%)", ticksuffix="%",
                showgrid=True, gridcolor="#F5F7FA"),
        yaxis=dict(title=y_axis_label, showgrid=False),
        legend_title="Réponses",
        plot_bgcolor="#FAFCFF", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color=C["text"], size=11),
        margin=dict(l=20, r=20, t=60, b=30),  # Augmenté t=60 pour laisser place au titre
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor=C["border"], borderwidth=1),
    )
    return fig

def chart_bivariate_domain(df: pd.DataFrame, socio_col: str,
                            domain: str, question_map: dict) -> go.Figure:
    """
    Graphique bivarié : répartition Satisfait/Insatisfait pour toutes les questions
    d'un domaine, par catégorie de variable socio.
    Retourne un graphique empilé à 2 classes.
    """
    qs_in_domain = [q for q in SCORE_GROUPS.get(domain, []) if q in question_map]
    if not qs_in_domain:
        return go.Figure()

    # Empiler toutes les questions du domaine, grouper par socio_col
    frames = []
    for q in qs_in_domain:
        tmp = df[[socio_col, question_map[q]]].copy()
        tmp["Reponse"] = recode_to_2_classes(tmp[question_map[q]])
        tmp = tmp[[socio_col, "Reponse"]].dropna()
        frames.append(tmp)

    if not frames:
        return go.Figure()

    combined = pd.concat(frames, ignore_index=True)
    ct = pd.crosstab(combined[socio_col], combined["Reponse"], normalize="index") * 100
    ct = ct.reindex(columns=RESPONSE_CLASSES, fill_value=0)

    return chart_stacked_2classes(
        ct,
        title=f"{domain} par {socio_col}",  # Ex: "Clarté des missions par Département"
        y_axis_label=socio_col,
    )

def chart_bivariate_question(df: pd.DataFrame, socio_col: str,
                            question: str, question_map: dict) -> go.Figure:
    """
    Graphique bivarié : répartition Satisfait/Insatisfait pour UNE question,
    par catégorie de variable socio.
    """
    col = question_map.get(question)
    if col is None:
        return go.Figure()

    tmp = df[[socio_col, col]].copy()
    tmp["Reponse"] = recode_to_2_classes(tmp[col])
    ct = pd.crosstab(tmp[socio_col], tmp["Reponse"], normalize="index") * 100
    ct = ct.reindex(columns=RESPONSE_CLASSES, fill_value=0)

    # Utiliser le nom renommé de la question
    renamed_question = get_renamed_question(question)
    # Tronquer si nécessaire (60 caractères maximum)
    short_q = renamed_question[:60] + "…" if len(renamed_question) > 60 else renamed_question
    
    return chart_stacked_2classes(
        ct,
        title=f"{short_q} par {socio_col}",  # Ex: "Clarté des missions par Département"
        y_axis_label=socio_col,
    )

def chart_pie_global(pct_bon: float) -> go.Figure:
    """
    Camembert Bon / Mauvais pour la Vue d'ensemble du score global.
    pct_bon : pourcentage de répondants "Satisfaits" globalement.
    """
    pct_mau = 100.0 - pct_bon
    fig = px.pie(
        names=["Satisfaits", "Insatisfaits"],
        values=[pct_bon, pct_mau],
        color=["Satisfaits", "Insatisfaits"],
        color_discrete_map={"Insatisfaits": C["red"], "Satisfaits": C["green"]},
        title="Répartition globale de la satisfaction QVT",
    )
    fig.update_traces(
        textinfo="percent+label",
        textfont=dict(color="white", size=12, family="Plus Jakarta Sans"),
        insidetextorientation="radial",
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFCFF")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 7. RENDU DES SECTIONS (logique UI par bloc)
# ─────────────────────────────────────────────────────────────────────────────

def render_topbar() -> None:
    """Affiche la barre de navigation en haut de la page."""
    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
        '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800'
        '&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,400;1,9..144,600&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="display:flex;justify-content:space-between;align-items:center;background:white;'
        'border-radius:12px;padding:14px 24px;margin-bottom:16px;'
        'box-shadow:0 1px 3px rgba(0,0,0,0.06),0 8px 20px rgba(47,78,64,0.06);border:1px solid #e8edf5;">'
        '<div style="display:flex;align-items:center;gap:12px;">'
        '<div style="width:48px;height:48px;background:linear-gradient(135deg,#27AE60,#2ECC71);'
        'border-radius:12px;display:flex;align-items:center;justify-content:center;">'
        '<svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
        '<path fill="white" d="M12 21s-7-4.35-9-6.5C1 11.5 4 7 7.5 7 9.24 7 11 8 12 9.5'
        ' 13 8 14.76 7 16.5 7 20 7 23 11.5 21 14.5 19 16.65 12 21 12 21z"/>'
        '</svg></div>'
        '<div style="margin-left:4px;">'
        '<div style="font-size:18px;font-weight:700;color:#0f2130;">QVT — Qualité de Vie au Travail</div>'
        '<div style="font-size:12px;color:#4b6272;margin-top:2px;">Analyse de la satisfaction · YODAN Analytics</div>'
        '</div></div>'
        '<a href="?back=1" class="back-btn" style="text-decoration:none;color:#fff;font-weight:600;">'
        '← Accueil</a></div>',
        unsafe_allow_html=True,
    )


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Affiche les filtres et retourne le DataFrame filtré.
    """
    genre_col = find_col(df, "Genre")
    dir_col   = find_col(df, "Direction") or find_col(df, "Departement") or find_col(df, "Département")
    age_col   = find_col(df, "Age")

    with st.expander("Filtres", expanded=False):
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        with c1:
            if dir_col:
                opts = ["Tous"] + sorted(df[dir_col].dropna().astype(str).unique())
                sel_dir = st.selectbox("Département / Direction", opts)
            else:
                sel_dir = "Tous"
                st.selectbox("Département / Direction", ["—"], disabled=True)
        with c2:
            if genre_col:
                opts = ["Tous"] + sorted(df[genre_col].dropna().astype(str).unique())
                sel_genre = st.selectbox("Genre", opts)
            else:
                sel_genre = "Tous"
                st.selectbox("Genre", ["—"], disabled=True)
        with c3:
            if age_col:
                ages = pd.to_numeric(df[age_col], errors="coerce").dropna()
                if not ages.empty:
                    age_rng = st.slider("Âge", int(ages.min()), int(ages.max()),
                                        (int(ages.min()), int(ages.max())))
                else:
                    age_rng = None
            else:
                age_rng = None
                st.slider("Âge", 18, 65, (18, 65), disabled=True)
        with c4:
            if st.button("Réinitialiser"):
                safe_rerun()

    # Application des filtres
    mask = pd.Series(True, index=df.index)
    if dir_col and sel_dir != "Tous":
        mask &= df[dir_col].astype(str) == sel_dir
    if genre_col and sel_genre != "Tous":
        mask &= df[genre_col].astype(str).map(normalize) == normalize(sel_genre)
    if age_rng and age_col:
        ages_s = pd.to_numeric(df[age_col], errors="coerce")
        mask &= ages_s.between(age_rng[0], age_rng[1])

    return df[mask].copy()


def render_tab_overview(df_f: pd.DataFrame, question_map: dict) -> None:
    """
    Onglet 1 — Vue d'ensemble :
    - KPIs démographiques + score global satisfait
    - Jauges % satisfaits par domaine
    """
    n = len(df_f)
    pct_sats = compute_pct_satisfait(df_f, question_map)
    pct_global = pct_sats.get("Global", 0.0)
    score_cols = [s for s in SCORE_GROUPS if s in df_f.columns]

    # ── Données démographiques ──────────────────────────────────────────────
    genre_col = find_col(df_f, "Genre")
    age_col   = find_col(df_f, "Age")
    anciennete_col = find_col(df_f, "Anciennete")
    male_pct =0.0
    male_count = 0
    anciennete_avg = None
    age_avg = None

    if genre_col:
        gs = df_f[genre_col].dropna().astype(str)
        counts_g = gs.value_counts()
        male_key   = next((k for k in counts_g.index if "hom" in k.lower()), None)
        total_g = counts_g.sum()
        if male_key:
            male_count = int(counts_g[male_key])
            male_pct = male_count / total_g * 100

    if age_col:
        ages = pd.to_numeric(df_f[age_col], errors="coerce").dropna()
        if not ages.empty:
            age_avg = int(round(ages.median()))

    if anciennete_col:
        anciennete = pd.to_numeric(df_f[anciennete_col], errors="coerce").dropna()
        if not anciennete.empty:
            anciennete_avg = int(round(anciennete.mean()))

    # ── KPI row (Score global + démographie) ───────────────────────────────
    sec_title("Indicateurs clés")
    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        kpi_card("Répondants", n, C["blue"])
    with kpi_cols[1]:
        color_global = C["green"] if pct_global >= 50 else C["red"]
        kpi_card("Satisfaction globale", pct_global, color_global, "%", decimals=0,
                sub="")
    with kpi_cols[2]:
        kpi_card(f"Hommes ({male_count})", male_pct, C["blue"], "%", decimals=0)
    with kpi_cols[3]:
        kpi_card(f"Anciennete ({anciennete_avg:.0f} ans)", anciennete_avg, C["orange"], " ans", decimals=0)
    with kpi_cols[4]:
        kpi_card("Âge moyen", f"{age_avg} ans" if age_avg else "—", C["text"])

    # ── Jauges % satisfaits par domaine ────────────────────────────────────
    if score_cols:
        sec_title("Satisfaction par domaine: Pourcentage d'Employés Satisfaits")
        gauge_cols = st.columns(len(score_cols))
        for i, domain in enumerate(score_cols):
            pct = pct_sats.get(domain, 0.0)
            display_pct = int(pct)
            badge = ("", "#15803D", "satisfait")
            with gauge_cols[i]:
                semi_gauge(display_pct, C["green"],
                        domain, "",
                        key=f"g_{domain}", badge_override=badge)

    score_cols = [s for s in SCORE_GROUPS if s in df_f.columns]
    q_stats    = question_stats(df_f, question_map)
    top_risks     = q_stats.nsmallest(5, "pct_sat") if not q_stats.empty else pd.DataFrame()
    top_strengths = q_stats.nlargest(5, "pct_sat")  if not q_stats.empty else pd.DataFrame()

    # ── Axes d'amélioration / Atouts ───────────────────────────────────────
    sec_title("Axes d'amélioration & Atouts clés")
    col_risk, col_str = st.columns(2)

    def _render_item_list(df_items: pd.DataFrame, is_risk: bool) -> None:
        """Render une liste d'items (risques ou atouts) via components.html."""
        color = C["red"] if is_risk else C["green"]
        title = "Axes d'amélioration prioritaires" if is_risk else "Atouts clés à mettre en avant"
        pct_key = "pct_ins" if is_risk else "pct_sat"
        pct_label = "insatisfaits" if is_risk else "satisfaits"

        header = textwrap.dedent(f"""
        <style>
        .q-items {{ margin-top:18px;display:block }}
        .q-items .item-row {{ margin-bottom:18px;padding:10px 12px;border-radius:10px;
        background:#fff;box-shadow:0 6px 18px rgba(16,24,40,0.03) }}
        </style>
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.6rem;">
        <span style="color:{color};"><b>{title}</b></span>
        </div>
        """)
        items_html = []
        for _, row in df_items.iterrows():
            bar = dual_status_bar(row["pct_ins"],row["pct_sat"],highlight="red" if is_risk else "green".strip())
            items_html.append(textwrap.dedent(f"""
            <div class="item-row" style="border-left:3px solid {color};">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
                <span style="font-size:0.79rem;color:#3B5878;font-weight:600;line-height:1.4;">
                {row['question']}</span>
                <div style="font-size:0.9rem;font-weight:800;color:{color};">
                {row[pct_key]:.0f}% {pct_label}</div>
            </div>
            {bar}
            </div>
            """))
        full_html = header + "<div class='q-items'>" + "".join(items_html) + "</div>"
        h = max(180, 90 * max(1, len(df_items)) + 40)
        components.html(full_html, height=h)

    with col_risk:
        _render_item_list(top_risks, is_risk=True)
    with col_str:
        _render_item_list(top_strengths, is_risk=False)


def render_tab_detail(df_f: pd.DataFrame, question_map: dict) -> None:
    """
    Onglet 2 — Analyses détaillées :
    - Axes d'amélioration & Atouts clés (top 5)
    - Analyse univariée (distribution socio)
    - Analyse bivariée (par domaine OU par question, selon socio)
    """
    socio_cols = [c for c in SOCIO_CANDIDATES if c in df_f.columns]
    score_cols = [s for s in SCORE_GROUPS if s in df_f.columns]


    # ── Analyse univariée ───────────────────────────────────────────────────
    sec_title("Analyse univariée — variables sociodémographiques")
    if not socio_cols:
        st.warning("Aucune variable sociodémographique reconnue dans le fichier.")
    else:
        sel_uni = st.selectbox("Variable à analyser", socio_cols, key="uni_var")
        st.plotly_chart(
            chart_bar_univarie(df_f[sel_uni].astype(str), sel_uni),
            use_container_width=True,
        )
        with st.expander("Tableau de fréquences", expanded=False):
            freq = df_f[sel_uni].astype(str).value_counts().reset_index()
            freq.columns = [sel_uni, "Effectif"]
            freq["Pourcentage (%)"] = (freq["Effectif"] / freq["Effectif"].sum() * 100).round(1)
            st.dataframe(freq, use_container_width=True, hide_index=True)

    # ── Analyse bivariée ────────────────────────────────────────────────────
    sec_title("Analyse bivariée — Satisfait / Insatisfait selon variable socio")
    if not socio_cols or not score_cols:
        st.warning("Données insuffisantes pour l'analyse bivariée.")
        return

    b1, b2 = st.columns(2)
    with b1:
        sel_socio = st.selectbox("Variable sociodémographique", socio_cols, key="bi_socio")
    with b2:
        sel_domain = st.selectbox("Domaine QVT", list(SCORE_GROUPS.keys()), key="bi_domain")

    # Sélecteur : Domaine entier OU question spécifique
    view_mode = st.radio(
        "Niveau d'analyse",
        ["Vue domaine (toutes les questions)", "Vue question (une question du domaine)"],
        horizontal=True,
        key="bi_mode",
    )

    if view_mode.startswith("Vue domaine"):
        # --- Graphique par domaine (toutes les questions agrégées) ---
        fig = chart_bivariate_domain(df_f, sel_socio, sel_domain, question_map)
        st.plotly_chart(fig, use_container_width=True)

    else:
        # --- Graphique par question spécifique du domaine ---
        qs_in_domain = [q for q in SCORE_GROUPS.get(sel_domain, []) if q in question_map]
        if not qs_in_domain:
            st.warning("Aucune question disponible pour ce domaine.")
        else:
            sel_q = st.selectbox("Question du domaine", qs_in_domain, key="bi_question")
            fig = chart_bivariate_question(df_f, sel_socio, sel_q, question_map)
            st.plotly_chart(fig, use_container_width=True)

            # Tableau croisé détaillé
            with st.expander("Tableau croisé détaillé", expanded=False):
                tmp = df_f.copy()
                tmp["Reponse"] = recode_to_2_classes(tmp[question_map[sel_q]])
                counts = pd.crosstab(tmp[sel_socio], tmp["Reponse"])
                counts = counts.reindex(columns=RESPONSE_CLASSES, fill_value=0)
                pct = counts.div(counts.sum(axis=1).replace(0, 1), axis=0) * 100

                # Table HTML colorée
                def _fg(hexcolor: str) -> str:
                    h = hexcolor.lstrip("#")
                    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                    lum = 0.2126*(r/255) + 0.7152*(g/255) + 0.0722*(b/255)
                    return "#ffffff" if lum < 0.65 else C["text"]

                html_rows = ['<div style="overflow:auto;padding-top:6px;">',
                            '<table style="border-collapse:separate;border-spacing:8px;width:100%;'
                            'font-family:Plus Jakarta Sans,sans-serif;">',
                            '<thead><tr>',
                            f'<th style="text-align:left;padding:8px 12px;color:{C["muted"]};'
                            f'font-weight:600;">{sel_socio}</th>']
                for resp in RESPONSE_CLASSES:
                    html_rows.append(f'<th style="text-align:center;padding:8px 12px;'
                                    f'color:{C["muted"]};font-weight:600;">{resp}</th>')
                html_rows.append('</tr></thead><tbody>')
                for grp in counts.index:
                    html_rows.append('<tr>')
                    html_rows.append(f'<td style="padding:8px 12px;color:{C["text"]};font-weight:600;">{grp}</td>')
                    for resp in RESPONSE_CLASSES:
                        raw = int(counts.loc[grp, resp])
                        pctv = pct.loc[grp, resp]
                        bg = RESPONSE_COLORS.get(resp, "#ffffff")
                        fg = _fg(bg)
                        html_rows.append(
                            f'<td style="background:{bg};color:{fg};padding:8px 12px;'
                            f'text-align:center;border-radius:6px;min-width:80px;">'
                            f'{pctv:.1f}% ({raw})</td>'
                        )
                    html_rows.append('</tr>')
                html_rows.append('</tbody></table></div>')
                h = min(600, 48 + len(counts) * 44)
                components.html("\n".join(html_rows), height=h)



# ─────────────────────────────────────────────────────────────────────────────
# 8. FONCTION PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="QVT Dashboard",
        page_icon="❤️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css()
    render_topbar()

    # Gestion du bouton "Accueil"
    params = get_query_params_safe()
    if params.get("back"):
        try:
            set_query_params_safe()
            st.switch_page("app.py")
        except Exception:
            pass

    # ── Import du fichier Excel ─────────────────────────────────────────────
    uploaded = st.file_uploader("Importer un fichier Excel (.xlsx)", type=["xlsx", "xls"])
    if uploaded is None:
        st.info("Importez votre fichier Excel pour démarrer l'analyse.")
        st.stop()

    # Chargement, enrichissement et scoring
    df_raw = load_excel(uploaded)
    df_raw = add_derived_columns(df_raw)
    question_map = resolve_questions(df_raw)

    if not question_map:
        st.error("Aucune colonne de question reconnue dans le fichier.")
        st.stop()

    df = compute_scores(df_raw, question_map)

    # ── Filtres ────────────────────────────────────────────────────────────
    df_f = render_filters(df)

    if len(df_f) == 0:
        st.warning("Aucun répondant correspondant aux filtres.")
        st.stop()

    # ── Onglets ────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["Vue d'ensemble", "Analyses détaillées"])

    with tab1:
        render_tab_overview(df_f, question_map)

    with tab2:
        render_tab_detail(df_f, question_map)



if __name__ == "__main__":
    main()
