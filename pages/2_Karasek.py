# =============================================================================
# karasek_app.py — Application Streamlit Karasek
# Design & palette du dashboard original Wave-CI
# Seuil théorique uniquement (point médian de l'échelle — non clinique)
# =============================================================================

from pathlib import Path
import base64
import io
import re
import sys
import unicodedata
from difflib import SequenceMatcher

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
import streamlit.components.v1 as components
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Karasek · Bien-être",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# PALETTE & CONSTANTES
# =============================================================================
KARASEK_COLORS = {
    "Actif":   "#22C55E",
    "Détendu": "#38A3E8",
    "Detendu": "#38A3E8",
    "Tendu":   "#EF4444",
    "Passif":  "#94A3B8",
}

LIKERT_MIN = 1
LIKERT_MAX = 4

# Seuils théoriques — point médian de l'échelle Likert 1-4 (non cliniques)
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
    "adq_resources_score":  5.0,
    "adq_role_score":       5.0,
}

RENAME_MAPPING = {
    # ── Utilisation des compétences (comp) ──────────────────────────────────
    "Dans mon travail, je dois apprendre des choses nouvelles":                                                              "Q1_comp",
    "Dans mon travail j’effectue des tâches répétitives":                                               "Q2_comp",
    "Dans mon travail j'effectue des tâches répétitives":                                                    "Q2_comp",
    "Mon travail me demande d’être créatif":                                                                  "Q3_comp",
    "Mon travail me demande d'être créatif":                                                                       "Q3_comp",
    "Mon travail me demande un haut niveau de compétence":                                                              "Q4_comp",
    "Dans mon travail, j’ai des activités variées":                                                          "Q5_comp",
    "Dans mon travail, j'ai des activités variées":                                                               "Q5_comp",
    "J’ai l’occasion de développer mes compétences professionnelles":                                    "Q6_comp",
    "J'ai l'occasion de développer mes compétences professionnelles":                                              "Q6_comp",
    # ── Autonomie décisionnelle (auto) ───────────────────────────────────────
    "Mon travail me permet souvent de prendre des décisions moi-même":                                             "Q1_auto",
    "Dans ma tâche, j’ai très peu de liberté pour décider comment je fais mon travail":            "Q2_auto",
    "Dans ma tâche, j'ai très peu de liberté pour décider comment je fais mon travail":                 "Q2_auto",
    "J’ai la possibilité d’influencer le déroulement de mon travail":                                    "Q3_auto",
    "J'ai la possibilité d'influencer le déroulement de mon travail":                                              "Q3_auto",
    # ── Demande psychologique (dem) ──────────────────────────────────────────
    "Mon travail me demande de travailler très vite":                                                                   "Q1_dem",
    "Mon travail demande de travailler intensement":                                                                          "Q2_dem",
    "On me demande d’effectuer une quantité de travail excessive":                                                  "Q3_dem",
    "On me demande d'effectuer une quantité de travail excessive":                                                       "Q3_dem",
    "Je dispose du temps nécessaire pour effectuer correctement mon travail":                                            "Q4_dem",
    "Je reçois des ordres contradictoires de la part d’autres personnes":                                          "Q5_dem",
    "Je reçois des ordres contradictoires de la part d'autres personnes":                                                "Q5_dem",
    "Mon travail nécessite de longues périodes de concentration intense":                                          "Q6_dem",
    "Mes tâches sont souvent interrompues avant d’être achevées, nécessitant de les reprendre plus tard": "Q7_dem",
    "Mes tâches sont souvent interrompues avant d'être achevées, nécessitant de les reprendre plus tard": "Q7_dem",
    "Mon travail est « très bouscu lé » ":                                                     "Q8_dem",
    "Mon travail est « très bouscu lé » ":                                                               "Q8_dem",
    "Mon travail est « très bouscu »":                                                              "Q8_dem",
    "Mon travail est « très bouscu lé »":                                                      "Q8_dem",
    "Attendre le travail de collègues ralentit souvent mon propre travail":                                              "Q9_dem",
    # ── Soutien hiérarchique (sup) ───────────────────────────────────────────
    "Mon supérieur se sent concerné par le bien-être de ses subordonnés":                                "Q1_sup",
    "Mon supérieur prête attention à ce que je dis":                                                          "Q2_sup",
    "Mon supérieur m’aide à mener ma tâche à bien":                                                  "Q3_sup",
    "Mon supérieur m'aide à mener ma tâche à bien":                                                       "Q3_sup",
    "Mon supérieur réussit facilement à faire collaborer ses subordonnés":                                "Q4_sup",
    # ── Soutien des collègues (col) ──────────────────────────────────────────
    "Les collègues avec qui je travaille sont des gens professionnellement compétent":                             "Q1_col",
    "Les collègues avec qui je travaille me manifestent de l’intérêt":                                   "Q2_col",
    "Les collègues avec qui je travaille me manifestent de l'intérêt":                                        "Q2_col",
    "Les collègues avec qui je travaille sont amicaux":                                                                  "Q3_col",
    "Les collègues avec qui je travaille m’aident à mener les tâches à bien":                      "Q4_col",
    "Les collègues avec qui je travaille m'aident à mener les tâches à bien":                            "Q4_col",
    # ── Reconnaissance (rec) ────────────────────────────────────────────────
    "On me traite injustement dans mon travail":                                                                              "Q1_rec",
    "Ma sécurité d’emploi est menacée":                                                                   "Q2_rec",
    "Ma sécurité d'emploi est menacée":                                                                        "Q2_rec",
    "Ma position professionnelle actuelle correspond bien à ma formation":                                               "Q3_rec",
    "Vu tous mes efforts, je reçois le respect et l’estime que je mérite":                                    "Q4_rec",
    "Vu tous mes efforts, je reçois le respect et l'estime que je mérite":                                         "Q4_rec",
    "Vu tous mes efforts, mes perspectives de promotion sont satisfaisantes":                                                  "Q5_rec",
    "Vu tous mes efforts, mon salaire est satisfaisant":                                                                      "Q6_rec",
    # ── Équité (equ) ────────────────────────────────────────────────────────
    "La charge de travail est répartie équitablement dans mon équipe":                                        "Q1_equ",
    # ── Culture (cult) ──────────────────────────────────────────────────────
    "Je m’identifie à la culture de l’entreprise?":                                                           "Q1_cult",
    "Je m'identifie à la culture de l'entreprise?":                                                                     "Q1_cult",
    "Je recommanderai ma compagnie à mes connaissances à la recherche d’un emploi":                          "Q2_cult",
    "Je recommanderai ma compagnie à mes connaissances à la recherche d'un emploi":                                "Q2_cult",
    # ── Satisfaction (sat) ──────────────────────────────────────────────────
    "Je suis satisfait de mon travail dans la compagnie":                                                                     "Q1_sat",
    # ── Adéquation ressources / objectifs (adq_resources) ───────────────────
    "Je sais ce que je dois faire pour atteindre les objectifs qui me sont fixés":                                      "Q1_adq_resources",
    "Je dispose de toutes les ressources nécessaires à l’accomplissement de mes taches quotidiennes":         "Q2_adq_resources",
    "Je dispose de toutes les ressources nécessaires à l'accomplissement de mes taches quotidiennes":              "Q2_adq_resources",
    # ── Adéquation formation / rôle (adq_role) ──────────────────────────────
    "Mes besoins de formations sont bien pris en compte":                                                                     "Q1_adq_role",
    "Les formations dispensées sont cohérentes avec les taches dont j’ai la responsabilité ou qui me sont assignées": "Q2_adq_role",
    "Les formations dispensées sont cohérentes avec les taches dont j'ai la responsabilité ou qui me sont assignées": "Q2_adq_role",
}

INVERT_ITEMS      = ["Q2_auto", "Q2_comp", "Q4_dem", "Q1_rec", "Q2_rec"]
SCORE_MULTIPLIERS = {"comp": 2, "auto": 4, "dem": 1, "sup": 1, "col": 1}
RH_SCORE_GROUPS   = ["rec", "equ", "cult", "adq_resources", "adq_role", "sat"]


# =============================================================================
# CSS — identique au dashboard original Wave-CI
# =============================================================================
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,400;1,9..144,600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #0F2340; }

