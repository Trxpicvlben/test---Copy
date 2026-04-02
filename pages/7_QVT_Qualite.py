# DASHBOARD QVT — version stylée (Karasek look)
# Lancer : streamlit run 1.py
# Dépendances : pip install streamlit plotly pandas numpy openpyxl

import re
import sys
import io
import base64
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import textwrap

# ------------------------------
# Palette & constantes (abrégées)
# ------------------------------
C = {
    "bg":        "#F0F7FF",
    "card":      "#FFFFFF",
    "text":      "#0F2633",    # neutral dark for good contrast
    "muted":     "#7F98A8",    # mid-muted gray-blue
    "border":    "#E6EEF6",
    # Mid-tone palette (neither vivid nor washed)
    "blue":      "#4A90E2",
    "orange":    "#F39C6B",
    "green":     "#66BB6A",
    "red":       "#E45757",
    "purple":    "#A78BFA",
    "dark_red":  "#FD0000",
    "light_red": "#E85D35",
    "light_grn": "#6DCF7A",
    "dark_grn":  "#1B7A32",
    "gray":      "#D5DADE22",
}

RESPONSE_ORDER  = ["Très insatisfait", "Insatisfait", "Satisfait", "Très satisfait"]
RESPONSE_COLORS = {
    # mid-tone response colors
    "Très insatisfait": C["red"],            # mid red
    "Insatisfait":      C["red"],           # mid orange
    "Satisfait":        C["green"],           # soft green
    "Très satisfait":   C["green"],           # mid-dark green
}

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

SCORE_COLORS = {
    "Sens du Travail":             C["purple"],
    "Relations Interpersonnelles": C["blue"],
    "Santé & Environnement":       C["green"],
    "Reconnaissance & Évolution":  C["orange"],
    "Équilibre de Vie":            "#F59E0B",
}

SOCIO_CANDIDATES = [
    "Departement", "Département", "Direction",
    "Poste de travail", "Fonction",
    "Genre",
    "Service", "Situation_matrimoniale",
    "Categorie_IMC", "Classe_Anciennete", "TrancheAge",
]

# ------------------------------
# CSS embarqué (Karasek look)
# ------------------------------
def _get_inline_css() -> str:
    # (utilise la feuille CSS du modèle — réduit pour lisibilité mais contient les classes principales)
    return """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,400;1,9..144,600&display=swap');
:root{--bg-soft:#eef2f7;--card:#ffffff;--text:#2f3d55;--border:#dde5f2}
html,body,[class*="css"],.stApp{font-family:'Plus Jakarta Sans',sans-serif!important}
.stApp{background:linear-gradient(180deg,#f4f6fb 0%,var(--bg-soft) 100%);color:var(--text)}
.section-title{display:flex;align-items:center;gap:0.7rem;font-family:'Fraunces',Georgia,serif!important;font-style:italic!important;font-size:1.25rem!important;color:#0F2340!important;margin:1.6rem 0 1rem!important;padding-bottom:0.65rem!important;border-bottom:2px solid #dde5f2!important}
.section-title::before{content:'';display:inline-block;width:4px;height:22px;background:linear-gradient(180deg,#2f66b3 0%,#4f8be4 100%);border-radius:2px;flex-shrink:0}
.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:8px}
.card-container{background:#fff;padding:20px;border-radius:14px;border:1px solid #f0f2f6;box-shadow:0 6px 20px rgba(0,0,0,0.04);text-align:center}
.kpi-card,.gauge-card{background:#fff;border:1px solid #dde5f2;border-radius:12px;padding:12px}
.kpi-label{font-size:0.72rem;color:#6B88A8;text-transform:uppercase;font-weight:700;margin-bottom:6px}
.kpi-value{font-family:'Fraunces',serif;font-size:1.6rem;font-weight:800}
.badge{display:inline-block;font-size:0.64rem;font-weight:700;padding:0.18rem 0.65rem;border-radius:999px}
.badge-red{background:#FEE2E2;color:#B91C1C}.badge-green{background:#DCFCE7;color:#15803D}.badge-blue{background:rgba(56,163,232,0.1);color:#38A3E8}
.back-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:10px 16px;border-radius:14px;background:linear-gradient(135deg,#2f66b3,#4f8be4);color:#ffffff!important;font-weight:700;text-decoration:none!important;box-shadow:0 6px 18px rgba(47,102,179,0.12);border:1px solid rgba(79,139,228,0.12)}
.back-btn:hover{filter:brightness(0.95);box-shadow:0 8px 22px rgba(47,102,179,0.14)}
.back-btn:focus{outline:none;box-shadow:0 8px 22px rgba(47,102,179,0.14)
.axe_title{color:"#E6350D"!important}}

/* Shared spacing for risk/strength items (applies to both columns) */
.q-items{margin-top:20px}
.q-items .item-row{margin-bottom:22px;padding:12px 16px;border-radius:10px;background:#fff;box-shadow:0 6px 18px rgba(16,24,40,0.03);}

/* Tab styling inspired from 2.py (data-baseweb selectors) */
[data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 3px !important;
    border: 1px solid #dde5f2 !important;
    box-shadow: 0 2px 8px rgba(47,102,179,0.07) !important;
}

[data-baseweb="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    color: #6B88A8 !important;
    border-radius: 9px !important;
    padding: 0.5rem 1.4rem !important;
    transition: all 0.18s !important;
}

[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(135deg, #2f66b3, #4f8be4) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 3px 12px rgba(47,102,179,0.30) !important;
}

[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] {
    display: none !important;
}
"""

