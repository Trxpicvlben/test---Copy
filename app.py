# ============================================================
# YODAN ANALYTICS — app.py
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="YODAN Analytics - Dashboard RPS",
    page_icon="📊",
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
    '.stButton>button{background:white!important;color:#1e40af!important;'
    'border:1.5px solid #bfdbfe!important;border-radius:10px!important;'
    'font-weight:600!important;font-size:13px!important;height:62px!important;'
    'width:100%!important;transition:all 0.2s!important}'
    '.stButton>button:hover{background:#1e40af!important;color:white!important;'
    'border-color:#1e40af!important;transform:translateY(-2px)!important}'
    '[data-testid="collapsedControl"]{background:#1e40af!important;border-radius:0 8px 8px 0!important}'
    '[data-testid="collapsedControl"] svg{fill:white!important}'
    '</style>',
    unsafe_allow_html=True
)

# ── Données ───────────────────────────────────────────────────
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    fp = os.path.join(base_path, 'data', 'mbi_donnees_fictives_600_sans_imc.csv')
    if not os.path.exists(fp):
        st.error(f"Fichier introuvable : {fp}")
        return pd.DataFrame()
    df = pd.read_csv(fp)
    if 'imc' not in df.columns:
        df['imc'] = (df['poids'] / ((df['taille']/100)**2)) if 'poids' in df.columns else 22.0
    return df

df = load_data()
if df.empty:
    st.stop()

total   = len(df)
nb_h    = (df['genre'] == 'Homme').sum()
nb_f    = (df['genre'] == 'Femme').sum()
pct_h   = nb_h / total * 100
pct_f   = nb_f / total * 100
age_moy = int(round(df['age'].mean()))

