# =============================================================================
# SECTION 0 — IMPORTS + CONFIG + TRADUCTIONS
# =============================================================================
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import io

st.set_page_config(
    layout="wide",
    page_title="Karasek · Bien-être",
    page_icon="",
    initial_sidebar_state="collapsed",
)

# ── Palette ───────────────────────────────────────────────────────────────────
COLORS = {
    "bg_primary":    "#F5F9FF",
    "bg_card":       "#FFFFFF",
    "accent_blue":   "#38A3E8",
    "accent_orange": "#F97316",
    "accent_green":  "#22C55E",
    "accent_red":    "#EF4444",
    "text_primary":  "#0F2340",
    "text_muted":    "#6B88A8",
    "border":        "#D6E8F7",
}

KARASEK_COLORS = {
    "Actif":   "#22C55E",
    "Détendu": "#38A3E8",
    "Tendu":   "#EF4444",
    "Passif":  "#94A3B8",
    "Active":  "#22C55E",
    "Relaxed": "#38A3E8",
    "Tense":   "#EF4444",
    "Passive": "#94A3B8",
}

THRESHOLDS = {
    "Dem_score":           22.5,
    "Lat_score":           60.0,
    "SS_score":            20.0,
    "comp_score":          30.0,
    "auto_score":          30.0,
    "sup_score":           10.0,
    "col_score":           10.0,
    "rec_score":           15.0,
    "equ_score":            2.5,
    "cult_score":           5.0,
    "sat_score":            2.5,
    "adq_resources_score":  2.5,
    "adq_role_score":       2.5,
}

T = {
    "fr": {
        "tab1": "Vue d'ensemble",
        "tab2": "Stress & Autonomie",
        "app_title": "Karasek Dashboard",
        "app_subtitle": "Analyse du bien-être au travail · Modèle de Karasek",
        "total_staff": "Effectif total",
        "men": "Hommes",
        "women": "Femmes",
        "avg_age": "Âge moyen",
        "overweight": "Surpoids & Obésité",
        "lifestyle_title": "Indicateurs de modes de vie",
        "sedentarity": "Sédentarité",
        "alcohol": "Alcool",
        "tobacco": "Tabagisme",
        "chronic": "Maladie chronique",
        "explore_title": "Exploration des données démographiques",
        "select_variable": "Variable à visualiser",
        "cross_with": "Croiser avec (optionnel)",
        "no_cross": "Aucun croisement",
        "n_respondents": "N",
        "pct": "%",
        "stress_kpis_title": "Indicateurs clés de stress au travail",
        "autonomy": "Autonomie décisionnelle",
        "autonomy_sub": "Flexibilité et contrôle perçus",
        "workload": "Charge mentale perçue",
        "workload_sub": "Intensité de la demande psychologique",
        "social_support": "Cohésion d'équipe",
        "social_support_sub": "Soutien social collègues & management",
        "mapp_title": "Grille MAPP du Stress",
        "mapp_subtitle": "Chaque point représente un agent. Les axes délimitent les zones du quadrant karasek.",
        "x_axis_mapp": "Latitude décisionnelle (autonomie & compétences)",
        "y_axis_mapp": "Demande psychologique (charge mentale)",
        "quadrant_pct_title": "Répartition par quadrant Karasek",
        "active": "Actif",
        "relaxed": "Détendu",
        "tense": "Tendu",
        "passive": "Passif",
        "radar_title": "Satisfaction organisationnelle",
        "radar_subtitle": "% de collaborateurs avec un niveau élevé de satisfaction par dimension",
        "radar_ref": "Référence 50%",
        "pct_satisfied": "Niveau élevé",
        "recognition": "Reconnaissance",
        "equity": "Équité de charge",
        "culture": "Culture d'entreprise",
        "satisfaction": "Satisfaction",
        "resources": "Ressources & Objectifs",
        "management_support": "Soutien management",
        "training": "Formation",
        "skills": "Compétences",
        "filter_title": "Filtres",
        "filter_direction": "Direction",
        "filter_csp": "Catégorie socio",
        "filter_genre": "Genre",
        "filter_age": "Tranche d'âge",
        "reset_btn": "↺ Réinitialiser",
        "n_filtered": "Effectif filtré",
        "lang_toggle": "EN",
        "var_genre": "Genre",
        "var_age": "Tranche d'âge",
        "var_anciennete": "Ancienneté",
        "var_csp": "Catégorie socioprofessionnelle",
        "var_imc": "Catégorie IMC",
        "var_imc_bin": "IMC (normal / surpoids)",
        "var_direction": "Direction",
        "var_tabac": "Tabagisme",
        "var_alcool": "Consommation d'alcool",
        "var_sport": "Pratique sportive",
        "var_maladie": "Maladie chronique",
        "cross_quadrant": "quadrant Karasek ",
        "cross_dem": "Charge mentale",
        "cross_lat": "Autonomie décisionnelle",
        "cross_ss": "Soutien social",
        "cross_rec": "Reconnaissance",
        "cross_equ": "Équité de charge",
        "cross_cult": "Culture d'entreprise",
        "cross_sat": "Satisfaction au travail",
        "cross_adq_res": "Ressources et Objectifs",
        "cross_adq_role": "Adéquation Formation",
        "cross_skills": "Utilisation des compétences",
        "cross_supmgmt": "Soutien du management",
        "high": "Élevé",
        "low": "Faible",
        "pct_label": "Pourcentage (%)",
        "hover_quad": "Zone",
        "hover_lat": "Autonomie",
        "hover_dem": "Charge mentale",
        "no_data": "Données insuffisantes pour ce croisement.",
        "missing_mapp": "Colonnes manquantes pour la grille MAPP",
        "all_option": "Tous",
        "select_cross_stress": "Choisir un croisement",
        "upload_csv": "Importer un fichier CSV (optionnel)",
        "upload_active": "Source active",
    },
    "en": {
        "tab1": "Overview",
        "tab2": "Stress & Autonomy",
        "app_title": "Karasek Dashboard",
        "app_subtitle": "Work well-being analysis · Karasek Model",
        "total_staff": "Total Workforce",
        "men": "Men",
        "women": "Women",
        "avg_age": "Average Age",
        "overweight": "Overweight & Obese",
        "lifestyle_title": "Lifestyle Indicators",
        "sedentarity": "Sedentary",
        "alcohol": "Alcohol",
        "tobacco": "Tobacco",
        "chronic": "Chronic Illness",
        "explore_title": "Demographic Data Explorer",
        "select_variable": "Choose a variable",
        "cross_with": "Cross with (optional)",
        "no_cross": "No cross-tabulation",
        "n_respondents": "N",
        "pct": "%",
        "stress_kpis_title": "Key Workplace Stress Indicators",
        "autonomy": "Decision-Making Autonomy",
        "autonomy_sub": "Perceived flexibility and control",
        "workload": "Perceived Mental Workload",
        "workload_sub": "Intensity of psychological demand",
        "social_support": "Team Cohesion",
        "social_support_sub": "Social support: colleagues & management",
        "mapp_title": "MAPP Stress Grid",
        "mapp_subtitle": "Each point represents one employee. Axes delimit Karasek Quadrants.",
        "x_axis_mapp": "Decision-making latitude (autonomy & skills)",
        "y_axis_mapp": "Psychological demand (mental workload)",
        "quadrant_pct_title": "Distribution by Karasek Quadrant",
        "active": "Active",
        "relaxed": "Relaxed",
        "tense": "Tense",
        "passive": "Passive",
        "radar_title": "Organizational Satisfaction",
        "radar_subtitle": "% of employees with a high satisfaction level per dimension",
        "radar_ref": "50% reference",
        "pct_satisfied": "High level",
        "recognition": "Recognition",
        "equity": "Workload Equity",
        "culture": "Company Culture",
        "satisfaction": "Satisfaction",
        "resources": "Resources & Goals",
        "management_support": "Management Support",
        "training": "Training",
        "skills": "Skills",
        "filter_title": "Filters",
        "filter_direction": "Department",
        "filter_csp": "Professional Category",
        "filter_genre": "Gender",
        "filter_age": "Age Group",
        "reset_btn": "↺ Reset",
        "n_filtered": "Filtered workforce",
        "lang_toggle": "FR",
        "var_genre": "Gender",
        "var_age": "Age Group",
        "var_anciennete": "Seniority",
        "var_csp": "Professional Category",
        "var_imc": "BMI Category",
        "var_imc_bin": "BMI (normal / overweight)",
        "var_direction": "Department",
        "var_tabac": "Tobacco Use",
        "var_alcool": "Alcohol Consumption",
        "var_sport": "Physical Activity",
        "var_maladie": "Chronic Illness",
        "cross_quadrant": "Karasek Quadrant ",
        "cross_dem": "Mental Workload",
        "cross_lat": "Decision-Making Autonomy",
        "cross_ss": "Social Support",
        "cross_rec": "Recognition",
        "cross_equ": "Workload Equity",
        "cross_cult": "Company Culture",
        "cross_sat": "Job Satisfaction",
        "cross_adq_res": "Resources and Objectives",
        "cross_adq_role": "Training Alignment",
        "cross_skills": "Skills Utilization",
        "cross_supmgmt": "Management Support",
        "high": "High",
        "low": "Low",
        "pct_label": "Percentage (%)",
        "hover_quad": "Zone",
        "hover_lat": "Autonomy",
        "hover_dem": "Mental Workload",
        "no_data": "Insufficient data for this cross-tabulation.",
        "missing_mapp": "Missing columns for MAPP grid",
        "all_option": "All",
        "select_cross_stress": "Choose a cross-tabulation",
        "upload_csv": "Upload a CSV file (optional)",
        "upload_active": "Active source",
    },
}