def load_css() -> None:
    st.markdown(f"<style>{_get_inline_css()}</style>", unsafe_allow_html=True)

# Query param helpers (compatibility across Streamlit versions)
def get_query_params_safe():
    """Return query params using the most appropriate Streamlit API.

    Prefer the new `st.query_params` property when available, then
    fall back to `st.get_query_params()` if present. Always avoid
    calling experimental_ APIs directly to prevent deprecation warnings.
    """
    try:
        # property introduced in newer Streamlit versions
        if hasattr(st, "query_params"):
            return dict(st.query_params)
    except Exception:
        pass
    # older stable API
    if hasattr(st, "get_query_params"):
        try:
            return st.get_query_params()
        except Exception:
            pass
    return {}

def set_query_params_safe(**params):
    """Set query params using the stable Streamlit API.

    Prefer `st.set_query_params()` if available; fall back to the
    experimental API only if necessary (kept as last resort).
    """
    if hasattr(st, "set_query_params"):
        try:
            return st.set_query_params(**params)
        except Exception:
            pass
    # Do not call experimental APIs to avoid deprecation warnings; if
    # the stable API is not available, silently skip setting params.
    return None


def safe_rerun():
    """Rerun the app using the best available API without causing deprecation warnings."""
    if hasattr(st, "rerun"):
        try:
            return st.rerun()
        except Exception:
            pass
    # Avoid calling experimental_rerun() to prevent visible deprecation warnings
    # on newer Streamlit versions; if rerun isn't available, do nothing.
    return None

# ------------------------------
# Helpers: normalisation & recodage
# ------------------------------
def normalize(text):
    t = str(text).strip().lower()
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", t)

def find_col(df, target):
    """Find a column in dataframe using a robust normalized match.

    Tries, in order: exact normalized match, startswith, contains, then
    a close match using difflib. Returns the original column name or None.
    """
    import difflib
    if df is None:
        return None
    nt = normalize(target)
    # normalized -> original mapping
    norm_map = {normalize(c): c for c in df.columns}
    # exact
    if nt in norm_map:
        return norm_map[nt]
    # startswith
    for k, orig in norm_map.items():
        if k.startswith(nt) or nt.startswith(k):
            return orig
    # contains
    for k, orig in norm_map.items():
        if nt in k or k in nt:
            return orig
    # fuzzy close match
    close = difflib.get_close_matches(nt, list(norm_map.keys()), n=1, cutoff=0.75)
    if close:
        return norm_map[close[0]]
    return None

def recode_response(series):
    out = pd.Series(pd.NA, index=series.index, dtype="object")
    num = pd.to_numeric(series, errors="coerce")
    out.loc[num == 1] = "Insatisfait"
    out.loc[num == 2] = "Insatisfait"
    out.loc[num == 3] = "Satisfait"
    out.loc[num == 4] = "Satisfait"
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

def add_derived_columns(df):
    out = df.copy()
    age_col  = find_col(out, "Age")
    anc_col  = find_col(out, "Anciennete")
    poids_col = find_col(out, "Poids")
    taille_col = find_col(out, "Taille")
    imc_col  = find_col(out, "IMC")
    # additional socio columns will be detected and copied below

    if age_col and "TrancheAge" not in out.columns:
        age = pd.to_numeric(out[age_col], errors="coerce")
        out["TrancheAge"] = pd.cut(age, bins=[0,20,30,40,50,60,np.inf],
                                labels=["<20","20-30","31-40","41-50","51-60","60+"], right=False)
    if anc_col and "Classe_Anciennete" not in out.columns:
        anc = pd.to_numeric(out[anc_col], errors="coerce")
        out["Classe_Anciennete"] = pd.cut(anc, bins=[0,2,5,10,20,np.inf],
                                        labels=["0-2 ans","3-5 ans","6-10 ans","11-20 ans","21+ ans"], include_lowest=True)
    if poids_col and taille_col and "IMC" not in out.columns:
        p = pd.to_numeric(out[poids_col], errors="coerce")
        t = pd.to_numeric(out[taille_col], errors="coerce")
        out["IMC"] = np.round(p / (t / 100) ** 2, 1)
    if (imc_col or "IMC" in out.columns) and "Categorie_IMC" not in out.columns:
        imc_vals = pd.to_numeric(out.get(imc_col, out.get("IMC", pd.Series(dtype=float))), errors="coerce")
        out["Categorie_IMC"] = pd.cut(imc_vals, bins=[-np.inf,18.5,24.9,29.9,np.inf],
                                    labels=["Sous-poids","Normal","Surpoids","Obésité"])
    # Ensure a standard set of socio columns exist (copy from detected variants)
    standard_socio = [
        "Taille", "Poids", "Departement", "Direction", "Anciennete",
        "Service", "Poste de travail", "Age", "Genre", "Fonction", "Situation_matrimoniale"
    ]
    for std in standard_socio:
        try:
            found = find_col(out, std)
            if found and std not in out.columns:
                out[std] = out[found]
        except Exception:
            # be permissive; if anything goes wrong continue
            continue
    return out

def resolve_questions(df):
    return {q: find_col(df, q) for q in QUESTIONS if find_col(df, q)}

# ------------------------------
# UI helpers (sec_title, kpi_card, gauges)
# ------------------------------
def sec_title(text: str) -> None:
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)