# ════════════════════════════════════════════════════════════
# TOPBAR
# ════════════════════════════════════════════════════════════
st.markdown(
    '<div style="display:flex;align-items:center;justify-content:center;'
    'background:white;border-radius:12px;padding:20px 24px;margin-bottom:20px;'
    'box-shadow:0 1px 3px rgba(0,0,0,0.06),0 4px 12px rgba(30,64,175,0.08);'
    'border:1px solid #e8edf5;">'
    '<div style="text-align:center;">'
    '<div style="font-size:24px;font-weight:700;color:#1e293b;letter-spacing:-0.3px;">'
    'Dashboard d\'Analyse des Risques PsychoSociaux</div>'
    '<div style="font-size:19px;font-weight:600;color:#334866;margin-top:8px;">'
    'Entreprise Pahaliah &amp; Fils</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

# ════════════════════════════════════════════════════════════
# VUE D'ENSEMBLE
# ════════════════════════════════════════════════════════════
st.markdown(
    '<div style="display:flex;align-items:center;gap:10px;margin:20px 0 14px;">'
    '<div style="width:4px;height:20px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
    '<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.3px;text-transform:uppercase;">Vue d\'ensemble</span>'
    '</div>',
    unsafe_allow_html=True
)

def kpi_card(icon, icon_color, icon_bg, bar_color, value, unit, sub, label):
    sub_html = f'<div style="font-size:11px;color:#94a3b8;margin-top:2px;">{sub}</div>' if sub else ''
    return (
        f'<div style="background:white;border-radius:12px;padding:18px 16px 14px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.05),0 4px 12px rgba(0,0,0,0.06);'
        f'border:1px solid #e8edf5;border-top:3px solid {bar_color};height:148px;">'
        f'<div style="width:34px;height:34px;background:{icon_bg};border-radius:8px;'
        f'display:flex;align-items:center;justify-content:center;margin-bottom:10px;">'
        f'<i class="{icon}" style="color:{icon_color};font-size:14px;"></i></div>'
        f'<div style="font-size:32px;font-weight:700;color:#1e293b;line-height:1;letter-spacing:-0.5px;">'
        f'{value}<span style="font-size:14px;font-weight:400;color:#64748b;">{unit}</span></div>'
        f'{sub_html}'
        f'<div style="font-size:11px;font-weight:600;color:#64748b;letter-spacing:0.7px;'
        f'text-transform:uppercase;margin-top:8px;">{label}</div>'
        f'</div>'
    )

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(kpi_card("fas fa-users","#1e40af","#eff6ff","#3b82f6",total,"","","Effectif total"), unsafe_allow_html=True)
with c2:
    if nb_f > nb_h:
        st.markdown(kpi_card("fas fa-female","#7c3aed","#f5f3ff","#a78bfa",f"{pct_f:.1f}","%",f"{nb_f} collaboratrices","Femmes"), unsafe_allow_html=True)
    else:
        st.markdown(kpi_card("fas fa-male","#0369a1","#f0f9ff","#38bdf8",f"{pct_h:.1f}","%",f"{nb_h} collaborateurs","Hommes"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("far fa-calendar-alt","#0f766e","#f0fdfa","#2dd4bf",age_moy," ans","","Âge moyen"), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# JAUGE
# ════════════════════════════════════════════════════════════
st.markdown(
    '<div style="display:flex;align-items:center;gap:10px;margin:28px 0 16px;">'
    '<div style="width:4px;height:20px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
    '<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.3px;text-transform:uppercase;">Indice de performance globale RPS</span>'
    '</div>',
    unsafe_allow_html=True
)

score = 72

if   score >= 75: statut, sc, sc_bg, sc_bd = "EXCELLENT", "#15803d", "#f0fdf4", "#86efac"
elif score >= 50: statut, sc, sc_bg, sc_bd = "BON",       "#1e40af", "#eff6ff", "#bfdbfe"
elif score >= 25: statut, sc, sc_bg, sc_bd = "VIGILANCE", "#d97706", "#fffbeb", "#fde68a"
else:             statut, sc, sc_bg, sc_bd = "CRITIQUE",  "#dc2626", "#fef2f2", "#fca5a5"

msgs = {
    "EXCELLENT": ("fas fa-shield-alt",          "Environnement de travail sain",
                "Les indicateurs psychosociaux sont au vert. Les pratiques de prévention sont bien ancrées. "
                "Maintenez cette dynamique par des évaluations régulières et continuez à impliquer les collaborateurs."),
    "BON":       ("fas fa-chart-line",           "Situation globalement favorable",
                "Le niveau de risques psychosociaux est maîtrisé dans l'ensemble. Quelques axes d'amélioration "
                "restent à explorer, notamment sur les dimensions stress et épuisement professionnel. "
                "Une attention particulière aux résultats MBI et COPSOQ permettra d'affiner les actions prioritaires."),
    "VIGILANCE": ("fas fa-exclamation-triangle", "Des signaux à ne pas négliger",
                "Plusieurs indicateurs révèlent une exposition modérée aux risques psychosociaux. "
                "Il est recommandé d'engager rapidement une analyse approfondie par dimension et de mettre "
                "en place un plan d'action ciblé avec un suivi mensuel."),
    "CRITIQUE":  ("fas fa-exclamation-circle",   "Situation nécessitant une intervention urgente",
                "Les indicateurs sont en zone critique. Une intervention immédiate est nécessaire : audit RPS complet, "
                "entretiens individuels et collectifs, et mise en place d'un comité de suivi dédié."),
}
m_icon, m_title, m_body = msgs[statut]

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=score,
    domain={'x':[0,1],'y':[0,1]},
    number={
        'font':{'size':60,'color':sc,'family':'Inter'},
        'valueformat':'.0f',
        'suffix':'<span style="font-size:22px;color:#94a3b8;"> / 100</span>'
    },
    gauge={
        'axis':{
            'range':[0,100],
            'tickvals':[0,25,50,75,100],
            'ticktext':['0','25','50','75','100'],
            'tickfont':{'size':12,'color':'#94a3b8','family':'Inter'},
            'tickwidth':1,'tickcolor':'#e2e8f0'
        },
        'bar':{'color':sc,'thickness':0.04},
        'bgcolor':'white','borderwidth':0,
        'steps':[
            {'range':[0,  25],'color':'#ef4444'},
            {'range':[25, 50],'color':'#fb923c'},
            {'range':[50, 75],'color':'#4ade80'},
            {'range':[75,100],'color':'#16a34a'},
        ],
        'threshold':{'line':{'color':sc,'width':5},'thickness':0.85,'value':score}
    }
))
fig.update_layout(
    height=300,
    margin=dict(l=60,r=60,t=20,b=10),
    paper_bgcolor='white',
    font={'family':'Inter'}
)

col_gauge, col_msg = st.columns([3, 2])

with col_gauge:
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:center;gap:10px;'
        f'padding:10px 20px;background:{sc_bg};border-radius:10px;'
        f'border:1.5px solid {sc_bd};margin-top:-8px;">'
        f'<div style="width:8px;height:8px;border-radius:50%;background:{sc};"></div>'
        f'<span style="font-size:14px;font-weight:700;color:{sc};letter-spacing:1.2px;">{statut}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

with col_msg:
    st.markdown('<div style="height:36px;"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="background:#f8fafc;border-radius:12px;padding:20px;'
        f'border:1px solid #e2e8f0;border-left:4px solid {sc};">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">'
        f'<div style="width:30px;height:30px;background:{sc_bg};border-radius:8px;'
        f'display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
        f'<i class="{m_icon}" style="color:{sc};font-size:13px;"></i></div>'
        f'<span style="font-size:13px;font-weight:700;color:#1e293b;">{m_title}</span>'
        f'</div>'
        f'<p style="margin:0 0 14px;font-size:12.5px;color:#475569;line-height:1.75;">{m_body}</p>'
        f'<div style="padding-top:12px;border-top:1px solid #e2e8f0;">'
        f'<p style="margin:0;font-size:11px;color:#94a3b8;text-align:center;">'
        f'<i class="fas fa-info-circle"></i>&nbsp;'
        f'Indice fictif — recalculé à l\'issue de tous les tests<br>'
        f'MBI · COPSOQ · Karasek · WHO · PSS-10 · QVT · Toile SST'
        f'</p></div></div>',
        unsafe_allow_html=True
    )

# ════════════════════════════════════════════════════════════
# 7 BOUTONS TESTS
# ════════════════════════════════════════════════════════════
st.markdown(
    '<div style="display:flex;align-items:center;gap:10px;margin:28px 0 14px;">'
    '<div style="width:4px;height:20px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
    '<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.3px;text-transform:uppercase;">Accès aux tests psychosociaux</span>'
    '</div>',
    unsafe_allow_html=True
)

# ── Ligne 1 : 4 icônes + 4 boutons ──
TESTS1 = [
    ("fas fa-fire",            "#dc2626","#fef2f2"),
    ("fas fa-clipboard-check", "#0369a1","#f0f9ff"),
    ("fas fa-briefcase",       "#7c3aed","#f5f3ff"),
    ("fas fa-heartbeat",       "#d97706","#fffbeb"),
]
ic1, ic2, ic3, ic4 = st.columns(4)
for col, (icon, color, bg) in zip([ic1,ic2,ic3,ic4], TESTS1):
    with col:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:5px;">'
            f'<div style="width:40px;height:40px;border-radius:10px;background:{bg};'
            f'display:inline-flex;align-items:center;justify-content:center;">'
            f'<i class="{icon}" style="color:{color};font-size:16px;"></i></div></div>',
            unsafe_allow_html=True
        )

