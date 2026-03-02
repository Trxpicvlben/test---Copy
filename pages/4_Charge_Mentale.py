# ============================================================
# YODAN ANALYTICS — 4_Charge_Mentale.py
# Charge Mentale & Stress
# Style : YODAN / Pahaliah & Fils
# ============================================================
import re
import io
import os
import unicodedata

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Un seul appel à set_page_config ───────────────────────────
st.set_page_config(
    page_title="Charge Mentale - YODAN Analytics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CONSTANTES
# ============================================================
COMPANY          = "Pahaliah & Fils"
SCORE_STRESS_MAX = 40

CSV_Q_COLS = [
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_ete_contrarie_par_un_evenement_inattendu",
    "au_cours_du_dernier_mois_a_quelle_frequence_vous_etes_vous_senti_incable_de_controler_les_choses_importantes_dans_votre_vie",
    "au_cours_du_dernier_mois_a_quelle_frequence_vous_etes_vous_senti_nerveux_ou_stresse",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_eu_le_sentiment_de_bien_maitriser_les_choses",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_senti_que_les_difficultes_s_accumulaient_au_point_de_ne_plus_pouvoir_les_surmonter",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_eu_confiance_en_votre_capacite_a_resoudre_vos_problemes_personnels",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_estime_que_les_choses_allaient_comme_vous_le_vouliez",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_eu_le_sentiment_que_vous_ne_pouviez_pas_maitriser_toutes_les_choses_que_vous_aviez_a_faire",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_pu_controler_vos_difficultes",
    "au_cours_du_dernier_mois_a_quelle_frequence_vous_etes_vous_senti_depasse_par_les_evenements",
]
Q_COLS = [f"Stress_Q{i+1}" for i in range(10)]

PALETTE = {
    "pink":   "#E35DA8",
    "blue":   "#4293D8",
    "orange": "#E98A2F",
    "teal":   "#22B8B2",
    "green":  "#39B56A",
    "red":    "#E25555",
    "ink":    "#24395F",
    "grid":   "#E4ECF8",
}
CHART_SEQUENCE = [
    PALETTE["blue"], PALETTE["pink"], PALETTE["orange"],
    PALETTE["teal"], PALETTE["green"], "#6A5ACD",
]
QUESTION_LABELS = {
    "Stress_Q1":  "Q1 - Contrarié(e) par un événement inattendu ?",
    "Stress_Q2":  "Q2 - Incapable de contrôler les choses importantes ?",
    "Stress_Q3":  "Q3 - Nerveux(se) ou stressé(e) ?",
    "Stress_Q4":  "Q4 - Sentiment de bien maîtriser les choses ? (inversé)",
    "Stress_Q5":  "Q5 - Difficultés accumulées au point de ne plus surmonter ? (inversé)",
    "Stress_Q6":  "Q6 - Confiance en votre capacité à résoudre vos problèmes ? (inversé)",
    "Stress_Q7":  "Q7 - Les choses allaient comme vous le vouliez ? (inversé)",
    "Stress_Q8":  "Q8 - Ne pouviez pas maîtriser toutes les choses à faire ?",
    "Stress_Q9":  "Q9 - Avez pu contrôler vos difficultés ? (inversé)",
    "Stress_Q10": "Q10 - Dépassé(e) par les événements ?",
}

# ============================================================
# CSS GLOBAL
# ============================================================
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <style>
    :root{
    --ink:#24395F; --muted:#6B7EA6; --blue:#4293D8; --pink:#E35DA8;
    --orange:#E98A2F; --teal:#22B8B2; --green:#39B56A; --danger:#E25555;
    --card:#FFFFFF; --line:#DCE7F7; --shadow:0 12px 28px rgba(36,57,95,0.10);
    }
    html,body,[class*="css"]{font-family:Inter,sans-serif!important;color:#0F172A}
    .main{background:#f1f4f9!important}
    .block-container{padding:1.5rem 2rem!important;max-width:1300px!important}
    #MainMenu,footer,header{visibility:hidden}
    .stApp{background:linear-gradient(145deg,#f3f7ff 0%,#eef5ff 45%,#f8fbff 100%);color:var(--ink);font-family:"Segoe UI",Roboto,Arial,sans-serif;}
    [data-testid="metric-container"]{background:white;border-radius:12px;padding:1.1rem 1.3rem;border:1px solid #e2e8f0;box-shadow:0 1px 4px rgba(15,23,42,0.06);transition:all 0.2s}
    [data-testid="metric-container"]:hover{transform:translateY(-2px);border-color:#93c5fd;box-shadow:0 4px 16px rgba(37,99,235,0.12)}
    [data-testid="stMetricLabel"] p{font-size:0.72rem!important;color:#64748b!important;text-transform:uppercase;letter-spacing:0.06em;font-weight:600!important}
    [data-testid="stMetricValue"]{font-family:Sora,sans-serif!important;font-size:1.7rem!important;font-weight:700!important;color:#0f172a!important}
    .stButton>button{background:white!important;color:#1e40af!important;border:1.5px solid #bfdbfe!important;border-radius:10px!important;font-weight:600!important;font-size:13px!important;transition:all 0.2s!important}
    .stButton>button:hover{background:#1e40af!important;color:white!important}
    .hero{background:linear-gradient(120deg,#1e2e67,#2d4b9a 55%,#1c8ea0);border-radius:16px;padding:16px 18px;border:1px solid rgba(35,58,120,0.20);margin-bottom:12px;box-shadow:0 14px 30px rgba(24,47,109,0.18);}
    .hero h1{margin:0;font-size:28px;color:#f5f9ff;letter-spacing:0.2px;}
    .hero p{margin:6px 0 0;color:#deebff;font-size:14px;}
    .section-card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px;margin-bottom:12px;box-shadow:var(--shadow);}
    .section-card h3,.section-card h4{color:var(--ink);letter-spacing:0.2px;}
    .filters-panel{background:linear-gradient(115deg,#eef4ff 0%,#f7fbff 48%,#f0fcff 100%);border:1px solid #d5e4ff;border-radius:16px;padding:14px 14px 12px;box-shadow:0 14px 28px rgba(45,75,154,0.12);margin-bottom:12px;position:relative;overflow:hidden;}
    .filters-title{margin:0;font-size:28px;font-weight:900;line-height:1;color:#223962;letter-spacing:0.2px;}
    .filters-sub{margin-top:8px;font-size:13px;color:#5f74a3;}
    .kpi-strip{background:#ffffff;border:1px solid #e6edf9;border-radius:14px;min-height:94px;box-shadow:0 8px 20px rgba(31,50,103,0.08);display:grid;grid-template-columns:6px 56px 1fr;align-items:center;overflow:hidden;}
    .kpi-accent{width:6px;height:100%;}
    .kpi-icon-wrap{display:flex;justify-content:center;}
    .kpi-icon{width:38px;height:38px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;color:#ffffff;}
    .kpi-body{padding:10px 14px 10px 6px;}
    .klabel{color:#7688af;font-size:12px;letter-spacing:0.2px;margin-bottom:3px;}
    .kval{color:#223252;font-weight:800;font-size:34px;line-height:1;}
    .stress-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;}
    .stress-box{background:#f6f9ff;border:1px solid #dce7f7;border-radius:12px;text-align:center;padding:12px 8px;}
    .stress-box .v{font-size:28px;font-weight:800;}
    .stress-box .l{color:#7687af;font-size:12px;text-transform:uppercase;}
    .pcard{background:#efe9de;border-radius:12px;border:1px solid rgba(20,20,20,0.1);overflow:hidden;}
    .pcard-head{height:14px;background:linear-gradient(90deg,#e5ccaa,#f1dfc4);}
    .pcard-body{padding:12px;color:#12152a;}
    .pcard-title{font-size:22px;font-weight:800;margin-bottom:8px;}
    .pcard-row{display:grid;grid-template-columns:1.4fr 1fr;gap:8px;align-items:center;}
    .pcard-grid{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:4px;}
    .picto-icon{position:relative;width:20px;height:20px;display:inline-block;}
    .pcard-value{font-size:30px;font-weight:800;text-align:center;}
    .pcard-caption{font-size:12px;text-align:center;color:#5f657d;}
    .pcard-alert{margin-top:8px;font-size:14px;font-weight:800;}
    .pcard-msg{font-size:12px;color:#4f556e;}
    .upload-note{background:#ffffff;border:1px solid #dce7f7;border-radius:14px;padding:16px;box-shadow:0 10px 24px rgba(35,58,120,0.08);max-width:760px;}
    .upload-note h3{margin:0 0 8px 0;color:#223559;font-size:24px;}
    .upload-note p{margin:0;color:#5f719a;}
    [data-testid="stMetric"]{background:#ffffff;border:1px solid #dce7f7;border-radius:12px;padding:10px 12px;box-shadow:0 8px 18px rgba(36,57,95,0.08);}
    [data-baseweb="tab-list"]{gap:8px;margin-bottom:8px;}
    [data-baseweb="tab"]{background:#e8effc;border:1px solid #cfdcf4;border-radius:10px;color:#30446e;padding:8px 14px;}
    [aria-selected="true"][data-baseweb="tab"]{background:#2d4b9a;color:#f6f9ff;border-color:#2d4b9a;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================
def style_figure(fig, height=420):
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(color=PALETTE["ink"], size=15),
        margin=dict(l=28, r=18, t=56, b=36),
        legend=dict(
            bgcolor="rgba(255,255,255,0.75)",
            bordercolor="#DCE7F7",
            borderwidth=1,
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="right",
            x=1.0,
        ),
        colorway=CHART_SEQUENCE,
        hoverlabel=dict(bgcolor="#1F2A44", font_color="#F3F7FF"),
    )
    fig.update_xaxes(showgrid=True, gridcolor=PALETTE["grid"], zerolinecolor=PALETTE["grid"])
    fig.update_yaxes(showgrid=True, gridcolor=PALETTE["grid"], zerolinecolor=PALETTE["grid"])
    return fig


def style_bar_figure(fig, height=420):
    style_figure(fig, height=height)
    fig.update_layout(bargap=0.52, bargroupgap=0.46, uniformtext_minsize=10, uniformtext_mode="hide")
    fig.update_traces(marker_line_width=0, selector=dict(type="bar"))
    fig.update_traces(width=0.18, selector=dict(type="bar"))
    return fig


def label_variable(col_name: str) -> str:
    return QUESTION_LABELS.get(col_name, col_name)


def slug(text: str) -> str:
    raw = str(text).strip().lower()
    raw = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii")
    raw = re.sub(r"[^a-z0-9]+", "_", raw)
    return raw.strip("_")


def lire_base_importee(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(uploaded_file)
    raise ValueError("Format non supporté. Utilisez CSV, XLSX ou XLS.")


def normaliser_colonnes(df_in: pd.DataFrame) -> pd.DataFrame:
    df = df_in.copy()
    rename_map = {}
    for col in df.columns:
        s = slug(col)
        if s in {"sexe", "sex"}:
            rename_map[col] = "Sexe"
        elif s == "age":
            rename_map[col] = "Age"
        elif s.startswith("situation_m"):
            rename_map[col] = "Situation_matrimoniale"
        elif s in {"taille_cm", "taille"}:
            rename_map[col] = "Taille_cm"
        elif s in {"poids_kg", "poids"}:
            rename_map[col] = "Poids_kg"
        elif s in {"anciennete", "anciennete_ans", "anciennete_annees"}:
            rename_map[col] = "Anciennete"
        elif s == "direction":
            rename_map[col] = "Direction"
        elif s == "fonction":
            rename_map[col] = "Fonction"
        elif s == "poste":
            rename_map[col] = "Poste"
        else:
            # Colonnes CSV longues → Stress_Qi
            csv_match = {csv: q for csv, q in zip(CSV_Q_COLS, Q_COLS)}
            if s in csv_match:
                rename_map[col] = csv_match[s]
            else:
                m = re.match(r"stress_?q_?(\d+)$", s)
                if m:
                    i = int(m.group(1))
                    if 1 <= i <= 10:
                        rename_map[col] = f"Stress_Q{i}"
    return df.rename(columns=rename_map)


def preparer_base(df_in: pd.DataFrame) -> pd.DataFrame:
    df = normaliser_colonnes(df_in)

    missing = [c for c in Q_COLS if c not in df.columns]
    if missing:
        raise ValueError("Colonnes manquantes : " + ", ".join(missing))

    df[Q_COLS] = df[Q_COLS].apply(pd.to_numeric, errors="coerce")
    df["score_stress"] = df[Q_COLS].sum(axis=1, min_count=1).clip(lower=0, upper=SCORE_STRESS_MAX)
    df["Score_Stress_Total"] = df["score_stress"]
    df["ICM_i"] = (df["score_stress"] / SCORE_STRESS_MAX) * 100
    df["TP_i"]  = (1 - df["score_stress"] / SCORE_STRESS_MAX) * 100

    if "Age" in df.columns:
        df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
        df["Tranche_Age"] = np.select(
            [df["Age"] <= 20,
            (df["Age"] >= 21) & (df["Age"] < 30),
            (df["Age"] >= 30) & (df["Age"] < 40),
            (df["Age"] >= 40) & (df["Age"] < 50),
            (df["Age"] >= 50) & (df["Age"] < 60),
            df["Age"] >= 60],
            ["20 ans et moins","21-29 ans","30-39 ans","40-49 ans","50-59 ans","60 ans et plus"],
            default="",
        )
        df["Tranche_Age"] = df["Tranche_Age"].replace("", np.nan)

    if "Taille_cm" in df.columns:
        df["Taille_cm"] = pd.to_numeric(df["Taille_cm"], errors="coerce")
        df["taille_cat"] = pd.cut(
            df["Taille_cm"],
            bins=[0, 159.9, 169.9, 179.9, 1000],
            labels=["<160 cm","160-169 cm","170-179 cm","180 cm et plus"],
            include_lowest=True,
        )

    if "Poids_kg" in df.columns:
        df["Poids_kg"] = pd.to_numeric(df["Poids_kg"], errors="coerce")
        df["poids_cat"] = pd.cut(
            df["Poids_kg"],
            bins=[0, 59.9, 74.9, 89.9, 1000],
            labels=["<60 kg","60-74 kg","75-89 kg","90 kg et plus"],
            include_lowest=True,
        )

    if "Anciennete" in df.columns:
        df["Anciennete"] = pd.to_numeric(df["Anciennete"], errors="coerce")
        df["anciennete_cat"] = np.select(
            [df["Anciennete"] <= 2, df["Anciennete"] <= 5,
            df["Anciennete"] <= 10, df["Anciennete"] <= 20],
            ["0-2 ans","3-5 ans","6-10 ans","11-20 ans"],
            default="20 ans et plus",
        )

    df["niveau"] = np.select(
        [df["score_stress"] <= 13,
        (df["score_stress"] > 13) & (df["score_stress"] <= 26),
        (df["score_stress"] > 26) & (df["score_stress"] <= 40)],
        ["Niveau de stress faible","Niveau de stress modere","Niveau de stress eleve"],
        default="",
    )
    df["niveau"] = df["niveau"].replace("", np.nan)
    return df


def find_csv() -> str | None:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for p in [
        os.path.join(base, "data", "Charge_mentale_2.csv"),
        "data/Charge_mentale_2.csv",
        "Charge_mentale_2.csv",
    ]:
        if os.path.exists(p):
            return p
    return None


def familles_filtres(df: pd.DataFrame):
    specs = {
        "Variables sociodemographiques": [
            ("Sexe",               "Sexe"),
            ("Tranche d'Age",      "Tranche_Age"),
            ("Situation matrimoniale", "Situation_matrimoniale"),
        ],
        "Variables anthropometriques": [
            ("Taille", "taille_cat"),
            ("Poids",  "poids_cat"),
        ],
        "Variables de travail": [
            ("Anciennete", "anciennete_cat"),
            ("Direction",  "Direction"),
            ("Fonction",   "Fonction"),
            ("Poste",      "Poste"),
        ],
    }
    familles, label_to_col = {}, {}
    for famille, entries in specs.items():
        labels = []
        for label, col in entries:
            col_use = col
            if col == "taille_cat" and col not in df.columns and "Taille_cm" in df.columns:
                col_use = "Taille_cm"
            if col == "poids_cat" and col not in df.columns and "Poids_kg" in df.columns:
                col_use = "Poids_kg"
            if col_use in df.columns:
                labels.append(label)
                label_to_col[label] = col_use
        if labels:
            familles[famille] = labels
    return familles, label_to_col


def pictogramme_card(value, title, mode="stress", scale_max=100.0):
    total_icons = 10
    val   = max(0.0, min(float(scale_max), float(value)))
    units = (val / float(scale_max)) * total_icons
    full_icons = int(np.floor(units))
    partial    = units - full_icons
    norm       = (val / float(scale_max)) * 100.0

    if mode == "stress" and scale_max == 10.0:
        label_value = f"{val:.1f}/10"
        txt_value   = f"{val:.1f} sur 10"
        unit_lbl    = "1 pictogramme = 1 point"
    else:
        label_value = f"{val:.1f}%"
        txt_value   = f"{val:.1f}%"
        unit_lbl    = "1 pictogramme = 10%"

    if mode == "stress":
        if norm < 30:
            color, title_msg = "#e25555", "Alerte rouge"
            msg = f"Le niveau de stress est de {txt_value}. Zone critique, risque d'epuisement eleve."
        elif norm < 60:
            color, title_msg = "#e0b33f", "Vigilance"
            msg = f"Le niveau de stress est de {txt_value}. Pression reelle, prevention recommandee."
        else:
            color, title_msg = "#4fb77e", "Stabilite"
            msg = f"Le niveau de stress est de {txt_value}. Equilibre globalement stable."
    else:
        if norm < 40:
            color, title_msg = "#e25555", "Niveau fragile"
            msg = f"Le taux de productivite est de {txt_value}. Soutien organisationnel recommande."
        elif norm < 70:
            color, title_msg = "#e0b33f", "Niveau intermediaire"
            msg = f"Le taux de productivite est de {txt_value}. Niveau correct mais sensible a la surcharge."
        else:
            color, title_msg = "#4fb77e", "Niveau favorable"
            msg = f"Le taux de productivite est de {txt_value}. Capacite operationnelle solide."

    def person_svg(c, size=20):
        return (
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
            f'<circle cx="12" cy="6" r="4" fill="{c}"></circle>'
            f'<path d="M4 22c0-4.4 3.6-8 8-8s8 3.6 8 8H4z" fill="{c}"></path>'
            f"</svg>"
        )

    icons = []
    for i in range(total_icons):
        if i < full_icons:
            ratio = 1.0
        elif i == full_icons:
            ratio = partial
        else:
            ratio = 0.0
        width = ratio * 100.0
        icons.append(
            f'<span class="picto-icon">'
            f'<span style="position:absolute;inset:0;">{person_svg("rgba(95,95,120,0.25)", 20)}</span>'
            f'<span style="position:absolute;inset:0;width:{width:.4f}%;overflow:hidden;white-space:nowrap;">'
            f'{person_svg(color, 20)}</span></span>'
        )

    return f"""
    <div class="pcard">
    <div class="pcard-head"></div>
    <div class="pcard-body">
        <div class="pcard-title">{title}</div>
        <div class="pcard-row">
        <div class="pcard-grid">{''.join(icons)}</div>
        <div class="pcard-right">
            <div class="pcard-value">{label_value}</div>
            <div class="pcard-caption">{unit_lbl}</div>
        </div>
        </div>
        <div class="pcard-alert" style="color:{color};">{title_msg}</div>
        <div class="pcard-msg">{msg}</div>
    </div>
    </div>
    """


def construire_psy_gauge(valeur: float, titre: str, mode: str = "stress") -> go.Figure:
    if mode == "stress":
        steps = [
            {"range": [0,  35], "color": "#4CAF50"},
            {"range": [35, 65], "color": "#FFC107"},
            {"range": [65,100], "color": "#F44336"},
        ]
        bar_color = "#F44336" if valeur >= 65 else ("#FFC107" if valeur >= 35 else "#4CAF50")
    else:
        steps = [
            {"range": [0,  35], "color": "#F44336"},
            {"range": [35, 65], "color": "#FFC107"},
            {"range": [65,100], "color": "#4CAF50"},
        ]
        bar_color = "#4CAF50" if valeur >= 65 else ("#FFC107" if valeur >= 35 else "#F44336")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(valeur, 1),
        number={"suffix": "%", "font": {"size": 32, "family": "Sora", "color": "#0f172a"}},
        title={"text": titre, "font": {"size": 14, "family": "Sora", "color": "#0f172a"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "#64748b", "size": 10}},
            "bar":  {"color": bar_color, "thickness": 0.72},
            "bgcolor": "#f8fafc",
            "bordercolor": "#e2e8f0",
            "borderwidth": 1,
            "steps": steps,
            "threshold": {
                "line": {"color": "#64748b", "width": 2},
                "thickness": 0.8,
                "value": 50,
            },
        },
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#0f172a"),
    )
    return fig


# ============================================================
# EN-TÊTE YODAN
# ============================================================
col_h1, col_h2 = st.columns([8, 2])
with col_h1:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">'
        f'<div style="width:42px;height:42px;background:linear-gradient(135deg,#1e40af,#3b82f6);'
        f'border-radius:10px;display:flex;align-items:center;justify-content:center;">'
        f'<i class="fas fa-brain" style="color:white;font-size:18px;"></i></div>'
        f'<div>'
        f'<div style="font-family:Sora,sans-serif;font-size:20px;font-weight:800;color:#0f172a;">'
        f'Charge Mentale & Stress</div>'
        f'<div style="font-size:13px;color:#64748b;">'
        f'Suivi de la charge mentale, du risque d\'épuisement et de la capacité productive · {COMPANY}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
with col_h2:
    if st.button("← Accueil", key="back_home_cm"):
        st.switch_page("app.py")

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:4px 0 16px;'>", unsafe_allow_html=True)

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
with st.sidebar:
    st.header("📂 Données")
    sidebar_up = st.file_uploader(
        "Charger un fichier Excel ou CSV",
        type=["xlsx", "xls", "csv"],
        key="cm_sidebar_uploader",
    )

if sidebar_up is not None:
    b = sidebar_up.read()
    if b:
        st.session_state["cm_file_bytes"] = b
        st.session_state["cm_file_name"]  = sidebar_up.name

df = None

if "cm_file_bytes" in st.session_state:
    fn  = st.session_state["cm_file_name"]
    buf = io.BytesIO(st.session_state["cm_file_bytes"])
    try:
        if fn.lower().endswith(".csv"):
            for enc in ("utf-8-sig", "latin-1", "cp1252", "iso-8859-1"):
                try:
                    buf.seek(0)
                    raw = pd.read_csv(buf, encoding=enc, sep=None, engine="python")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Impossible de décoder le fichier CSV (encodage non reconnu).")
        else:
            raw = pd.read_excel(buf)
        df = preparer_base(raw)
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement : {e}")
        st.stop()
else:
    csv_path = find_csv()
    if csv_path:
        try:
            for enc in ("utf-8-sig", "latin-1", "cp1252", "iso-8859-1"):
                try:
                    raw = pd.read_csv(csv_path, encoding=enc, sep=None, engine="python")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Impossible de décoder le fichier CSV (encodage non reconnu).")
            df = preparer_base(raw)
        except Exception as e:
            st.error(f"❌ Erreur CSV local : {e}")
            st.stop()

if df is None:
    st.markdown(
        """
        <div class="upload-note">
        <h3>Import requis pour démarrer</h3>
        <p>Chargez votre fichier CSV/Excel dans la barre latérale pour activer le tableau de bord.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    main_up = st.file_uploader("Ou importez votre fichier ici", type=["xlsx","xls","csv"], key="cm_main_uploader")
    if main_up is not None:
        b = main_up.read()
        if b:
            st.session_state["cm_file_bytes"] = b
            st.session_state["cm_file_name"]  = main_up.name
            st.rerun()
    st.stop()

# ============================================================
# TABLEAU DE BORD
# ============================================================
st.markdown(
    """
    <div class="hero">
    <h1>Audit de la Charge Mentale et du Stress des Employés — Tableau de Bord</h1>
    <p>Pilotage psychologique et analyses statistiques.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_pilotage, tab_analyse = st.tabs(["Pilotage", "Analyse des données"])

# ── TAB PILOTAGE ─────────────────────────────────────────────
with tab_pilotage:
    st.markdown(
        """
        <div class="filters-panel">
        <p class="filters-title">Filtres d'analyse</p>
        <p class="filters-sub">Affinez rapidement le segment observé pour une lecture psychologique précise.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    familles, label_to_col = familles_filtres(df)
    if not familles:
        st.error("Aucune variable de filtrage compatible détectée.")
        st.stop()

    c1, c2, c3 = st.columns(3)
    fam       = c1.selectbox("Type de variable", list(familles.keys()))
    var_label = c2.selectbox("Variable", familles[fam])
    var       = label_to_col[var_label]
    mods      = ["Tous"] + sorted(df[var].dropna().astype(str).unique().tolist())
    mod       = c3.selectbox("Modalité", mods)

    df_v  = df if mod == "Tous" else df[df[var].astype(str) == mod]
    n     = len(df_v)
    age_m = float(df_v["Age"].median()) if ("Age" in df_v.columns and n > 0) else 0.0
    ph    = float((df_v["Sexe"].astype(str).str.lower() == "homme").mean() * 100) if ("Sexe" in df_v.columns and n > 0) else 0.0
    pf    = float((df_v["Sexe"].astype(str).str.lower() == "femme").mean() * 100) if ("Sexe" in df_v.columns and n > 0) else 0.0
    icm10 = float((df_v["score_stress"].mean() / SCORE_STRESS_MAX) * 10) if n > 0 else 0.0
    tp    = float(df_v["TP_i"].mean()) if n > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4, gap="large")
    k1.markdown(f'<div class="kpi-strip"><div class="kpi-accent" style="background:#ff8f9a;"></div><div class="kpi-icon-wrap"><span class="kpi-icon" style="background:#ff8f9a;">🏢</span></div><div class="kpi-body"><div class="klabel">Employés</div><div class="kval">{n}</div></div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-strip"><div class="kpi-accent" style="background:#5a63d8;"></div><div class="kpi-icon-wrap"><span class="kpi-icon" style="background:#5a63d8;">♂</span></div><div class="kpi-body"><div class="klabel">Hommes</div><div class="kval">{ph:.1f}%</div></div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-strip"><div class="kpi-accent" style="background:#ff5fa5;"></div><div class="kpi-icon-wrap"><span class="kpi-icon" style="background:#ff5fa5;">♀</span></div><div class="kpi-body"><div class="klabel">Femmes</div><div class="kval">{pf:.1f}%</div></div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-strip"><div class="kpi-accent" style="background:#4fc785;"></div><div class="kpi-icon-wrap"><span class="kpi-icon" style="background:#4fc785;">📊</span></div><div class="kpi-body"><div class="klabel">Âge moyen</div><div class="kval">{age_m:.1f} ans</div></div></div>', unsafe_allow_html=True)

    n_base = max(n, 1)
    pct_f = (df_v["niveau"] == "Niveau de stress faible").sum()  * 100 / n_base
    pct_m = (df_v["niveau"] == "Niveau de stress modere").sum()  * 100 / n_base
    pct_h = (df_v["niveau"] == "Niveau de stress eleve").sum()   * 100 / n_base

    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
    left, right = st.columns([1.2, 1.0], gap="large")
    with left:
        st.markdown(
            f"""
            <div class="section-card">
            <h4 style="margin:0 0 10px 0;">Distribution des niveaux de stress</h4>
            <div class="stress-grid">
                <div class="stress-box"><div class="v" style="color:#4fd2be;">~{pct_f:.0f}%</div><div class="l">Faible</div></div>
                <div class="stress-box"><div class="v" style="color:#e8c278;">~{pct_m:.0f}%</div><div class="l">Modéré</div></div>
                <div class="stress-box"><div class="v" style="color:#ff808f;">~{pct_h:.0f}%</div><div class="l">Élevé</div></div>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        pie_df = pd.DataFrame({
            "Niveau":   ["Faible","Modéré","Élevé"],
            "Effectif": [
                int((df_v["niveau"] == "Niveau de stress faible").sum()),
                int((df_v["niveau"] == "Niveau de stress modere").sum()),
                int((df_v["niveau"] == "Niveau de stress eleve").sum()),
            ],
        })
        fig_pie = px.pie(
            pie_df, names="Niveau", values="Effectif", hole=0.58,
            color="Niveau",
            color_discrete_map={"Faible": PALETTE["teal"], "Modéré": PALETTE["orange"], "Élevé": PALETTE["red"]},
        )
        style_figure(fig_pie, height=340)
        fig_pie.update_layout(margin=dict(l=8, r=8, t=20, b=8), legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"))
        fig_pie.update_traces(textinfo="percent", textfont_size=14, marker=dict(line=dict(color="#ffffff", width=2)))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
    g1, g2 = st.columns(2, gap="large")
    with g1:
        st.markdown(pictogramme_card(icm10, "Indice de Stress (ICM) sur 10", mode="stress", scale_max=10.0), unsafe_allow_html=True)
    with g2:
        st.markdown(pictogramme_card(tp, "Taux de Productivité", mode="productivite", scale_max=100.0), unsafe_allow_html=True)


# ── TAB ANALYSE ──────────────────────────────────────────────
with tab_analyse:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### Contexte de l'étude")
    st.markdown(
        """
        Cette étude évalue la charge mentale perçue des employés via les 10 questions `Stress_Q1` à `Stress_Q10`.
        Le score cumulé est converti en :
        - `ICM_i` : indice de charge mentale (0–100 %)
        - `ICM sur 10` : version de pilotage clinique
        - `TP_i` : taux de productivité théorique
        """
    )

    st.markdown("### Données générales")
    total_employes  = st.number_input("Nombre total d'employés dans l'entreprise", min_value=1, value=max(int(df.shape[0]), 1), step=1)
    pct_repondants  = (int(df.shape[0]) / max(int(total_employes), 1)) * 100

    sexe_clean  = df["Sexe"].astype(str).str.strip().str.lower() if "Sexe" in df.columns else pd.Series(dtype=str)
    nb_hommes   = int(sexe_clean.isin(["homme","h"]).sum()) if not sexe_clean.empty else 0
    nb_femmes   = int(sexe_clean.isin(["femme","f"]).sum()) if not sexe_clean.empty else 0
    total_sexe  = max(nb_hommes + nb_femmes, 1)
    pct_hommes  = (nb_hommes / total_sexe) * 100
    pct_femmes  = (nb_femmes / total_sexe) * 100

    anciennete_med = np.nan
    if "Anciennete" in df.columns:
        anc = pd.to_numeric(df["Anciennete"], errors="coerce")
        if anc.notna().any():
            anciennete_med = float(anc.median())

    d1, d2, d3, d4, d5 = st.columns(5)
    d1.markdown(f'<div class="kpi-strip"><div class="kpi-accent" style="background:#ff8f9a;"></div><div class="kpi-icon-wrap"><span class="kpi-icon" style="background:#ff8f9a;">👥</span></div><div class="kpi-body"><div class="klabel">Répondants</div><div class="kval">{int(df.shape[0])}</div></div></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="kpi-strip"><div class="kpi-accent" style="background:#5a63d8;"></div><div class="kpi-icon-wrap"><span class="kpi-icon" style="background:#5a63d8;">📈</span></div><div class="kpi-body"><div class="klabel">% répondants</div><div class="kval">{pct_repondants:.1f}%</div></div></div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="kpi-strip"><div class="kpi-accent" style="background:#4b7be5;"></div><div class="kpi-icon-wrap"><span class="kpi-icon" style="background:#4b7be5;">♂</span></div><div class="kpi-body"><div class="klabel">Hommes</div><div class="kval">{pct_hommes:.1f}%</div></div></div>', unsafe_allow_html=True)
    d4.markdown(f'<div class="kpi-strip"><div class="kpi-accent" style="background:#e35da8;"></div><div class="kpi-icon-wrap"><span class="kpi-icon" style="background:#e35da8;">♀</span></div><div class="kpi-body"><div class="klabel">Femmes</div><div class="kval">{pct_femmes:.1f}%</div></div></div>', unsafe_allow_html=True)
    d5.markdown(f'<div class="kpi-strip"><div class="kpi-accent" style="background:#39b56a;"></div><div class="kpi-icon-wrap"><span class="kpi-icon" style="background:#39b56a;">⏳</span></div><div class="kpi-body"><div class="klabel">Ancienneté médiane</div><div class="kval">{(f"{anciennete_med:.1f} ans" if not np.isnan(anciennete_med) else "N/A")}</div></div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Analyses univariées ──────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### Analyses univariées")
    all_cols = list(df.columns)
    var_uni       = st.selectbox("Choisir une variable", all_cols, key="uni_var", format_func=label_variable)
    var_uni_label = label_variable(var_uni)
    series_uni    = df[var_uni]

    if var_uni == "Sexe":
        if "niveau" not in df.columns:
            st.warning("La colonne 'niveau' est absente.")
        else:
            df_s = df[["Sexe","niveau"]].copy()
            df_s["Sexe"] = df_s["Sexe"].astype(str).str.strip().str.title()
            df_s = df_s[df_s["Sexe"].isin(["Femme","Homme"])]
            if df_s.empty:
                st.warning("Valeurs de sexe non exploitables.")
            else:
                sex_counts = df_s["Sexe"].value_counts().reindex(["Femme","Homme"]).fillna(0).astype(int)
                sex_pct    = (sex_counts / max(int(sex_counts.sum()), 1) * 100).round(1)
                ux1, ux2   = st.columns([1.05, 1.25], gap="large")
                with ux1:
                    fig_sexe = px.pie(
                        pd.DataFrame({"Sexe":["Femme","Homme"],"Effectif":[int(sex_counts["Femme"]),int(sex_counts["Homme"])]}),
                        names="Sexe", values="Effectif", hole=0.58,
                        color="Sexe",
                        color_discrete_map={"Femme": PALETTE["pink"], "Homme": PALETTE["blue"]},
                        title="Répartition par sexe",
                    )
                    style_figure(fig_sexe, height=360)
                    fig_sexe.update_layout(legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center"))
                    fig_sexe.update_traces(textinfo="percent", textfont_size=14, marker=dict(line=dict(color="#ffffff", width=2)))
                    st.plotly_chart(fig_sexe, use_container_width=True)
                with ux2:
                    s1, s2 = st.columns(2)
                    s1.metric("Femmes", f"{sex_pct['Femme']:.1f}%")
                    s2.metric("Hommes", f"{sex_pct['Homme']:.1f}%")
                    ecart    = abs(float(sex_pct["Femme"]) - float(sex_pct["Homme"]))
                    dominant = "féminine" if sex_pct["Femme"] >= sex_pct["Homme"] else "masculine"
                    part_dom = max(float(sex_pct["Femme"]), float(sex_pct["Homme"]))
                    st.markdown(
                        f'<div style="background:#f5f8ff;border:1px solid #dce7f7;border-radius:12px;padding:14px 16px;">'
                        f'<div style="font-size:16px;color:#3b4d6f;line-height:1.6;">Une prédominance <b>{dominant}</b> est observée ({part_dom:.1f}%, écart de {ecart:.1f} pts).</div></div>',
                        unsafe_allow_html=True,
                    )

    elif var_uni == "Tranche_Age":
        freq = series_uni.astype(str).value_counts(dropna=False).reset_index()
        freq.columns = ["Tranche_Age","Effectif"]
        order = ["60 ans et plus","50-59 ans","40-49 ans","30-39 ans","21-29 ans","20 ans et moins"]
        freq["Tranche_Age"] = pd.Categorical(freq["Tranche_Age"], categories=order, ordered=True)
        freq = freq.sort_values("Tranche_Age").dropna(subset=["Tranche_Age"])
        freq["Pourcentage"] = (freq["Effectif"] / max(freq["Effectif"].sum(), 1) * 100).round(1)
        l_uni, r_uni = st.columns([1.7, 1.1], gap="large")
        with l_uni:
            fig_uni = px.bar(freq, x="Pourcentage", y="Tranche_Age", orientation="h",
                            text="Pourcentage", title="Distribution des tranches d'âge")
            fig_uni.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
            style_bar_figure(fig_uni, height=520)
            fig_uni.update_layout(showlegend=False, xaxis_title="Pourcentage (%)", yaxis_title="")
            st.plotly_chart(fig_uni, use_container_width=True)
        with r_uni:
            for _, row in freq.iterrows():
                st.markdown(
                    f'<div style="background:#f5f8ff;border:1px solid #dce7f7;border-left:5px solid #5b95e6;border-radius:12px;padding:12px 14px;margin-bottom:10px;">'
                    f'<span style="font-weight:800;color:#24395f;">{row["Tranche_Age"]}</span>'
                    f' : {int(row["Effectif"])} ({row["Pourcentage"]:.1f}%)</div>',
                    unsafe_allow_html=True,
                )
        st.dataframe(freq, use_container_width=True)

    elif pd.api.types.is_numeric_dtype(series_uni):
        fig_uni = px.histogram(df, x=var_uni, nbins=20, title=f"Distribution — {var_uni_label}")
        style_figure(fig_uni, height=420)
        st.plotly_chart(fig_uni, use_container_width=True)
        st.dataframe(series_uni.describe().to_frame("Statistiques"), use_container_width=True)

    else:
        freq = series_uni.astype(str).value_counts(dropna=False).reset_index()
        freq.columns = ["Modalite","Effectif"]
        freq["Pourcentage"] = (freq["Effectif"] / max(len(series_uni), 1) * 100).round(2)
        fig_uni = px.bar(freq, x="Modalite", y="Effectif", text="Pourcentage",
                        title=f"Distribution — {var_uni_label}", color="Modalite",
                        color_discrete_sequence=CHART_SEQUENCE)
        fig_uni.update_traces(texttemplate="%{text:.1f}%")
        style_bar_figure(fig_uni, height=420)
        fig_uni.update_layout(showlegend=False)
        st.plotly_chart(fig_uni, use_container_width=True)
        st.dataframe(freq, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Analyses bivariées ───────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### Analyses bivariées")
    bx1, bx2 = st.columns(2)
    var_x       = bx1.selectbox("Variable 1", all_cols, index=0, key="bi_x", format_func=label_variable)
    default_y   = 1 if len(all_cols) > 1 else 0
    var_y       = bx2.selectbox("Variable 2", all_cols, index=default_y, key="bi_y", format_func=label_variable)
    var_x_label = label_variable(var_x)
    var_y_label = label_variable(var_y)

    if var_x == var_y:
        st.warning("Choisissez deux variables différentes.")
    else:
        sx    = df[var_x]
        sy    = df[var_y]
        num_x = pd.api.types.is_numeric_dtype(sx)
        num_y = pd.api.types.is_numeric_dtype(sy)
        table_pct = None

        if num_x and num_y:
            tmp = df[[var_x, var_y]].apply(pd.to_numeric, errors="coerce").dropna()
            tmp["X_cl"] = pd.qcut(tmp[var_x], q=5, duplicates="drop").astype(str)
            tmp["Y_cl"] = pd.qcut(tmp[var_y], q=5, duplicates="drop").astype(str)
            ct     = pd.crosstab(tmp["X_cl"], tmp["Y_cl"])
            ct_pct = (ct.div(ct.sum(axis=1).replace(0, np.nan), axis=0) * 100).round(2).fillna(0)
            grouped = ct_pct.reset_index().melt(id_vars="X_cl", var_name="Y_cl", value_name="Pourcentage")
            fig_bi  = px.bar(grouped, x="X_cl", y="Pourcentage", color="Y_cl", barmode="group",
                            title=f"Classes de {var_x_label} × classes de {var_y_label}")
            fig_bi.update_traces(texttemplate="%{y:.1f}%", textposition="auto", cliponaxis=False)
            style_bar_figure(fig_bi, height=440)
            fig_bi.update_yaxes(title="Pourcentage (%)", range=[0, 100])
            st.plotly_chart(fig_bi, use_container_width=True)
            table_pct = ct_pct.copy()

        elif num_x and not num_y:
            tmp = df[[var_x, var_y]].copy()
            tmp[var_x] = pd.to_numeric(tmp[var_x], errors="coerce")
            tmp = tmp.dropna(subset=[var_x, var_y])
            tmp["X_cl"] = pd.qcut(tmp[var_x], q=5, duplicates="drop").astype(str)
            ct     = pd.crosstab(tmp["X_cl"], tmp[var_y].astype(str))
            ct_pct = (ct.div(ct.sum(axis=1).replace(0, np.nan), axis=0) * 100).round(2).fillna(0)
            grouped = ct_pct.reset_index().melt(id_vars="X_cl", var_name=var_y, value_name="Pourcentage")
            fig_bar = px.bar(grouped, x="X_cl", y="Pourcentage", color=var_y, barmode="group",
                            title=f"Classes de {var_x_label} × {var_y_label}")
            fig_bar.update_traces(texttemplate="%{y:.1f}%", textposition="auto", cliponaxis=False)
            style_bar_figure(fig_bar, height=420)
            fig_bar.update_yaxes(title="Pourcentage (%)", range=[0, 100])
            st.plotly_chart(fig_bar, use_container_width=True)
            table_pct = ct_pct.copy()

        elif not num_x and num_y:
            tmp = df[[var_x, var_y]].copy()
            tmp[var_y] = pd.to_numeric(tmp[var_y], errors="coerce")
            tmp = tmp.dropna(subset=[var_x, var_y])
            tmp["Y_cl"] = pd.qcut(tmp[var_y], q=5, duplicates="drop").astype(str)
            ct     = pd.crosstab(tmp[var_x].astype(str), tmp["Y_cl"])
            ct_pct = (ct.div(ct.sum(axis=1).replace(0, np.nan), axis=0) * 100).round(2).fillna(0)
            grouped = ct_pct.reset_index().melt(id_vars=var_x, var_name="Y_cl", value_name="Pourcentage")
            fig_bar = px.bar(grouped, x=var_x, y="Pourcentage", color="Y_cl", barmode="group",
                            title=f"{var_x_label} × classes de {var_y_label}")
            fig_bar.update_traces(texttemplate="%{y:.1f}%", textposition="auto", cliponaxis=False)
            style_bar_figure(fig_bar, height=420)
            fig_bar.update_yaxes(title="Pourcentage (%)", range=[0, 100])
            st.plotly_chart(fig_bar, use_container_width=True)
            table_pct = ct_pct.copy()

        else:
            ct     = pd.crosstab(df[var_x].astype(str), df[var_y].astype(str))
            ct_pct = (ct.div(ct.sum(axis=1).replace(0, np.nan), axis=0) * 100).round(2).fillna(0)
            grouped = ct_pct.reset_index().melt(id_vars=var_x, var_name=var_y, value_name="Pourcentage")
            fig_group = px.bar(grouped, x=var_x, y="Pourcentage", color=var_y, barmode="group",
                            title=f"{var_x_label} × {var_y_label}")
            fig_group.update_traces(texttemplate="%{y:.1f}%", textposition="auto", cliponaxis=False)
            style_bar_figure(fig_group, height=420)
            fig_group.update_yaxes(title="Pourcentage (%)", range=[0, 100])
            st.plotly_chart(fig_group, use_container_width=True)
            table_pct = ct_pct.copy()

        if table_pct is not None:
            table_pct["Total (%)"] = np.where(table_pct.sum(axis=1) > 0, 100.0, 0.0)
            st.markdown(f"#### Tableau croisé (% lignes) : {var_x_label} × {var_y_label}")
            st.dataframe(table_pct, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