# =============================================================================
# HELPERS
# =============================================================================
def resolve_csp_col(df):
    for c in ("Categorie Socio", "Catégorie Socio", "CSP"):
        if c in df.columns: return c
    return None

def resolve_quadrant_col(df):
    for c in ("Karasek_quadrant_theoretical", "Karasek_quadrant_internal"):
        if c in df.columns: return c
    return None

def _norm_text(v):
    return re.sub(r"\s+", " ", str(v).strip()).casefold()

# =============================================================================
# CSS
# =============================================================================
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,400;1,9..144,600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #0F2340;
    font-size: 19px;
}

.stApp {
    background-color: #F0F7FF;
    background-image:
        radial-gradient(ellipse 1000px 500px at 10% -5%, rgba(56,163,232,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 600px 400px at 90% 105%, rgba(249,115,22,0.08) 0%, transparent 50%);
}

[data-testid="stSidebar"],
[data-testid="collapsedControl"],
section[data-testid="stSidebarContent"] { display: none !important; }

.main .block-container {
    padding-top: 0.75rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1500px;
}

/* ── HERO HEADER ── */
.hero-band {
    background: linear-gradient(135deg, #FFFFFF 0%, #F5F9FF 100%);
    border: 1px solid #D0E8F8;
    border-radius: 20px;
    padding: 1.4rem 2rem 1.3rem;
    margin-bottom: 0.9rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(56,163,232,0.08), 0 1px 0 rgba(255,255,255,0.9) inset;
}
.hero-band::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #38A3E8, #F97316, #38A3E8);
    background-size: 200% 100%;
    animation: shimmer 4s linear infinite;
}
@keyframes shimmer {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
.hero-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.hero-wordmark h1 {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 2rem;
    font-weight: 600;
    font-style: italic;
    color: #0F2340;
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1;
}
.hero-wordmark h1 span {
    color: #38A3E8;
}
.hero-subtitle {
    font-size: 0.86rem;
    color: #4E6A88;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-weight: 600;
    margin-top: 0.4rem;
}
.hero-right {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.hero-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #F97316;
    background: rgba(249,115,22,0.08);
    border: 1px solid rgba(249,115,22,0.25);
    border-radius: 999px;
    padding: 0.3rem 0.8rem;
}
.hero-chip::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #F97316;
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

/* ── FILTER BAR ── */
.filter-shell {
    background: #FFFFFF;
    border: 1px solid #D0E8F8;
    border-radius: 16px;
    padding: 1rem 1.5rem 0.8rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 2px 12px rgba(56,163,232,0.06);
    position: sticky;
    top: 0.55rem;
    z-index: 40;
    backdrop-filter: blur(6px);
}
.filter-label {
    font-size: 0.76rem;
    font-weight: 700;
    color: #2F577F;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
    display: block;
}

/* ── SECTION TITLE ── */
.section-title {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    font-family: 'Fraunces', serif;
    font-size: 1.2rem;
    font-style: italic;
    font-weight: 400;
    color: #0F2340;
    margin: 1.8rem 0 1rem;
    padding-bottom: 0.65rem;
    border-bottom: 2px solid #E4F0FB;
}
.section-title::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 20px;
    background: linear-gradient(180deg, #38A3E8 0%, #F97316 100%);
    border-radius: 2px;
    flex-shrink: 0;
}

/* ── KPI CARDS ── */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #D6E8F7;
    border-radius: 16px;
    padding: 1.3rem 1.2rem 1.1rem;
    text-align: center;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    animation: slideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 8px rgba(56,163,232,0.06);
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #38A3E8, #F97316);
    opacity: 0;
    transition: opacity 0.22s;
}
.kpi-card:hover {
    transform: translateY(-4px);
    border-color: #AAD5F5;
    box-shadow: 0 10px 32px rgba(56,163,232,0.15);
}
.kpi-card:hover::after { opacity: 1; }
.kpi-label {
    font-size: 0.8rem;
    color: #4E6A88 !important;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-weight: 700;
    margin-bottom: 0.55rem;
    display: block;
}
.kpi-icon {
    width: 38px; height: 38px;
    border-radius: 12px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.55rem;
}
.kpi-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.35rem;
    font-weight: 800;
    color: #0F2340 !important;
    line-height: 1;
    letter-spacing: -0.04em;
}
@keyframes slideUp {
    from { opacity:0; transform:translateY(14px); }
    to   { opacity:1; transform:translateY(0); }
}