b1, b2, b3, b4 = st.columns(4)
with b1:
    if st.button("MBI Burnout",   use_container_width=True, key="mbi"):
        st.switch_page("pages/1_MBI_Burnout.py")
with b2:
    if st.button("COPSOQ Stress", use_container_width=True, key="copsoq"):
        st.switch_page("pages/5_Copsoq.py")
with b3:
    if st.button("Karasek",       use_container_width=True, key="karasek"):
        st.switch_page("pages/2_Karasek.py")
with b4:
    if st.button("WHO Santé",     use_container_width=True, key="who"):
        st.info("🚧 En construction")

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── Ligne 2 ──
TESTS2_icons = [
    ("fas fa-brain",  "#0891b2","#ecfeff"),
    ("fas fa-star",   "#0f766e","#f0fdfa"),
    ("fas fa-spider", "#7c3aed","#f5f3ff"),
]
ic5, ic6, ic7, _ = st.columns(4)
for col, (icon, color, bg) in zip([ic5, ic6, ic7], TESTS2_icons):
    with col:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:5px;">'
            f'<div style="width:40px;height:40px;border-radius:10px;background:{bg};'
            f'display:inline-flex;align-items:center;justify-content:center;">'
            f'<i class="{icon}" style="color:{color};font-size:16px;"></i></div></div>',
            unsafe_allow_html=True
        )

b5, b6, b7, _ = st.columns(4)
with b5:
    if st.button("PSS-10 Stress", use_container_width=True, key="pss10"):
        st.switch_page("pages/4_Charge_Mentale.py")
with b6:
    if st.button("QVT Qualité",   use_container_width=True, key="qvt"):
        st.switch_page("pages/7_QVT_Qualite.py")
with b7:
    if st.button("Toile SST",     use_container_width=True, key="sst"):
        st.switch_page("pages/3_SST.py")

# ── FOOTER ────────────────────────────────────────────────────
st.markdown(
    '<div style="margin-top:40px;padding:14px 0;border-top:1px solid #e2e8f0;'
    'display:flex;align-items:center;justify-content:space-between;">'
    '<div style="display:flex;align-items:center;gap:10px;">'
    '<div style="width:24px;height:24px;background:linear-gradient(135deg,#1e40af,#3b82f6);'
    'border-radius:6px;display:flex;align-items:center;justify-content:center;">'
    '<i class="fas fa-chart-line" style="color:white;font-size:10px;"></i></div>'
    '<span style="font-size:13px;font-weight:600;color:#374151;">YODAN Analytics</span>'
    '<span style="font-size:12px;color:#cbd5e1;">·</span>'
    '<span style="font-size:12px;color:#94a3b8;">Dashboard v2.0 Pro · 2026</span>'
    '</div>'
    '<span style="font-size:11px;color:#cbd5e1;letter-spacing:0.4px;">'
    'MBI · COPSOQ · Karasek · WHO · PSS-10 · QVT · Toile SST'
    '</span></div>',
    unsafe_allow_html=True
)