.stApp {
    background-color: #F0F7FF;
    background-image:
        radial-gradient(ellipse 1000px 500px at 10% -5%, rgba(56,163,232,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 600px 400px at 90% 105%, rgba(249,115,22,0.08) 0%, transparent 50%);
}
.main .block-container { padding-top: 0.75rem; padding-left: 2rem; padding-right: 2rem; max-width: 1500px; }

/* SIDEBAR */
[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #D0E8F8 !important; }

/* HERO */
.hero-band {
    background: linear-gradient(135deg, #FFFFFF 0%, #F5F9FF 100%);
    border: 1px solid #D0E8F8; border-radius: 20px; padding: 1.4rem 2rem 1.3rem;
    margin-bottom: 0.9rem; position: relative; overflow: hidden;
    box-shadow: 0 4px 24px rgba(56,163,232,0.08), 0 1px 0 rgba(255,255,255,0.9) inset;
}
.hero-band::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #38A3E8, #F97316, #38A3E8);
    background-size: 200% 100%; animation: shimmer 4s linear infinite;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
.hero-inner { display: flex; align-items: center; justify-content: space-between; }
.hero-wordmark h1 {
    font-family: 'Fraunces', Georgia, serif; font-size: 2rem; font-weight: 600;
    font-style: italic; color: #0F2340; letter-spacing: -0.02em; margin: 0; line-height: 1;
}
.hero-wordmark h1 span { color: #38A3E8; }
.hero-subtitle { font-size: 0.86rem; color: #4E6A88; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600; margin-top: 0.4rem; }
.hero-chip {
    display: inline-flex; align-items: center; gap: 0.4rem; font-size: 0.65rem;
    font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #F97316;
    background: rgba(249,115,22,0.08); border: 1px solid rgba(249,115,22,0.25);
    border-radius: 999px; padding: 0.3rem 0.8rem;
}
.hero-chip::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: #F97316; animation: blink 2s ease-in-out infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* SECTION TITLE */
.section-title {
    display: flex; align-items: center; gap: 0.7rem; font-family: 'Fraunces', serif;
    font-size: 1.2rem; font-style: italic; font-weight: 400; color: #0F2340;
    margin: 1.8rem 0 1rem; padding-bottom: 0.65rem; border-bottom: 2px solid #E4F0FB;
}
.section-title::before {
    content: ''; display: inline-block; width: 4px; height: 20px;
    background: linear-gradient(180deg, #38A3E8 0%, #F97316 100%); border-radius: 2px; flex-shrink: 0;
}

/* KPI CARD */
.kpi-card {
    background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 16px;
    padding: 1.3rem 1.2rem 1.1rem; text-align: center;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    animation: slideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 8px rgba(56,163,232,0.06); position: relative; overflow: hidden;
}
.kpi-card::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #38A3E8, #F97316); opacity: 0; transition: opacity 0.22s;
}
.kpi-card:hover { transform: translateY(-4px); border-color: #AAD5F5; box-shadow: 0 10px 32px rgba(56,163,232,0.15); }
.kpi-card:hover::after { opacity: 1; }
.kpi-label { font-size: 0.8rem; color: #4E6A88 !important; text-transform: uppercase; letter-spacing: 0.09em; font-weight: 700; margin-bottom: 0.55rem; display: block; }
.kpi-icon { width: 38px; height: 38px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 0.55rem; }
.kpi-value { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.35rem; font-weight: 800; color: #0F2340 !important; line-height: 1; letter-spacing: -0.04em; }
@keyframes slideUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }

/* GAUGE CARD */
.gauge-card {
    background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 18px;
    padding: 1.6rem 1.2rem 1.3rem; text-align: center;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
    animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 8px rgba(56,163,232,0.06); height: 100%; position: relative; overflow: hidden;
}
.gauge-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #38A3E8, #F97316); opacity: 0; transition: opacity 0.22s; }
.gauge-card:hover { transform: translateY(-4px); border-color: #AAD5F5; box-shadow: 0 12px 36px rgba(56,163,232,0.15); }
.gauge-card:hover::before { opacity: 1; }
.gauge-semi-wrap { position: relative; width: 180px; height: 90px; margin: 0 auto 0.7rem; overflow: hidden; }
.gauge-semi-bg   { position: absolute; width: 180px; height: 180px; border-radius: 50%; background: #EDF5FD; top: 0; left: 0; }
.gauge-semi-fill {
    position: absolute; width: 180px; height: 180px; border-radius: 50%; top: 0; left: 0;
    background: conic-gradient(from 270deg, var(--gauge-color,#38A3E8) 0deg, var(--gauge-color,#38A3E8) calc(var(--g,0deg)), transparent calc(var(--g,0deg)));
}
.gauge-semi-inner { position: absolute; width: 112px; height: 112px; background: #FFFFFF; border-radius: 50%; top: 34px; left: 34px; box-shadow: inset 0 2px 8px rgba(56,163,232,0.06); }
.gauge-value    { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.9rem; font-weight: 800; color: #0F2340; line-height: 1; letter-spacing: -0.04em; }
.gauge-pct      { font-size: 1rem; font-weight: 500; color: #6B88A8; }
.gauge-label    { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.96rem; font-weight: 700; color: #0F2340; margin-top: 0.55rem; }
.gauge-sublabel { font-size: 0.84rem; color: #4E6A88; margin-top: 0.25rem; line-height: 1.5; }
.gauge-badge    { display: inline-block; margin-top: 0.7rem; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; padding: 0.22rem 0.85rem; border-radius: 999px; }
.gauge-badge.good  { background: #DCFCE7; color: #15803D; }
.gauge-badge.alert { background: #FEE2E2; color: #B91C1C; }

/* PROGRESS */
.prog-track { background: #EDF5FD; border-radius: 999px; height: 7px; overflow: hidden; margin-top: 5px; }
.prog-fill  { height: 7px; border-radius: 999px; width: 0%; transition: width 1.1s cubic-bezier(0.4,0,0.2,1); }
.panel-relief { background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 16px; padding: 0.9rem 1rem 0.6rem; box-shadow: 0 3px 14px rgba(56,163,232,0.08); }

/* WORKZONE / LS CARDS */
.workzone-card, .ls-card {
    background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 14px;
    padding: 1.1rem 1rem; text-align: center; transition: transform 0.2s, box-shadow 0.2s;
    animation: slideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 6px rgba(56,163,232,0.05);
}
.workzone-card:hover, .ls-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(56,163,232,0.12); }

/* TABS */
[data-baseweb="tab-list"] { background: #FFFFFF !important; border-radius: 12px; padding: 4px; gap: 3px; border: 1px solid #D0E8F8; box-shadow: 0 2px 8px rgba(56,163,232,0.07); }
[data-baseweb="tab"] { font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 600 !important; font-size: 0.88rem !important; color: #6B88A8 !important; border-radius: 9px !important; padding: 0.5rem 1.4rem !important; transition: all 0.2s !important; }
[aria-selected="true"][data-baseweb="tab"] { background: linear-gradient(135deg, #38A3E8, #2B8FD0) !important; color: #FFFFFF !important; font-weight: 700 !important; box-shadow: 0 3px 12px rgba(56,163,232,0.3) !important; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

/* SELECTS & BUTTONS */
[data-baseweb="select"] > div { background-color: #FFFFFF !important; border-color: #C8DFF2 !important; border-radius: 10px !important; color: #0F2340 !important; }
.stButton > button { background: linear-gradient(135deg, #38A3E8, #2B8FD0) !important; border: none !important; color: #FFFFFF !important; border-radius: 10px !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important; font-size: 0.8rem !important; letter-spacing: 0.02em !important; box-shadow: 0 3px 10px rgba(56,163,232,0.25) !important; transition: all 0.18s !important; }
.stButton > button:hover { background: linear-gradient(135deg, #F97316, #EA6A0A) !important; box-shadow: 0 4px 16px rgba(249,115,22,0.3) !important; transform: translateY(-1px) !important; }

/* PLOTLY */
div[data-testid="stPlotlyChart"] { border: 1px solid #D6E8F7; border-radius: 12px; background: #FFFFFF; box-shadow: 0 4px 16px rgba(56,163,232,0.06); padding: 4px; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #EDF5FD; }
::-webkit-scrollbar-thumb { background: #AAD5F5; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #38A3E8; }

hr { border: none; border-top: 1px solid #E4F0FB; margin: 1rem 0; }
@property --g { syntax: '<angle>'; inherits: false; initial-value: 0deg; }
</style>
""", unsafe_allow_html=True)


def inject_animation_js():
    components.html("""
<script>
const rootDoc = window.parent && window.parent.document ? window.parent.document : document;
function easeOut(t) { return 1 - Math.pow(1-t,3); }
function cleanNum(v,min,max){var n=parseFloat(v);if(!isFinite(n))n=0;if(typeof min==='number')n=Math.max(min,n);if(typeof max==='number')n=Math.min(max,n);return n;}
function isVisible(el){if(!el||!el.isConnected)return false;const s=rootDoc.defaultView.getComputedStyle(el);if(s.display==='none'||s.visibility==='hidden'||s.opacity==='0')return false;const r=el.getBoundingClientRect();return r.width>0&&r.height>0;}
function numberKey(el){return[cleanNum(el.dataset.target,0,null),el.dataset.suffix||'',el.dataset.prefix||'',el.dataset.decimals||0].join('|');}
function animateNumber(el){
    const target=cleanNum(el.dataset.target,0,null),suffix=el.dataset.suffix||'',prefix=el.dataset.prefix||'',decimals=el.dataset.decimals?parseInt(el.dataset.decimals,10):0,key=numberKey(el);
    if(el.dataset.animKey===key)return;el.dataset.animKey=key;
    const duration=700,start=performance.now();
    (function step(now){const t=Math.min(1,(now-start)/duration),cur=Math.max(0,target*easeOut(t));
    el.textContent=prefix+(decimals===0?Math.round(cur):cur.toFixed(decimals))+suffix;
    if(t<1)requestAnimationFrame(step);else el.textContent=prefix+(decimals===0?Math.round(target):target.toFixed(decimals))+suffix;})(start);
}
function animateGauge(fill){
    const target=cleanNum(fill.dataset.target,0,100),key=String(target);
    if(fill.dataset.animKey===key)return;fill.dataset.animKey=key;
    const counter=fill.closest('.gauge-card')?.querySelector('.gauge-counter'),duration=800,start=performance.now();
    fill.style.setProperty('--g','0deg');
    requestAnimationFrame(()=>setTimeout(()=>fill.style.setProperty('--g',(target*1.8).toFixed(1)+'deg'),60));
    if(counter){(function step(now){const t=Math.min(1,(now-start)/duration);counter.textContent=Math.round(target*easeOut(t));if(t<1)requestAnimationFrame(step);else counter.textContent=Math.round(target);})(start);}
}
function animateProgress(el){
    const target=cleanNum(el.dataset.target,0,100),key=String(target);
    if(el.dataset.animKey===key)return;el.dataset.animKey=key;
    el.style.width='0%';requestAnimationFrame(()=>setTimeout(()=>el.style.width=target+'%',40));
}
function runFor(el){if(el.matches('.animate-number'))animateNumber(el);else if(el.matches('.gauge-semi-fill[data-target]'))animateGauge(el);else if(el.matches('.prog-fill[data-target]'))animateProgress(el);}
const observed=new WeakSet(),io=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting&&isVisible(e.target))runFor(e.target);});},{threshold:0.2});
function register(){
    rootDoc.querySelectorAll('.animate-number,.gauge-semi-fill[data-target],.prog-fill[data-target]').forEach(el=>{
        if(el.matches('.animate-number')){const k=numberKey(el);if(el.dataset.animKey&&el.dataset.animKey!==k)delete el.dataset.animKey;}
        else{const t=cleanNum(el.dataset.target,0,100);if(el.dataset.animKey&&el.dataset.animKey!==String(t))delete el.dataset.animKey;}
        if(!observed.has(el)){io.observe(el);observed.add(el);}
        if(isVisible(el)){const r=el.getBoundingClientRect(),vh=rootDoc.defaultView?.innerHeight||900;if(r.top<vh*0.92&&r.bottom>0)runFor(el);}
    });
}
setTimeout(register,60);
let _t=null;new MutationObserver(()=>{if(_t)clearTimeout(_t);_t=setTimeout(()=>setTimeout(register,60),90);}).observe(rootDoc.body,{childList:true,subtree:true});
rootDoc.addEventListener('click',evt=>{if(evt.target?.closest('[role="tab"]'))setTimeout(()=>setTimeout(register,60),120);},true);
</script>
""", height=0)


# =============================================================================
# HELPERS TEXTE & COLONNES
# =============================================================================
def _norm(v):
    return re.sub(r"\s+", " ", str(v).strip()).casefold()

def _pp(text):
    text = str(text).strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def _find_pat(columns, patterns):
    for col in columns:
        nc = _pp(col)
        for pat in patterns:
            if re.search(pat, nc): return col
    return None

def _find_age_col(df):
    for col in df.columns:
        nc = _pp(col)
        if "tranche" in nc: continue
        if re.search(r"\bage\b", nc):
            s = pd.to_numeric(df[col], errors="coerce")
            if not s.dropna().empty: return col
    return None

def resolve_csp_col(df):
    for c in ("Categorie Socio", "Catégorie Socio", "CSP"):
        if c in df.columns: return c
    return None

def resolve_quadrant_col(df):
    return "Karasek_quadrant_theoretical" if "Karasek_quadrant_theoretical" in df.columns else None


# =============================================================================
# PREPROCESSING & SCORING
# =============================================================================
def enrich_sociodem(df):
    df = df.copy(); cols = list(df.columns)
    age_col = _find_age_col(df)
    if age_col and "Tranche_age" not in df.columns:
        age_num = pd.to_numeric(df[age_col], errors="coerce")
        df["Tranche_age"] = pd.cut(age_num, bins=[0,30,40,50,np.inf],
                                labels=["20-30 ans","31-40 ans","41-50 ans","51 ans et plus"], right=True)
    anc_col = _find_pat(cols, [r"anciennet"])
    if anc_col and "Tranche_anciennete" not in df.columns:
        anc_num = pd.to_numeric(df[anc_col], errors="coerce")
        df["Tranche_anciennete"] = pd.cut(anc_num, bins=[-1,2,5,10,20,np.inf],
                                        labels=["0-2 ans","3-5 ans","6-10 ans","11-20 ans","21 ans et +"])
    poids_col  = _find_pat(cols, [r"\bpoids\b"])
    taille_col = _find_pat(cols, [r"\btaille\b"])
    if poids_col and taille_col:
        poids  = pd.to_numeric(df[poids_col],  errors="coerce")
        taille = pd.to_numeric(df[taille_col], errors="coerce")
        if not taille[taille>0].empty and float(taille[taille>0].median()) > 3:
            taille = taille / 100.0
        imc = (poids / taille**2).replace([np.inf,-np.inf], np.nan)
        df["IMC"] = imc
        df["Categorie_IMC"] = pd.cut(imc, bins=[0,18.5,25,30,200],
                                    labels=["Insuffisance pondérale","Corpulence normale","Surpoids","Obésité"],
                                    include_lowest=True)
        # Correction DTypePromotionError : on s'assure que le résultat peut contenir du texte et des NaN
        df["IMC_binaire"] = np.where(
            df["Categorie_IMC"].isin(["Insuffisance pondérale", "Corpulence normale"]), 
            "Normal",
            np.where(df["Categorie_IMC"].isna(), None, "Surpoids/Obésité")
        )
        # Optionnel : convertir None en np.nan après coup si nécessaire, 
        # mais pour Streamlit/Pandas, None ou np.nan dans une colonne d'objets fonctionne très bien.
    return df


def clean_pii(df):
    out = df.copy(); ops = []
    PII = [r"\bnom\b",r"\bprenom",r"\be[- ]?mail\b",r"\bmail\b",r"\bcourriel\b",
        r"\btelephone\b",r"\btel\b",r"\bphone\b",r"\bcommentaire",r"\bobservation",r"\bremarque",r"\bnumero\b"]
    dropped = []
    for col in list(out.columns):
        if any(re.search(p, _pp(col)) for p in PII) or re.match(r"^#\s*$|^unnamed", str(col).strip(), re.I):
            out = out.drop(columns=[col]); dropped.append(str(col))
    if dropped: ops.append(f"Colonnes PII supprimées ({len(dropped)}): " + ", ".join(dropped))
    miss = out.isna().mean(); to_drop = miss[miss>0.5].index.tolist()
    if to_drop:
        out = out.drop(columns=to_drop)
        ops.append("Colonnes >50% manquants supprimées: " + ", ".join(str(c) for c in to_drop))
    log = "Nettoyage appliqué:\n- " + "\n- ".join(ops) if ops else "Aucune opération appliquée."
    return out, log


def compute_group_score(df, suffix, multiplier=1):
    cols = [c for c in df.columns if c.endswith(f"_{suffix}")]
    if not cols: return pd.Series(np.nan, index=df.index, name=f"{suffix}_score")
    ssum = df[cols].sum(axis=1, skipna=True); n_ans = df[cols].notna().sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        score = ssum / n_ans.replace(0, np.nan) * len(cols) * multiplier
    return score.where(n_ans>0, np.nan).rename(f"{suffix}_score")


def _fuzzy_rename(df):
    """Rename question columns to Q-codes using normalized text matching (tolerant to apostrophe variants)."""
    import unicodedata, re
    def _norm_q(text):
        t = unicodedata.normalize("NFKD", str(text))
        t = "".join(ch for ch in t if not unicodedata.combining(ch))
        t = t.lower().strip()
        t = re.sub(r"[\u2018\u2019\u201a\u201b\u2032\u0060]", "'", t)  # normalize apostrophes
        t = re.sub(r"[\s]+", " ", t)
        return t

    norm_map = {_norm_q(k): v for k, v in RENAME_MAPPING.items()}
    rename = {}
    for col in df.columns:
        nc = _norm_q(col)
        if nc in norm_map:
            rename[col] = norm_map[nc]
    return df.rename(columns=rename) if rename else df


def build_karasek_scores(df):
    df_out = df.copy()
    # Robust rename using normalized text
    df_out = _fuzzy_rename(df_out)
    # Likert cleaning
    lk = [c for c in df_out.columns if re.match(r"Q\d+_(comp|auto|dem|sup|col|rec|equ|cult|adq_resources|adq_role|sat)$", c)]
    for col in lk:
        s = pd.to_numeric(df_out[col], errors="coerce")
        df_out[col] = s.where(s.between(LIKERT_MIN, LIKERT_MAX))
    # Inversion
    avail = [c for c in INVERT_ITEMS if c in df_out.columns]
    if avail: df_out[avail] = (LIKERT_MIN + LIKERT_MAX) - df_out[avail]
    # Karasek sub-scores: compute from items if available, else keep existing
    for g, mult in SCORE_MULTIPLIERS.items():
        col_name = f"{g}_score"
        computed = compute_group_score(df_out, g, multiplier=mult)
        if computed.notna().any():
            df_out[col_name] = computed
        elif col_name not in df_out.columns:
            df_out[col_name] = np.nan
        # else: pre-existing column kept as-is
    # Composite Karasek scores
    comp_cols = [c for c in ["comp_score","auto_score"] if c in df_out.columns]
    ss_cols   = [c for c in ["sup_score","col_score"]   if c in df_out.columns]
    if "Lat_score" not in df_out.columns or df_out["Lat_score"].isna().all():
        df_out["Lat_score"] = sum(df_out[c] for c in comp_cols) if comp_cols else np.nan
    if "Dem_score" not in df_out.columns or df_out["Dem_score"].isna().all():
        df_out["Dem_score"] = df_out.get("dem_score", pd.Series(np.nan, index=df_out.index))
    if "SS_score" not in df_out.columns or df_out["SS_score"].isna().all():
        df_out["SS_score"] = sum(df_out[c] for c in ss_cols) if ss_cols else np.nan
    # RH scores: compute from items if available, else keep existing
    for g in RH_SCORE_GROUPS:
        col_name = f"{g}_score"
        computed = compute_group_score(df_out, g, multiplier=1)
        if computed.notna().any():
            df_out[col_name] = computed
        elif col_name not in df_out.columns:
            df_out[col_name] = np.nan
        # else: pre-existing column kept as-is
    return df_out

def classify_karasek(df):
    """Seuil théorique uniquement — point médian de l'échelle (non clinique)."""
    df_out = df.copy()
    if any(c not in df_out.columns for c in ["Dem_score","Lat_score","SS_score"]):
        return df_out
    DT, LT, ST = THRESHOLDS["Dem_score"], THRESHOLDS["Lat_score"], THRESHOLDS["SS_score"]
    df_out["Karasek_quadrant_theoretical"] = np.select(
        [(df_out["Lat_score"]>=LT)&(df_out["Dem_score"]>=DT),
        (df_out["Lat_score"]>=LT)&(df_out["Dem_score"]< DT),
        (df_out["Lat_score"]< LT)&(df_out["Dem_score"]>=DT)],
        ["Actif","Detendu","Tendu"], default="Passif")
    df_out["Job_strain_theoretical"]  = np.where((df_out["Dem_score"]>=DT)&(df_out["Lat_score"]<LT), "Présent","Absent")
    df_out["Iso_strain_theoretical"]  = np.where((df_out["Dem_score"]>=DT)&(df_out["SS_score"]<ST),  "Présent","Absent")
    for col, thresh in THRESHOLDS.items():
        if col in df_out.columns:
            df_out[f"{col}_theo_cat"] = np.where(df_out[col].isna(), "Non renseigné",
                                                np.where(df_out[col]<=thresh, "Faible","Élevé"))
    return df_out


# =============================================================================
# DATA LOADER
# =============================================================================
@st.cache_data(show_spinner=False)
def load_raw_from_bytes(file_bytes, file_name):
    buf = io.BytesIO(file_bytes)
    if file_name.lower().endswith(".csv"):
        try:    df = pd.read_csv(buf, sep=None, engine="python", encoding="utf-8-sig")
        except: buf.seek(0); df = pd.read_csv(buf, sep=None, engine="python", encoding="latin-1")
    else:
        df = pd.read_excel(buf)
    df.columns = [str(c).strip() for c in df.columns]
    return enrich_sociodem(df)


@st.cache_data(show_spinner=False)
def load_scored_from_bytes(file_bytes, file_name, _version=3):
    df = load_raw_from_bytes(file_bytes, file_name)
    df = build_karasek_scores(df)
    return classify_karasek(df)


# =============================================================================
# FILTRES SIDEBAR
# =============================================================================
def _clean_opts(series):
    out = {}
    for raw in series.dropna().astype(str):
        c = re.sub(r"\s+", " ", raw.strip())
        if c: out.setdefault(_norm(c), c)
    return sorted(out.values(), key=_norm)


def render_sidebar(df_raw):
    """Renvoie (df_raw filtré, df_scored filtré)."""
    with st.sidebar:
        st.markdown("""
        <div style="font-family:'Fraunces',serif;font-size:1.15rem;font-style:italic;
                    color:#0F2340;font-weight:400;margin-bottom:1.2rem;padding-bottom:0.6rem;
                    border-bottom:2px solid #E4F0FB;">Filtres</div>""", unsafe_allow_html=True)

        ALL = "Tous"
        dirs = [ALL] + (_clean_opts(df_raw["Direction"]) if "Direction" in df_raw.columns else [])
        if st.session_state.get("sb_dir") not in dirs: st.session_state["sb_dir"] = ALL
        sel_dir = st.selectbox("Direction", dirs, key="sb_dir")

        dep = df_raw
        if "Direction" in df_raw.columns and sel_dir != ALL:
            mask = df_raw["Direction"].astype(str).map(_norm) == _norm(sel_dir)
            if not mask.any(): mask = df_raw["Direction"].astype(str).map(_norm).str.contains(_norm(sel_dir), regex=False)
            dep = df_raw[mask]

        csp_c = resolve_csp_col(df_raw)
        csps  = [ALL] + (_clean_opts(dep[csp_c]) if csp_c else [])
        if st.session_state.get("sb_csp") not in csps: st.session_state["sb_csp"] = ALL
        sel_csp = st.selectbox("Catégorie socio", csps, key="sb_csp")

        genres = [ALL] + (_clean_opts(dep["Genre"]) if "Genre" in dep.columns else [])
        if st.session_state.get("sb_genre") not in genres: st.session_state["sb_genre"] = ALL
        sel_genre = st.selectbox("Genre", genres, key="sb_genre")

        age_s = pd.to_numeric(df_raw["Age"], errors="coerce").dropna() if "Age" in df_raw.columns else pd.Series(dtype=float)
        sel_age = None
        if not age_s.empty:
            ab = (int(np.floor(age_s.min())), int(np.ceil(age_s.max())))
            cur = st.session_state.get("sb_age", ab)
            if not isinstance(cur, tuple): cur = ab
            safe_val = (max(ab[0], int(cur[0])), min(ab[1], int(cur[1])))
            sel_age = st.slider("Tranche d'âge", min_value=ab[0], max_value=ab[1], value=safe_val, key="sb_age")

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("↺ Réinitialiser", key="sb_reset", use_container_width=True):
            for k in ["sb_dir","sb_csp","sb_genre","sb_age"]: st.session_state.pop(k, None)
            st.rerun()

    # Application
    out = df_raw.copy()
    if "Direction" in out.columns and sel_dir != ALL:
        mask = out["Direction"].astype(str).map(_norm) == _norm(sel_dir)
        if not mask.any(): mask = out["Direction"].astype(str).map(_norm).str.contains(_norm(sel_dir), regex=False)
        out = out[mask]
    if csp_c and sel_csp != ALL:
        out = out[out[csp_c].astype(str).map(_norm) == _norm(sel_csp)]
    if "Genre" in out.columns and sel_genre != ALL:
        out = out[out["Genre"].astype(str).map(_norm) == _norm(sel_genre)]
    if sel_age and "Age" in out.columns:
        ages = pd.to_numeric(out["Age"], errors="coerce")
        out = out[(ages >= sel_age[0]) & (ages <= sel_age[1])]
    return out


# =============================================================================
# HTML COMPONENTS
# =============================================================================
def section_title(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)

def svg_icon(path_d, bg, fg):
    return (f'<span class="kpi-icon" style="background:{bg};color:{fg};">'
            f'<svg viewBox="0 0 24 24" width="17" height="17" fill="none">'
            f'<path d="{path_d}" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>'
            f'</svg></span>')

def html_kpi(value, label, suffix="", prefix="", decimals=0, subtitle="", icon=""):
    num = float(pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0] or 0)
    rend = f"{num:.{decimals}f}" if decimals > 0 else str(int(round(num)))
    sub  = f'<div style="margin-top:0.4rem;font-size:0.78rem;font-weight:600;color:#4E6A88;">{subtitle}</div>' if subtitle else ""
    ico  = icon if str(icon).strip().startswith("<") else ""
    return f"""<div class="kpi-card">{ico}<span class="kpi-label">{label}</span>
    <div class="kpi-value animate-number" data-target="{num}" data-suffix="{suffix}" data-prefix="{prefix}" data-decimals="{decimals}">{prefix}{rend}{suffix}</div>{sub}</div>"""

def html_ls_n(pct, n, label):
    num = float(pct) if not pd.isna(pct) else 0.0
    col = "#22C55E" if num < 35 else "#EF4444" if num > 60 else "#F97316"
    return f"""<div class="ls-card" style="border-top:3px solid {col};">
    <span class="kpi-label">{label}</span>
    <div class="kpi-value animate-number" style="color:{col};font-size:1.8rem;" data-target="{int(round(num))}" data-suffix="%" data-prefix="" data-decimals="0">{int(round(num))}%</div>
    <div style="margin-top:0.3rem;font-size:0.78rem;font-weight:600;color:#4E6A88;">{int(n)}</div></div>"""

def html_gauge(value, label, sublabel, inverted=False):
    """inverted=True : score élevé = risque (ex: Demande psychologique élevée = mauvais)."""
    t = max(0.0, min(100.0, float(value) if not pd.isna(value) else 0.0))
    d = int(round(t))

    if inverted:
        if t > 60:
            col, bcls, btxt = "#EF4444", "alert", "Élevée"
        elif t > 40:
            col, bcls, btxt = "#F97316", "moderate", "Modérée"
        else:
            col, bcls, btxt = "#22C55E", "good", "Faible"
    else:
        if t > 60:
            col, bcls, btxt = "#22C55E", "good", "Bon"
        elif t > 40:
            col, bcls, btxt = "#F97316", "moderate", "Modérée"
        else:
            col, bcls, btxt = "#EF4444", "alert", "Mauvais"

    return f"""<div class="gauge-card">
    <div class="gauge-semi-wrap">
        <div class="gauge-semi-bg"></div>
        <div class="gauge-semi-fill" style="--gauge-color:{col};--g:{t*1.8:.1f}deg;" data-target="{d}"></div>
        <div class="gauge-semi-inner"></div>
    </div>
    <div class="gauge-value"><span class="gauge-counter" style="color:{col};">{d}</span><span class="gauge-pct">%</span></div>
    <div class="gauge-label">{label}</div><div class="gauge-sublabel">{sublabel}</div>
    <span class="gauge-badge {bcls}">{btxt}</span></div>"""
    
def html_prog(label, pct, color, n=0):
    v = max(0.0, min(100.0, float(pct) if not pd.isna(pct) else 0.0))
    return f"""<div style="margin-bottom:1rem;">
    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
        <span style="font-size:0.78rem;color:#3B5878;font-family:'Plus Jakarta Sans',sans-serif;font-weight:500;">{label}</span>
        <span style="font-size:0.82rem;font-weight:700;color:{color};font-family:'Plus Jakarta Sans',sans-serif;">{v:.0f}% ({int(n)})</span>
    </div>
    <div class="prog-track"><div class="prog-fill" style="background:{color};width:{v:.1f}%;" data-target="{v:.1f}"></div></div></div>"""

def html_zone(label, pct, n, color):
    v = max(0.0, min(100.0, float(pct) if not pd.isna(pct) else 0.0))
    return f"""<div class="workzone-card" style="border-top:3px solid {color};">
    <span style="font-size:0.8rem;color:{color};text-transform:uppercase;letter-spacing:0.09em;font-weight:700;margin-bottom:0.55rem;display:block;">{label}</span>
    <div class="animate-number" style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.8rem;font-weight:800;color:{color};line-height:1;letter-spacing:-0.04em;" data-target="{int(round(v))}" data-suffix="%" data-prefix="" data-decimals="0">{int(round(v))}%</div>
    <div style="margin-top:0.35rem;font-size:0.78rem;font-weight:600;color:{color};">{int(n)}</div></div>"""
# =============================================================================
# PLOTLY HELPERS
# =============================================================================
def _plotly_base(fig, height=None):
    upd = dict(
        plot_bgcolor="#FAFCFF", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#0F2340", size=12),
        xaxis=dict(showgrid=True, gridcolor="#EDF5FD", gridwidth=1, showline=True,
                linecolor="#D6E8F7", zeroline=False, tickfont=dict(color="#6B88A8",size=11)),
        yaxis=dict(showgrid=True, gridcolor="#EDF5FD", gridwidth=1, showline=False,
                zeroline=False, tickfont=dict(color="#6B88A8",size=11)),
        legend=dict(bgcolor="rgba(255,255,255,0.95)", bordercolor="#D6E8F7", borderwidth=1,
                    font=dict(color="#0F2340",size=11)),
        margin=dict(l=40,r=20,t=50,b=40),
    )
    if height: upd["height"] = height
    fig.update_layout(**upd)
    return fig


def make_barplot(df, col):
    cnt = df[col].value_counts().reset_index(); cnt.columns=[col,"n"]
    cnt["pct"] = (cnt["n"]/cnt["n"].sum()*100).round(1)
    pal = ["#38A3E8","#F97316","#22C55E","#EF4444","#A78BFA","#06B6D4","#FB923C","#84CC16"]
    fig = go.Figure()
    for i, row in cnt.iterrows():
        fig.add_trace(go.Bar(y=[row[col]], x=[row["pct"]], orientation="h",
            marker_color=pal[i%len(pal)], marker=dict(opacity=0.9, line=dict(width=0)),
            text=f"{row['pct']}%  ({row['n']})", textposition="outside",
            textfont=dict(color="#6B88A8",size=11,family="Plus Jakarta Sans"), showlegend=False))
    _plotly_base(fig, height=max(250, len(cnt)*55+80))
    fig.update_xaxes(range=[0,130], title_text="Pourcentage (%)")
    return fig


def make_stacked(df, x_col, hue_col):
    if x_col not in df.columns or hue_col not in df.columns: return None
    tmp = df[[x_col,hue_col]].dropna()
    if tmp.empty: return None
    ct  = pd.crosstab(tmp[x_col], tmp[hue_col])
    pct = ct.div(ct.sum(axis=1), axis=0)*100
    bmap = {"Eleve":"#22C55E","Élevé":"#22C55E","Faible":"#EF4444","Présent":"#EF4444","Absent":"#22C55E"}
    gen  = ["#38A3E8","#F97316","#22C55E","#EF4444","#A78BFA","#06B6D4"]
    def gc(cat,idx):
        if cat in KARASEK_COLORS: return KARASEK_COLORS[cat]
        if cat in bmap:           return bmap[cat]
        return gen[idx%len(gen)]
    fig = go.Figure()
    for i, cat in enumerate(pct.columns):
        vals, ns = pct[cat].values, ct[cat].values
        txts = [f"{v:.1f}%  ({n})" if v>=6 else "" for v,n in zip(vals,ns)]
        fig.add_trace(go.Bar(name=str(cat), y=list(pct.index), x=vals, orientation="h",
            marker_color=gc(str(cat),i), marker=dict(opacity=0.9,line=dict(width=0)),
            text=txts, textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white",size=11,family="Plus Jakarta Sans")))
    _plotly_base(fig, height=max(280, len(pct.index)*55+100))
    fig.update_layout(barmode="stack", xaxis=dict(range=[0,100],title_text="Pourcentage (%)"))
    return fig


def make_radar(scores, labels):
    vals = [scores.get(l,0) for l in labels]
    vc = vals+[vals[0]]; lc = labels+[labels[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[50]*(len(labels)+1), theta=lc, fill="toself",
        fillcolor="rgba(249,115,22,0.05)", line=dict(color="rgba(249,115,22,0.4)",dash="dot",width=1.5),
        name="Référence 50%", hoverinfo="skip"))
    fig.add_trace(go.Scatterpolar(r=vc, theta=lc, fill="toself",
        fillcolor="rgba(56,163,232,0.12)", line=dict(color="#38A3E8",width=2.5),
        marker=dict(color="#38A3E8",size=7,line=dict(color="#FFFFFF",width=2)),
        name="Niveau élevé", hovertemplate="<b>%{theta}</b><br>%{r:.1f}%<extra></extra>"))
    fig.update_layout(
        polar=dict(bgcolor="#FAFCFF",
            angularaxis=dict(tickfont=dict(color="#0F2340",size=10,family="Plus Jakarta Sans"),linecolor="#D6E8F7",gridcolor="#EDF5FD"),
            radialaxis=dict(visible=True,range=[0,100],tickfont=dict(color="#6B88A8",size=9),gridcolor="#EDF5FD",linecolor="#D6E8F7",ticksuffix="%")),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Plus Jakarta Sans",color="#0F2340"),
        legend=dict(bgcolor="rgba(255,255,255,0.95)",bordercolor="#D6E8F7",borderwidth=1,font=dict(color="#0F2340",size=11),x=0.75,y=1.1),
        height=500, margin=dict(l=60,r=60,t=40,b=40))
    return fig


def get_pct_high(df, score_col):
    cat = f"{score_col}_theo_cat"
    if cat in df.columns:
        v = df[cat].dropna()
        if len(v) > 0:
            result = float(v.isin(["Eleve", "Élevé", "Elevé", "High"]).sum() / len(v) * 100)
            return 100 - result if score_col == "Dem_score" else result
    if score_col in THRESHOLDS and score_col in df.columns:
        v = pd.to_numeric(df[score_col], errors="coerce").dropna()
        if len(v) > 0:
            result = float((v > THRESHOLDS[score_col]).sum() / len(v) * 100)
            return 100 - result if score_col == "Dem_score" else result
    return 0.0


def get_high_stats(df, score_col):
    cat = f"{score_col}_theo_cat"
    if cat in df.columns:
        v = df[cat].dropna(); n_h = int(v.isin(["Eleve","Élevé","Elevé","High"]).sum())
        return float(n_h/len(v)*100) if len(v)>0 else 0.0, n_h, int(len(v))
    if score_col in df.columns:
        v = pd.to_numeric(df[score_col],errors="coerce").dropna()
        t = THRESHOLDS.get(score_col); n_h = int((v>t).sum()) if t is not None else 0
        return float(n_h/len(v)*100) if len(v)>0 else 0.0, n_h, int(len(v))
    return 0.0, 0, 0


def _fig_to_png(fig):
    try:
        if hasattr(fig,"to_image"): return fig.to_image(format="png")
        buf = io.BytesIO(); fig.savefig(buf,format="png",dpi=300,bbox_inches="tight"); buf.seek(0); return buf.getvalue()
    except: return None


# =============================================================================
# MAIN
# =============================================================================
inject_css()
inject_animation_js()

st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
    '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,400;1,9..144,600&display=swap" rel="stylesheet">',
    unsafe_allow_html=True
)

# TOPBAR
_col_top, _col_back = st.columns([9, 1])
with _col_top:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;background:white;border-radius:12px;'
        'padding:14px 24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06),'
        '0 4px 12px rgba(30,110,79,0.08);border:1px solid #e8edf5;">'
        '<div style="width:38px;height:38px;background:linear-gradient(135deg,#1e6e4f,#3aaa7a);'
        'border-radius:10px;display:flex;align-items:center;justify-content:center;">'
        '<i class="fas fa-brain" style="color:white;font-size:15px;"></i></div>'
        '<div>'
        '<div style="font-size:16px;font-weight:700;color:#1e293b;font-family:\'Plus Jakarta Sans\',sans-serif;">Modèle de Karasek — Demande–Contrôle–Soutien</div>'
        '<div style="font-size:11px;color:#64748b;margin-top:1px;font-family:\'Plus Jakarta Sans\',sans-serif;">Analyse des risques psychosociaux au travail (Job Strain & Iso-Strain)</div>'
        '</div></div>',
        unsafe_allow_html=True
    )
with _col_back:
    if st.button("← Accueil", key="back_home_karasek", use_container_width=True):
        st.switch_page("app.py")

# UPLOAD
uploaded_file = st.file_uploader(
    "Charger un fichier Excel ou CSV",
    type=["xlsx", "xls", "csv"],
    help="Le fichier doit contenir les items Likert du questionnaire de Karasek (1–4) ou leurs libellés complets.",
    key="karasek_uploader",
)
if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    if file_bytes:
        st.session_state["_kara_file_bytes"] = file_bytes
        st.session_state["_kara_file_name"]  = uploaded_file.name

if "_kara_file_bytes" not in st.session_state:
    st.info("Veuillez charger un fichier de données (Excel ou CSV) pour démarrer l'analyse.")
    st.stop()

_fb = st.session_state["_kara_file_bytes"]
_fn = st.session_state["_kara_file_name"]

with st.spinner("Chargement et traitement des données…"):
    df_raw_orig = load_raw_from_bytes(_fb, _fn)
    df_raw_orig, cleaning_log = clean_pii(df_raw_orig)

with st.expander("Journal de nettoyage automatique", expanded=False):
    st.text(cleaning_log)
    df_sc_tmp = load_scored_from_bytes(_fb, _fn)
    n_lk = sum(1 for c in df_sc_tmp.columns if re.match(r"Q\d+_(comp|auto|dem|sup|col|rec|equ|cult|adq_resources|adq_role|sat)$", c))
    st.write(f"Items Likert Karasek détectés : {n_lk}")
    st.caption("Les seuils utilisés sont des seuils théoriques basés sur le point médian de l'échelle Likert (1–4). "
            "Ce sont des indicateurs conventionnels — ils ne constituent pas des seuils cliniques diagnostiques.")
    # Debug: show which RH scores were computed
    _sc_tmp2 = load_scored_from_bytes(_fb, _fn)
    _rh_debug = []
    for _g in ["adq_resources_score", "adq_role_score", "rec_score", "equ_score", "cult_score", "sat_score"]:
        if _g in _sc_tmp2.columns:
            _n = _sc_tmp2[_g].notna().sum()
            _m = _sc_tmp2[_g].mean() if _n > 0 else float("nan")
            _rh_debug.append(f"{_g}: n={_n}, moy={_m:.2f}" if _n > 0 else f"{_g}: aucune valeur calculée")
        else:
            _rh_debug.append(f"{_g}: ABSENT du dataframe")
    with st.expander("Diagnostic scores RH (cliquer pour vérifier)", expanded=False):
        for line in _rh_debug:
            st.write(line)

# FILTRES SIDEBAR
df_f = render_sidebar(df_raw_orig)

# Appliquer les mêmes filtres sur df_scored via l'index
df_sc_all  = load_scored_from_bytes(_fb, _fn)
# Reconstruire les filtres sur df_sc_all à partir de l'index filtré
common_idx = df_f.index.intersection(df_sc_all.index)
df_sc      = df_sc_all.loc[common_idx]
df         = df_f.copy()

with st.sidebar:
    n_f = len(df)
    st.markdown(f"""<div style="text-align:center;padding:0.7rem;background:#EDF5FD;border-radius:10px;margin-top:0.8rem;">
    <span style="font-size:0.7rem;color:#6B88A8;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">Effectif filtré</span><br>
    <span style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.6rem;font-weight:800;color:#38A3E8;"
        class="animate-number" data-target="{n_f}" data-suffix="" data-prefix="" data-decimals="0">{n_f}</span>
    </div>""", unsafe_allow_html=True)

if len(df) == 0:
    st.warning("Aucun répondant ne correspond aux filtres sélectionnés.")
    st.stop()

# ONGLETS
tab_gen, tab_quad, tab_cross = st.tabs(["Vue d'ensemble", "Stress & Quadrants", "Croisement"])


# =============================================================================
# TAB 1 — VUE D'ENSEMBLE
# =============================================================================
with tab_gen:
    # ─── Données générales ───────────────────────────────────────────────────
    section_title("Données Générales de la Population")
    total_n = len(df)
    gs = df["Genre"].astype(str).str.strip().str.lower() if "Genre" in df.columns else pd.Series(dtype=str)
    n_men   = int(gs.isin({"homme","male","m"}).sum())   if not gs.empty else 0
    n_women = int(gs.isin({"femme","female","f"}).sum()) if not gs.empty else 0
    avg_age = pd.to_numeric(df["Age"], errors="coerce").mean() if "Age" in df.columns else 0.0

    sit_col = _find_pat(list(df.columns), [r"situation.*matrimon"])
    if sit_col:
        sv = df[sit_col].value_counts(dropna=True)
        sit_top, sit_n = (str(sv.index[0]), int(sv.iloc[0])) if not sv.empty else ("N/A", 0)
        sit_pct = sit_n / total_n * 100 if total_n > 0 else 0.0
    else:
        sit_top, sit_n, sit_pct = "N/A", 0, 0.0

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.markdown(html_kpi(total_n,"Effectif total",
        icon=svg_icon("M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M9.5 7a3 3 0 1 0 0-6 3 3 0 0 0 0 6M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a3 3 0 0 1 0 5.75","rgba(56,163,232,0.1)","#38A3E8")), unsafe_allow_html=True)
    with c2: st.markdown(html_kpi(n_men/total_n*100 if total_n>0 else 0,"Hommes",suffix="%",decimals=0,subtitle=f"{n_men}",
        icon=svg_icon("M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4M5 21a7 7 0 0 1 14 0","rgba(56,163,232,0.1)","#38A3E8")), unsafe_allow_html=True)
    with c3: st.markdown(html_kpi(n_women/total_n*100 if total_n>0 else 0,"Femmes",suffix="%",decimals=0,subtitle=f"{n_women}",
        icon=svg_icon("M12 11a4 4 0 1 0-4-4 4 4 0 0 0 4 4M8 15h8l1.5 6h-11zM12 15v6","rgba(249,115,22,0.1)","#F97316")), unsafe_allow_html=True)
    with c4: st.markdown(html_kpi(avg_age,"Âge moyen",suffix=" ans",decimals=0,
        icon=svg_icon("M8 2v4M16 2v4M3 10h18M5 6h14a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z","rgba(249,115,22,0.1)","#F97316")), unsafe_allow_html=True)
    with c5: st.markdown(html_kpi(sit_pct,"Situation matrimoniale",suffix="%",decimals=0,subtitle=f"{sit_top} — {sit_n}",
        icon=svg_icon("M12 21.7C5.4 21.7 2 16.4 2 12S5.4 2.3 12 2.3 22 7.6 22 12s-3.4 9.7-10 9.7zM8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01","rgba(34,197,94,0.1)","#22C55E")), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Modes de vie ────────────────────────────────────────────────────────
    section_title("Indicateurs de modes de vie")
    alcool_col = next((c for c in df.columns if re.search(r"consommation.*alcool|alcool", _pp(c))), None)
    sport_col  = _find_pat(list(df.columns), [r"pratique.*sport",r"\bsport\b"])
    tabac_col  = _find_pat(list(df.columns), [r"tabag"])

    def _yn(col, val="Oui"):
        if col is None or col not in df.columns: return 0.0, 0
        s = df[col].astype(str).str.strip().str.lower()
        n = int((s==val.lower()).sum())
        return n/len(s)*100 if len(s)>0 else 0.0, n

    pct_tab, n_tab   = _yn(tabac_col)
    pct_alc, n_alc   = _yn(alcool_col)
    n_sed            = int((df[sport_col].astype(str).str.strip().str.lower()=="non").sum()) if sport_col and sport_col in df.columns else 0
    pct_sed          = n_sed/total_n*100 if total_n>0 else 0.0

    if "IMC_binaire" in df.columns:
        n_surp  = int((df["IMC_binaire"].astype(str).str.strip()=="Surpoids/Obésité").sum())
        pct_surp = n_surp/total_n*100
    else:
        pct_surp, n_surp = 0.0, 0

    cl1,cl2,cl3,cl4 = st.columns(4)
    with cl1: st.markdown(html_ls_n(pct_tab,  n_tab,  "Tabagisme"),            unsafe_allow_html=True)
    with cl2: st.markdown(html_ls_n(pct_alc,  n_alc,  "Consommation d'alcool"),unsafe_allow_html=True)
    with cl3: st.markdown(html_ls_n(pct_sed,  n_sed,  "Sédentarité"),          unsafe_allow_html=True)
    with cl4: st.markdown(html_ls_n(pct_surp, n_surp, "Surpoids & Obésité"),   unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Satisfaction organisationnelle ─────────────────────────────────────
    section_title("Satisfaction organisationnelle")
    DIMS = [
        ("rec_score","Reconnaissance"), ("equ_score","Équité de charge"),
        ("cult_score","Culture d'entreprise"), ("sat_score","Satisfaction"),
        ("adq_resources_score","Ressources & Objectifs"), ("sup_score","Soutien management"),
        ("adq_role_score","Formation"), ("comp_score","Compétences"),
    ]
    dim_stats = {lbl: get_high_stats(df_sc, sc) for sc, lbl in DIMS}
    dim_pcts  = {lbl: v[0] for lbl, v in dim_stats.items()}

    with st.container(border=True):
        st.markdown('<p style="color:#4E6A88;font-size:0.98rem;margin:0.12rem 0 0.65rem;line-height:1.5;">% de collaborateurs avec un niveau élevé de satisfaction par dimension</p>', unsafe_allow_html=True)
        rc1, rc2 = st.columns([6,4])
        with rc1:
            st.plotly_chart(make_radar(dim_pcts, [d[1] for d in DIMS]), use_container_width=True, key="radar_gen")
        with rc2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            bars_html = "".join(html_prog(lbl, pct, "#22C55E" if pct>50 else "#EF4444", n) for lbl,(pct,n,_) in dim_stats.items())
            st.markdown(bars_html, unsafe_allow_html=True)


# =============================================================================
# TAB 2 — STRESS & QUADRANTS
# =============================================================================
with tab_quad:
    # ─── Jauges ──────────────────────────────────────────────────────────────
    section_title("Indicateurs clés de stress au travail")
    g1,g2,g3 = st.columns(3)
    with g1: st.markdown(html_gauge(get_pct_high(df_sc,"Lat_score"),  "Autonomie décisionnelle", "Flexibilité et contrôle perçus",        inverted=False), unsafe_allow_html=True)
    with g2: st.markdown(html_gauge(get_pct_high(df_sc,"Dem_score"),  "Charge mentale perçue",   "Intensité de la demande psychologique",  inverted=False),  unsafe_allow_html=True)
    with g3: st.markdown(html_gauge(get_pct_high(df_sc,"SS_score"),   "Cohésion d'équipe",       "Soutien social collègues & management",  inverted=False), unsafe_allow_html=True)

    # ─── Quadrants KPI ───────────────────────────────────────────────────────
    section_title("Répartition par quadrant Karasek")
    quad_col = resolve_quadrant_col(df_sc)
    if quad_col:
        qc1,qc2,qc3,qc4 = st.columns(4)
        tv = len(df_sc.dropna(subset=[quad_col]))
        aliases = {"Tendu":["Tendu","Tense"],"Actif":["Actif","Active"],"Passif":["Passif","Passive"],"Détendu":["Detendu","Détendu","Relaxed"]}
        zone_col = {"Tendu":"#EF4444","Actif":"#22C55E","Passif":"#94A3B8","Détendu":"#38A3E8"}
        for raw, cui in [("Tendu",qc1),("Actif",qc2),("Passif",qc3),("Détendu",qc4)]:
            n = int(df_sc[quad_col].isin(aliases[raw]).sum())
            with cui: st.markdown(html_zone(raw, n/tv*100 if tv>0 else 0, n, zone_col[raw]), unsafe_allow_html=True)
    else:
        st.info("Scores Karasek manquants — vérifiez que le fichier contient les items Dem/Lat/SS.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Grille MAPP ─────────────────────────────────────────────────────────
    section_title("Grille MAPP du Stress")
    st.markdown('<p style="color:#4E6A88;font-size:0.98rem;margin-top:-0.3rem;line-height:1.55;">Chaque point représente un agent. Les axes délimitent les zones du quadrant Karasek.</p>', unsafe_allow_html=True)

    if quad_col and "Dem_score" in df_sc.columns and "Lat_score" in df_sc.columns:
        df_p = df_sc[["Dem_score","Lat_score",quad_col]].dropna().copy()
        if df_p.empty:
            st.info("Données insuffisantes pour la grille MAPP.")
        else:
            qmap = {"Actif":"Actif","Detendu":"Détendu","Détendu":"Détendu","Tendu":"Tendu","Passif":"Passif"}
            df_p["quad_display"] = df_p[quad_col].map(qmap).fillna(df_p[quad_col])
            cmap = {v: KARASEK_COLORS.get(k,"#94A3B8") for k,v in qmap.items()}
            fig_sc = px.scatter(df_p, x="Lat_score", y="Dem_score", color="quad_display",
                color_discrete_map=cmap, opacity=0.75,
                labels={"Lat_score":"Latitude décisionnelle (autonomie & compétences)",
                        "Dem_score":"Demande psychologique (charge mentale)","quad_display":"Zone"},
                custom_data=["quad_display","Lat_score","Dem_score"])
            fig_sc.update_traces(marker=dict(size=8,line=dict(width=1,color="white")),
                hovertemplate="<b>Zone</b>: %{customdata[0]}<br>Autonomie: %{customdata[1]:.1f}<br>Charge: %{customdata[2]:.1f}<extra></extra>")
            fig_sc.add_vline(x=THRESHOLDS["Lat_score"], line_dash="dot", line_color="rgba(249,115,22,0.45)", line_width=1.8)
            fig_sc.add_hline(y=THRESHOLDS["Dem_score"], line_dash="dot", line_color="rgba(249,115,22,0.45)", line_width=1.8)
            xmn,xmx = df_p["Lat_score"].min(),df_p["Lat_score"].max()
            ymn,ymx = df_p["Dem_score"].min(),df_p["Dem_score"].max()
            xr,yr   = xmx-xmn, ymx-ymn
            px_,py_ = max(xr*0.04,0.5), max(yr*0.04,0.5)
            anns = {"Actif":(xmx-px_,ymx-py_,"right","top"),"Passif":(xmn+px_,ymn+py_,"left","bottom"),
                    "Détendu":(xmx-px_,ymn+py_,"right","bottom"),"Tendu":(xmn+px_,ymx-py_,"left","top")}
            for quad,(qx,qy,xa,ya) in anns.items():
                qk = "Detendu" if quad=="Détendu" else quad
                fig_sc.add_annotation(x=qx,y=qy,text=quad.upper(),showarrow=False,
                    font=dict(size=12,color=KARASEK_COLORS.get(qk,"#94A3B8"),family="Plus Jakarta Sans"),
                    opacity=0.3,xanchor=xa,yanchor=ya)
            _plotly_base(fig_sc, height=500)
            fig_sc.update_layout(xaxis_title="Latitude décisionnelle (autonomie & compétences)",
                yaxis_title="Demande psychologique (charge mentale)", legend_title_text="Zone")
            st.plotly_chart(fig_sc, use_container_width=True, key="mapp_chart")
    else:
        st.warning("Colonnes manquantes pour la grille MAPP (Dem_score, Lat_score).")

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Heatmap par direction ────────────────────────────────────────────────
    dir_col_hm = next((c for c in df_sc.columns if _pp(c)=="direction"), None)
    if dir_col_hm and quad_col:
        section_title("Heatmap Karasek par direction")
        ct_hm = pd.crosstab(df_sc[dir_col_hm], df_sc[quad_col], normalize="index")*100
        quads_hm = ["Tendu","Actif","Passif","Detendu"]
        for q in quads_hm:
            if q not in ct_hm.columns: ct_hm[q] = 0
        ct_hm = ct_hm.sort_values("Tendu", ascending=True)
        cmaps = {"Tendu":["#ffffff","#e74c3c"],"Actif":["#ffffff","#3498db"],"Passif":["#ffffff","#f39c12"],"Detendu":["#ffffff","#2ecc71"]}
        fig_hm, axes = plt.subplots(1,4,figsize=(20,1+len(ct_hm)*0.4),sharey=True)
        fig_hm.patch.set_facecolor("#f8f9fa")
        for ax, q in zip(axes, quads_hm):
            cm = LinearSegmentedColormap.from_list(f"c_{q}", cmaps[q])
            sns.heatmap(ct_hm[[q]], ax=ax, cmap=cm, vmin=0, vmax=60, annot=True, fmt=".0f",
                        annot_kws={"size":8}, linewidths=0.5, linecolor="#eee", cbar=False)
            ax.set_title(q.upper(), fontsize=11, fontweight="bold", color=cmaps[q][1])
            ax.set_xlabel("%", fontsize=9); ax.tick_params(axis="y", labelsize=9)
            for spine in ax.spines.values(): spine.set_visible(False)
        plt.suptitle("Répartition Karasek par Direction — seuil théorique", fontsize=13, fontweight="bold", y=1.02)
        png_hm = _fig_to_png(fig_hm)
        if png_hm:
            st.download_button("Télécharger PNG", data=png_hm, file_name="heatmap_direction.png", mime="image/png", key="dl_hm")
        st.pyplot(fig_hm, use_container_width=True)
        plt.close(fig_hm)


# =============================================================================
# TAB 3 — CROISEMENT
# =============================================================================
with tab_cross:
    section_title("Exploration des données démographiques")

    csp_actual = resolve_csp_col(df) or "Categorie Socio"
    alc_lbl    = "Consommation d'alcool"
    alc_col2   = next((c for c in df.columns if re.search(r"consommation.*alcool|alcool", _pp(c))), None)
    sport_col2 = _find_pat(list(df.columns), [r"pratique.*sport",r"\bsport\b"])
    tabac_col2 = _find_pat(list(df.columns), [r"tabag"])

    VAR_MAP = {
        "Genre":                         "Genre",
        "Tranche d'âge":                 "Tranche_age",
        "Ancienneté":                    "Tranche_anciennete",
        "Catégorie socioprofessionnelle": csp_actual,
        "Catégorie IMC":                 "Categorie_IMC",
        "IMC (normal / surpoids)":       "IMC_binaire",
        "Direction":                     "Direction",
        "Tabagisme":                     tabac_col2 or "",
        alc_lbl:                         alc_col2   or "",
        "Pratique sportive":             sport_col2 or "",
        "Maladie chronique":             next((c for c in df.columns if re.search(r"maladie.*chron", _pp(c))), ""),
    }
    CROSS_MAP = {
        "Aucun croisement":                 None,
        "Quadrant Karasek":                 quad_col,
        "Charge mentale (catég.)":          "Dem_score_theo_cat",
        "Autonomie décisionnelle (catég.)": "Lat_score_theo_cat",
        "Soutien social (catég.)":          "SS_score_theo_cat",
        "Reconnaissance (catég.)":          "rec_score_theo_cat",
        "Satisfaction (catég.)":            "sat_score_theo_cat",
        "Culture d'entreprise (catég.)":    "cult_score_theo_cat",
        "Équité de charge (catég.)":        "equ_score_theo_cat",
    }
    avail_vars  = [k for k,v in VAR_MAP.items()  if v and v in df_sc.columns]
    avail_cross = [k for k,v in CROSS_MAP.items() if v is None or (v and v in df_sc.columns)]

    cx1,cx2 = st.columns(2)
    with cx1:
        st.markdown('<span style="font-size:0.76rem;font-weight:700;color:#2F577F;letter-spacing:0.1em;text-transform:uppercase;">Variable à visualiser</span>', unsafe_allow_html=True)
        sel_var   = st.selectbox("Variable",    avail_vars,  key="cr_var",   label_visibility="collapsed")
    with cx2:
        st.markdown('<span style="font-size:0.76rem;font-weight:700;color:#2F577F;letter-spacing:0.1em;text-transform:uppercase;">Croiser avec (optionnel)</span>', unsafe_allow_html=True)
        sel_cross = st.selectbox("Croisement", avail_cross, key="cr_cross", label_visibility="collapsed")

    real_col  = VAR_MAP.get(sel_var)    if sel_var   else None
    cross_col = CROSS_MAP.get(sel_cross) if sel_cross else None

    if real_col and real_col in df_sc.columns:
        if cross_col and cross_col in df_sc.columns:
            fig_cr = make_stacked(df_sc, real_col, cross_col)
            if fig_cr:
                st.plotly_chart(fig_cr, use_container_width=True, key="cr_stacked")
                tmp = df_sc[[real_col, cross_col]].dropna()
                if not tmp.empty:
                    pct_tbl = pd.crosstab(tmp[real_col].astype(str), tmp[cross_col].astype(str), normalize="index").mul(100).round(1)
                    st.markdown("**Tableau de distribution (%)**")
                    st.dataframe(pct_tbl.style.format("{:.1f}%"), use_container_width=True)
                    with st.expander("Effectifs bruts"):
                        st.dataframe(pd.crosstab(tmp[real_col].astype(str), tmp[cross_col].astype(str), margins=True, margins_name="Total"), use_container_width=True)
            else:
                st.info("Données insuffisantes pour ce croisement.")
        else:
            # ── Univarié
            c_chart, c_table = st.columns([6,4])
            with c_chart:
                fig_bar = make_barplot(df_sc, real_col)
                if fig_bar: st.plotly_chart(fig_bar, use_container_width=True, key="cr_bar")
            with c_table:
                cnt = df_sc[real_col].value_counts().reset_index()
                cnt.columns = [sel_var, "N"]
                cnt["%"] = (cnt["N"]/cnt["N"].sum()*100).round(1)
                st.dataframe(cnt, use_container_width=True, hide_index=True)
    else:
        st.info("Sélectionnez une variable pour afficher le graphique.")

# =============================================================================
# FIN
# =============================================================================