def kpi_card(label, value, color=C["blue"], suffix="", decimals=0, sub=""):
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            disp = f"{value:.{decimals}f}{suffix}"
        else:
            disp = f"{value}{suffix}"
    except Exception:
        disp = str(value)
    sub_html = f'<div class="kpi-sub" style="font-size:0.72rem;color:#9AAFBF;margin-top:6px">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="kpi-card">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value" style="color:{color};">{disp}</div>
    {sub_html}
    </div>""", unsafe_allow_html=True)

def semi_gauge(pct, color, label, sublabel, key="", badge_override=None):
    """Rendu SVG d'une jauge semi-circulaire.

    badge_override: optional tuple (badge_bg, badge_c, badge_t) to force the badge
    (background color, text color, label). If None, the badge is derived from pct.
    """
    pct = max(0.0, min(100.0, float(pct)))
    angle = pct / 100 * 180
    r, cx, cy = 68, 88, 78
    ex = cx + r * np.cos(np.radians(180 - angle))
    ey = cy - r * np.sin(np.radians(180 - angle))
    arc = f'M {cx-r} {cy} A {r} {r} 0 0 1 {ex:.2f} {ey:.2f}' if angle > 1 else ""
    # Determine badge (or use override provided)
    if badge_override is not None:
        badge_bg, badge_c, badge_t = badge_override
    else:
        # Use green for Élevé; use red for both Moyen and Faible (per user request)
        if pct > 65:
            badge_bg, badge_c, badge_t = ("#DCFCE7", "#15803D", "Élevé")
        elif pct > 40:
            badge_bg, badge_c, badge_t = ("#FEE2E2", "#B91C1C", "Moyen")
        else:
            badge_bg, badge_c, badge_t = ("#FEE2E2", "#B91C1C", "Faible")
    st.markdown(f"""
    <div class="gauge-card">
        <svg width="176" height="96" style="display:block;margin:0 auto;">
            <path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}"
                fill="none" stroke="#EDF5FD" stroke-width="12" stroke-linecap="round"/>
            {'<path d="' + arc + '" fill="none" stroke="' + color + '" stroke-width="12" stroke-linecap="round"/>' if arc else ''}
            <text x="{cx}" y="76" text-anchor="middle" font-size="23" font-weight="800"
                fill="{color}" font-family="DM Serif Display, serif">{pct:.0f}</text>
            <text x="{cx}" y="92" text-anchor="middle" font-size="10" fill="#6B88A8"
                font-family="Plus Jakarta Sans">%</text>
        </svg>
        <div style="font-weight:700;font-size:0.82rem;color:{C['text']};line-height:1.35;
                    text-align:center;margin-top:0.15rem;">{label}</div>
        <div style="font-size:0.7rem;color:{C['muted']};text-align:center;
                    margin:0.15rem 0 0.45rem;line-height:1.4;">{sublabel}</div>
        <div style="text-align:center;">
            <span class="badge" style="background:{badge_bg};color:{badge_c};">{badge_t}</span>
        </div>
    </div>""", unsafe_allow_html=True)

def dual_status_bar(neg_pct, pos_pct, neg_color, pos_color):
        """Return an HTML fragment showing negative/positive stacked bar with percentages."""
        try:
                n = max(0.0, float(neg_pct))
        except Exception:
                n = 0.0
        try:
                p = max(0.0, float(pos_pct))
        except Exception:
                p = 0.0
        total = n + p
        if total == 0:
                return '<div style="height:8px;border-radius:8px;background:#E0E7EF;margin-top:6px"></div>'
        # scale to 100
        n_w = n / total * 100
        p_w = p / total * 100
        return f"""
        <div style="display:flex;align-items:center;gap:8px;margin-top:6px;">
            <div style="flex:1;background:#f1f5f9;border-radius:8px;overflow:hidden;height:12px;position:relative;">
                <div style="width:{n_w:.2f}%;height:100%;background:{neg_color};float:left;"></div>
                <div style="width:{p_w:.2f}%;height:100%;background:{pos_color};float:right;"></div>
            </div>

        </div>
        """
# ------------------------------
# Plotly helpers (small set)
# ------------------------------
LAYOUT_BASE = dict(
    plot_bgcolor="#FAFCFF",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color=C["text"], size=12),
    margin=dict(l=40, r=20, t=50, b=40),
)

def apply_layout(fig, title="", height=None):
    upd = dict(**LAYOUT_BASE, title=dict(text=title, font=dict(family="DM Serif Display, serif", size=14, color=C["text"]), x=0.02))
    if height:
        upd["height"] = height
    fig.update_layout(**upd)
    return fig

def radar_chart(score_means: dict) -> go.Figure:
    dims  = list(score_means.keys())
    vals  = list(score_means.values())
    if not dims:
        return go.Figure()
    dims_ = dims + [dims[0]]
    vals_ = vals + [vals[0]]
    fig = go.Figure()
    # Radar: plot only the measured scores (remove hardcoded reference to a 4-point scale)
    fig.add_trace(go.Scatterpolar(r=vals_, theta=dims_, fill="toself", fillcolor="rgba(56,163,232,0.13)", line=dict(color=C["blue"], width=2.5), marker=dict(color=C["blue"], size=7), name="Score moyen"))
    # Do not force a radial axis range tied to a 4-point scale; let Plotly choose appropriate bounds
    fig.update_layout(polar=dict(radialaxis=dict()), height=360, margin=dict(l=60,r=60,t=40,b=40))
    return fig


def stacked_pct_chart(crosstab: pd.DataFrame, title: str, y_title: str) -> go.Figure:
    fig = go.Figure()
    for label in RESPONSE_ORDER:
        if label not in crosstab.columns:
            continue
        # show white, bold percent labels inside each segment
        fig.add_trace(go.Bar(
            x=crosstab[label], y=crosstab.index, orientation="h",
            name=label, marker_color=RESPONSE_COLORS[label],
            texttemplate="<b>%{x:.1f}%</b>", textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=11, family="Plus Jakarta Sans"),
            marker=dict(line=dict(color="white", width=0.8)),
        ))
    fig.update_layout(
        barmode="stack",
        title=dict(text=title, font=dict(family="DM Serif Display, serif", size=13, color=C["text"]), x=0.01),
    xaxis=dict(range=[0, 100], title="Pourcentage (%)", ticksuffix="%",
        showgrid=True, gridcolor="#F5F7FA", zeroline=False,
        tickfont=dict(color=C["text"], size=11)),
    yaxis=dict(title=y_title, tickfont=dict(color=C["text"], size=11), showgrid=False),
        legend_title="Réponses",
        plot_bgcolor="#FAFCFF", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color=C["text"], size=11),
        margin=dict(l=20, r=20, t=50, b=30),
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor=C["border"], borderwidth=1),
    )
    return fig


def bar_univarie(series: pd.Series, var_label: str) -> go.Figure:
    counts = series.value_counts().reset_index()
    counts.columns = [var_label, "n"]
    total = counts["n"].sum()
    counts["pct"] = counts["n"] / total * 100
    # Mid-tone palette for category bars
    palette = ["#4A90E2", "#F39C6B", "#A78BFA", "#66BB6A", "#F2B86B",
            "#4EC0D9", "#FB9A6B", "#84CC6A"]
    fig = go.Figure()
    for i, row in counts.iterrows():
        # show percent and effectif inside the bar in white and bold, e.g. "56.0% (112)"
        txt = f"{row['pct']:.1f}% ({int(row['n'])})"
        fig.add_trace(go.Bar(
            y=[str(row[var_label])], x=[row["pct"]], orientation="h",
            marker_color=palette[i % len(palette)], opacity=0.88,
            text=txt,
            textposition="inside",
            insidetextanchor="middle",
            # use a valid weight value for Plotly (either int or 'normal'/'bold')
            textfont=dict(color="white", size=12, family="Plus Jakarta Sans", weight='bold'),
            showlegend=False, name=str(row[var_label]),
        ))
    height = max(260, len(counts) * 52 + 80)
    fig = apply_layout(fig, f"Distribution — {var_label}", height)
    # Limit axis to 0..100%
    fig.update_xaxes(range=[0, 100], title_text="Pourcentage (%)", ticksuffix="%", tickfont=dict(color=C["text"]))
    fig.update_yaxes(title_text=var_label, tickfont=dict(color=C["text"]))
    return fig


def bar_bivarie(df_sub: pd.DataFrame, x_col: str, y_col: str, y_label: str) -> go.Figure:
    """Score moyen d'une dimension QVT par catégorie d'une variable socio."""
    groups = df_sub.groupby(x_col)[y_col].agg(["mean", "count"]).reset_index()
    groups.columns = [x_col, "mean", "n"]
    groups = groups.sort_values("mean", ascending=True)

    # Use mid-tone conditional coloring based on mean
    colors_list = [
        C["green"] if v >= 3 else C["orange"] if v >= 2.5 else C["red"]
        for v in groups["mean"]
    ]
    fig = go.Figure(go.Bar(
        y=groups[x_col].astype(str),
        x=groups["mean"],
        orientation="h",
        marker_color=colors_list,
        opacity=0.88,
        text=[f"{v:.2f}  (n={n})" for v, n in zip(groups["mean"], groups["n"])],
        textposition="outside",
        textfont=dict(color=C["text"], size=11, family="Plus Jakarta Sans"),
    ))
    height = max(260, len(groups) * 52 + 80)
    fig = apply_layout(fig, f"{y_label} selon {x_col}", height)
    # Avoid forcing axis bounds linked to a 4-point scale and remove "/4" from title
    fig.update_xaxes(title_text="Score moyen", tickfont=dict(color=C["text"]))
    fig.update_yaxes(title_text=x_col, tickfont=dict(color=C["text"]))
    # (removed fixed reference line tied to a 4-point scale)
    return fig


def stacked_bivarie(df_sub: pd.DataFrame, x_col: str, q_col: str, q_label: str) -> go.Figure:
    """Répartition des réponses à une question selon une variable socio."""
    tmp = df_sub.copy()
    tmp["Reponse"] = recode_response(tmp[q_col])
    ct = pd.crosstab(tmp[x_col], tmp["Reponse"], normalize="index") * 100
    ct = ct.reindex(columns=RESPONSE_ORDER, fill_value=0)
    return stacked_pct_chart(ct, f"Réponses à « {q_label[:55]}… » selon {x_col}", x_col)

# ------------------------------
# Data loading & scoring
# ------------------------------
@st.cache_data
def load_excel(file) -> pd.DataFrame:
    return pd.read_excel(file)

def compute_scores(df: pd.DataFrame, question_map: dict) -> pd.DataFrame:
    out = df.copy()
    for score_name, qs in SCORE_GROUPS.items():
        cols = [question_map[q] for q in qs if q in question_map]
        if cols:
            raw = out[cols].apply(pd.to_numeric, errors="coerce")
            out[score_name] = raw.mean(axis=1)
    q_cols = list(question_map.values())
    if q_cols:
        out["Score_Global"] = out[q_cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    return out

def question_stats(df: pd.DataFrame, question_map: dict) -> pd.DataFrame:
    rows = []
    for q, col in question_map.items():
        recoded = recode_response(df[col])
        counts = recoded.value_counts()
        total = counts.sum()
        pct_neg = (counts.get("Très insatisfait", 0) + counts.get("Insatisfait", 0)) / total * 100 if total else 0
        pct_pos = (counts.get("Satisfait", 0) + counts.get("Très satisfait", 0)) / total * 100 if total else 0
        avg = pd.to_numeric(df[col], errors="coerce").mean()
        rows.append({"question": q, "col": col, "pct_neg": pct_neg, "pct_pos": pct_pos, "avg": avg, "n_valid": int(total)})
    return pd.DataFrame(rows).sort_values("avg")

# ------------------------------
# App principale
# ------------------------------
def main():
    st.set_page_config(page_title="QVT Dashboard", page_icon="❤️", layout="wide", initial_sidebar_state="expanded")
    load_css()

    # Topbar (fonts + top header like reference)
    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
        '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,400;1,9..144,600&display=swap" rel="stylesheet">',
        unsafe_allow_html=True
    )
    # Topbar: full-width card with icon/title and back link on the right
    st.markdown(
        '<div style="display:flex;justify-content:space-between;align-items:center;background:white;border-radius:12px;padding:14px 24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06),0 8px 20px rgba(47,78,64,0.06);border:1px solid #e8edf5;">'
        '<div style="display:flex;align-items:center;gap:12px;">'
            '<div style="width:48px;height:48px;background:linear-gradient(135deg,#27AE60,#2ECC71);border-radius:12px;display:flex;align-items:center;justify-content:center;">'
                '<svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
                '<path fill="white" d="M12 21s-7-4.35-9-6.5C1 11.5 4 7 7.5 7 9.24 7 11 8 12 9.5 13 8 14.76 7 16.5 7 20 7 23 11.5 21 14.5 19 16.65 12 21 12 21z"/>'
                '</svg>'
            '</div>'
            '<div style="margin-left:4px;">'
                '<div style="font-size:18px;font-weight:700;color:#0f2130;font-family:\'Plus Jakarta Sans\',sans-serif;">QVT — Qualité de Vie au Travail</div>'
                '<div style="font-size:12px;color:#4b6272;margin-top:2px;font-family:\'Plus Jakarta Sans\',sans-serif;">Analyse de la satisfaction et du bien-être · YODAN Analytics</div>'
            '</div>'
        '</div>'
        '<div>'
            '<a href="?back=1" class="back-btn" style="text-decoration:none;color:#3b82f6;font-weight:600;">← Accueil</a>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    params = get_query_params_safe()
    if params.get("back"):
        try:
            # clear params to avoid looping
            set_query_params_safe()
            st.switch_page("app.py")
        except Exception:
            pass

    # Upload
    uploaded = st.file_uploader("Importer un fichier Excel (.xlsx)", type=["xlsx", "xls"])
    if uploaded is None:
        st.info("Importez votre fichier Excel pour démarrer l'analyse (colonnes QVT + variables sociodémographiques).")
        st.stop()

    df_raw = load_excel(uploaded)
    df_raw = add_derived_columns(df_raw)
    question_map = resolve_questions(df_raw)

    if not question_map:
        st.error("Aucune colonne de question reconnue dans le fichier.")
        st.stop()

    df = compute_scores(df_raw, question_map)

    # Filtres simples
    genre_col = find_col(df, "Genre")
    dir_col   = find_col(df, "Direction") or find_col(df, "Departement") or find_col(df, "Département")
    with st.expander("Filtres", expanded=False):
        cols = st.columns([2,2,2,1])
        with cols[0]:
            if dir_col:
                opts_dir = ["Tous"] + sorted(df[dir_col].dropna().astype(str).unique().tolist())
                sel_dir = st.selectbox("Département / Direction", opts_dir, index=0)
            else:
                sel_dir = "Tous"
                st.selectbox("Département / Direction", ["—"], disabled=True)
        with cols[1]:
            if genre_col:
                opts_genre = ["Tous"] + sorted(df[genre_col].dropna().astype(str).unique().tolist())
                sel_genre = st.selectbox("Genre", opts_genre, index=0)
            else:
                sel_genre = "Tous"
                st.selectbox("Genre", ["—"], disabled=True)
        with cols[2]:
            age_col = find_col(df, "Age")
            if age_col:
                ages = pd.to_numeric(df[age_col], errors="coerce").dropna()
                if not ages.empty:
                    age_rng = st.slider("Âge", int(ages.min()), int(ages.max()), (int(ages.min()), int(ages.max())))
                else:
                    age_rng = None
            else:
                age_rng = None
                st.slider("Âge", 18, 65, (18,65), disabled=True)
        with cols[3]:
            if st.button("Réinitialiser"):
                safe_rerun()

    mask = pd.Series(True, index=df.index)
    if dir_col and sel_dir != "Tous":
        mask &= df[dir_col].astype(str) == sel_dir
    if genre_col and sel_genre != "Tous":
        # Compare normalized strings to tolerate case / whitespace / accent variations
        mask &= df[genre_col].astype(str).map(normalize) == normalize(sel_genre)
    if 'age_rng' in locals() and age_col and age_rng:
        ages_s = pd.to_numeric(df[age_col], errors="coerce")
        mask &= ages_s.between(age_rng[0], age_rng[1])
    df_f = df[mask].copy()
    n = len(df_f)
    if n == 0:
        st.warning("Aucun répondant correspondant aux filtres.")
        st.stop()

    # Derived values used by the tabs
    avg_global = df_f["Score_Global"].mean() if "Score_Global" in df_f else 0.0
    # available questions, score columns and socio columns used in analyses
    available_questions = list(question_map.keys())
    score_cols = [s for s in SCORE_GROUPS if s in df.columns]
    socio_cols = [c for c in SOCIO_CANDIDATES if c in df.columns]
    # score means for radar / bars
    score_means = {s: df_f[s].mean() for s in score_cols}
    # question statistics used in risk/strength lists
    q_stats = question_stats(df_f, question_map)
    top_risks = q_stats.nsmallest(5, "avg") if not q_stats.empty else pd.DataFrame()
    top_strengths = q_stats.nlargest(5, "avg") if not q_stats.empty else pd.DataFrame()

    # Tabs (full analyses copied from the detailed script)
    tab1, tab2, tab3 = st.tabs(["Vue d'ensemble", "Analyses détaillées", "Analyse finales"])

    with tab1:
        sec_title("Indicateurs clés")
        pct_sat = (df_f["Score_Global"] >= 3).mean() * 100 if "Score_Global" in df_f else 0

        # Demographic KPIs: nombre d'hommes / nombre de femmes / âge moyen
        male_count = 0
        female_count = 0
        male_pct = 0.0
        female_pct = 0.0
        age_avg = None

        # Compute gender counts on the currently filtered dataframe so KPIs react to the Genre filter
        if genre_col:
            gs = df_f[genre_col].dropna().astype(str)
            if not gs.empty:
                counts = gs.value_counts()
                male_key = next((k for k in counts.index if 'hom' in k.lower()), None)
                female_key = next((k for k in counts.index if 'fem' in k.lower()), None)
                if male_key:
                    male_count = int(counts.get(male_key, 0))
                if female_key:
                    female_count = int(counts.get(female_key, 0))
                total = int(counts.sum())
                if total:
                    male_pct = male_count / total * 100
                    female_pct = female_count / total * 100

        age_col_now = find_col(df, "Age")
        if age_col_now:
            ages = pd.to_numeric(df_f[age_col_now], errors="coerce").dropna()
            if not ages.empty:
                age_avg = int(round(ages.mean()))

        # Prepare KPI items in order and create responsive columns so remaining KPIs expand
        displayed = ["Répondants"]
        sel_genre_norm = normalize(sel_genre) if sel_genre and isinstance(sel_genre, str) else "tous"
        show_male = (sel_genre == "Tous") or ("hom" in sel_genre_norm)
        show_female = (sel_genre == "Tous") or ("fem" in sel_genre_norm)
        if show_male and male_count > 0:
            displayed.append("Homme")
        if show_female and female_count > 0:
            displayed.append("Femme")
        displayed.append("Age")

        # Set column weights: keep first KPI narrower, let remaining take more space
        if len(displayed) <= 1:
            weights = [1]
        else:
            weights = [1] + [2] * (len(displayed) - 1)
        cols_kpi = st.columns(weights)

        # Fill columns according to displayed list
        col_idx = 0
        with cols_kpi[col_idx]:
            kpi_card("Répondants", n, C['blue'], "", 0)
        col_idx += 1

        if "Homme" in displayed:
            with cols_kpi[col_idx]:
                male_label = f"<i class='fa fa-mars' style='color:{C['blue']};margin-right:8px;'></i>Nombre d'Hommes ({male_count})"
                male_value = f"{male_pct:.1f}%"
                kpi_card(male_label, male_value, C['blue'], "", 0)
            col_idx += 1

        if "Femme" in displayed:
            with cols_kpi[col_idx]:
                female_label = f"<i class='fa fa-venus' style='color:{C['orange']};margin-right:8px;'></i>Nombre de Femmes ({female_count})"
                female_value = f"{female_pct:.1f}%"
                kpi_card(female_label, female_value, C['orange'], "", 0)
            col_idx += 1

        # Age moyenne in the last slot
        with cols_kpi[col_idx]:
            if age_avg is not None:
                kpi_card("Age moyen", f"{age_avg} ans", C['text'], "", 0)
            else:
                kpi_card("Age moyen", "—", C['text'], "", 0)

        # Scores par dimension (normalisé 0–100 %) — keep these gauges
        if score_cols:
            sec_title("Scores par dimension ")
            gauge_cols = st.columns(len(score_cols))
            for i, sc in enumerate(score_cols):
                # compute normalized percent (1..4 -> 0..100)
                try:
                    avg = df_f[sc].median()
                except Exception:
                    avg = float('nan')
                pct = (avg - 1) / 3 * 100 if not pd.isna(avg) else 0
                # Display a truncated integer (avoid rounding 64.8 -> 65 visually)
                display_pct = int(pct) if not pd.isna(pct) else 0
                # Determine badge (using the float pct to be precise)
                if pct > 65:
                    badge_bg, badge_c, badge_t = ("#DCFCE7", "#15803D", "Élevé")
                elif pct > 40:
                    badge_bg, badge_c, badge_t = ("#FEE2E2", "#B91C1C", "Moyen")
                else:
                    badge_bg, badge_c, badge_t = ("#FEE2E2", "#B91C1C", "Faible")
                # Choose stroke color to match badge semantics: Élevé -> green, Moyen/Faible -> red
                stroke_color = C["green"] if badge_t == "Élevé" else C["red"]
                with gauge_cols[i]:
                    semi_gauge(display_pct, stroke_color, sc, "Score normalisé", key=f"g_{sc}", badge_override=(badge_bg, badge_c, badge_t))

        # The genre pie chart was removed per user request.
        # (Previously: Répartition par genre)



    with tab2:

        # ── JAUGES RISQUES / FORCES ──────────────────────────────────────────
        sec_title("Axes d’amélioration  & Atouts clés")
        col_risk, col_str = st.columns(2)

        with col_risk:
            st.markdown(textwrap.dedent("""
            <div class="risk-card">
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">
                    <span style="font-family:'DM Serif Display',serif;font-style:italic;font-size:1rem;color:#0F2340;"></span>
                </div>
                <p style="font-size:0.74rem;color:#6B88A8;margin:0 0 0.8rem;">
                </strong>
                </p>
            </div>
            """), unsafe_allow_html=True)

            # Render RISQUES header and items as raw HTML via components.html to avoid Markdown parsing
            header_html = textwrap.dedent("""
            <style>
            .q-section { padding-top: 8px; }
            .q-items { margin-top: 18px; display:block; }
            .q-items .item-row { margin-bottom: 18px; padding: 10px 12px; border-radius:10px; background: #fff; box-shadow:0 6px 18px rgba(16,24,40,0.03); }
            </style>
            <div class="risk-card q-section">
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.6rem;">
                    <span style="color: red;"><b>Axes d’amélioration prioritaires</b></span>
                    <span style="font-family:'DM Serif Display',serif;font-style:italic;font-size:1rem;color:#0F2340;"></span>
                </div>

            </div>
            """)
            items = []
            for _, row in top_risks.iterrows():
                # use mid-tone colors for the negative/positive bars
                bar = dual_status_bar(row["pct_neg"], row["pct_pos"], C["red"], C["gray"])
                bar = textwrap.dedent(bar).strip()
                item_html = textwrap.dedent(f"""
                <div class="item-row" style="border-left:3px solid {C['red']};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
                        <span style="font-size:0.79rem;color:#3B5878;font-weight:600;line-height:1.4;">{row['question']}</span>
                        <div style="text-align:right;line-height:1.1;">
                            <div style="font-size:0.9rem;font-weight:800;color:{C['red']};">{row['pct_neg']:.0f}% insatisfaits</div>
                        </div>
                    </div>
                    {bar}
                </div>
                """)
                items.append(item_html)
            items_html = "<div class='q-items' style='margin-top:0.7rem;'>" + "".join(items) + "</div>"
            total_html = header_html + items_html
            h = max(180, 90 * max(1, len(items)) + 40)
            components.html(total_html, height=h)

        with col_str:
            st.markdown(textwrap.dedent("""
            <div class="strength-card">
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">
                    <span style="font-family:'DM Serif Display',serif;font-style:italic;font-size:1rem;color:#0F2340;"></span>
                </div>

            </div>
            """), unsafe_allow_html=True)

            header_html = textwrap.dedent("""
            <style>
            .q-section { padding-top: 8px; }
            .q-items { margin-top: 18px; display:block; }
            .q-items .item-row { margin-bottom: 18px; padding: 10px 12px; border-radius:10px; background: #fff; box-shadow:0 6px 18px rgba(16,24,40,0.03); }
            </style>
            <div class="strength-card q-section">
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.6rem;">
                    <span style="color: green;"><b>Atouts clés à mettre en avant</b></span>
                    <span style="font-family:'DM Serif Display',serif;font-style:italic;font-size:1rem;color:#0F2340;"></span>
                </div>
            
            </div>
            """)
            items = []
            for _, row in top_strengths.iterrows():
                # use mid-tone colors for the bars
                bar = dual_status_bar(row["pct_neg"], row["pct_pos"], C["gray"], C["green"])
                bar = textwrap.dedent(bar).strip()
                item_html = textwrap.dedent(f"""
                <div class="item-row" style="border-left:3px solid {C['green']};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
                        <span style="font-size:0.79rem;color:#3B5878;font-weight:600;line-height:1.4;">{row['question']}</span>
                        <div style="text-align:right;line-height:1.1;">
                            <div style="font-size:0.9rem;font-weight:800;color:{C['green']};">{row['pct_pos']:.0f}% satisfaits</div>
                        </div>
                    </div>
                    {bar}
                </div>
                """)
                items.append(item_html)
            items_html = "<div class='q-items' style='margin-top:0.7rem;'>" + "".join(items) + "</div>"
            total_html = header_html + items_html
            h = max(180, 90 * max(1, len(items)) + 40)
            components.html(total_html, height=h)

        # ── ANALYSES UNIVARIÉES ──────────────────────────────────────────────
        sec_title("Analyse univariée — variables sociodémographiques")

        if not socio_cols:
            st.warning("Aucune variable sociodémographique reconnue dans le fichier.")
        else:
            # Sélecteur de variable
            sel_uni = st.selectbox("Variable à analyser", socio_cols, key="uni_var")

            # Graphique
            st.plotly_chart(
                bar_univarie(df_f[sel_uni].astype(str), sel_uni),
                width='stretch'
            )

            # Tableau de fréquences
            with st.expander("Tableau de fréquences", expanded=False):
                freq = df_f[sel_uni].astype(str).value_counts(normalize=False).reset_index()
                freq.columns = [sel_uni, "Effectif"]
                freq["Pourcentage (%)"] = (freq["Effectif"] / freq["Effectif"].sum() * 100).round(1)
                st.dataframe(freq, width='stretch', hide_index=True)

        # ── ANALYSES BIVARIÉES ───────────────────────────────────────────────
        sec_title("Analyse bivariée — score QVT selon variable sociodémographique")
        if not socio_cols or not score_cols:
            st.warning("Données insuffisantes pour l'analyse bivariée.")
        else:
            b1, b2, b3 = st.columns(3)
            with b1:
                sel_socio = st.selectbox("Variable sociodémographique", socio_cols, key="bi_socio")
            with b2:
                score_options = score_cols + (["Score_Global"] if "Score_Global" in df_f else [])
                sel_score = st.selectbox("Dimension QVT", score_options, key="bi_score")
            with b3:
                # Removed the 'Scores moyens' option — always show 'Répartition réponses'
                st.markdown("<div style='padding-top:0.6rem;color:#6B88A8;font-size:0.95rem;'>Type de visualisation : <strong>Répartition réponses</strong></div>", unsafe_allow_html=True)

            # Always render the 'Répartition réponses' view (stacked distribution by question)
            # Choisir une question dans le groupe de la dimension sélectionnée
            if sel_score in SCORE_GROUPS:
                qs_in_group = [q for q in SCORE_GROUPS[sel_score] if q in question_map]
            else:
                qs_in_group = available_questions
            if qs_in_group:
                sel_q_bi = st.selectbox("Question", qs_in_group, key="bi_question")
                st.plotly_chart(
                    stacked_bivarie(df_f, sel_socio, question_map[sel_q_bi], sel_q_bi),
                    width='stretch',
                )

            # Tableau croisé — afficher le tableau croisé correspondant au graphique empilé
            with st.expander("Tableau croisé détaillé", expanded=False):
                # build counts and percentages per response category for the selected question
                tmp = df_f.copy()
                # recode the selected question to the human-readable response categories
                tmp["Reponse"] = recode_response(tmp[question_map[sel_q_bi]])
                # counts by socio group x response
                counts = pd.crosstab(tmp[sel_socio], tmp["Reponse"]).reindex(columns=RESPONSE_ORDER, fill_value=0)
                # percentages per row
                pct = counts.div(counts.sum(axis=1).replace(0, 1), axis=0) * 100
                # format cells as: '56.0% (112)'
                display_df = counts.copy().astype(object)
                for col in counts.columns:
                    display_df[col] = pct[col].round(1).astype(str) + "% (" + counts[col].astype(int).astype(str) + ")"
                display_df = display_df.reset_index()
                display_df.columns = [sel_socio] + list(counts.columns)

                # Build an HTML table with colored cells matching the RESPONSE_COLORS
                def _text_color_for(hexcolor: str) -> str:
                    # simple luminance check to pick white or dark text for contrast
                    h = hexcolor.lstrip('#')
                    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                    # relative luminance
                    lum = (0.2126 * (r/255) + 0.7152 * (g/255) + 0.0722 * (b/255))
                    return '#ffffff' if lum < 0.65 else C['text']

                cols = [sel_socio] + list(counts.columns)
                table_html = ['<div style="overflow:auto;padding-top:6px;">']
                table_html.append('<table style="border-collapse:separate;border-spacing:8px;width:100%;font-family:Plus Jakarta Sans, sans-serif;">')
                # header
                table_html.append('<thead><tr>')
                for c in cols:
                    table_html.append(f'<th style="text-align:left;padding:8px 12px;color:{C["muted"]};font-weight:600;">{c}</th>')
                table_html.append('</tr></thead>')
                # body
                table_html.append('<tbody>')
                for _, row in display_df.iterrows():
                    table_html.append('<tr>')
                    # first column: group label
                    table_html.append(f'<td style="padding:8px 12px;color:{C["text"]};font-weight:600;">{row[sel_socio]}</td>')
                    for resp in counts.columns:
                        raw = counts.loc[row[sel_socio], resp]
                        pctv = pct.loc[row[sel_socio], resp]
                        bg = RESPONSE_COLORS.get(resp, '#ffffff')
                        fg = _text_color_for(bg)
                        cell_html = f"{pctv:.1f}% ({int(raw)})"
                        table_html.append(
                            f'<td style="background:{bg};color:{fg};padding:8px 12px;text-align:center;border-radius:6px;min-width:80px;">{cell_html}</td>'
                        )
                    table_html.append('</tr>')
                table_html.append('</tbody></table></div>')
                total_html = '\n'.join(table_html)
                # estimate height
                h = min(600, 48 + len(display_df) * 44)
                components.html(total_html, height=h)

    with tab3: 
        st.header("Analyse finale")
        st.write("Résumé global")

        # --- Score final normalisé (compute on the filtered dataframe so the chart reacts to filters) ---
        df_f["Score_final_normalise"] = (
            df_f[list(question_map.values())]
            .apply(pd.to_numeric, errors="coerce")
            .apply(lambda x: ((x - 1) / 3) * 100)
            .mean(axis=1)
        )

        # Classification Bon/Mauvais (on filtered set)
        df_f["Categorie_Global"] = np.where(df_f["Score_final_normalise"] < 50, "Mauvais", "Bon")

        # --- Graphique Score Global (use filtered counts) ---
        counts_global = df_f["Categorie_Global"].value_counts()
        fig_global = px.pie(
            names=counts_global.index,
            values=counts_global.values,
            title="Répartition des employés selon la Bonne ou la Mauvaise Qualité de Vie au Travail",
            color=counts_global.index,
            color_discrete_map={"Mauvais": C["red"], "Bon": C["green"]}
        )
        # make labels inside the pie white and bold for readability on colored slices
        fig_global.update_traces(textinfo="percent+label", textfont=dict(color="white", size=12, family="Plus Jakarta Sans"), insidetextorientation='radial')
        st.plotly_chart(fig_global, width='stretch', key="fig_global_tab3")

if __name__ == "__main__":
    main()