/* ── GAUGE CARDS ── */
.gauge-card {
    background: #FFFFFF;
    border: 1px solid #D6E8F7;
    border-radius: 18px;
    padding: 1.6rem 1.2rem 1.3rem;
    text-align: center;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 8px rgba(56,163,232,0.06);
    height: 100%;
    position: relative;
    overflow: hidden;
}
.gauge-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #38A3E8, #F97316);
    opacity: 0;
    transition: opacity 0.22s;
}
.gauge-card:hover {
    transform: translateY(-4px);
    border-color: #AAD5F5;
    box-shadow: 0 12px 36px rgba(56,163,232,0.15);
}
.gauge-card:hover::before { opacity: 1; }
.gauge-semi-wrap {
    position: relative;
    width: 180px; height: 90px;
    margin: 0 auto 0.7rem;
    overflow: hidden;
}
.gauge-semi-bg {
    position: absolute;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: #EDF5FD;
    top: 0; left: 0;
}
.gauge-semi-fill {
    position: absolute;
    width: 180px; height: 180px;
    border-radius: 50%;
    top: 0; left: 0;
    background: conic-gradient(
        from 270deg,
        var(--gauge-color, #38A3E8) 0deg,
        var(--gauge-color, #38A3E8) calc(var(--g, 0deg)),
        transparent               calc(var(--g, 0deg))
    );
    transition: --g 1.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.gauge-semi-inner {
    position: absolute;
    width: 112px; height: 112px;
    background: #FFFFFF;
    border-radius: 50%;
    top: 34px; left: 34px;
    box-shadow: inset 0 2px 8px rgba(56,163,232,0.06);
}
.gauge-semi-tick {
    position: absolute;
    width: 2px; height: 18px;
    background: #D6E8F7;
    top: 4px; left: 89px;
    transform-origin: bottom center;
}
.gauge-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: #0F2340;
    line-height: 1;
    letter-spacing: -0.04em;
}
.gauge-pct { font-size: 1rem; font-weight: 500; color: #6B88A8; }
.gauge-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.96rem;
    font-weight: 700;
    color: #0F2340;
    margin-top: 0.55rem;
}
.gauge-sublabel {
    font-size: 0.84rem;
    color: #4E6A88;
    margin-top: 0.25rem;
    line-height: 1.5;
}
.gauge-badge {
    display: inline-block;
    margin-top: 0.7rem;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.22rem 0.85rem;
    border-radius: 999px;
}
.gauge-badge.good  { background: #DCFCE7; color: #15803D; }
.gauge-badge.warn  { background: #FEF3C7; color: #B45309; }
.gauge-badge.alert { background: #FEE2E2; color: #B91C1C; }

/* ── PROGRESS BARS ── */
.prog-track {
    background: #EDF5FD;
    border-radius: 999px;
    height: 7px;
    overflow: hidden;
    margin-top: 5px;
}
.panel-relief {
    background: #FFFFFF;
    border: 1px solid #D6E8F7;
    border-radius: 16px;
    padding: 0.9rem 1rem 0.6rem;
    box-shadow: 0 3px 14px rgba(56,163,232,0.08);
}
.prog-fill {
    height: 7px;
    border-radius: 999px;
    width: 0%;
    transition: width 1.1s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── ZONE CARDS ── */
.workzone-card {
    background: #FFFFFF;
    border: 1px solid #D6E8F7;
    border-radius: 14px;
    padding: 1.1rem 1rem;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
    animation: slideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 6px rgba(56,163,232,0.05);
}
.workzone-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(56,163,232,0.12);
}

/* ── LIFESTYLE CARDS ── */
.ls-card {
    background: #FFFFFF;
    border: 1px solid #D6E8F7;
    border-radius: 14px;
    padding: 1.1rem 1rem;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
    animation: slideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 6px rgba(56,163,232,0.05);
}
.ls-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(56,163,232,0.1);
}

/* ── SAT KPI CARDS ── */
.sat-kpi-card {
    background: #FFFFFF;
    border: 1px solid #D6E8F7;
    border-radius: 14px;
    padding: 1.1rem 1rem;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 6px rgba(56,163,232,0.05);
}
.sat-kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(56,163,232,0.1);
}

/* ── TABS ── */
[data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border-radius: 12px;
    padding: 4px;
    gap: 3px;
    border: 1px solid #D0E8F8;
    box-shadow: 0 2px 8px rgba(56,163,232,0.07);
}
[data-baseweb="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    color: #6B88A8 !important;
    border-radius: 9px !important;
    padding: 0.5rem 1.4rem !important;
    transition: all 0.2s !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(135deg, #38A3E8, #2B8FD0) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 3px 12px rgba(56,163,232,0.3) !important;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

/* ── SELECTS ── */
[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-color: #C8DFF2 !important;
    border-radius: 10px !important;
    color: #0F2340 !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: #38A3E8 !important;
    box-shadow: 0 0 0 3px rgba(56,163,232,0.15) !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #38A3E8, #2B8FD0) !important;
    border: none !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 3px 10px rgba(56,163,232,0.25) !important;
    transition: all 0.18s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #F97316, #EA6A0A) !important;
    box-shadow: 0 4px 16px rgba(249,115,22,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ── SLIDER ── */
[data-testid="stSlider"] [role="slider"] {
    background: #38A3E8 !important;
    border-color: #38A3E8 !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #D6E8F7 !important;
    box-shadow: 0 2px 8px rgba(56,163,232,0.06) !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #EDF5FD; }
::-webkit-scrollbar-thumb { background: #AAD5F5; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #38A3E8; }

hr { border: none; border-top: 1px solid #E4F0FB; margin: 1rem 0; }

@property --g {
    syntax: '<angle>';
    inherits: false;
    initial-value: 0deg;
}
</style>
""", unsafe_allow_html=True)

def inject_animation_js():
    components.html("""
    <script>
    const rootDoc = window.parent && window.parent.document ? window.parent.document : document;
    function easeOut(t) { return 1 - Math.pow(1 - t, 3); }
    function cleanNum(v, min, max) {
        var n = parseFloat(v);
        if (!isFinite(n)) n = 0;
        if (typeof min === 'number') n = Math.max(min, n);
        if (typeof max === 'number') n = Math.min(max, n);
        return n;
    }
    function isVisible(el) {
        if (!el || !el.isConnected) return false;
        const style = rootDoc.defaultView.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
    }
    function numberKey(el) {
        return [cleanNum(el.dataset.target,0,null), el.dataset.suffix||'', el.dataset.prefix||'', el.dataset.decimals||0].join('|');
    }
    function animateNumber(el) {
        const target = cleanNum(el.dataset.target, 0, null);
        const suffix = el.dataset.suffix || '';
        const prefix = el.dataset.prefix || '';
        const decimals = el.dataset.decimals ? parseInt(el.dataset.decimals, 10) : 0;
        const key = numberKey(el);
        if (el.dataset.animKey === key) return;
        el.dataset.animKey = key;
        const duration = 700;
        const start = performance.now();
        (function step(now) {
            const t = Math.min(1, (now - start) / duration);
            const current = Math.max(0, target * easeOut(t));
            el.textContent = prefix + (decimals === 0 ? Math.round(current) : current.toFixed(decimals)) + suffix;
            if (t < 1) requestAnimationFrame(step);
            else el.textContent = prefix + (decimals === 0 ? Math.round(target) : target.toFixed(decimals)) + suffix;
        })(start);
    }
    function animateGauge(fill) {
        const target = cleanNum(fill.dataset.target, 0, 100);
        const key = String(target);
        if (fill.dataset.animKey === key) return;
        fill.dataset.animKey = key;
        const counter = fill.closest('.gauge-card')?.querySelector('.gauge-counter');
        const duration = 800;
        const start = performance.now();
        fill.style.setProperty('--g', '0deg');
        requestAnimationFrame(() => setTimeout(() => fill.style.setProperty('--g', (target * 1.8).toFixed(1) + 'deg'), 60));
        if (counter) {
            (function step(now) {
                const t = Math.min(1, (now - start) / duration);
                counter.textContent = Math.round(target * easeOut(t));
                if (t < 1) requestAnimationFrame(step);
                else counter.textContent = Math.round(target);
            })(start);
        }
    }
    function animateProgress(el) {
        const target = cleanNum(el.dataset.target, 0, 100);
        const key = String(target);
        if (el.dataset.animKey === key) return;
        el.dataset.animKey = key;
        el.style.width = '0%';
        requestAnimationFrame(() => setTimeout(() => el.style.width = target + '%', 40));
    }
    function runFor(el) {
        if (el.matches('.animate-number')) animateNumber(el);
        else if (el.matches('.gauge-semi-fill[data-target]')) animateGauge(el);
        else if (el.matches('.prog-fill[data-target]')) animateProgress(el);
    }
    const observed = new WeakSet();
    const io = new IntersectionObserver(entries => {
        entries.forEach(e => { if (e.isIntersecting && isVisible(e.target)) runFor(e.target); });
    }, { threshold: 0.2 });
    function register() {
        rootDoc.querySelectorAll('.animate-number, .gauge-semi-fill[data-target], .prog-fill[data-target]').forEach(el => {
            if (el.matches('.animate-number')) { const k = numberKey(el); if (el.dataset.animKey && el.dataset.animKey !== k) delete el.dataset.animKey; }
            else { const t = cleanNum(el.dataset.target, 0, 100); if (el.dataset.animKey && el.dataset.animKey !== String(t)) delete el.dataset.animKey; }
            if (!observed.has(el)) { io.observe(el); observed.add(el); }
            if (isVisible(el)) {
                const r = el.getBoundingClientRect(), vh = rootDoc.defaultView?.innerHeight || 900;
                if (r.top < vh * 0.92 && r.bottom > 0) runFor(el);
            }
        });
    }
    setTimeout(register, 60);
    let t = null;
    new MutationObserver(() => { if (t) clearTimeout(t); t = setTimeout(() => setTimeout(register, 60), 90); }).observe(rootDoc.body, { childList: true, subtree: true });
    rootDoc.addEventListener('click', evt => { if (evt.target?.closest('[role="tab"]')) setTimeout(() => setTimeout(register, 60), 120); }, true);
    </script>
    """, height=0)

# =============================================================================
# DATA
# =============================================================================
@st.cache_data
def load_data(path):
    for enc in ("utf-8-sig", "latin-1"):
        try: return pd.read_csv(path, encoding=enc, sep=None, engine="python")
        except: continue
    return pd.DataFrame()

def load_uploaded_data(uploaded_file):
    raw = uploaded_file.getvalue()
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc, sep=None, engine="python")
        except Exception:
            continue
    return pd.DataFrame()

def apply_filters(df, dir_val, csp_val, genre_val, age_range):
    out = df.copy()
    t_all = T.get(st.session_state.get("lang", "fr"), {}).get("all_option", "Tous")
    if "Direction" in out.columns and dir_val and dir_val != t_all:
        dir_norm = out["Direction"].astype(str).map(_norm_text)
        selected = _norm_text(dir_val)
        mask = (dir_norm == selected)
        # Fallback for label variants (e.g., short/long names such as "Abidjan Nord")
        if not mask.any():
            mask = dir_norm.str.contains(selected, regex=False)
        out = out[mask]
    csp_col = resolve_csp_col(out)
    if csp_col and csp_val and csp_val != t_all:
        out = out[out[csp_col].astype(str).map(_norm_text) == _norm_text(csp_val)]
    if "Genre" in out.columns and genre_val and genre_val != t_all:
        out = out[out["Genre"].astype(str).map(_norm_text) == _norm_text(genre_val)]
    if "Age" in out.columns and age_range:
        ages = pd.to_numeric(out["Age"], errors="coerce")
        out = out[(ages >= age_range[0]) & (ages <= age_range[1])]
    return out

def pct_category(df, col, val):
    if not col or col not in df.columns: return 0.0
    valid = df[col].dropna()
    return float((valid == val).sum() / len(valid) * 100) if len(valid) > 0 else 0.0

def get_pct_high(df, score_col):
    if score_col in {"adq_resources_score", "adq_role_score"}:
        if score_col in THRESHOLDS and score_col in df.columns:
            valid = pd.to_numeric(df[score_col], errors="coerce").dropna()
            if len(valid) > 0: return float((valid > THRESHOLDS[score_col]).sum() / len(valid) * 100)
    cat_col = f"{score_col}_theo_cat"
    if cat_col in df.columns:
        valid = df[cat_col].dropna()
        if len(valid) > 0: return float(valid.isin(["Eleve","Élevé","Elevé","High"]).sum() / len(valid) * 100)
    if score_col in THRESHOLDS and score_col in df.columns:
        valid = pd.to_numeric(df[score_col], errors="coerce").dropna()
        if len(valid) > 0: return float((valid > THRESHOLDS[score_col]).sum() / len(valid) * 100)
    return 0.0

def get_high_stats(df, score_col):
    if score_col in {"adq_resources_score", "adq_role_score"} and score_col in THRESHOLDS and score_col in df.columns:
        valid = pd.to_numeric(df[score_col], errors="coerce").dropna()
        if len(valid) > 0:
            high_n = int((valid > THRESHOLDS[score_col]).sum())
            return float(high_n / len(valid) * 100), high_n, int(len(valid))
    cat_col = f"{score_col}_theo_cat"
    if cat_col in df.columns:
        valid = df[cat_col].dropna()
        if len(valid) > 0:
            high_n = int(valid.isin(["Eleve", "Élevé", "Elevé", "High"]).sum())
            return float(high_n / len(valid) * 100), high_n, int(len(valid))
    if score_col in THRESHOLDS and score_col in df.columns:
        valid = pd.to_numeric(df[score_col], errors="coerce").dropna()
        if len(valid) > 0:
            high_n = int((valid > THRESHOLDS[score_col]).sum())
            return float(high_n / len(valid) * 100), high_n, int(len(valid))
    return 0.0, 0, 0

# =============================================================================
# PLOTLY HELPERS
# =============================================================================

def plotly_layout(fig, title="", height=None):
    upd = dict(
        plot_bgcolor="#FAFCFF",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#0F2340", size=12),
        title=dict(text=title, font=dict(family="Fraunces, serif", size=14, color="#0F2340"), x=0.02),
        xaxis=dict(showgrid=True, gridcolor="#EDF5FD", gridwidth=1,
                showline=True, linecolor="#D6E8F7", zeroline=False,
                tickfont=dict(color="#6B88A8", size=11)),
        yaxis=dict(showgrid=True, gridcolor="#EDF5FD", gridwidth=1,
                showline=False, zeroline=False,
                tickfont=dict(color="#6B88A8", size=11)),
        legend=dict(bgcolor="rgba(255,255,255,0.95)", bordercolor="#D6E8F7",
                    borderwidth=1, font=dict(color="#0F2340", size=11)),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    if height: upd["height"] = height
    fig.update_layout(**upd)
    return fig

def make_barplot(df, col, lang):
    counts = df[col].value_counts().reset_index()
    counts.columns = [col, "n"]
    counts["pct"] = (counts["n"] / counts["n"].sum() * 100).round(1)
    palette = ["#38A3E8","#F97316","#22C55E","#EF4444","#A78BFA","#06B6D4","#FB923C","#84CC16"]
    fig = go.Figure()
    for i, row in counts.iterrows():
        fig.add_trace(go.Bar(
            y=[row[col]], x=[row["pct"]], orientation="h",
            marker_color=palette[i % len(palette)], marker=dict(opacity=0.9, line=dict(width=0)),
            text=f"{row['pct']}%  ({row['n']})", textposition="outside",
            textfont=dict(color="#6B88A8", size=11, family="Plus Jakarta Sans"),
            showlegend=False,
        ))
    fig = plotly_layout(fig, height=max(250, len(counts) * 55 + 80))
    fig.update_xaxes(range=[0, 130], title_text=T[lang]["pct_label"])
    return fig

def make_stacked_bar(df, x_col, hue_col, lang):
    if not x_col or not hue_col: return None
    if x_col not in df.columns or hue_col not in df.columns: return None
    tmp = df[[x_col, hue_col]].dropna()
    if tmp.empty: return None
    ct  = pd.crosstab(tmp[x_col], tmp[hue_col])
    pct = ct.div(ct.sum(axis=1), axis=0) * 100
    binary_map = {"Eleve":"#22C55E","Élevé":"#22C55E","Faible":"#EF4444","High":"#22C55E","Low":"#EF4444","Présent":"#EF4444","Absent":"#22C55E"}
    generic = ["#38A3E8","#F97316","#22C55E","#EF4444","#A78BFA","#06B6D4"]
    def get_color(cat, idx):
        if cat in KARASEK_COLORS: return KARASEK_COLORS[cat]
        if cat in binary_map:     return binary_map[cat]
        return generic[idx % len(generic)]
    fig = go.Figure()
    for i, cat in enumerate(pct.columns):
        vals, ns = pct[cat].values, ct[cat].values
        texts = [f"{v:.1f}%  ({n})" if v >= 6 else "" for v, n in zip(vals, ns)]
        fig.add_trace(go.Bar(
            name=str(cat), y=list(pct.index), x=vals, orientation="h",
            marker_color=get_color(str(cat), i), marker=dict(opacity=0.9, line=dict(width=0)),
            text=texts, textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=11, family="Plus Jakarta Sans"),
        ))
    fig = plotly_layout(fig, height=max(280, len(pct.index) * 55 + 100))
    fig.update_layout(barmode="stack", xaxis=dict(range=[0, 100], title_text=T[lang]["pct_label"]))
    return fig

def make_radar(scores, labels, lang):
    values = [scores.get(l, 0) for l in labels]
    vc = values + [values[0]]
    lc = labels + [labels[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[50]*(len(labels)+1), theta=lc, fill="toself",
        fillcolor="rgba(249,115,22,0.05)",
        line=dict(color="rgba(249,115,22,0.4)", dash="dot", width=1.5),
        name=T[lang]["radar_ref"], hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=vc, theta=lc, fill="toself",
        fillcolor="rgba(56,163,232,0.12)",
        line=dict(color="#38A3E8", width=2.5),
        marker=dict(color="#38A3E8", size=7, line=dict(color="#FFFFFF", width=2)),
        name=T[lang]["pct_satisfied"],
        hovertemplate="<b>%{theta}</b><br>%{r:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#FAFCFF",
            angularaxis=dict(tickfont=dict(color="#0F2340", size=10, family="Plus Jakarta Sans"),
                             linecolor="#D6E8F7", gridcolor="#EDF5FD"),
            radialaxis=dict(visible=True, range=[0, 100],
                            tickfont=dict(color="#6B88A8", size=9),
                            gridcolor="#EDF5FD", linecolor="#D6E8F7", ticksuffix="%"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color="#0F2340"),
        legend=dict(bgcolor="rgba(255,255,255,0.95)", bordercolor="#D6E8F7",
                    borderwidth=1, font=dict(color="#0F2340", size=11), x=0.75, y=1.1),
        height=500, margin=dict(l=60, r=60, t=40, b=40),
    )
    return fig

# =============================================================================
# HTML COMPONENTS
# =============================================================================
def section_title(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)

def kpi_icon_svg(path_d, bg, fg):
    return (
        f'<span class="kpi-icon" style="background:{bg};color:{fg};">'
        f'<svg viewBox="0 0 24 24" width="17" height="17" fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<path d="{path_d}" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>'
        f'</svg></span>'
    )

def html_kpi_card(value, label, suffix="", prefix="", decimals=0, subtitle="", icon=""):
    num = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    num = 0.0 if pd.isna(num) else float(num)
    rendered = f"{num:.{decimals}f}" if decimals > 0 else str(int(round(num)))
    subtitle_html = f'<div style="margin-top:0.4rem;font-size:0.78rem;font-weight:600;color:#4E6A88;">{subtitle}</div>' if subtitle else ""
    icon_html = icon if str(icon).strip().startswith("<") else ""
    return f"""
    <div class="kpi-card">
        {icon_html}
        <span class="kpi-label">{label}</span>
        <div class="kpi-value animate-number"
             data-target="{num}" data-suffix="{suffix}" data-prefix="{prefix}" data-decimals="{decimals}">{prefix}{rendered}{suffix}</div>
        {subtitle_html}
    </div>
    """

def html_lifestyle_card(value, label, suffix="%"):
    num = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    num = 0.0 if pd.isna(num) else float(num)
    disp = int(round(num))
    color = "#22C55E" if num < 35 else "#EF4444" if num > 60 else "#F97316"
    border = color
    return f"""
    <div class="ls-card" style="border-top: 3px solid {border};">
        <span class="kpi-label">{label}</span>
        <div class="kpi-value animate-number" style="color:{color};font-size:1.8rem;"
            data-target="{disp}" data-suffix="{suffix}" data-prefix="" data-decimals="0">{disp}{suffix}</div>
    </div>
    """

def html_gauge(value, label, sublabel, is_favorable):
    target = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    target = 0.0 if pd.isna(target) else max(0.0, min(100.0, float(target)))
    disp = int(round(target))
    if target > 50:
        color, badge_cls, badge_txt = "#22C55E", "good", "Élevé"
    else:
        color, badge_cls, badge_txt = "#EF4444", "alert", "Faible"
    return f"""
    <div class="gauge-card">
        <div class="gauge-semi-wrap">
            <div class="gauge-semi-bg"></div>
            <div class="gauge-semi-fill" style="--gauge-color:{color}; --g:{target*1.8:.1f}deg;" data-target="{disp}"></div>
            <div class="gauge-semi-inner"></div>
            <div class="gauge-semi-tick"></div>
        </div>
        <div class="gauge-value">
            <span class="gauge-counter" style="color:{color};">{disp}</span><span class="gauge-pct">%</span>
        </div>
        <div class="gauge-label">{label}</div>
        <div class="gauge-sublabel">{sublabel}</div>
        <span class="gauge-badge {badge_cls}">{badge_txt}</span>
    </div>
    """

def html_progress_row(label, pct, color, n_count=0):
    val = pd.to_numeric(pd.Series([pct]), errors="coerce").iloc[0]
    val = 0.0 if pd.isna(val) else max(0.0, min(100.0, float(val)))
    return f"""
    <div style="margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span style="font-size:0.78rem;color:#3B5878;font-family:'Plus Jakarta Sans',sans-serif;font-weight:500;">{label}</span>
            <span style="font-size:0.82rem;font-weight:700;color:{color};font-family:'Plus Jakarta Sans',sans-serif;">{val:.0f}% ({int(n_count)})</span>
        </div>
        <div class="prog-track">
            <div class="prog-fill" style="background:{color};width:{val:.1f}%;" data-target="{val:.1f}"></div>
        </div>
    </div>
    """

def html_workzone_card(label, pct, n_count, color):
    val = pd.to_numeric(pd.Series([pct]), errors="coerce").iloc[0]
    val = 0.0 if pd.isna(val) else max(0.0, min(100.0, float(val)))
    disp = int(round(val))
    return f"""
    <div class="workzone-card" style="border-top: 3px solid {color};">
        <span class="kpi-label">{label}</span>
        <div class="kpi-value animate-number" style="color:{color};font-size:1.8rem;"
             data-target="{disp}" data-suffix="%" data-prefix="" data-decimals="0">{disp}%</div>
        <div style="margin-top:0.35rem;font-size:0.78rem;font-weight:600;color:#4E6A88;">{int(n_count)}</div>
    </div>
    """

# =============================================================================
# UI HELPERS
# =============================================================================
def safe_selectbox(label, options, key, on_change=None, args=()):
    if not options:
        st.selectbox(label, ["—"], key=f"{key}_empty", disabled=True)
        return None
    if key not in st.session_state or st.session_state.get(key) not in options:
        st.session_state[key] = options[0]
    return st.selectbox(
        label,
        options=options,
        key=key,
        label_visibility="collapsed",
        on_change=on_change,
        args=args,
    )

def reset_dashboard_state(all_opt, age_bounds):
    for k in ("filter_dirs","filter_csps","filter_genres"):
        st.session_state[k] = all_opt
    if age_bounds: st.session_state["filter_age_range"] = age_bounds
    for k in [k for k in list(st.session_state.keys()) if k.startswith("sel_")]:
        st.session_state.pop(k, None)

def on_direction_change(all_opt):
    st.session_state["filter_csps"] = all_opt
    st.session_state["filter_genres"] = all_opt

# =============================================================================
# HEADER + FILTERS
# =============================================================================
def render_header(lang):
    h_left, h_right = st.columns([9, 1])
    with h_left:
        st.markdown(f"""
        <div class="hero-band">
            <div class="hero-inner">
                <div class="hero-wordmark">
                    <h1>Karasek <span>Dashboard</span></h1>
                    <div class="hero-subtitle">{T[lang]['app_subtitle']}</div>
                </div>
                <div class="hero-chip">Tableau de bord interactif</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with h_right:
        st.write("")
        st.write("")
        if st.button(T[lang]["lang_toggle"], key="lang_btn", use_container_width=True):
            new_lang = "en" if lang == "fr" else "fr"
            for k in [k for k in list(st.session_state.keys()) if k.startswith("sel_")]:
                del st.session_state[k]
            st.session_state["lang"] = new_lang
            st.rerun()

def render_top_filters(df_raw, lang):
    t = T[lang]
    all_opt = t["all_option"]
    def cleaned_options(series):
        out = {}
        for raw in series.dropna().astype(str):
            cleaned = re.sub(r"\s+", " ", raw.strip())
            if not cleaned:
                continue
            out.setdefault(_norm_text(cleaned), cleaned)
        return sorted(out.values(), key=_norm_text)

    dirs = [all_opt] + (cleaned_options(df_raw["Direction"]) if "Direction" in df_raw.columns else [])
    current_dir = st.session_state.get("filter_dirs", all_opt)
    if current_dir not in dirs:
        current_dir = all_opt
        st.session_state["filter_dirs"] = all_opt

    dep_df = df_raw
    if "Direction" in df_raw.columns and current_dir != all_opt:
        dep_df = df_raw[df_raw["Direction"].astype(str).map(_norm_text) == _norm_text(current_dir)]

    csp_c = resolve_csp_col(df_raw)
    csps = [all_opt] + (cleaned_options(dep_df[csp_c]) if csp_c else [])
    genres = [all_opt] + (cleaned_options(dep_df["Genre"]) if "Genre" in dep_df.columns else [])
    age_series = pd.to_numeric(df_raw["Age"], errors="coerce").dropna() if "Age" in df_raw.columns else pd.Series(dtype=float)
    age_bounds = None
    if not age_series.empty:
        age_bounds = (int(np.floor(age_series.min())), int(np.ceil(age_series.max())))
        if "filter_age_range" not in st.session_state or not isinstance(st.session_state.get("filter_age_range"), tuple):
            st.session_state["filter_age_range"] = age_bounds
        else:
            cur_lo, cur_hi = st.session_state["filter_age_range"]
            st.session_state["filter_age_range"] = (max(age_bounds[0], int(cur_lo)), min(age_bounds[1], int(cur_hi)))

    with st.container(border=True):
        f1, f2, f3, f4, f5 = st.columns([2.4, 2.4, 1.8, 3.0, 1.6])
        with f1:
            st.markdown(f'<span class="filter-label">{t["filter_direction"]}</span>', unsafe_allow_html=True)
            sel_dirs = safe_selectbox("", dirs, key="filter_dirs", on_change=on_direction_change, args=(all_opt,))
        with f2:
            st.markdown(f'<span class="filter-label">{t["filter_csp"]}</span>', unsafe_allow_html=True)
            sel_csps = safe_selectbox("", csps, key="filter_csps")
        with f3:
            st.markdown(f'<span class="filter-label">{t["filter_genre"]}</span>', unsafe_allow_html=True)
            sel_genres = safe_selectbox("", genres, key="filter_genres")
        with f4:
            st.markdown(f'<span class="filter-label">{t["filter_age"]}</span>', unsafe_allow_html=True)
            if age_bounds:
                sel_age_range = st.slider("", min_value=age_bounds[0], max_value=age_bounds[1],
                                        value=st.session_state["filter_age_range"],
                                        key="filter_age_range", label_visibility="collapsed")
            else:
                st.slider("", 0, 1, (0,1), disabled=True, label_visibility="collapsed")
                sel_age_range = None
        with f5:
            st.write("")
            st.markdown("<div style='height:0.82rem;'></div>", unsafe_allow_html=True)
            if st.button(t["reset_btn"], key="reset_dashboard_btn", use_container_width=True,
                        on_click=reset_dashboard_state, args=(all_opt, age_bounds)):
                st.rerun()
    return sel_dirs, sel_csps, sel_genres, sel_age_range

# =============================================================================
# TAB 1
# =============================================================================
def render_tab1(df, lang):
    t = T[lang]
    section_title(t["total_staff"] + (" — Données démographiques" if lang=="fr" else " — Demographics"))
    total_n = len(df)
    genre_series = df["Genre"].astype(str).str.strip().str.lower() if "Genre" in df.columns else pd.Series(dtype=str)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(html_kpi_card(total_n, t["total_staff"],
            icon=kpi_icon_svg("M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M9.5 7a3 3 0 1 0 0-6 3 3 0 0 0 0 6M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a3 3 0 0 1 0 5.75",
                "rgba(56,163,232,0.1)", "#38A3E8")), unsafe_allow_html=True)
    with c2:
        n_men = int(genre_series.isin({"homme","male","m"}).sum()) if not genre_series.empty else 0
        st.markdown(html_kpi_card(n_men/total_n*100 if total_n>0 else 0, t["men"], suffix="%", decimals=0, subtitle=f"{n_men}",
            icon=kpi_icon_svg("M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4M5 21a7 7 0 0 1 14 0",
                "rgba(56,163,232,0.1)", "#38A3E8")), unsafe_allow_html=True)
    with c3:
        n_women = int(genre_series.isin({"femme","female","f"}).sum()) if not genre_series.empty else 0
        st.markdown(html_kpi_card(n_women/total_n*100 if total_n>0 else 0, t["women"], suffix="%", decimals=0, subtitle=f"{n_women}",
            icon=kpi_icon_svg("M12 11a4 4 0 1 0-4-4 4 4 0 0 0 4 4M8 15h8l1.5 6h-11zM12 15v6",
                "rgba(249,115,22,0.1)", "#F97316")), unsafe_allow_html=True)
    with c4:
        avg_age = pd.to_numeric(df["Age"], errors="coerce").mean() if "Age" in df.columns else 0
        st.markdown(html_kpi_card(avg_age, t["avg_age"], suffix=" ans" if lang=="fr" else " yrs", decimals=0,
            icon=kpi_icon_svg("M8 2v4M16 2v4M3 10h18M5 6h14a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z",
                "rgba(249,115,22,0.1)", "#F97316")), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_title(t["lifestyle_title"])
    alcool_col = next((c for c in ("Consommation reguliere d\u2019alcool","Consommation reguliere d'alcool") if c in df.columns), None)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(html_lifestyle_card(pct_category(df,'Pratique reguliere du sport','Non'), t["sedentarity"]), unsafe_allow_html=True)
    with c2: st.markdown(html_lifestyle_card(pct_category(df, alcool_col,'Oui') if alcool_col else 0.0, t["alcohol"]), unsafe_allow_html=True)
    with c3: st.markdown(html_lifestyle_card(pct_category(df,'tabagisme','Oui'), t["tobacco"]), unsafe_allow_html=True)
    with c4: st.markdown(html_lifestyle_card(pct_category(df,'Avez-vous une maladie chronique','Oui'), t["chronic"]), unsafe_allow_html=True)
    with c5: st.markdown(html_lifestyle_card(pct_category(df,'IMC_binaire','Surpoids/Obésité'), t["overweight"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_title(t["explore_title"])
    csp_actual = resolve_csp_col(df) or "Categorie Socio"
    VAR_MAP = {
        t["var_genre"]:"Genre", t["var_age"]:"Tranche_age",
        t["var_anciennete"]:"Tranche_anciennete", t["var_csp"]:csp_actual,
        t["var_imc"]:"Categorie_IMC", t["var_imc_bin"]:"IMC_binaire",
        t["var_direction"]:"Direction", t["var_tabac"]:"tabagisme",
        t["var_alcool"]:alcool_col or "", t["var_sport"]:"Pratique reguliere du sport",
        t["var_maladie"]:"Avez-vous une maladie chronique",
    }
    CROSS_MAP = {
        t["no_cross"]:None, t["cross_quadrant"]:resolve_quadrant_col(df),
        t["cross_dem"]:"Dem_score_theo_cat", t["cross_lat"]:"Lat_score_theo_cat",
        t["cross_ss"]:"SS_score_theo_cat", t["cross_rec"]:"rec_score_theo_cat",
        t["cross_sat"]:"sat_score_theo_cat", t["cross_cult"]:"cult_score_theo_cat",
        t["cross_equ"]:"equ_score_theo_cat",
    }
    available_vars  = [k for k, v in VAR_MAP.items()  if v and v in df.columns]
    available_cross = [k for k, v in CROSS_MAP.items() if v is None or v in df.columns]
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown(f'<span class="filter-label">{t["select_variable"]}</span>', unsafe_allow_html=True)
        sel_var = safe_selectbox(t["select_variable"], available_vars, key="sel_var_tab1")
    with cc2:
        st.markdown(f'<span class="filter-label">{t["cross_with"]}</span>', unsafe_allow_html=True)
        sel_cross = safe_selectbox(t["cross_with"], available_cross, key="sel_cross_tab1")
    real_col  = VAR_MAP.get(sel_var)   if sel_var   else None
    cross_col = CROSS_MAP.get(sel_cross) if sel_cross else None
    if real_col and real_col in df.columns:
        if cross_col:
            fig = make_stacked_bar(df, real_col, cross_col, lang)
            if fig: st.plotly_chart(fig, use_container_width=True, key="chart_tab1_cross")
            else:   st.info(t["no_data"])
        else:
            col_chart, col_table = st.columns([6, 4])
            with col_chart:
                st.plotly_chart(make_barplot(df, real_col, lang), use_container_width=True, key="chart_tab1_bar")
            with col_table:
                cnt = df[real_col].value_counts().reset_index()
                cnt.columns = [sel_var, t["n_respondents"]]
                cnt[t["pct"]] = (cnt[t["n_respondents"]] / cnt[t["n_respondents"]].sum() * 100).round(1)
                st.dataframe(cnt, use_container_width=True, hide_index=True)

# =============================================================================
# TAB 2
# =============================================================================
def render_tab2(df, lang):
    t = T[lang]
    quad_col = resolve_quadrant_col(df)
    section_title(t["stress_kpis_title"])
    g1, g2, g3 = st.columns(3)
    with g1: st.markdown(html_gauge(get_pct_high(df,"Lat_score"), t["autonomy"],       t["autonomy_sub"],       True), unsafe_allow_html=True)
    with g2: st.markdown(html_gauge(get_pct_high(df,"Dem_score"), t["workload"],       t["workload_sub"],       False), unsafe_allow_html=True)
    with g3: st.markdown(html_gauge(get_pct_high(df,"SS_score"),  t["social_support"], t["social_support_sub"], True), unsafe_allow_html=True)

    st.markdown(f'<p style="font-family:Plus Jakarta Sans,sans-serif;font-size:0.9rem;font-weight:700;color:#2F577F;margin:1.2rem 0 0.55rem;letter-spacing:0.06em;text-transform:uppercase;">{t["quadrant_pct_title"]}</p>', unsafe_allow_html=True)
    if quad_col:
        qc1, qc2, qc3, qc4 = st.columns(4)
        total_v = len(df.dropna(subset=[quad_col]))
        zone_colors = {"Tendu":"#EF4444","Actif":"#22C55E","Passif":"#94A3B8","Detendu":"#38A3E8","Détendu":"#38A3E8"}
        aliases = {"Tendu":["Tendu","Tense"],"Actif":["Actif","Active"],"Passif":["Passif","Passive"],"Détendu":["Detendu","Détendu","Relaxed"]}
        for raw, lbl, col in [("Tendu",t["tense"],qc1),("Actif",t["active"],qc2),("Passif",t["passive"],qc3),("Détendu",t["relaxed"],qc4)]:
            n = int(df[quad_col].isin(aliases.get(raw,[raw])).sum())
            with col: st.markdown(html_workzone_card(lbl, n/total_v*100 if total_v>0 else 0, n, zone_colors.get(raw,"#94A3B8")), unsafe_allow_html=True)
    else:
        st.info(t["no_data"])

    st.markdown("<br>", unsafe_allow_html=True)
    section_title(t["mapp_title"])
    st.markdown(f'<p style="color:#4E6A88;font-size:0.98rem;margin-top:-0.3rem;line-height:1.55;">{t["mapp_subtitle"]}</p>', unsafe_allow_html=True)
    req = ["Dem_score","Lat_score"] + ([quad_col] if quad_col else [])
    if any(c not in df.columns for c in req):
        st.warning(t["missing_mapp"])
    else:
        df_plot = df[req].dropna().copy()
        if df_plot.empty:
            st.info(t["no_data"])
        else:
            qmap = ({"Actif":"Active","Detendu":"Relaxed","Détendu":"Relaxed","Tendu":"Tense","Passif":"Passive"}
                    if lang=="en" else
                    {"Actif":"Actif","Detendu":"Détendu","Détendu":"Détendu","Tendu":"Tendu","Passif":"Passif"})
            df_plot["quad_display"] = df_plot[quad_col].map(qmap).fillna(df_plot[quad_col])
            color_map = {v: KARASEK_COLORS.get(k,"#94A3B8") for k,v in qmap.items()}
            fig_sc = px.scatter(df_plot, x="Lat_score", y="Dem_score", color="quad_display",
                                color_discrete_map=color_map, opacity=0.75,
                                labels={"Lat_score":t["x_axis_mapp"],"Dem_score":t["y_axis_mapp"],"quad_display":t["hover_quad"]},
                                custom_data=["quad_display","Lat_score","Dem_score"])
            fig_sc.update_traces(marker=dict(size=8, line=dict(width=1, color="white")),
                                 hovertemplate=f"<b>{t['hover_quad']}</b>: %{{customdata[0]}}<br>{t['hover_lat']}: %{{customdata[1]:.1f}}<br>{t['hover_dem']}: %{{customdata[2]:.1f}}<extra></extra>")
            fig_sc.add_vline(x=60.0, line_dash="dot", line_color="rgba(249,115,22,0.45)", line_width=1.8)
            fig_sc.add_hline(y=22.5, line_dash="dot", line_color="rgba(249,115,22,0.45)", line_width=1.8)
            x_min,x_max = df_plot["Lat_score"].min(),df_plot["Lat_score"].max()
            y_min,y_max = df_plot["Dem_score"].min(), df_plot["Dem_score"].max()
            xr,yr = x_max-x_min, y_max-y_min
            px_,py_ = max(xr*0.04,0.5), max(yr*0.04,0.5)
            annots = {qmap["Actif"]:(x_max-px_,y_max-py_,"right","top"),qmap["Passif"]:(x_min+px_,y_min+py_,"left","bottom"),
                      qmap["Détendu"]:(x_max-px_,y_min+py_,"right","bottom"),qmap["Tendu"]:(x_min+px_,y_max-py_,"left","top")}
            for quad,(qx,qy,xa,ya) in annots.items():
                fig_sc.add_annotation(x=qx,y=qy,text=quad.upper(),showarrow=False,
                    font=dict(size=12,color=color_map.get(quad,"#94A3B8"),family="Plus Jakarta Sans"),
                    opacity=0.3,xanchor=xa,yanchor=ya)
            fig_sc = plotly_layout(fig_sc, height=500)
            fig_sc.update_layout(xaxis_title=t["x_axis_mapp"], yaxis_title=t["y_axis_mapp"], legend_title_text=t["hover_quad"])
            st.plotly_chart(fig_sc, use_container_width=True, key="chart_tab2_mapp")

    DIMENSIONS = [
        ("rec_score",t["recognition"]),("equ_score",t["equity"]),
        ("cult_score",t["culture"]),   ("sat_score",t["satisfaction"]),
        ("adq_resources_score",t["resources"]),("sup_score",t["management_support"]),
        ("adq_role_score",t["training"]),("comp_score",t["skills"]),
    ]
    dim_stats = {}
    for sc, lbl in DIMENSIONS:
        pct, n_high, _ = get_high_stats(df, sc)
        dim_stats[lbl] = (pct, n_high)
    dim_pcts = {lbl: v[0] for lbl, v in dim_stats.items()}
    section_title(t["radar_title"])
    with st.container(border=True):
        st.markdown(f'<p style="color:#4E6A88;font-size:0.98rem;margin:0.12rem 0 0.65rem;line-height:1.5;">{t["radar_subtitle"]}</p>', unsafe_allow_html=True)
        labels = [d[1] for d in DIMENSIONS]
        col_radar, col_legend = st.columns([6, 4])
        with col_radar:
            st.plotly_chart(make_radar(dim_pcts, labels, lang), use_container_width=True, key="chart_tab2_radar")
        with col_legend:
            st.markdown("<br><br>", unsafe_allow_html=True)
            bars_html = ""
            for label, (pct, n_high) in dim_stats.items():
                color = "#22C55E" if pct > 50 else "#EF4444"
                bars_html += html_progress_row(label, pct, color, n_high)
            st.markdown(bars_html, unsafe_allow_html=True)

# =============================================================================
# MAIN
# =============================================================================
def main():
    inject_css()
    inject_animation_js()
        # ── Topbar YODAN ──────────────────────────────────────────
    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    col_top, col_back = st.columns([9, 1])
    with col_top:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;background:white;border-radius:12px;'
            'padding:14px 24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06),'
            '0 4px 12px rgba(30,64,175,0.08);border:1px solid #e8edf5;">'
            '<div style="width:38px;height:38px;background:linear-gradient(135deg,#7c3aed,#a78bfa);'
            'border-radius:10px;display:flex;align-items:center;justify-content:center;">'
            '<i class="fas fa-briefcase" style="color:white;font-size:15px;"></i></div>'
            '<div>'
            '<div style="font-size:16px;font-weight:700;color:#1e293b;">Karasek — Modèle Demande-Contrôle</div>'
            '<div style="font-size:11px;color:#64748b;margin-top:1px;">Analyse du stress professionnel · Pahaliah &amp; Fils</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
    with col_back:
        st.write("")
        st.write("")
        if st.button("← Accueil", key="back_home_karasek", use_container_width=True):
            st.switch_page("app.py")
        
    if "lang" not in st.session_state:
        st.session_state["lang"] = "fr"
    lang = st.session_state["lang"]

    render_header(lang)
    lang = st.session_state["lang"]

    default_path = "data/karasek_wave_ci_clean.csv"
    uploaded = st.file_uploader(T[lang]["upload_csv"], type=["csv"], key="uploaded_csv")
    if uploaded is not None:
        df_raw = load_uploaded_data(uploaded)
        src_label = uploaded.name
    else:
        df_raw = load_data(default_path)
        src_label = default_path

    st.caption(f"{T[lang]['upload_active']}: {src_label}")
    if df_raw.empty:
        st.error("CSV introuvable ou illisible.")
        st.stop()

    sel_dirs, sel_csps, sel_genres, sel_age_range = render_top_filters(df_raw, lang)
    df = apply_filters(df_raw, sel_dirs, sel_csps, sel_genres, sel_age_range)

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.6rem;margin:-0.3rem 0 0.6rem auto;width:fit-content;">
        <span style="font-size:0.65rem;color:#6B88A8;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">
            {T[lang]['n_filtered']}
        </span>
        <span style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.05rem;font-weight:800;color:#38A3E8;
                    background:rgba(56,163,232,0.08);padding:0.1rem 0.6rem;border-radius:8px;
                    border:1px solid rgba(56,163,232,0.2);"
            class="animate-number" data-target="{len(df)}" data-suffix="" data-prefix="" data-decimals="0">{len(df)}</span>
    </div>
    """, unsafe_allow_html=True)

    if len(df) == 0:
        st.warning("Aucun répondant ne correspond aux filtres sélectionnés.")
        st.stop()

    t = T[lang]
    tab1, tab2 = st.tabs([t["tab1"], t["tab2"]])
    with tab1: render_tab1(df, lang)
    with tab2: render_tab2(df, lang)

if __name__ == "__main__":
    main()