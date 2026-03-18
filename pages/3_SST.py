# ===============================
# CHARGEMENT DES PACKAGES
# ===============================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import io

# ===============================
# CONFIGURATION DE LA PAGE
# ===============================
st.set_page_config(
    page_title="Tableau de Bord - Santé et Sécurité au Travail (SST)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===============================
# CSS PERSONNALISÉ
# ===============================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,400;1,9..144,600&display=swap" rel="stylesheet">
<style>
    /* ── Variables ── */
    :root {
        --bg-soft:  #eef2f7;
        --card:     #ffffff;
        --text:     #2f3d55;
        --accent:   #2f66b3;
        --border:   #dde5f2;
    }

    /* ── Base typographie : Plus Jakarta Sans ── */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(180deg, #f4f6fb 0%, var(--bg-soft) 100%);
        color: var(--text);
    }

    /* Style général */
    .main > div {
        padding: 0rem 1rem;
    }

    /* ── Grands titres de section : Fraunces italic (style COPSOQ) ── */
    .section-title {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        font-family: 'Fraunces', Georgia, serif !important;
        font-size: 1.25rem !important;
        font-style: italic !important;
        font-weight: 400 !important;
        color: #0F2340 !important;
        margin: 1.6rem 0 1rem !important;
        padding-bottom: 0.65rem !important;
        border-bottom: 2px solid #dde5f2 !important;
    }

    .section-title::before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 22px;
        background: linear-gradient(180deg, #2f66b3 0%, #4f8be4 100%);
        border-radius: 2px;
        flex-shrink: 0;
    }

    /* ── Onglets style COPSOQ ── */
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
        transition: all 0.2s !important;
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

    /* Conteneur du radar */
    .radar-container {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        display: flex;
        justify-content: center;
    }

    /* Titre compact */
    .compact-title {
        background-color: #2c3e50;
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Points d'amélioration en colonnes */
    .non-questions-box {
        background-color: #f8d7da;
        border-left: 4px solid #e74c3c;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
        font-size: 0.9rem;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .non-questions-box h5 {
        margin-top: 0;
        margin-bottom: 8px;
        color: #721c24;
        font-size: 1rem;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .non-questions-box ul {
        margin: 0;
        padding-left: 20px;
    }
    .non-questions-box li {
        margin-bottom: 8px;
        line-height: 1.4;
    }

    .no-non-message {
        font-style: italic;
        color: #27ae60;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        background-color: #d4edda;
        border-radius: 5px;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Cacher les éléments inutiles */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── Sidebar blanche ── */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #dde5f2;
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stText {
        color: #0F2340 !important;
    }

    /* Style pour la liste des principes */
    .principles-list {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        font-size: 1rem;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .principles-list ol {
        column-count: 2;
        column-gap: 40px;
    }
    .principles-list li {
        margin-bottom: 8px;
        break-inside: avoid;
    }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TOPBAR SST
# ════════════════════════════════════════════════════════════
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
    unsafe_allow_html=True
)
_col_top, _col_back = st.columns([9, 1])
with _col_top:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;background:white;border-radius:12px;'
        'padding:14px 24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06),'
        '0 4px 12px rgba(30,64,175,0.08);border:1px solid #e8edf5;">'
        '<div style="width:38px;height:38px;background:linear-gradient(135deg,#0369a1,#38bdf8);'
        'border-radius:10px;display:flex;align-items:center;justify-content:center;">'
        '<i class="fas fa-hard-hat" style="color:white;font-size:15px;"></i></div>'
        '<div>'
        '<div style="font-size:16px;font-weight:700;color:#1e293b;font-family:\'Plus Jakarta Sans\',sans-serif;">SST — Santé &amp; Sécurité au Travail</div>'
        '<div style="font-size:11px;color:#64748b;margin-top:1px;font-family:\'Plus Jakarta Sans\',sans-serif;">Analyse des niveaux de maturité SST · Pahaliah &amp; Fils</div>'
        '</div></div>',
        unsafe_allow_html=True
    )
with _col_back:
    if st.button("← Accueil", key="back_home_sst", use_container_width=True):
        st.switch_page("app.py")

# ════════════════════════════════════════════════════════════
# IMPORT FICHIER
# ════════════════════════════════════════════════════════════

# ===============================
# CHARGEMENT DES DONNÉES
# ===============================


# ===============================
# NETTOYAGE DES DONNÉES
# ===============================
def clean_data(data_raw):
    if data_raw is None:
        return None
    
    # Convertir toutes les colonnes de réponses en chaînes et remplacer NaN par "NA"
    for col in data_raw.columns:
        data_raw[col] = data_raw[col].astype(str)
        data_raw[col] = data_raw[col].fillna("NA")
    
    return data_raw

# ===============================
# TEXTE COMPLET DES QUESTIONS PAR PRINCIPE
# ===============================
texte_questions = {
    "AT_MP": [
        "Les AT sont déclarées",
        "Les AT sont analysés pour identifier la cause",
        "Les AT sont enregistrés et présentés en Comité SST",
        "Les enquêtes se limitent à la recherche de causes immédiates",
        "Il y a un suivi de la réalisation des actions",
        "Des indicateurs de sinistralité sont affichés",
        "Les Maladies professionnelles et les incidents sont pris en compte",
        "Les AT/MP des CDD et intérimaires sont enregistrés",
        "Les AT/MP sont analysés selon une méthode définie",
        "Le CSST ou management participe aux analyses",
        "Les mesures sont intégrées dans un plan d'action",
        "Le Document Unique est mis à jour",
        "Les analyses sont diffusées au personnel",
        "Un comité fait des propositions après un AT/MP",
        "Les tendances AT/MP alimentent la stratégie",
        "Les salariés sont encouragés à signaler les risques",
        "Une veille exploite les AT/MP graves d'activités similaires"
    ],
    "Maintenance": [
        "Les équipements sont réparés en cas de panne",
        "L'entreprise ne connaît pas la liste des équipements à vérifier",
        "Certains équipements sont vérifiés sans suivi des remarques",
        "Les équipements soumis à vérification sont identifiés",
        "Les vérifications sont effectuées",
        "Les travaux sont réalisés au coup par coup",
        "La maintenance est principalement curative",
        "Les responsables maintenance sont identifiés",
        "Un responsable suit le matériel sur site extérieur",
        "Les vérifications couvrent tous les matériaux",
        "Les vérifications suivent un planning",
        "La prise en compte des anomalies est formalisée",
        "La maintenance préventive est planifiée",
        "La maintenance est pilotée par indicateurs",
        "La coordination entre services est recherchée",
        "Les besoins utilisateurs sont pris en compte",
        "Recherche de nouvelles technologies",
        "La liste des équipements est mise à jour par veille",
        "L'analyse des vérifications fait évoluer les cahiers des charges"
    ],
    "Sous_traitants": [
        "Évaluation des risques a priori pour entreprises extérieures",
        "Situations dangereuses gérées au coup par coup",
        "Évaluation des risques rédigée dans un plan de prévention",
        "Sous forme de check-list",
        "Objectif principal : répondre à une obligation",
        "Généralement inconnu des intervenants",
        "Une personne désignée pour signer",
        "Le CSST est informé",
        "Évaluation des risques avant travaux par les 2 entreprises",
        "L'utilisatrice commente le plan aux salariés",
        "Les entreprises veillent au respect",
        "Modifications prises en compte, CSST participe aux visites",
        "Débriefing en fin de travaux",
        "Choix des sous-traitants basé sur leurs performances SST",
        "Accompagnement des sous-traitants dans leur gestion SST"
    ],
    "Interimaires": [
        "Appel à intérimaires dans l'urgence sans accueil",
        "Contenu des missions non défini",
        "Analyse du besoin avec l'ETT",
        "Fourniture des EPI définie",
        "Accueil minimal assuré",
        "Connaissance des travaux interdits",
        "Liste des postes à risques communiquée",
        "Échange préalable formalisé avec l'ETT",
        "L'ETT connaît les postes",
        "Anticipation des besoins",
        "Liste des postes accessibles",
        "Accueil adapté à chaque poste",
        "Parcours d'intégration incluant la SST",
        "Nouvelle analyse si changement de poste",
        "L'agence est prévenue",
        "Bilan en fin de mission",
        "Partenariat effectif avec les agences",
        "Intérimaires associés aux échanges SST"
    ],
    "Preparation": [
        "SST prise en compte à l'achat",
        "Limité à une phrase de conformité",
        "Postes et allées encombrés",
        "Outils pas toujours adaptés",
        "Critères sécurité intégrés à la commande",
        "Conception basée sur réglementation et ergonomie",
        "Protections collectives installées",
        "EPI appropriés fournis",
        "Responsable désigné pour l'extérieur",
        "Cahiers des charges établis",
        "Rubrique sécurité systématique",
        "Conception basée sur analyse des situations",
        "Réception par service compétent",
        "Vérification avant mise en service",
        "CSST consulté",
        "Analyse préalable pour les chantiers",
        "Gestion des matériels organisée",
        "Salariés associés au processus d'achat",
        "Environnement analysé avec le personnel",
        "Analyse avant modifications"
    ],
    "Sante": [
        "SST abordée dans l'entreprise",
        "Visites médicales réalisées",
        "Évaluation limitée au chimique et nuisances",
        "Évaluation transcrite dans le DU",
        "CSST informé",
        "Sollicitation du médecin du travail",
        "FDS disponibles et actualisées",
        "Fiches d'exposition CMR existent",
        "Réflexions pour réduire les risques",
        "Risque santé intègre toutes les nuisances et TMS",
        "Actions en amont avec CSST/DP",
        "Travail avec fournisseurs",
        "Modalités définies pour achats",
        "Maintien dans l'emploi recherché",
        "Préoccupation des risques émergents",
        "Santé prise en compte dès la conception",
        "CSST/DP associé"
    ],
    "EvRP": [
        "EvRP peu ou pas réalisée",
        "DU succinct pour obligation",
        "Pas de plan d'action",
        "EvRP réalisée et mise à jour chaque année",
        "Travaux extérieurs pris en compte",
        "Basée sur description des activités",
        "Connaissance basée sur les accidents",
        "Plans d'action sans priorités",
        "Mise à jour par direction sans concertation",
        "Méthodologie basée sur observation",
        "EvRP collective avec managers et équipes",
        "Pilote désigné",
        "Plan d'action général",
        "Pilotes, moyens et délais précisés",
        "Délais globalement tenus",
        "CSST/DP associé",
        "EvRP moteur du système SST",
        "Intègre veilles technologiques",
        "Direction évalue les moyens",
        "Salariés systématiquement associés"
    ],
    "Formation": [
        "Compétences SST faibles",
        "Chacun se fie à son expérience",
        "Formation limitée au réglementaire",
        "SST identifiés/formés",
        "Formations réglementaires identifiées et réalisées",
        "Formation technique limitée aux postes",
        "Outils et formations standards",
        "Équipiers première intervention formés",
        "Formation au poste inclut SST",
        "Membres CSST formés",
        "Accueil minimal des nouveaux",
        "Besoins formation recensés et actualisés",
        "Validité des habilitations suivie",
        "Formations planifiées",
        "CSST consulté",
        "Formation des membres actualisée",
        "Nouvel arrivant évalué",
        "Tutorat organisé",
        "Recours à l'externe si besoin",
        "Indicateurs de suivi",
        "Délégation de pouvoir formée",
        "Programme intègre besoins des entretiens",
        "Tient compte des objectifs SST",
        "Risques transversaux couverts",
        "Tous niveaux hiérarchiques concernés",
        "Évaluation de la qualité des formations",
        "Appropriation des compétences externes",
        "Capitalisation et diffusion des bonnes pratiques"
    ],
    "Responsabilites": [
        "Fonction sécurité non identifiée",
        "Actions au coup par coup",
        "Encadrement ne veille pas",
        "Salariés non impliqués",
        "Peu ou pas de procédures SST",
        "Pas de réunion CSST/DP",
        "Une personne en charge SST",
        "Considérée comme seul responsable",
        "Encadrement s'inquiète de l'application",
        "Écart instructions/pratiques",
        "Salariés sensibilisés",
        "Connaissance de consignes",
        "CSST/DP informé mais peu sollicité",
        "Responsable SST compétent et conseiller",
        "Anime la démarche",
        "Acteurs opérationnels associés",
        "Encadrement exemplaire",
        "Moteur en détection des risques",
        "CSST/DP associé",
        "Président CSST a moyens",
        "Responsabilités définies mais cloisonnées",
        "Communication organisée mais non évaluée",
        "SST composante de tous les managers",
        "Responsabilités réparties avec coordination",
        "Échanges réguliers avec encadrement",
        "Audits SST terrain",
        "Règles de sécurité valorisées",
        "CSST/DP pleinement impliqué",
        "Communication réelle avec direction"
    ],
    "Management": [
        "Pas de démarche structurée",
        "Absence d'accident justifie inutilité",
        "Accidents fatalité ou erreur humaine",
        "Actions SST externalisées",
        "Direction ne définit pas d'objectifs",
        "Budget significatif alloué",
        "Prévention technique essentiellement",
        "Moyens considérés suffisants",
        "Démarche imposée de l'extérieur",
        "Pas de recours à ressources extérieures",
        "Seulement organismes de contrôle",
        "Objectifs de résultats à court terme",
        "Direction prend en compte les risques",
        "Démarche volontaire mais directive",
        "Mission partagée avec réseau interne",
        "Efficacité des EP évaluée",
        "Appel à ressources extérieures",
        "Objectifs variés mais abandonnés",
        "Engagement particulier de la direction",
        "Anticipation des nouveaux risques",
        "Coordination avec qualité et environnement",
        "Démarche participative",
        "Relations basées sur la confiance",
        "Objectifs SST dans stratégie",
        "Ressources SST évaluées",
        "Benchmarking avec partenaires",
        "Démarche SST valorise l'image"
    ]
}

# ===============================
# DÉFINITION DES PALIERS POUR CHAQUE PRINCIPE
# ===============================
paliers_limits = {
    "AT_MP": {
        1: list(range(1, 3)),     # Questions 1-2
        2: list(range(3, 7)),     # Questions 3-6
        3: list(range(7, 14)),    # Questions 7-13
        4: list(range(14, 18))    # Questions 14-17
    },
    "Maintenance": {
        1: list(range(1, 4)),     # Questions 1-3
        2: list(range(4, 10)),    # Questions 4-9
        3: list(range(10, 16)),   # Questions 10-15
        4: list(range(16, 20))    # Questions 16-19
    },
    "Sous_traitants": {
        1: list(range(1, 3)),     # Questions 1-2
        2: list(range(3, 9)),     # Questions 3-8
        3: list(range(9, 13)),    # Questions 9-12
        4: list(range(13, 16))    # Questions 13-15
    },
    "Interimaires": {
        1: list(range(1, 3)),     # Questions 1-2
        2: list(range(3, 8)),     # Questions 3-7
        3: list(range(8, 17)),    # Questions 8-16
        4: list(range(17, 19))    # Questions 17-18
    },
    "Preparation": {
        1: list(range(1, 5)),     # Questions 1-4
        2: list(range(5, 10)),    # Questions 5-9
        3: list(range(10, 18)),   # Questions 10-17
        4: list(range(18, 21))    # Questions 18-20
    },
    "Sante": {
        1: list(range(1, 3)),     # Questions 1-2
        2: list(range(3, 10)),    # Questions 3-9
        3: list(range(10, 15)),   # Questions 10-14
        4: list(range(15, 18))    # Questions 15-17
    },
    "EvRP": {
        1: list(range(1, 4)),     # Questions 1-3
        2: list(range(4, 10)),    # Questions 4-9
        3: list(range(10, 17)),   # Questions 10-16
        4: list(range(17, 21))    # Questions 17-20
    },
    "Formation": {
        1: list(range(1, 5)),     # Questions 1-4
        2: list(range(5, 12)),    # Questions 5-11
        3: list(range(12, 22)),   # Questions 12-21
        4: list(range(22, 29))    # Questions 22-28
    },
    "Responsabilites": {
        1: list(range(1, 7)),     # Questions 1-6
        2: list(range(7, 14)),    # Questions 7-13
        3: list(range(14, 23)),   # Questions 14-22
        4: list(range(23, 30))    # Questions 23-29
    },
    "Management": {
        1: list(range(1, 6)),     # Questions 1-5
        2: list(range(6, 13)),    # Questions 6-12
        3: list(range(13, 19)),   # Questions 13-18
        4: list(range(19, 28))    # Questions 19-27
    }
}
# ===============================
# NOMS DES PRINCIPES
# ===============================
noms_principes = {
    "AT_MP": "Analyse des AT-MP",
    "Maintenance": "Vérifications périodiques et maintenance",
    "Sous_traitants": "Attitude vis-à-vis des sous-traitants",
    "Interimaires": "Attitude vis-à-vis des intérimaires",
    "Preparation": "Préparation et organisation du travail",
    "Sante": "Santé au travail",
    "EvRP": "Évaluation des risques",
    "Formation": "Formation et compétences SST",
    "Responsabilites": "Responsabilités et communication",
    "Management": "Pratiques managériales"
}

# ===============================
# FONCTION POUR CALCULER LE PALIER ATTEINT
# ===============================
def calculate_palier_hierarchique(row_data, principe, questions_par_principe):
    # Extraire les réponses pour ce principe
    cols = questions_par_principe[principe]
    
    # Filtrer pour ne garder que les colonnes qui existent
    valid_cols = [c for c in cols if c < len(row_data)]
    
    if not valid_cols:
        return 0
    
    # Récupérer les réponses
    responses = [row_data.iloc[c] for c in valid_cols]
    
    # Vérifier chaque palier séquentiellement
    current_palier = 0
    
    for palier_num in range(1, 5):
        if palier_num not in paliers_limits[principe]:
            continue
            
        palier_indices = paliers_limits[principe][palier_num]
        
        # Vérifier si tous les indices du palier existent
        if max(palier_indices) > len(responses):
            break
        
        # Récupérer les réponses pour ce palier
        palier_responses = [responses[i-1] for i in palier_indices]
        
        # Vérifier si TOUTES les réponses du palier sont "Oui"
        all_valid = all(
            not pd.isna(r) and str(r) != "NA" and str(r) != "" and str(r) == "Oui"
            for r in palier_responses
        )
        
        if all_valid:
            current_palier = palier_num
        else:
            break
    
    return current_palier

# ===============================
# FONCTION POUR IDENTIFIER LES QUESTIONS AVEC RÉPONSE "NON"
# ===============================
def get_non_questions(row_data, principe, questions_par_principe):
    # Extraire les indices des colonnes pour ce principe
    cols = questions_par_principe[principe]
    textes = texte_questions[principe]
    
    # Filtrer pour ne garder que les colonnes qui existent
    valid_cols = [c for c in cols if c < len(row_data)]
    
    if not valid_cols:
        return None
    
    # Récupérer les réponses
    responses = [row_data.iloc[c] for c in valid_cols]
    
    # Identifier les indices où la réponse est "Non"
    non_indices = [i for i, r in enumerate(responses) if str(r) == "Non"]
    
    if not non_indices:
        return None
    
    # Récupérer les textes correspondants (questions complètes)
    non_questions = [textes[i] for i in non_indices]
    
    return non_questions

# ════════════════════════════════════════════════════════════
# CHARGEMENT ET PRÉPARATION DES DONNÉES
# ════════════════════════════════════════════════════════════
_main_up = st.file_uploader(
    "Charger un fichier Excel ou CSV",
    type=["xlsx", "xls", "csv"],
    help="Glissez-déposez ou cliquez pour sélectionner votre fichier de données.",
    key="sst_main_uploader",
)
if _main_up is not None:
    _b = _main_up.read()
    if _b:
        st.session_state["sst_file_bytes"] = _b
        st.session_state["sst_file_name"] = _main_up.name

if "sst_file_bytes" not in st.session_state:
    st.info("Veuillez charger un fichier de données (Excel ou CSV) pour démarrer l'analyse.")
    st.stop()

_fn = st.session_state["sst_file_name"]
_buf = io.BytesIO(st.session_state["sst_file_bytes"])
try:
    if _fn.lower().endswith(".csv"):
        data_raw = pd.read_csv(_buf, sep=None, engine="python")
    else:
        data_raw = pd.read_excel(_buf)
except Exception as e:
    st.error(f"❌ Erreur lors du chargement : {e}")
    st.stop()
    data_raw = None

if data_raw is not None:
    data_raw = clean_data(data_raw)
    
    # ===============================
    # DÉTECTION AUTOMATIQUE DES PRINCIPES
    # ===============================
    total_questions = data_raw.shape[1]
    
    # Définir les limites de questions pour chaque principe
    questions_per_principe = {
        "AT_MP": 17,
        "Maintenance": 19,
        "Sous_traitants": 15,
        "Interimaires": 18,
        "Preparation": 20,
        "Sante": 17,
        "EvRP": 20,
        "Formation": 28,
        "Responsabilites": 29,
        "Management": 27
    }
    
    # Ajuster si le nombre de colonnes ne correspond pas
    total_calcule = sum(questions_per_principe.values())
    if total_calcule != total_questions:
        st.info(f"Ajustement automatique... ({total_questions} questions détectées)")
        facteur = total_questions / total_calcule
        for key in questions_per_principe:
            questions_per_principe[key] = round(questions_per_principe[key] * facteur)
        
        # Ajuster la différence
        diff = total_questions - sum(questions_per_principe.values())
        last_key = list(questions_per_principe.keys())[-1]
        questions_per_principe[last_key] += diff
    
    # Calculer les indices de début et fin (commencer à la colonne 0)
    debut = 0
    questions_par_principe = {}
    
    for principe, nb_questions in questions_per_principe.items():
        fin = debut + nb_questions - 1
        questions_par_principe[principe] = list(range(debut, fin + 1))
        debut = fin + 1
    
    # ===============================
    # CALCUL DES PALIERS POUR TOUS LES RÉPONDANTS
    # ===============================
    paliers_data = {}
    
    for principe in questions_par_principe.keys():
        paliers_data[principe] = []
    
    for i in range(len(data_raw)):
        row_data = data_raw.iloc[i]
        
        for principe in questions_par_principe.keys():
            palier = calculate_palier_hierarchique(row_data, principe, questions_par_principe)
            paliers_data[principe].append(palier)
    
    paliers_df = pd.DataFrame(paliers_data)
    
    # ===============================
    # INTERFACE STREAMLIT - OPTIMISÉE
    # ===============================
    
    # Titre compact
    st.markdown('<div class="compact-title"> Tableau de Bord - Santé et Sécurité au Travail (SST) </div>', unsafe_allow_html=True)
    
    # Expandeur avec la liste des principes (juste après le titre)
    with st.expander("Voir la liste des 10 principes évalués"):
        st.markdown("""
        <div class="principles-list">
            <ol>
                <li><strong>AT/MP</strong> - Analyse des accidents du travail et des maladies professionnelles</li>
                <li><strong>Maintenance</strong> - Vérifications périodiques et maintenance des équipements</li>
                <li><strong>Sous-traitants</strong> - Attitude de l'entreprise vis-à-vis des sous-traitants</li>
                <li><strong>Intérimaires</strong> - Attitude de l'entreprise vis-à-vis des intérimaires</li>
                <li><strong>Préparation</strong> - Préparation et organisation du travail</li>
                <li><strong>Santé</strong> - Santé au travail</li>
                <li><strong>EvRP</strong> - Réalisation et mise à jour de l’évaluation des risques et du plan d’actions</li>
                <li><strong>Formation</strong> - Programme de formation et compétence SST</li>
                <li><strong>Responsabilités</strong> - Responsabilités, communication et implication des salariés</li>
                <li><strong>Management</strong> - Pratiques managériales de prévention</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Utiliser la première ligne de données
    idx = 0
    
    # Radar chart avec principes en toutes lettres (agrandies)
    paliers_values = [paliers_df.loc[idx, principe] for principe in questions_par_principe.keys()]
    
    # Noms complets des principes (non coupés)
    categories = [
        "Sous-traitants", "Maintenance", "AT/MP",
        "Intérimaires", "Préparation", "Santé",
        "EvRP", "Formation", "Responsabilités", 
        "Management"
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=paliers_values + [paliers_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name="Niveau de maturité",
        line_color='#e74c3c',
        fillcolor='rgba(231, 76, 60, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 4],
                tickvals=[0, 1, 2, 3, 4],
                tickfont=dict(size=12)
            ),
            angularaxis=dict(
                tickfont=dict(size=16, color='black', family='Arial'),
                rotation=90,
                tickangle=0
            )
        ),
        showlegend=False,
        title="Niveau de maturité SST - Évaluation globale",
        title_font=dict(size=16, family='Arial'),
        height=700,
        width=1000,
        margin=dict(l=150, r=150, t=60, b=100),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    # Afficher le radar dans un conteneur stylisé centré
    st.markdown('<div class="radar-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 10, 1])
    with col2:
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Points d'amélioration en dessous avec questions complètes
    st.markdown("### Points d'amélioration")
    
    raw_row = data_raw.iloc[idx]
    has_any_non = False
    
    # Créer 2 colonnes pour les points d'amélioration
    col_left, col_right = st.columns(2)
    
    principe_list = list(questions_par_principe.keys())
    mid_point = len(principe_list) // 2
    
    with col_left:
        for principe in principe_list[:mid_point]:
            non_questions = get_non_questions(raw_row, principe, questions_par_principe)
            if non_questions:
                has_any_non = True
                # Afficher les questions complètes
                questions_html = "".join([f"<li>{q}</li>" for q in non_questions])
                st.markdown(f"""
                <div class="non-questions-box">
                    <h5>{noms_principes[principe]}</h5>
                    <ul>
                        {questions_html}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    with col_right:
        for principe in principe_list[mid_point:]:
            non_questions = get_non_questions(raw_row, principe, questions_par_principe)
            if non_questions:
                has_any_non = True
                # Afficher les questions complètes
                questions_html = "".join([f"<li>{q}</li>" for q in non_questions])
                st.markdown(f"""
                <div class="non-questions-box">
                    <h5>{noms_principes[principe]}</h5>
                    <ul>
                        {questions_html}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    if not has_any_non:
        st.markdown("""
        <div class="no-non-message">
            ✅ Toutes les réponses sont 'Oui'
        </div>
        """, unsafe_allow_html=True)