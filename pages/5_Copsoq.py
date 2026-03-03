# =============================================================================
# app.py — fichier unique fusionnant config.py, preprocessing.py,
#           data_loader.py et l'application Streamlit principale.
# =============================================================================

from pathlib import Path
import base64
import io
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from numbers import Real

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st
import streamlit.components.v1 as components


# =============================================================================
# CONFIG (anciennement config.py)
# =============================================================================

QUESTION_TEXT_MAP = {
    "Q1": "Prenez-vous du retard dans votre travail ?",
    "Q2": "Disposez-vous d'un temps suffisant pour accomplir vos taches professionnelles ?",
    "Q3": "Travaillez-vous a une cadence elevee tout au long de la journee ?",
    "Q4": "Est-il necessaire de maintenir un rythme soutenu au travail ?",
    "Q5": "Durant votre travail, devez-vous avoir l'oeil sur beaucoup de choses ?",
    "Q6": "Votre travail exige-t-il que vous vous souveniez de beaucoup de choses ?",
    "Q7": "Au travail, etes-vous informe(e) suffisamment a l'avance des decisions importantes, des changements ou de projets futurs ?",
    "Q8": "Recevez-vous toutes les informations dont vous avez besoin pour bien faire votre travail ?",
    "Q9": "Votre travail est-il reconnu et apprecie par le management ?",
    "Q10": "Etes-vous traite(e) equitablement au travail ?",
    "Q11": "Les conflits sont-ils resolus de maniere equitable ?",
    "Q12": "Le travail est-il reparti equitablement ?",
    "Q13": "Votre travail a-t-il des objectifs clairs ?",
    "Q14": "Savez-vous exactement ce que l'on attend de vous au travail ?",
    "Q15": "Au travail, etes-vous soumis(e) a des demandes contradictoires ?",
    "Q16": "Devez-vous parfois faire des choses qui auraient du etre faites autrement ?",
    "Q17": "Dans quelle mesure diriez-vous que votre superieur(e) hierarchique accorde une grande priorite a la satisfaction au travail ?",
    "Q18": "Dans quelle mesure diriez-vous que votre superieur(e) hierarchique est competent(e) dans la planification du travail ?",
    "Q19": "A quelle frequence votre superieur(e) hierarchique est-il (elle) dispose(e) a vous ecouter au sujet de vos problemes au travail ?",
    "Q20": "A quelle frequence recevez-vous de l'aide et du soutien de votre superieur(e) hierarchique ?",
    "Q21": "Le management fait-il confiance aux salaries quant a leur capacite a bien faire leur travail ?",
    "Q22": "Pouvez-vous faire confiance aux informations venant du management ?",
    "Q23": "Y a-t-il une bonne cooperation entre les collegues au travail ?",
    "Q24": "Dans l'ensemble, les salaries se font-ils confiance entre eux ?",
    "Q25": "A quelle frequence recevez-vous de l'aide et du soutien de vos collegues ?",
    "Q26": "A quelle frequence vos collegues se montrent-ils a l'ecoute de vos problemes au travail ?",
    "Q27": "Avez-vous une grande marge de manoeuvre dans votre travail ?",
    "Q28": "Pouvez-vous intervenir sur la quantite de travail qui vous est attribuee ?",
    "Q29": "Votre travail necessite-t-il que vous preniez des initiatives ?",
    "Q30": "Votre travail vous donne-il la possibilite d'apprendre des choses nouvelles ?",
    "Q31": "En general, diriez-vous que votre sante est :",
    "Q32": "A quelle frequence avez-vous ete irritable ?",
    "Q33": "A quelle frequence avez-vous ete stresse(e) ?",
    "Q34": "A quelle frequence vous etes-vous senti(e) a bout de force ?",
    "Q35": "A quelle frequence avez-vous ete emotionnellement epuise(e) ?",
    "Q36": "Votre travail vous place-t-il dans des situations destabilisantes sur le plan emotionnel ?",
    "Q37": "Votre travail est-il eprouvant sur le plan emotionnel ?",
    "Q38": "Sentez-vous que votre travail vous prend tellement d'energie que cela a un impact negatif sur votre vie privee ?",
    "Q39": "Sentez-vous que votre travail vous prend tellement de temps que cela a un impact negatif sur votre vie privee ?",
    "Q40": "Etes-vous inquiet(ete) a l'idee de perdre votre emploi ?",
    "Q41": "Craignez-vous d'etre mute(e) a un autre poste de travail contre votre volonte ?",
    "Q42": "Votre travail a-t-il du sens pour vous ?",
    "Q43": "Avez-vous le sentiment que le travail que vous faites est important ?",
    "Q44": "Recommanderiez-vous a un ami proche de postuler sur un emploi dans votre entreprise ?",
    "Q45": "Pensez-vous que votre entreprise est d'une grande importance pour vous ?",
    "Q46": "A quel point etes-vous satisfait(e) de votre travail dans son ensemble, en prenant en consideration tous les aspects ?",
}

SUBDOMAINS = {
    "charge_travail": ["Q1", "Q2"],
    "rythme_travail": ["Q3", "Q4"],
    "exigences_cognitives": ["Q5", "Q6"],
    "previsibilite": ["Q7", "Q8"],
    "reconnaissance": ["Q9", "Q10"],
    "equite": ["Q11", "Q12"],
    "clarte_roles": ["Q13", "Q14"],
    "conflit_roles": ["Q15", "Q16"],
    "qualite_leadership_superieur_hierarchique": ["Q17", "Q18"],
    "soutien_social_superieur_hierarchique": ["Q19", "Q20"],
    "confiance_salaries_management": ["Q21", "Q22"],
    "confiance_collegues": ["Q23", "Q24"],
    "soutien_social_collegues": ["Q25", "Q26"],
    "marge_manoeuvre": ["Q27", "Q28"],
    "possibilites_epanouissement": ["Q29", "Q30"],
    "sante_auto_evaluee": ["Q31"],
    "stress": ["Q32", "Q33"],
    "epuisement": ["Q34", "Q35"],
    "exigence_emotionnelle": ["Q36", "Q37"],
    "conflit_famille_travail": ["Q38", "Q39"],
    "insecurite_professionnelle": ["Q40", "Q41"],
    "sens_travail": ["Q42", "Q43"],
    "engagement_entreprise": ["Q44", "Q45"],
    "satisfaction_travail": ["Q46"],
}

SUBDOMAINS_LABELS = {
    "Charge de travail": ["Q1", "Q2"],
    "Rythme travail": ["Q3", "Q4"],
    "Exigences cognitive": ["Q5", "Q6"],
    "Previsibilite": ["Q7", "Q8"],
    "Reconnaissance": ["Q9", "Q10"],
    "Equite": ["Q11", "Q12"],
    "Clarte des roles": ["Q13", "Q14"],
    "Conflit de roles": ["Q15", "Q16"],
    "Qualite de leadership du superieur hierarchique": ["Q17", "Q18"],
    "Soutien social de la part du superieur hierarchique": ["Q19", "Q20"],
    "Confiance entre les salaries et le management": ["Q21", "Q22"],
    "Confiance entre les collegues": ["Q23", "Q24"],
    "Soutien social entre les collegues": ["Q25", "Q26"],
    "Marge de manoeuvre": ["Q27", "Q28"],
    "Possibilites d'epanouissement": ["Q29", "Q30"],
    "Sante auto evaluee": ["Q31"],
    "Stress": ["Q32", "Q33"],
    "Epuisement": ["Q34", "Q35"],
    "Exigence emotionnelle": ["Q36", "Q37"],
    "Conflit famille-travail": ["Q38", "Q39"],
    "Insecurite Professionnelle": ["Q40", "Q41"],
    "Sens du travail": ["Q42", "Q43"],
    "Engagement dans l'entreprise": ["Q44", "Q45"],
    "Satisfaction au travail": ["Q46"],
}


# =============================================================================
# PREPROCESSING (anciennement preprocessing.py)
# =============================================================================

IMC_BINS = [0, 18.5, 25, 30, 35, 40, float("inf")]
IMC_LABELS = [
    "Insuffisance ponderale",
    "Corpulence normale",
    "Surpoids",
    "Obesite moderee",
    "Obesite severe",
    "Obesite morbide",
]


def _pp_normalize_text(text: str) -> str:
    """Normalisation interne au module preprocessing."""
    text = str(text).strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _find_by_patterns(columns: list, patterns: list) -> str | None:
    for col in columns:
        normalized_col = _pp_normalize_text(col)
        for pattern in patterns:
            if re.search(pattern, normalized_col):
                return col
    return None


def _find_age_numeric_col(df: "pd.DataFrame") -> "str | None":
    """
    Cherche la colonne Age numérique en excluant toute colonne contenant 'tranche'.
    Retourne le nom de la colonne si elle contient des valeurs numériques, sinon None.
    Gère aussi le cas où work_df[col] retourne un DataFrame (colonnes en doublon).
    """
    for col in df.columns:
        col_norm = _pp_normalize_text(col)
        # Exclure les colonnes tranche d'age, tranche anciennete, etc.
        if "tranche" in col_norm:
            continue
        if re.search(r"\bage\b", col_norm):
            series = df[col]
            # Sécurité : si doublon de colonnes, prendre la première
            if isinstance(series, pd.DataFrame):
                series = series.iloc[:, 0]
            vals = pd.to_numeric(series, errors="coerce")
            if not vals.dropna().empty:
                return col
    return None


def _find_closest_column(columns: list, target: str, min_score: float = 0.6) -> str | None:
    if not columns:
        return None
    normalized_target = _pp_normalize_text(target)
    best_col = None
    best_score = -1.0
    for col in columns:
        score = SequenceMatcher(None, normalized_target, _pp_normalize_text(col)).ratio()
        if score > best_score:
            best_score = score
            best_col = col
    if best_col is None or best_score < min_score:
        return None
    return best_col


def add_demographic_derived_columns(df: pd.DataFrame) -> tuple:
    work_df = df.copy()
    ops: list = []
    cols = list(work_df.columns)

    age_col = _find_age_numeric_col(work_df)
    tranche_age_col = _find_by_patterns(cols, [r"tranche.*age"])
    if age_col is not None and "Tranche d'age" not in work_df.columns and tranche_age_col is None:
        age_vals = pd.to_numeric(work_df[age_col], errors="coerce")
        work_df["Tranche d'age"] = pd.cut(
            age_vals,
            bins=[0, 20, 30, 40, 50, 60, float("inf")],
            labels=["-20", "20-30", "31-40", "41-50", "51-60", "60+"],
            include_lowest=True,
        )
        ops.append(f"Tranche d'age creee depuis: {age_col}")
    elif "Tranche d'age" in work_df.columns:
        ops.append("Tranche d'age existante conservee et utilisee")
    elif tranche_age_col is not None:
        work_df["Tranche d'age"] = work_df[tranche_age_col]
        ops.append(f"Tranche d'age existante detectee et alignee depuis: {tranche_age_col}")
    else:
        ops.append("Tranche d'age: colonnes age/tranche d'age non trouvees")

    anciennete_col = _find_by_patterns(cols, [r"anciennete", r"anciennet"])
    if "Tranche anciennete" in work_df.columns:
        ops.append("Tranche anciennete existante conservee")
    elif anciennete_col is not None:
        anc_vals = pd.to_numeric(work_df[anciennete_col], errors="coerce")
        work_df["Tranche anciennete"] = pd.cut(
            anc_vals,
            bins=[0, 2, 5, 10, 20, float("inf")],
            labels=["0-2", "3-5", "6-10", "11-20", ">21"],
            include_lowest=True,
        )
        ops.append(f"Tranche anciennete creee depuis: {anciennete_col}")
    else:
        ops.append("Tranche anciennete: colonne anciennete non trouvee")

    imc_col = _find_by_patterns(cols, [r"\bimc\b"])
    if imc_col is not None and imc_col in work_df.columns:
        work_df = work_df.drop(columns=[imc_col])
        ops.append(f"IMC existant supprime: {imc_col}")

    poids_col = _find_by_patterns(cols, [r"\bpoids\b"])
    taille_col = _find_closest_column(cols, "Taille (cm)") or _find_by_patterns(cols, [r"\btaille\b"])
    if poids_col is not None and taille_col is not None:
        poids_vals = pd.to_numeric(work_df[poids_col], errors="coerce")
        taille_vals = pd.to_numeric(work_df[taille_col], errors="coerce")
        taille_positive = taille_vals[taille_vals > 0]
        if not taille_positive.empty and float(taille_positive.median()) > 3:
            taille_m = taille_vals / 100.0
        else:
            taille_m = taille_vals
        imc_vals = poids_vals / (taille_m ** 2)
        imc_vals = imc_vals.replace([float("inf"), float("-inf")], np.nan)
        work_df["IMC"] = imc_vals
        work_df["Categorie IMC"] = pd.cut(
            work_df["IMC"],
            bins=[0, 18.5, 25, 30, 200],
            labels=["Maigreur", "Normal", "Surpoids", "Obesite"],
            include_lowest=True,
        )
        ops.append(f"IMC/Categorie IMC calcules depuis: poids={poids_col}, taille={taille_col}")
    else:
        ops.append("IMC/Categorie IMC: colonnes poids/taille non trouvees")

    return work_df, ops


def clean_common_variables(
    df: pd.DataFrame,
    drop_first_col: bool = False,
    drop_indices: list | None = None,
    fill_marital: bool = True,
    missing_threshold: float = 0.5,
) -> tuple:
    """
    Nettoyage automatique des variables communes d'un DataFrame COPSOQ.
    Retourne (df_nettoyé, cleaning_log).
    """
    cleaned_df = df.copy()
    ops = []
    removed_columns_manual: list = []
    removed_columns_missing: list = []

    # --- Suppression des colonnes d'identification personnelle (PII) ---
    _PII_PATTERNS = [
        r"\bnom\b",
        r"\bprenom",
        r"\be[- ]?mail\b",
        r"\bmail\b",
        r"\bcourriel\b",
        r"\btelephone\b",
        r"\btel\b",
        r"\bphone\b",
        r"\bcommentaire",
        r"\bobservation",
        r"\bremarque",
        r"\bnumero\b",
        r"\bidentifiant\b",
        r"\bid\b",
    ]
    # Patterns vérifiés sur le nom brut (avant normalisation) — ex: "#", "Unnamed: 0"
    _PII_RAW_PATTERNS = [
        r"^#\s*$",
        r"^unnamed",
    ]
    _pii_dropped: list = []
    for col in list(cleaned_df.columns):
        col_raw = str(col).strip()
        col_norm = _pp_normalize_text(col)
        matched = any(re.search(pat, col_norm) for pat in _PII_PATTERNS)
        if not matched:
            matched = any(re.search(pat, col_raw, re.IGNORECASE) for pat in _PII_RAW_PATTERNS)
        if matched:
            cleaned_df = cleaned_df.drop(columns=[col])
            _pii_dropped.append(str(col))
    if _pii_dropped:
        ops.append(
            f"Colonnes PII supprimees ({len(_pii_dropped)}): "
            + ", ".join(_pii_dropped)
        )

    if drop_first_col and cleaned_df.shape[1] > 1:
        first_col = cleaned_df.columns[0]
        cleaned_df = cleaned_df.iloc[:, 1:]
        removed_columns_manual.append(str(first_col))
        ops.append(f"Premiere colonne supprimee: {first_col}")

    if drop_indices:
        valid_drop = [i for i in drop_indices if i in cleaned_df.index]
        if valid_drop:
            cleaned_df = cleaned_df.drop(valid_drop)
            ops.append(f"Lignes supprimees: {valid_drop}")

    if fill_marital:
        marital_col = _find_by_patterns(list(cleaned_df.columns), [r"situation", r"mari"])
        if marital_col is not None:
            cleaned_df[marital_col] = cleaned_df[marital_col].fillna("Non renseigne")
            ops.append(f"Situation matrimoniale completee: {marital_col}")

    missing_ratio = cleaned_df.isna().mean()
    cols_to_drop = missing_ratio[missing_ratio > missing_threshold].index.tolist()
    if cols_to_drop:
        cleaned_df = cleaned_df.drop(columns=cols_to_drop)
    removed_columns_missing = [str(c) for c in cols_to_drop]
    if cols_to_drop:
        ops.append(
            "Colonnes > "
            + f"{missing_threshold * 100:.0f}% manquants supprimees: "
            + ", ".join(str(c) for c in cols_to_drop)
        )

    # --- Tranche d'age ---
    _TRANCHE_AGE_CANONICAL = "Tranche d'age"
    _TRANCHE_AGE_NORM_VARIANTS = {"tranche d age", "tranche age", "tranche d ages"}

    age_col = _find_age_numeric_col(cleaned_df)

    # Collecter TOUTES les colonnes qui sont des variantes de tranche d'age
    _tranche_age_all = [
        _col for _col in cleaned_df.columns
        if _pp_normalize_text(str(_col)) in _TRANCHE_AGE_NORM_VARIANTS
    ]

    if age_col is not None and not _tranche_age_all:
        # Aucune tranche existante : on la crée depuis Age numérique
        age_vals = pd.to_numeric(cleaned_df[age_col], errors="coerce")
        cleaned_df[_TRANCHE_AGE_CANONICAL] = pd.cut(
            age_vals,
            bins=[0, 20, 30, 40, 50, 60, float("inf")],
            labels=["-20", "20-30", "31-40", "41-50", "51-60", "60+"],
            include_lowest=True,
        )
        ops.append(f"Tranche d'age creee depuis: {age_col}")
    elif _tranche_age_all:
        # Garder uniquement la première variante trouvée, supprimer les autres
        _keep = _tranche_age_all[0]
        _to_drop_tranche = [c for c in _tranche_age_all[1:]]
        if _to_drop_tranche:
            cleaned_df = cleaned_df.drop(columns=_to_drop_tranche)
            ops.append(f"Doublons Tranche d'age supprimes: {_to_drop_tranche}")
        # Renommer en canonique si nécessaire
        if _keep != _TRANCHE_AGE_CANONICAL:
            cleaned_df = cleaned_df.rename(columns={_keep: _TRANCHE_AGE_CANONICAL})
            ops.append(f"Tranche d'age renommee depuis: {_keep}")
        else:
            ops.append("Tranche d'age existante conservee")
    else:
        ops.append("Tranche d'age: colonne Age numerique et tranche d'age non trouvees")

    # --- Tranche ancienneté ---
    _TRANCHE_ANC_CANONICAL = "Tranche anciennete"

    anciennete_col = _find_by_patterns(list(cleaned_df.columns), [r"anciennete", r"anciennet"])
    # Collecter TOUTES les variantes de tranche anciennete
    _tranche_anc_all = [
        _col for _col in cleaned_df.columns
        if _pp_normalize_text(str(_col)) in {"tranche anciennete"}
    ]
    _tranche_anc_existing = _tranche_anc_all[0] if _tranche_anc_all else None
    # Supprimer les doublons éventuels
    if len(_tranche_anc_all) > 1:
        cleaned_df = cleaned_df.drop(columns=_tranche_anc_all[1:])
        ops.append(f"Doublons Tranche anciennete supprimes: {_tranche_anc_all[1:]}")

    if _tranche_anc_existing is not None:
        if _tranche_anc_existing != _TRANCHE_ANC_CANONICAL:
            cleaned_df = cleaned_df.rename(columns={_tranche_anc_existing: _TRANCHE_ANC_CANONICAL})
            ops.append(f"Tranche anciennete renommee depuis: {_tranche_anc_existing}")
        else:
            ops.append("Tranche anciennete existante conservee")
    elif anciennete_col is not None:
        anc_vals = pd.to_numeric(cleaned_df[anciennete_col], errors="coerce")
        cleaned_df[_TRANCHE_ANC_CANONICAL] = pd.cut(
            anc_vals,
            bins=[0, 2, 5, 10, 20, float("inf")],
            labels=["0-2", "3-5", "6-10", "11-20", "21+"],
            include_lowest=True,
        )
        ops.append(f"Tranche anciennete creee depuis: {anciennete_col}")
    else:
        ops.append("Tranche anciennete: colonne anciennete non trouvee")

    # --- IMC ---
    imc_col = _find_by_patterns(list(cleaned_df.columns), [r"\bimc\b"])
    if imc_col is not None:
        cleaned_df = cleaned_df.drop(columns=[imc_col])
        removed_columns_manual.append(str(imc_col))
        ops.append(f"IMC existant supprime: {imc_col}")

    poids_col = _find_by_patterns(list(cleaned_df.columns), [r"\bpoids\b"])
    taille_col = _find_by_patterns(list(cleaned_df.columns), [r"\btaille\b"])
    if poids_col is not None and taille_col is not None:
        poids_vals = pd.to_numeric(cleaned_df[poids_col], errors="coerce")
        taille_vals = pd.to_numeric(cleaned_df[taille_col], errors="coerce")
        taille_positive = taille_vals[taille_vals > 0]
        if not taille_positive.empty and float(taille_positive.median()) > 3:
            taille_m = taille_vals / 100.0
        else:
            taille_m = taille_vals
        imc_vals = poids_vals / (taille_m ** 2)
        imc_vals = imc_vals.replace([float("inf"), float("-inf")], np.nan)
        cleaned_df["IMC"] = imc_vals
        cleaned_df["Categorie IMC"] = pd.cut(
            cleaned_df["IMC"],
            bins=[0, 18.5, 25, 30, 200],
            labels=["Maigreur", "Normal", "Surpoids", "Obesite"],
            include_lowest=True,
        )
        ops.append(f"IMC/Categorie IMC calcules depuis: poids={poids_col}, taille={taille_col}")

    # --- Remplissage "Non renseigne" pour toutes les colonnes catégorielles/texte restantes ---
    # On exclut les colonnes numériques pures (Age, IMC, Q1-Q46, etc.)
    _qx_pattern = re.compile(r"^Q\d+$", re.IGNORECASE)
    _numeric_cols_to_skip = set()
    for col in cleaned_df.columns:
        if _qx_pattern.match(str(col)):
            _numeric_cols_to_skip.add(col)
        elif pd.api.types.is_numeric_dtype(cleaned_df[col]):
            _numeric_cols_to_skip.add(col)

    _categorical_filled: list = []
    for col in cleaned_df.columns:
        if col in _numeric_cols_to_skip:
            continue
        # Forcer un scalaire Python natif pour éviter ValueError sur CategoricalDtype
        try:
            _has_na = cleaned_df[col].isna().values.any()
        except Exception:
            _has_na = cleaned_df[col].isnull().sum() > 0
        if _has_na:
            if hasattr(cleaned_df[col], "cat"):
                if "Non renseigne" not in cleaned_df[col].cat.categories:
                    cleaned_df[col] = cleaned_df[col].cat.add_categories("Non renseigne")
            cleaned_df[col] = cleaned_df[col].fillna("Non renseigne")
            _categorical_filled.append(str(col))

    if _categorical_filled:
        ops.append(
            f"Remplissage 'Non renseigne' ({len(_categorical_filled)} colonne(s)): "
            + ", ".join(_categorical_filled)
        )

    cleaning_log = "Nettoyage COPSOQ applique:\n- " + "\n- ".join(ops) if ops else "Aucune operation appliquee."
    cleaned_df.attrs["cleaning_log"] = cleaning_log
    return cleaned_df, cleaning_log


def build_df_qx(df: pd.DataFrame, threshold: float = 0.65) -> pd.DataFrame:
    source_df = df.copy()
    if "Categorie IMC" not in source_df.columns:
        source_df, _ = add_demographic_derived_columns(source_df)

    source_cols = list(source_df.columns)
    normalized_cols = {col: _pp_normalize_text(col) for col in source_cols}
    available_cols = set(source_cols)
    qx_matches: dict = {}

    for qx, question_text in QUESTION_TEXT_MAP.items():
        target = _pp_normalize_text(question_text)
        best_col = None
        best_score = -1.0

        for col in list(available_cols):
            score = SequenceMatcher(None, target, normalized_cols[col]).ratio()
            if score > best_score:
                best_score = score
                best_col = col

        if best_col is not None and best_score >= threshold:
            qx_matches[qx] = best_col
            available_cols.remove(best_col)

    rename_map = {src_col: qx for qx, src_col in qx_matches.items() if src_col != qx}
    df_qx = source_df.rename(columns=rename_map)

    for qx in sorted(qx_matches.keys(), key=lambda item: int(item[1:])):
        if qx in df_qx.columns:
            df_qx[qx] = pd.to_numeric(df_qx[qx], errors="coerce")

    return normalize_qx_columns_0_100(df_qx)


def normalize_qx_columns_0_100(df_qx: pd.DataFrame, min_scale: float = 1.0, max_scale: float = 5.0) -> pd.DataFrame:
    normalized_df = df_qx.copy()
    if max_scale <= min_scale:
        raise ValueError("max_scale doit etre strictement superieur a min_scale.")

    qx_cols = [col for col in normalized_df.columns if re.match(r"^Q\d+$", str(col), flags=re.IGNORECASE)]
    if not qx_cols:
        return normalized_df

    span = max_scale - min_scale
    for col in qx_cols:
        vals = pd.to_numeric(normalized_df[col], errors="coerce")
        normalized_df[col] = (((vals - min_scale) / span) * 100).clip(lower=0, upper=100)
    return normalized_df


def _yes_rate(series: pd.Series) -> float:
    clean = series.astype(str).str.strip().str.lower()
    if clean.empty:
        return 0.0
    return float((clean == "oui").mean() * 100)


def add_subdomain_scores(df: pd.DataFrame, subdomains: dict = SUBDOMAINS) -> pd.DataFrame:
    scored_df = df.copy()
    for subdomain, questions in subdomains.items():
        existing_questions = [q for q in questions if q in scored_df.columns]
        if not existing_questions:
            scored_df[subdomain] = pd.NA
            continue
        scored_df[subdomain] = scored_df[existing_questions].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    return scored_df


def build_subdomain_values_dict(df_qx: pd.DataFrame, subdomains: dict = SUBDOMAINS_LABELS) -> dict:
    result: dict = {}
    for name, questions in subdomains.items():
        available = [q for q in questions if q in df_qx.columns]
        if not available:
            result[name] = pd.Series([pd.NA] * len(df_qx), index=df_qx.index, dtype="object")
            continue
        vals = df_qx[available].apply(pd.to_numeric, errors="coerce").mean(axis=1)
        result[name] = vals
    return result


def build_global_subdomain_means_dict(df_qx: pd.DataFrame, subdomains: dict = SUBDOMAINS_LABELS) -> dict:
    result: dict = {}
    for name, questions in subdomains.items():
        available = [q for q in questions if q in df_qx.columns]
        if not available:
            result[name] = float("nan")
            continue
        row_scores = df_qx[available].apply(pd.to_numeric, errors="coerce").mean(axis=1)
        result[name] = float(row_scores.mean(skipna=True))
    return result


def build_df_scores(df_qx: pd.DataFrame, subdomains: dict = SUBDOMAINS_LABELS) -> pd.DataFrame:
    df_scores = df_qx.copy()
    for subdomain_name, questions in subdomains.items():
        available = [q for q in questions if q in df_scores.columns]
        if not available:
            df_scores[subdomain_name] = pd.NA
            continue
        df_scores[subdomain_name] = df_scores[available].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    return df_scores


def compute_subdomain_means(df: pd.DataFrame, subdomains: dict = SUBDOMAINS) -> pd.Series:
    scored_df = add_subdomain_scores(df, subdomains=subdomains)
    return scored_df[list(subdomains.keys())].mean(axis=0, skipna=True)


def build_general_indicators(df: pd.DataFrame) -> dict:
    work_df = df.copy()
    cols = list(work_df.columns)
    genre_col = _find_closest_column(cols, "Genre") or _find_by_patterns(cols, [r"\bgenre\b", r"\bsexe\b"])
    if genre_col is not None:
        genre = work_df[genre_col].astype(str).str.strip().str.lower()
    else:
        genre = pd.Series([""] * len(work_df), index=work_df.index)

    total = int(len(work_df))
    nb_hommes = int((genre == "homme").sum())
    nb_femmes = int((genre == "femme").sum())
    # Calculer la médiane de l'âge si la colonne d'âge existe
    age_col = _find_age_numeric_col(work_df)
    if age_col is not None:
        series_age = work_df[age_col]
        if isinstance(series_age, pd.DataFrame):
            series_age = series_age.iloc[:, 0]
        age_vals = pd.to_numeric(series_age, errors="coerce")
        age_median = age_vals.median(skipna=True)
        if not pd.isna(age_median):
            age_moyen = age_median  # Renommez cette variable en age_median pour plus de clarté
        else:
            age_moyen = "N/A"
    elif "Tranche d'age" in work_df.columns:
        # Fallback sur la tranche d'âge modale si l'âge n'est pas disponible
        tranche_mode = work_df["Tranche d'age"].dropna().mode()
        age_moyen = str(tranche_mode.iloc[0]) if not tranche_mode.empty else "N/A"
    else:
        age_moyen = "N/A"

    poids_col = _find_closest_column(cols, "Poids (kg)") or _find_by_patterns(cols, [r"\bpoids\b"])
    taille_col = _find_closest_column(cols, "Taille (cm)") or _find_by_patterns(cols, [r"\btaille\b"])

    if poids_col is not None and taille_col is not None:
        poids_vals = pd.to_numeric(work_df[poids_col], errors="coerce")
        taille_vals = pd.to_numeric(work_df[taille_col], errors="coerce")
        taille_positive = taille_vals[taille_vals > 0]
        if not taille_positive.empty and float(taille_positive.median()) > 3:
            taille_m = taille_vals / 100.0
        else:
            taille_m = taille_vals
        imc = poids_vals / (taille_m ** 2)
        imc = imc.replace([float("inf"), float("-inf")], np.nan)
        work_df["IMC"] = imc
        work_df["Categorie IMC"] = pd.cut(
            work_df["IMC"],
            bins=IMC_BINS,
            labels=IMC_LABELS,
            right=False,
        )
    else:
        work_df["IMC"] = np.nan
        work_df["Categorie IMC"] = pd.Series([pd.NA] * len(work_df), index=work_df.index)

    situation_col = (
        _find_closest_column(cols, "Situation matrimoniale")
        or _find_by_patterns(cols, [r"situation.*matrimon", r"matrimon"])
    )
    if situation_col is not None:
        situation = (
            work_df[situation_col]
            .value_counts(dropna=False)
            .rename_axis("Situation matrimoniale")
            .reset_index(name="Effectif")
        )
        situation["Pourcentage"] = (situation["Effectif"] / total * 100).round(1)
    else:
        situation = pd.DataFrame(
            [{"Situation matrimoniale": "N/A", "Effectif": 0, "Pourcentage": 0.0}]
        )

    alcool_col = (
        _find_closest_column(cols, "Consommation reguliere alcool")
        or _find_by_patterns(cols, [r"consommation.*alcool", r"alcool"])
    )
    tabac_col = _find_closest_column(cols, "Tabagisme") or _find_by_patterns(cols, [r"tabag", r"fumeur"])
    sport_col = (
        _find_closest_column(cols, "Pratique reguliere sport")
        or _find_by_patterns(cols, [r"pratique.*sport", r"\bsport\b"])
    )

    alcool_series = work_df[alcool_col] if alcool_col is not None else pd.Series(dtype="object")
    tabac_series = work_df[tabac_col] if tabac_col is not None else pd.Series(dtype="object")
    sport_series = work_df[sport_col] if sport_col is not None else pd.Series(dtype="object")

    imc_distribution = (
        work_df["Categorie IMC"]
        .value_counts(dropna=False)
        .rename_axis("Categorie IMC")
        .reset_index(name="Effectif")
    )
    imc_distribution["Pourcentage"] = (imc_distribution["Effectif"] / total * 100).round(1)

    return {
        "total_effectif": total,
        "nombre_hommes": nb_hommes,
        "nombre_femmes": nb_femmes,
        "age_moyen": age_moyen,
        "taux_alcool": _yes_rate(alcool_series),
        "taux_fumeur": _yes_rate(tabac_series),
        "taux_sport": _yes_rate(sport_series),
        "situation_matrimoniale": situation,
        "imc_distribution": imc_distribution,
    }


# =============================================================================
# DATA LOADER — à partir d'un fichier uploadé (BytesIO)
# =============================================================================

@st.cache_data(show_spinner=False)
def load_data_from_bytes(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """Charge un DataFrame depuis les bytes d'un fichier Excel ou CSV uploadé."""
    buf = io.BytesIO(file_bytes)
    if file_name.lower().endswith(".csv"):
        df = pd.read_csv(buf, sep=None, engine="python")
    else:
        df = pd.read_excel(buf)
    df.columns = [str(col).strip() for col in df.columns]
    df, _ = add_demographic_derived_columns(df)
    return df


@st.cache_data(show_spinner=False)
def load_data_qx_from_bytes(file_bytes: bytes, file_name: str, threshold: float = 0.65) -> pd.DataFrame:
    df = load_data_from_bytes(file_bytes, file_name)
    return build_df_qx(df, threshold=threshold)


@st.cache_data(show_spinner=False)
def load_data_scores_from_bytes(file_bytes: bytes, file_name: str, threshold: float = 0.65) -> pd.DataFrame:
    df_qx = load_data_qx_from_bytes(file_bytes, file_name, threshold=threshold)
    return build_df_scores(df_qx)


# =============================================================================
# APPLICATION STREAMLIT (anciennement app.py)
# =============================================================================

def load_css() -> None:
    css_path = next(
        (
            Path(p) / "assets" / "style.css"
            for p in [Path.cwd(), Path(__file__).parent, *map(Path, sys.path)]
            if (Path(p) / "assets" / "style.css").exists()
        ),
        None,
    )
    if css_path is not None:
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)


def load_js() -> None:
    js_path = next(
        (
            Path(p) / "assets" / "animations.js"
            for p in [Path.cwd(), Path(__file__).parent, *map(Path, sys.path)]
            if (Path(p) / "assets" / "animations.js").exists()
        ),
        None,
    )
    if js_path is not None:
        js = js_path.read_text(encoding="utf-8")
        components.html(f"<script>\n{js}\n</script>", height=0)


def find_asset(filename: str) -> Path | None:
    """Cherche un fichier asset dans cwd, __file__.parent, et sys.path."""
    for p in [Path.cwd(), Path(__file__).parent, *map(Path, sys.path)]:
        asset_path = Path(p) / "assets" / filename
        if asset_path.exists():
            return asset_path
    return None


def image_as_base64(path: Path | str) -> str:
    if isinstance(path, str):
        # Si c'est un nom de fichier, le chercher dans les assets
        found_path = find_asset(path)
        if found_path is None:
            return ""
        path = found_path
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def _to_numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return series
    return pd.to_numeric(series.astype(str).str.replace(",", ".", regex=False), errors="coerce")


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _fuzzy_find_column(source_df: pd.DataFrame, candidates: list, min_score: float = 0.76) -> str | None:
    if source_df.empty or not candidates:
        return None
    columns = list(source_df.columns)
    normalized_cols = {_normalize_text(col): col for col in columns}

    for candidate in candidates:
        c_norm = _normalize_text(candidate)
        if c_norm in normalized_cols:
            return normalized_cols[c_norm]

    best_col = None
    best_score = 0.0
    for col in columns:
        col_norm = _normalize_text(col)
        for candidate in candidates:
            c_norm = _normalize_text(candidate)
            contains_bonus = 0.12 if c_norm in col_norm or col_norm in c_norm else 0.0
            score = SequenceMatcher(None, col_norm, c_norm).ratio() + contains_bonus
            if score > best_score:
                best_score = score
                best_col = col
    return best_col if best_score >= min_score else None


def _ensure_tranche_anciennete(source_df: pd.DataFrame) -> pd.DataFrame:
    out = source_df.copy()
    existing = _fuzzy_find_column(out, ["Tranche anciennete", "Tranche ancienneté"])
    if existing is not None:
        return out

    anciennete_col = _fuzzy_find_column(
        out,
        ["Anciennete", "Ancienneté", "anciennete annees", "anciennete en annees"],
    )
    if anciennete_col is None:
        return out

    anc_vals = pd.to_numeric(out[anciennete_col], errors="coerce")
    if anc_vals.dropna().empty:
        return out

    out["Tranche anciennete"] = pd.cut(
        anc_vals,
        bins=[0, 2, 5, 10, 20, float("inf")],
        labels=["0-2", "3-5", "6-10", "11-20", "21+"],
        include_lowest=True,
    )
    return out


AGE_MODALITY_ORDER = ["-20", "20-30", "31-40", "41-50", "51-60", "60+"]


def _is_age_tranche_column(col_name: str) -> bool:
    normalized = str(col_name).strip().lower().replace(" ", "")
    return normalized in {"tranched'age", "trancheage", "tranchedage"}


def _age_sort_key(label: str) -> tuple:
    value = str(label).strip().replace(" ", "")
    if value in AGE_MODALITY_ORDER:
        return (0, f"{AGE_MODALITY_ORDER.index(value):02d}")
    return (1, value)


def _format_df_for_display(source_df: pd.DataFrame, decimals: int = 2) -> pd.DataFrame:
    out = source_df.copy()
    numeric_cols = out.select_dtypes(include=["number"]).columns
    if len(numeric_cols) > 0:
        out[numeric_cols] = out[numeric_cols].round(decimals)
    return out


def _categorize_to_four_levels(series: pd.Series) -> pd.Series:
    """Categorize numeric series into 4 levels using quartiles.

    Labels: 'Tres faible', 'Faible', 'Fort', 'Tres fort'.
    """
    num = _to_numeric(series)
    if num.dropna().empty:
        return pd.Series([pd.NA] * len(series), index=series.index)
    q25 = num.quantile(0.25)
    q50 = num.quantile(0.50)
    q75 = num.quantile(0.75)

    def _classify(value: float) -> object:
        if pd.isna(value):
            return pd.NA
        if value <= q25:
            return "Tres faible"
        if value <= q50:
            return "Faible"
        if value <= q75:
            return "Fort"
        return "Tres fort"

    return num.apply(_classify)


def _get_univariate_stats(series: pd.Series, n_rows: int, col_name: str | None = None) -> tuple:
    if pd.api.types.is_numeric_dtype(series):
        desc = series.describe()
        stats = {
            "mean": float(desc.get("mean", float("nan"))),
            "std": float(desc.get("std", float("nan"))),
            "min": float(desc.get("min", float("nan"))),
            "25%": float(desc.get("25%", float("nan"))),
            "median": float(desc.get("50%", float("nan"))),
            "75%": float(desc.get("75%", float("nan"))),
            "max": float(desc.get("max", float("nan"))),
        }
    else:
        s = series.astype("object")
        mode = s.mode(dropna=True)
        mode_value = mode.iloc[0] if not mode.empty else "Aucun"
        value_counts = s.value_counts(dropna=True)
        freq_mode = int(value_counts.max()) if not value_counts.empty else 0
        stats = {
            "Unique": int(s.nunique(dropna=True)),
            "Mode": str(mode_value),
            "Freq Mode": int(freq_mode),
            "% Mode": float(round((freq_mode / n_rows) * 100, 2) if n_rows else float("nan")),
        }

    freq = series.value_counts(dropna=False, normalize=True).mul(100).rename("Frequence (%)").reset_index()
    freq.columns = ["Categorie", "Frequence (%)"]
    freq["Categorie"] = freq["Categorie"].astype(str).replace("nan", "Valeurs manquantes")
    if col_name and _is_age_tranche_column(col_name):
        freq = freq.sort_values(by="Categorie", key=lambda s: s.map(_age_sort_key)).reset_index(drop=True)
    return stats, freq


def _build_univariate_figure(source_df: pd.DataFrame, col: str):
    s = source_df[col]
    if pd.api.types.is_numeric_dtype(s) and s.nunique(dropna=True) > 5:
        fig, ax = plt.subplots(figsize=(7, 4.2))
        sns.histplot(s.dropna(), kde=True, ax=ax, color="#2563eb")
        ax.set_title(f"Histogramme - {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequence")
        fig.tight_layout()
        return fig

    fig, ax = plt.subplots(figsize=(8, 6))
    counts = s.dropna().astype(str).value_counts()
    if counts.empty:
        ax.text(0.5, 0.5, "Aucune donnee", ha="center", va="center")
        ax.axis("off")
        fig.tight_layout()
        return fig

    if _is_age_tranche_column(col):
        ordered_labels = [label for label in AGE_MODALITY_ORDER if label in counts.index]
        extra_labels = [label for label in counts.index if label not in AGE_MODALITY_ORDER]
        labels = ordered_labels + sorted(extra_labels)
        values = [int(counts[label]) for label in labels]
    else:
        top = counts.head(5)
        labels = top.index.astype(str).tolist()
        values = top.values.tolist()
    total = sum(values)
    small_pct_threshold = 6.0

    def _pct_label(pct: float) -> str:
        return f"{pct:.2f}%" if pct >= small_pct_threshold else ""

    wedges, _, autotexts = ax.pie(
        values,
        labels=None,
        autopct=_pct_label,
        startangle=90,
        pctdistance=0.70,
        textprops={"fontsize": 10, "fontweight": "bold"},
    )
    for i, text in enumerate(autotexts):
        pct = (values[i] / total) * 100 if total else 0
        if pct >= small_pct_threshold:
            text.set_text(f"{labels[i]}\n{pct:.2f}%")
            text.set_fontsize(9)
        text.set_color("white")

    small_slices = []
    for i, wedge in enumerate(wedges):
        pct = (values[i] / total) * 100 if total else 0
        if pct >= small_pct_threshold:
            continue
        angle = (wedge.theta1 + wedge.theta2) / 2.0
        x = float(np.cos(np.deg2rad(angle)))
        y = float(np.sin(np.deg2rad(angle)))
        small_slices.append({"idx": i, "x": x, "y": y, "pct": pct})

    def _spread_side(points: list, min_gap: float = 0.20) -> dict:
        if not points:
            return {}
        y_min, y_max = -1.18, 1.18
        ordered = sorted(points, key=lambda p: p["y"])
        ys = []
        prev = y_min - min_gap
        for p in ordered:
            y_value = max(p["y"] * 1.12, prev + min_gap)
            ys.append(y_value)
            prev = y_value
        overflow = ys[-1] - y_max
        if overflow > 0:
            ys = [y - overflow for y in ys]
            if ys[0] < y_min:
                shift = y_min - ys[0]
                ys = [y + shift for y in ys]
        return {p["idx"]: y for p, y in zip(ordered, ys)}

    right_side = [p for p in small_slices if p["x"] >= 0]
    left_side = [p for p in small_slices if p["x"] < 0]
    y_text_map = {**_spread_side(right_side), **_spread_side(left_side)}

    for p in small_slices:
        i = p["idx"]
        x = p["x"]
        y = p["y"]
        pct = p["pct"]
        ax.annotate(
            f"{labels[i]} ({pct:.2f}%)",
            xy=(x * 1.0, y * 1.0),
            xytext=(0.5 * np.sign(x), y_text_map.get(i, 1.12 * y)),
            ha="left" if x >= 0 else "right",
            va="center",
            fontsize=9,
            fontweight="bold",
            color="#111827",
            arrowprops={"arrowstyle": "->", "color": "#6b7280", "lw": 1.0},
        )
    ax.legend(
        wedges,
        labels,
        title="Modalites",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
    )
    ax.set_title(f"Répartition - {col}")
    fig.tight_layout()
    return fig


def _fig_to_png_bytes(fig) -> bytes | None:
    try:
        if hasattr(fig, "to_image"):
            return fig.to_image(format="png")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0.25)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None


ORDER_LEVELS = ["Tres faible", "Faible", "Fort", "Tres fort"]

# Palette "risque normal" : Tres faible = bon (jaune clair) → Tres fort = mauvais (rouge)
# Utilisée quand un score ÉLEVÉ = MAUVAIS (ex: stress, charge de travail)
LEVEL_COLORS_RISK = {
    "Tres faible": "#4ADE80",   # vert
    "Faible":      "#FACC15",   # jaune
    "Fort":        "#FB923C",   # orange
    "Tres fort":   "#EF4444",   # rouge
}

# Palette "inversée" : Tres faible = mauvais (rouge) → Tres fort = bon (vert)
# Utilisée quand un score ÉLEVÉ = BON (ex: reconnaissance, autonomie, satisfaction)
LEVEL_COLORS_GOOD = {
    "Tres faible": "#EF4444",   # rouge
    "Faible":      "#FB923C",   # orange
    "Fort":        "#FACC15",   # jaune
    "Tres fort":   "#4ADE80",   # vert
}

# Compatibilité avec le reste du code (utilisé dans tab_croissement / bivariate)
LEVEL_COLORS = LEVEL_COLORS_RISK

# -----------------------------------------------------------------------------
# Polarité de couleur par sous-domaine (cat_col = f"{label}__Categorie")
# "inverted" = score élevé est bon → palette GOOD
# "normal"   = score élevé est mauvais → palette RISK
# -----------------------------------------------------------------------------
_SUBDOMAIN_POLARITY: dict[str, str] = {
    # --- Contraintes Quantitatives : score élevé = mauvais ---
    "Charge de travail":        "normal",
    "Rythme de travail":        "normal",
    "Exigences cognitive":      "normal",

    # --- Organisation et Leadership ---
    "Previsibilite":            "inverted",   # élevé = bien informé = bon
    "Reconnaissance":           "inverted",   # élevé = très reconnu = bon
    "Equite":                   "inverted",   # élevé = très équitable = bon
    "Clarte des roles":         "inverted",   # élevé = très clair = bon
    "Conflit de roles":         "normal",     # élevé = fort conflit = mauvais
    "Qualite de leadership du superieur hierarchique": "inverted",
    "Soutien social de la part du superieur hierarchique": "inverted",
    "Confiance entre les salaries et le management": "inverted",

    # --- Relations Horizontales ---
    "Confiance entre les collegues":             "inverted",
    "Soutien social de la part des collegues":   "inverted",

    # --- Autonomie ---
    "Marge de manoeuvre":              "inverted",
    "Possibilitee d'epanouissement":   "inverted",

    # --- Santé et Bien-être ---
    "Sante auto evaluee":      "inverted",   # score élevé = bonne santé = bon
    "Stress":                  "normal",
    "Epuisement":              "normal",
    "Exigence emotionnelle":   "normal",
    "Conflit famille-travail": "normal",
    "Insecurite professionnelle": "normal",

    # --- Vécu Professionnel ---
    "Sens du travail":              "inverted",
    "Engagement dans l'entreprise": "inverted",
    "Satisfaction au travail":      "inverted",
}


def _colors_for_subdomain(label: str) -> dict:
    """Retourne la palette de couleurs adaptée à la polarité du sous-domaine."""
    polarity = _SUBDOMAIN_POLARITY.get(label, "normal")
    return LEVEL_COLORS_GOOD if polarity == "inverted" else LEVEL_COLORS_RISK


RPS_DOMAINS_CFG = {
    "Contraintes Quantitatives": [
        ("Charge de travail", "Charge de travail"),
        ("Rythme de travail", "Rythme travail"),
        ("Exigences cognitive", "Exigences cognitive"),
    ],
    "Organisation et Leadership": [
        ("Previsibilite", "Previsibilite"),
        ("Reconnaissance", "Reconnaissance"),
        ("Equite", "Equite"),
        ("Clarte des roles", "Clarte des roles"),
        ("Conflit de roles", "Conflit de roles"),
        ("Qualite de leadership du superieur hierarchique", "Qualite de leadership du superieur hierarchique"),
        ("Soutien social de la part du superieur hierarchique", "Soutien social de la part du superieur hierarchique"),
        ("Confiance entre les salaries et le management", "Confiance entre les salaries et le management"),
    ],
    "Relations Horizontales": [
        ("Confiance entre les collegues", "Confiance entre les collegues"),
        ("Soutien social de la part des collegues", "Soutien social entre les collegues"),
    ],
    "Autonomie": [
        ("Marge de manoeuvre", "Marge de manoeuvre"),
        ("Possibilitee d'epanouissement", "Possibilites d'epanouissement"),
    ],
    "Sante et Bien-etre": [
        ("Sante auto evaluee", "Sante auto evaluee"),
        ("Stress", "Stress"),
        ("Epuisement", "Epuisement"),
        ("Exigence emotionnelle", "Exigence emotionnelle"),
        ("Conflit famille-travail", "Conflit famille-travail"),
        ("Insecurite professionnelle", "Insecurite Professionnelle"),
    ],
    "Vecu Professionnel": [
        ("Sens du travail", "Sens du travail"),
        ("Engagement dans l'entreprise", "Engagement dans l'entreprise"),
        ("Satisfaction au travail", "Satisfaction au travail"),
    ],
}


def _pick_existing_column(source_df: pd.DataFrame, candidates: list) -> str | None:
    for name in candidates:
        if name in source_df.columns:
            return name
    return None


def _build_rps_domain_categories(source_scores_df: pd.DataFrame) -> tuple:
    out = pd.DataFrame(index=source_scores_df.index)
    domain_map: dict = {}
    missing: list = []
    label_map: dict = {}

    for domain, items in RPS_DOMAINS_CFG.items():
        domain_cols: list = []
        for label, score_col in items:
            if score_col not in source_scores_df.columns:
                missing.append({"Groupe": domain, "Sous-domaine": label, "Colonne attendue": score_col})
                continue
            cat_col = f"{label}__Categorie"
            out[cat_col] = _categorize_to_four_levels(source_scores_df[score_col])
            domain_cols.append(cat_col)
            label_map[cat_col] = label
        domain_map[domain] = domain_cols

    return out, domain_map, missing, label_map


def _pct_text(value: float) -> str:
    rounded = round(float(value), 1)
    if float(rounded).is_integer():
        return f"{int(rounded)}%"
    return f"{rounded:.1f}%"


def _normalize_to_four_levels(series: pd.Series) -> pd.Series:
    mapping = {
        "Tres faible": "Tres faible",
        "Très faible": "Tres faible",
        "Faible": "Faible",
        "Modere": "Faible",
        "Modéré": "Faible",
        "Moderé": "Faible",
        "Fort": "Fort",
        "Tres fort": "Tres fort",
        "Très fort": "Tres fort",
    }
    return series.astype("object").map(lambda v: mapping.get(str(v).strip(), str(v)))


def _plot_domain_stacked_bar(cat_df: pd.DataFrame, domain_cols: list, title: str, label_map: dict):
    valid_cols = [col for col in domain_cols if col in cat_df.columns]
    if not valid_cols:
        return None

    rows = []
    for col in valid_cols:
        collapsed = _normalize_to_four_levels(cat_df[col]).dropna()
        pct = collapsed.value_counts(normalize=True).mul(100).reindex(ORDER_LEVELS, fill_value=0)
        rows.append(pct)
    stacked = pd.DataFrame(rows, index=valid_cols)

    fig, ax = plt.subplots(figsize=(10, max(3.5, 0.6 * len(valid_cols) + 1.5)))
    y = np.arange(len(stacked))

    row_labels = [label_map.get(col, col) for col in stacked.index]
    row_palettes = [_colors_for_subdomain(lbl) for lbl in row_labels]
    row_polarities = [_SUBDOMAIN_POLARITY.get(lbl, "normal") for lbl in row_labels]

    has_normal   = any(p == "normal"   for p in row_polarities)
    has_inverted = any(p == "inverted" for p in row_polarities)
    mixed = has_normal and has_inverted

    for i, (col, palette) in enumerate(zip(stacked.index, row_palettes)):
        left = 0.0
        for level in ORDER_LEVELS:
            v = float(stacked.loc[col, level])
            ax.barh(i, v, left=left, color=palette[level])
            if v > 0:
                ax.text(left + v / 2, i, _pct_text(v), ha="center", va="center",
                        color="white", fontsize=9, fontweight="bold")
            left += v

    ax.set_yticks(y, row_labels)
    ax.set_xlim(0, 100)
    ax.set_xticks(np.arange(0, 101, 10))
    ax.set_xlabel("Pourcentage (%)")
    ax.set_title(title)

    # --- Légende en bas : RISK si tous normal, GOOD si tous inverted, GOOD par défaut si mixte ---
    legend_palette = LEVEL_COLORS_RISK if (has_normal and not has_inverted) else LEVEL_COLORS_GOOD
    patches_legend = [plt.Rectangle((0, 0), 1, 1, color=legend_palette[lvl], label=lvl) for lvl in ORDER_LEVELS]
    ax.legend(
        handles=patches_legend,
        ncol=len(ORDER_LEVELS),
        bbox_to_anchor=(0.5, -0.14),
        loc="upper center",
        frameon=True,
        title_fontsize=8,
        fontsize=8,
    )
    fig.subplots_adjust(bottom=0.18)
    fig.tight_layout()
    return fig


def _domain_distribution_table(cat_df: pd.DataFrame, domain_cols: list, label_map: dict) -> pd.DataFrame:
    valid_cols = [col for col in domain_cols if col in cat_df.columns]
    rows = []
    for col in valid_cols:
        collapsed = _normalize_to_four_levels(cat_df[col]).dropna()
        pct = collapsed.value_counts(normalize=True).mul(100).reindex(ORDER_LEVELS, fill_value=0)
        row = {"Sous-domaine": label_map.get(col, col)}
        for level in ORDER_LEVELS:
            row[level] = float(pct[level])
        row["Total"] = float(sum(row[level] for level in ORDER_LEVELS))
        rows.append(row)
    return pd.DataFrame(rows)


def _style_domain_table(df: pd.DataFrame) -> "pd.io.formats.style.Styler":
    """Applique un fond coloré sur les colonnes de niveaux selon la polarité de chaque sous-domaine."""
    _CELL_COLORS_RISK = {
        "Tres faible": "#bbf7d0",
        "Faible":      "#fef08a",
        "Fort":        "#fed7aa",
        "Tres fort":   "#fecaca",
    }
    _CELL_COLORS_GOOD = {
        "Tres faible": "#fecaca",
        "Faible":      "#fed7aa",
        "Fort":        "#fef08a",
        "Tres fort":   "#bbf7d0",
    }

    def _style_row(row: pd.Series) -> list:
        subdomain = row.get("Sous-domaine", "")
        palette = _CELL_COLORS_GOOD if _SUBDOMAIN_POLARITY.get(str(subdomain), "normal") == "inverted" else _CELL_COLORS_RISK
        return [
            f"background-color: {palette[col]}; color: #111;" if col in ORDER_LEVELS else ""
            for col in row.index
        ]

    fmt = {lvl: "{:.1f}%" for lvl in ORDER_LEVELS}
    if "Total" in df.columns:
        fmt["Total"] = "{:.1f}%"
    return df.round(1).style.apply(_style_row, axis=1).format(fmt)


def _style_bivariate_table(ct: pd.DataFrame, subdomain_label: str) -> "pd.io.formats.style.Styler":
    """Applique un fond coloré sur le tableau croisé selon la polarité du sous-domaine outcome."""
    _CELL_COLORS_RISK = {
        "Tres faible": "#bbf7d0",
        "Faible":      "#fef08a",
        "Fort":        "#fed7aa",
        "Tres fort":   "#fecaca",
    }
    _CELL_COLORS_GOOD = {
        "Tres faible": "#fecaca",
        "Faible":      "#fed7aa",
        "Fort":        "#fef08a",
        "Tres fort":   "#bbf7d0",
    }
    palette = _CELL_COLORS_GOOD if _SUBDOMAIN_POLARITY.get(subdomain_label, "normal") == "inverted" else _CELL_COLORS_RISK

    def _style_row(row: pd.Series) -> list:
        return [
            f"background-color: {palette[col]}; color: #111;" if col in ORDER_LEVELS else ""
            for col in row.index
        ]

    level_cols = [c for c in ORDER_LEVELS if c in ct.columns]
    fmt = {lvl: "{:.1f}%" for lvl in level_cols}
    if "Total" in ct.columns:
        fmt["Total"] = "{:.1f}%"
    return ct.round(1).style.apply(_style_row, axis=1).format(fmt)


def _resolve_socio_columns(source_df: pd.DataFrame) -> dict:
    candidates = {
        "Poste de travail": ["Poste de travail", "Poste"],
        "Direction": ["Direction"],
        "Departement": ["Departement", "Département"],
        "Service": ["Service"],
        "Fonction": ["Fonction"],
        "Tranche d'age": ["Tranche d'age", "Tranche age", "Tranche d'âge"],
        "Tranche anciennete": ["Tranche anciennete", "Tranche ancienneté"],
        "Genre": ["Genre"],
        "Situation matrimoniale": ["Situation matrimoniale", "Situation"],
        "Categorie IMC": ["Categorie IMC", "Catégorie IMC", "IMC"],
        "Consommation reguliere alcool": ["Consommation reguliere alcool", "Alcool"],
        "Tabagisme": ["Tabagisme", "Tabac"],
        "Pratique reguliere sport": ["Pratique reguliere sport", "Sport"],
    }
    out: dict = {}
    for label, names in candidates.items():
        if label == "Situation matrimoniale":
            found = _fuzzy_find_column(
                source_df,
                names + ["Situation matimonial", "Situation matrimoniale", "Situation maritale"],
            )
        else:
            found = _pick_existing_column(source_df, names)
        if found is not None:
            out[label] = found
    return out


def _bivariate_table(socio_series: pd.Series, outcome_series: pd.Series) -> pd.DataFrame | None:
    outcome_collapsed = _normalize_to_four_levels(outcome_series)
    temp = pd.DataFrame({"socio": socio_series, "outcome": outcome_collapsed}).dropna()
    if temp.empty:
        return None
    ct = pd.crosstab(temp["socio"], temp["outcome"], normalize="index").mul(100)
    ct = ct.reindex(columns=ORDER_LEVELS, fill_value=0)
    ct["Total"] = ct.sum(axis=1)
    return ct


def _plot_bivariate_stacked(ct: pd.DataFrame, title: str, subdomain_label: str = ""):
    """Graphique barres empilées horizontales pour le croisement socio-démographique."""
    palette = _colors_for_subdomain(subdomain_label)
    polarity = _SUBDOMAIN_POLARITY.get(subdomain_label, "normal")

    fig, ax = plt.subplots(figsize=(10, max(3.5, 0.6 * len(ct) + 1.5)))
    y = np.arange(len(ct))

    legend_patches = [
        plt.Rectangle((0, 0), 1, 1, color=palette[lvl], label=lvl)
        for lvl in ORDER_LEVELS
    ]

    for i in range(len(ct)):
        left = 0.0
        for level in ORDER_LEVELS:
            v = float(ct.iloc[i][level]) if level in ct.columns else 0.0
            ax.barh(i, v, left=left, color=palette[level])
            if v > 0:
                ax.text(left + v / 2, i, _pct_text(v), ha="center", va="center",
                        color="white", fontsize=9, fontweight="bold")
            left += v

    ax.set_yticks(y, ct.index.astype(str))
    ax.set_xlim(0, 100)
    ax.set_xticks(np.arange(0, 101, 10))
    ax.set_xlabel("Pourcentage (%)")
    ax.set_title(title)

    legend_title = (
        ""
        if polarity == "inverted"
        else ""
    )
    ax.legend(
        handles=legend_patches,
        ncol=len(ORDER_LEVELS),
        bbox_to_anchor=(0.5, -0.14),
        loc="upper center",
        frameon=True,
        title=legend_title,
        title_fontsize=8,
        fontsize=8,
    )
    fig.subplots_adjust(bottom=0.18)
    fig.tight_layout()
    return fig


# =============================================================================
# POINT D'ENTREE STREAMLIT
# =============================================================================

st.set_page_config(
    page_title="Tableau d'analyse COPSOQ",
    page_icon=":busts_in_silhouette:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_css()
load_js()

# ════════════════════════════════════════════════════════════
# TOPBAR YODAN
# ════════════════════════════════════════════════════════════
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">',
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
        '<i class="fas fa-clipboard-check" style="color:white;font-size:15px;"></i></div>'
        '<div>'
        '<div style="font-size:16px;font-weight:700;color:#1e293b;">COPSOQ — Copenhagen Psychosocial Questionnaire</div>'
        '<div style="font-size:11px;color:#64748b;margin-top:1px;">Analyse des facteurs psychosociaux au travail · Pahaliah &amp; Fils</div>'
        '</div></div>',
        unsafe_allow_html=True
    )
with _col_back:
    st.write("")
    st.write("")
    if st.button("← Accueil", key="back_home_copsoq", use_container_width=True):
        st.switch_page("app.py")

# --- Upload du fichier de données ---
with st.sidebar:
    st.header("📂 Données")
    uploaded_file = st.file_uploader(
        "Charger un fichier Excel ou CSV",
        type=["xlsx", "xls", "csv"],
        help="Glissez-déposez ou cliquez pour sélectionner votre fichier de données.",
    )

# Stocker les bytes dans session_state pour éviter le rechargement à chaque interaction
if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    if file_bytes:  # nouveau fichier uploadé
        st.session_state["_file_bytes"] = file_bytes
        st.session_state["_file_name"] = uploaded_file.name

if "_file_bytes" not in st.session_state:
    st.info("Veuillez charger un fichier de données (Excel ou CSV)pour démarrer l'analyse.")
    # Proposer aussi un uploader dans la zone principale (sous le message)
    main_uploaded = st.file_uploader(
        "Ou importez votre fichier ici",
        type=["xlsx", "xls", "csv"],
        help="Importer un fichier depuis la zone principale.",
        key="main_uploader",
    )
    if main_uploaded is not None:
        main_bytes = main_uploaded.read()
        if main_bytes:
            st.session_state["_file_bytes"] = main_bytes
            st.session_state["_file_name"] = main_uploaded.name
    if "_file_bytes" not in st.session_state:
        st.stop()

_file_bytes = st.session_state["_file_bytes"]
_file_name = st.session_state["_file_name"]

with st.spinner("Chargement et traitement des données…"):
    df_raw = load_data_from_bytes(_file_bytes, _file_name)
    df_scores_raw = load_data_scores_from_bytes(_file_bytes, _file_name)

# --- Nettoyage automatique des variables communes ---
df_raw, cleaning_log = clean_common_variables(df_raw)

# --- Compter les questions COPSOQ détectées ---
_matched_q_count = sum(1 for q in QUESTION_TEXT_MAP if q in load_data_qx_from_bytes(_file_bytes, _file_name).columns)

with st.expander("Journal de nettoyage automatique", expanded=False):
    st.text(cleaning_log)
    st.write(f"Questions COPSOQ detectees automatiquement: {_matched_q_count}/46")

tab_generales, tab_analyse_simple, tab_domaines_rps, tab_croissement = st.tabs(
    ["Générale", "Analyse simple", "Domaines", "Croissement"]
)

# --- Données globales (hors tabs pour éviter le rechargement à chaque interaction) ---
df = _ensure_tranche_anciennete(df_raw.copy())
df_scores = df_scores_raw.copy()

# --- Bloc filtres dans la sidebar ---
filtered_df = df.copy()
filtered_scores = df_scores.copy()

with tab_generales:
    st.markdown('<h3 class="section-title">Données Générales de l\'Entreprise</h3>', unsafe_allow_html=True)

    kpi = build_general_indicators(df)
    age_moyen = kpi.get("age_moyen")
    # Déterminer si l'Age (numérique) est disponible ou si on utilise Tranche d'age
    _age_col_present = _find_age_numeric_col(df)
    _age_numeric_ok = False
    if _age_col_present is not None:
        _age_vals_check = pd.to_numeric(df[_age_col_present], errors="coerce")
        _age_numeric_ok = not _age_vals_check.dropna().empty

    if _age_numeric_ok and isinstance(age_moyen, Real):
        age_moyen_display = f"{age_moyen:.0f} ans"
    elif age_moyen in (None, "", "N/A"):
        age_moyen_display = "N/A"
    else:
        # Fallback sur mode de Tranche d'age — afficher avec "ans" pour cohérence visuelle
        age_moyen_display = f"{age_moyen}"
    age_kpi_label = "Age Moyen"

    top_situation = "N/A"
    if not kpi["situation_matrimoniale"].empty:
        top_situation = str(kpi["situation_matrimoniale"].iloc[0]["Situation matrimoniale"])

    effectif_img_b64 = image_as_base64("effectif.png")
    homme_img_b64 = image_as_base64("homme.png")
    femme_img_b64 = image_as_base64("femme.png")
    age_img_b64 = image_as_base64("age.png")
    fume_img_b64 = image_as_base64("fume.png")
    alcool_img_b64 = image_as_base64("alcool.png")
    sport_img_b64 = image_as_base64("sport.png")
    couple_img_b64 = image_as_base64("couple.png")

    # Calculer les pourcentages pour hommes et femmes
    total_effectif = kpi['total_effectif']
    pourcentage_hommes = (kpi['nombre_hommes'] / total_effectif * 100) if total_effectif > 0 else 0
    pourcentage_femmes = (kpi['nombre_femmes'] / total_effectif * 100) if total_effectif > 0 else 0
    
    
    cards = [
        ("Nombre de Repondant", f"{total_effectif}", "&#128101;"),
        (
            f"Nombre d'Hommes ({kpi['nombre_hommes']})",
            f'<span class="rps-score-value" data-rps-score="true" data-rps-target="{pourcentage_hommes}" data-rps-decimals="1" data-rps-suffix="%" data-rps-final="{pourcentage_hommes:.1f}%">0.0%</span>',
            f'<img class="card-footer-image" src="data:image/png;base64,{homme_img_b64}" alt="homme" />',
        ),
        (
            f"Nombre de Femmes ({kpi['nombre_femmes']})",
            f'<span class="rps-score-value" data-rps-score="true" data-rps-target="{pourcentage_femmes}" data-rps-decimals="1" data-rps-suffix="%" data-rps-final="{pourcentage_femmes:.1f}%">0.0%</span>',
            f'<img class="card-footer-image" src="data:image/png;base64,{femme_img_b64}" alt="femme" />',
        ),
        (
            age_kpi_label,
            age_moyen_display,
            f'<img class="card-footer-image" src="data:image/png;base64,{age_img_b64}" alt="age" />',
        ),
        (
            "Taux de consomamation d'alcool",
            f'<span class="rps-score-value" data-rps-score="true" data-rps-target="{kpi["taux_alcool"]}" data-rps-decimals="1" data-rps-suffix="%" data-rps-final="{kpi["taux_alcool"]:.1f}%">0.0%</span>',
            f'<img class="card-footer-image" src="data:image/png;base64,{alcool_img_b64}" alt="alcool" />',
        ),
        (
            "Taux de consomamation de tabac",
            f'<span class="rps-score-value" data-rps-score="true" data-rps-target="{kpi["taux_fumeur"]}" data-rps-decimals="1" data-rps-suffix="%" data-rps-final="{kpi["taux_fumeur"]:.1f}%">0.0%</span>',
            f'<img class="card-footer-image" src="data:image/png;base64,{fume_img_b64}" alt="fumeur" />',
        ),
        (
            "Pratique sport",
            f'<span class="rps-score-value" data-rps-score="true" data-rps-target="{kpi["taux_sport"]}" data-rps-decimals="1" data-rps-suffix="%" data-rps-final="{kpi["taux_sport"]:.1f}%">0.0%</span>',
            f'<img class="card-footer-image" src="data:image/png;base64,{sport_img_b64}" alt="sport" />',
        ),
        (
            "Situation matrimoniale",
            top_situation,
            f'<img class="card-footer-image" src="data:image/png;base64,{couple_img_b64}" alt="situation matrimoniale" />',
        ),
    ]

    cards_html = ""
    for index, (label, value, emoji) in enumerate(cards):
        delay_ms = index * 80
        anim_labels = {
            "Nombre de Repondant",
            "Nombre d'Hommes",
            "Nombre de Femmes",
            "Taux alcool",
            "Taux fumeur",
            "Pratique sport",
        }
        value_html = f'<p class="card-value kpi-drop-fade" style="animation-delay: {delay_ms}ms;">{value}</p>'
        if label in anim_labels:
            is_rate = label in {"Taux alcool", "Taux fumeur", "Pratique sport"}
            decimals = 1 if is_rate else 0
            suffix = "%" if is_rate else ""
            try:
                numeric_value = float(str(value).replace("%", "").strip())
                start_text = "0.0%" if is_rate else "0"
                value_html = (
                    f'<p class="card-value kpi-drop-fade" style="animation-delay: {delay_ms}ms;">'
                    f'<span class="rps-score-value" data-rps-score="true" data-rps-target="{numeric_value}" '
                    f'data-rps-decimals="{decimals}" data-rps-suffix="{suffix}" data-rps-final="{value}">{start_text}</span>'
                    "</p>"
                )
            except Exception:
                pass
        if index == 0 and effectif_img_b64:
            cards_html += (
                '<div class="card-container">'
                f'<p class="card-title">{label}</p>'
                f"{value_html}"
                f'<img class="card-center-image" src="data:image/png;base64,{effectif_img_b64}" alt="effectif" />'
                "</div>"
            )
        else:
            cards_html += (
                '<div class="card-container">'
                f'<p class="card-title">{label}</p>'
                f"{value_html}"
                '<div class="card-footer">'
                f"{emoji}"
                "</div>"
                "</div>"
            )

    st.markdown(f'<div class="kpi-grid">{cards_html}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # =========================================================================
    # SECTION Z-SCORES & SCORE GLOBAL RPS
    # =========================================================================
    # Méthodologie :
    # 1. Score brut sous-domaine = moyenne normalisée 0-100 de chaque répondant
    # 2. Score entreprise (µ) = moyenne de tous les répondants sur ce sous-domaine
    # 3. Score orienté risque = si polarity "inverted" → 100 - µ (on ramène tout en convention risque)
    # 4. Z-score inter-sous-domaines = (µ_risque - µ_global_risque) / σ_global_risque
    #    → Z > 0 = ce sous-domaine est plus risqué que la moyenne de l'entreprise
    #    → Z > +1 = à surveiller ; Z > +2 = niveau critique
    # 5. Score global domaine = moyenne des scores orientés risque de ses sous-domaines
    # 6. Score global RPS entreprise = moyenne des 6 scores domaines (0-100, risque)

    # --- Calcul des scores entreprise par sous-domaine ---
    _SUBDOMAIN_POLARITY_SCORE = {
        "Charge de travail":        "normal",
        "Rythme travail":           "normal",
        "Exigences cognitive":      "normal",
        "Previsibilite":            "inverted",
        "Reconnaissance":           "inverted",
        "Equite":                   "inverted",
        "Clarte des roles":         "inverted",
        "Conflit de roles":         "normal",
        "Qualite de leadership du superieur hierarchique": "inverted",
        "Soutien social de la part du superieur hierarchique": "inverted",
        "Confiance entre les salaries et le management": "inverted",
        "Confiance entre les collegues":             "inverted",
        "Soutien social entre les collegues":        "inverted",
        "Marge de manoeuvre":              "inverted",
        "Possibilites d'epanouissement":   "inverted",
        "Sante auto evaluee":      "inverted",
        "Stress":                  "normal",
        "Epuisement":              "normal",
        "Exigence emotionnelle":   "normal",
        "Conflit famille-travail": "normal",
        "Insecurite Professionnelle": "normal",
        "Sens du travail":              "inverted",
        "Engagement dans l'entreprise": "inverted",
        "Satisfaction au travail":      "inverted",
    }

    _RPS_DOMAIN_SUBDOMAINS = {
        "Contraintes Quantitatives": ["Charge de travail", "Rythme travail", "Exigences cognitive"],
        "Organisation et Leadership": ["Previsibilite", "Reconnaissance", "Equite", "Clarte des roles",
                                       "Conflit de roles", "Qualite de leadership du superieur hierarchique",
                                       "Soutien social de la part du superieur hierarchique",
                                       "Confiance entre les salaries et le management"],
        "Relations Horizontales": ["Confiance entre les collegues", "Soutien social entre les collegues"],
        "Autonomie": ["Marge de manoeuvre", "Possibilites d'epanouissement"],
        "Sante et Bien-etre": ["Sante auto evaluee", "Stress", "Epuisement",
                               "Exigence emotionnelle", "Conflit famille-travail", "Insecurite Professionnelle"],
        "Vecu Professionnel": ["Sens du travail", "Engagement dans l'entreprise", "Satisfaction au travail"],
    }

    def _compute_zscore_metrics(source_df: pd.DataFrame) -> dict:
        """
        Calcule pour chaque sous-domaine :
          - mean_raw    : score moyen entreprise (0-100)
          - mean_risk   : converti en score de risque (0=aucun risque, 100=risque max)
          - z_score     : Z normalisé parmi tous les sous-domaines (risque relatif)
          - alert_level : 'ok' / 'vigilance' / 'critique'
        Et pour chaque domaine / global.
        """
        all_labels = list(_SUBDOMAIN_POLARITY_SCORE.keys())
        means_raw = {}
        means_risk = {}
        for label in all_labels:
            col = label
            if col not in source_df.columns:
                continue
            mu = source_df[col].mean(skipna=True)
            if pd.isna(mu):
                continue
            means_raw[label] = float(mu)
            polarity = _SUBDOMAIN_POLARITY_SCORE.get(label, "normal")
            means_risk[label] = (100.0 - float(mu)) if polarity == "inverted" else float(mu)

        if len(means_risk) < 2:
            return {}

        risk_values = np.array(list(means_risk.values()))
        mu_global = float(risk_values.mean())
        sigma_global = float(risk_values.std(ddof=1)) if len(risk_values) > 1 else 1.0
        if sigma_global < 1e-6:
            sigma_global = 1.0

        subdomain_stats = {}
        for label, risk_val in means_risk.items():
            z = (risk_val - mu_global) / sigma_global
            if z > 2.0:
                alert = "critique"
            elif z > 1.0:
                alert = "vigilance"
            else:
                alert = "ok"
            subdomain_stats[label] = {
                "mean_raw": means_raw.get(label, np.nan),
                "mean_risk": risk_val,
                "z_score": round(z, 2),
                "alert_level": alert,
            }

        # Scores domaines
        domain_stats = {}
        domain_risk_vals = []
        for domain, subdomains in _RPS_DOMAIN_SUBDOMAINS.items():
            vals = [means_risk[s] for s in subdomains if s in means_risk]
            if not vals:
                continue
            d_risk = float(np.mean(vals))
            domain_stats[domain] = {"mean_risk": d_risk}
            domain_risk_vals.append(d_risk)

        global_rps = float(np.mean(domain_risk_vals)) if domain_risk_vals else np.nan

        return {
            "subdomains": subdomain_stats,
            "domains": domain_stats,
            "global_rps": global_rps,
            "mu_global": mu_global,
            "sigma_global": sigma_global,
        }

    zscore_data = _compute_zscore_metrics(filtered_scores)

    # --- Score Global RPS ---
    global_rps = zscore_data.get("global_rps", np.nan)
    if not pd.isna(global_rps):
        if global_rps <= 33:
            rps_color = "#166534"; rps_bg = "#DCFCE7"; rps_label = "✅ Environnement favorable"
        elif global_rps <= 50:
            rps_color = "#854D0E"; rps_bg = "#FEF9C3"; rps_label = "⚠️ Vigilance modérée"
        elif global_rps <= 66:
            rps_color = "#C05600"; rps_bg = "#FED7AA"; rps_label = "⚠️ Risque modéré"
        else:
            rps_color = "#991B1B"; rps_bg = "#FEE2E2"; rps_label = "❌ Risque élevé"

        st.markdown(
            f"""
            <div style="background:{rps_bg}; border:2px solid {rps_color}; border-radius:14px;
                        padding:18px 28px; margin-bottom:18px; display:flex; align-items:center; justify-content:space-between;">
                <div>
                    <p style="margin:0; font-size:13px; color:{rps_color}; font-weight:600; text-transform:uppercase; letter-spacing:.05em;">
                        Score Global RPS Entreprise
                    </p>
                    <p style="margin:4px 0 0; font-size:28px; font-weight:800; color:{rps_color};">
                        {global_rps:.1f} / 100
                    </p>
                    <p style="margin:2px 0 0; font-size:14px; color:{rps_color};">{rps_label}</p>
                    <p style="margin:6px 0 0; font-size:11px; color:{rps_color}; opacity:.75;">
                        0 = aucun risque · 100 = risque maximal · Moyenne des 6 domaines (convention risque)
                    </p>
                </div>
                <div style="font-size:48px;">🎯</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Radar Charts ---
    st.markdown('<h3 class="section-title">Radar RPS — Vue d\'ensemble</h3>', unsafe_allow_html=True)

    import plotly.graph_objects as go

    def _risk_badge(score: float) -> tuple:
        """Retourne (icone, label, couleur_texte, couleur_fond, couleur_bordure) selon le score de risque."""
        if score <= 33:
            return "✅", "Favorable", "#166534", "#DCFCE7", "#4ADE80"
        elif score <= 50:
            return "⚠️", "Vigilance modérée", "#854D0E", "#FEF9C3", "#FACC15"
        elif score <= 66:
            return "🟠", "Risque modéré", "#C05600", "#FED7AA", "#FB923C"
        else:
            return "❌", "Risque élevé", "#991B1B", "#FEE2E2", "#EF4444"

    def _domain_interpret_html(domain_name: str, domain_risk: float) -> str:
        ico, lbl, tc, bg, bc = _risk_badge(domain_risk)
        descriptions = {
            "Contraintes Quantitatives": "Charge, rythme et exigences cognitives imposées par le travail.",
            "Organisation et Leadership": "Qualité du management, équité, clarté des rôles et confiance.",
            "Relations Horizontales": "Soutien et confiance entre collègues.",
            "Autonomie": "Marge de manœuvre et épanouissement des salariés.",
            "Sante et Bien-etre": "Stress, épuisement, santé perçue et équilibre vie pro/perso.",
            "Vecu Professionnel": "Sens du travail, engagement et satisfaction globale.",
        }
        desc = descriptions.get(domain_name, "")
        return (
            f'<div style="background:{bg};border:1px solid {bc};border-radius:10px;padding:10px 14px;margin-top:4px;">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
            f'<span style="font-size:18px;">{ico}</span>'
            f'<span style="font-weight:700;color:{tc};font-size:14px;">{lbl}</span>'
            f'<span style="margin-left:auto;font-weight:800;color:{tc};font-size:15px;">{domain_risk:.1f}/100</span>'
            f'</div>'
            f'<p style="margin:0;font-size:11px;color:{tc};opacity:.85;">{desc}</p>'
            f'</div>'
        )

    radar_col1, radar_col2 = st.columns([1, 1])

    with radar_col1:
        # Radar 6 domaines
        domain_stats = zscore_data.get("domains", {})
        if domain_stats:
            d_labels = list(domain_stats.keys())
            d_values = [domain_stats[d]["mean_risk"] for d in d_labels]
            d_labels_wrap = [l.replace(" et ", "<br>").replace(" ", "<br>", 1) if len(l) > 18 else l for l in d_labels]
            fig_radar_domain = go.Figure()
            fig_radar_domain.add_trace(go.Scatterpolar(
                r=d_values + [d_values[0]],
                theta=d_labels_wrap + [d_labels_wrap[0]],
                fill="toself",
                fillcolor="rgba(239,68,68,0.18)",
                line=dict(color="#EF4444", width=2.5),
                name="Score risque domaine",
                hovertemplate="<b>%{theta}</b><br>Score risque: %{r:.1f}/100<extra></extra>",
            ))
            fig_radar_domain.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9), tickvals=[0, 25, 50, 75, 100]),
                    angularaxis=dict(tickfont=dict(size=10)),
                ),
                showlegend=False,
                title=dict(text="Scores de Risque par Domaine RPS", font=dict(size=13), x=0.5),
                height=360,
                margin=dict(l=50, r=50, t=50, b=20),
            )
            st.plotly_chart(fig_radar_domain, use_container_width=True)

            # --- Interprétation domaines ---
            st.markdown(
                '<p style="font-size:12px;font-weight:700;color:#374151;margin:6px 0 4px;text-transform:uppercase;letter-spacing:.04em;">🔍 Interprétation des 6 domaines</p>',
                unsafe_allow_html=True,
            )
            interp_html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">'
            for d_name, d_val in zip(d_labels, d_values):
                interp_html += _domain_interpret_html(d_name, d_val)
            interp_html += '</div>'

            # Identifier le domaine le plus risqué
            worst_domain = d_labels[int(np.argmax(d_values))]
            worst_val = max(d_values)
            best_domain = d_labels[int(np.argmin(d_values))]
            best_val = min(d_values)
            _, worst_lbl, worst_tc, worst_bg, worst_bc = _risk_badge(worst_val)
            _, best_lbl, best_tc, best_bg, best_bc = _risk_badge(best_val)

            interp_html += (
                f'<div style="background:#F1F5F9;border-radius:10px;padding:10px 14px;margin-top:8px;">'
                f'<p style="margin:0 0 4px;font-size:12px;font-weight:700;color:#1E3A5F;">📌 Points clés</p>'
                f'<p style="margin:2px 0;font-size:12px;color:#374151;">🔴 <b>Domaine prioritaire :</b> <span style="color:{worst_tc};font-weight:600;">{worst_domain}</span> ({worst_val:.1f}/100 — {worst_lbl})</p>'
                f'<p style="margin:2px 0;font-size:12px;color:#374151;">🟢 <b>Domaine le plus sain :</b> <span style="color:{best_tc};font-weight:600;">{best_domain}</span> ({best_val:.1f}/100 — {best_lbl})</p>'
                f'</div>'
            )
            st.markdown(interp_html, unsafe_allow_html=True)
        else:
            st.info("Données insuffisantes pour le radar domaines.")

    with radar_col2:
        # Radar sous-domaines avec sélecteur domaine
        subdomain_stats = zscore_data.get("subdomains", {})
        selected_radar_domain = st.selectbox(
            "Sélectionner un domaine RPS",
            options=list(_RPS_DOMAIN_SUBDOMAINS.keys()),
            key="radar_subdomain_selector",
        )
        sub_labels_for_domain = _RPS_DOMAIN_SUBDOMAINS.get(selected_radar_domain, [])
        sub_risk_vals = []
        sub_short_labels = []
        sub_full_labels = []
        for s in sub_labels_for_domain:
            if s in subdomain_stats:
                sub_risk_vals.append(subdomain_stats[s]["mean_risk"])
                short = s if len(s) <= 20 else s[:18] + "…"
                sub_short_labels.append(short)
                sub_full_labels.append(s)

        if sub_risk_vals and len(sub_risk_vals) >= 3:
            fig_radar_sub = go.Figure()
            fig_radar_sub.add_trace(go.Scatterpolar(
                r=sub_risk_vals + [sub_risk_vals[0]],
                theta=sub_short_labels + [sub_short_labels[0]],
                fill="toself",
                fillcolor="rgba(251,146,60,0.18)",
                line=dict(color="#FB923C", width=2.5),
                name="Score risque sous-domaine",
                hovertemplate="<b>%{theta}</b><br>Score risque: %{r:.1f}/100<extra></extra>",
            ))
            ref_val = zscore_data.get("mu_global", 50)
            fig_radar_sub.add_trace(go.Scatterpolar(
                r=[ref_val] * (len(sub_short_labels) + 1),
                theta=sub_short_labels + [sub_short_labels[0]],
                mode="lines",
                line=dict(color="#147089", width=1.5, dash="dot"),
                name=f"Moy. entreprise ({ref_val:.1f})",
            ))
            fig_radar_sub.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9), tickvals=[0, 25, 50, 75, 100]),
                    angularaxis=dict(tickfont=dict(size=9)),
                ),
                showlegend=True,
                legend=dict(font=dict(size=9), orientation="h", y=-0.08),
                title=dict(text=f"Sous-domaines — {selected_radar_domain}", font=dict(size=13), x=0.5),
                height=360,
                margin=dict(l=50, r=50, t=50, b=40),
            )
            st.plotly_chart(fig_radar_sub, use_container_width=True)

            # --- Interprétation sous-domaines ---
            # Score global du domaine sélectionné
            domain_risk_selected = zscore_data.get("domains", {}).get(selected_radar_domain, {}).get("mean_risk", None)
            if domain_risk_selected is not None:
                d_ico, d_lbl, d_tc, d_bg, d_bc = _risk_badge(domain_risk_selected)
                st.markdown(
                    f'<div style="background:{d_bg};border:1px solid {d_bc};border-radius:10px;padding:8px 14px;margin-bottom:8px;display:flex;align-items:center;gap:10px;">'
                    f'<span style="font-size:20px;">{d_ico}</span>'
                    f'<div><p style="margin:0;font-size:12px;color:{d_tc};font-weight:700;">Domaine sélectionné : {selected_radar_domain}</p>'
                    f'<p style="margin:0;font-size:13px;color:{d_tc};font-weight:800;">Score risque global : {domain_risk_selected:.1f}/100 — {d_lbl}</p></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # Tableau d'interprétation par sous-domaine
            st.markdown(
                '<p style="font-size:12px;font-weight:700;color:#374151;margin:4px 0;text-transform:uppercase;letter-spacing:.04em;">🔍 Détail des sous-domaines</p>',
                unsafe_allow_html=True,
            )
            sub_interp_html = ""
            for full_lbl, risk_val in zip(sub_full_labels, sub_risk_vals):
                z_val = subdomain_stats.get(full_lbl, {}).get("z_score", 0.0)
                alert = subdomain_stats.get(full_lbl, {}).get("alert_level", "ok")
                ico, lbl, tc, bg, bc = _risk_badge(risk_val)

                z_tag = ""
                if alert == "critique":
                    z_tag = f'<span style="background:#FEE2E2;color:#991B1B;border-radius:4px;padding:1px 6px;font-size:10px;font-weight:700;">Z={z_val:+.2f} CRITIQUE</span>'
                elif alert == "vigilance":
                    z_tag = f'<span style="background:#FED7AA;color:#C05600;border-radius:4px;padding:1px 6px;font-size:10px;font-weight:700;">Z={z_val:+.2f} VIGILANCE</span>'
                else:
                    z_tag = f'<span style="background:#F1F5F9;color:#6B7280;border-radius:4px;padding:1px 6px;font-size:10px;">Z={z_val:+.2f}</span>'

                sub_interp_html += (
                    f'<div style="background:{bg};border-left:3px solid {bc};border-radius:6px;'
                    f'padding:6px 12px;margin-bottom:5px;display:flex;align-items:center;justify-content:space-between;">'
                    f'<div><p style="margin:0;font-size:12px;font-weight:600;color:{tc};">{ico} {full_lbl}</p></div>'
                    f'<div style="display:flex;align-items:center;gap:8px;">'
                    f'{z_tag}'
                    f'<span style="font-weight:800;font-size:13px;color:{tc};">{risk_val:.1f}</span>'
                    f'</div></div>'
                )

            # Résumé texte
            worst_sub = sub_full_labels[int(np.argmax(sub_risk_vals))] if sub_risk_vals else "—"
            best_sub = sub_full_labels[int(np.argmin(sub_risk_vals))] if sub_risk_vals else "—"
            worst_sub_val = max(sub_risk_vals) if sub_risk_vals else 0
            best_sub_val = min(sub_risk_vals) if sub_risk_vals else 0
            above_ref = [sub_full_labels[i] for i, v in enumerate(sub_risk_vals) if v > ref_val]

            sub_interp_html += (
                f'<div style="background:#F1F5F9;border-radius:8px;padding:8px 12px;margin-top:6px;">'
                f'<p style="margin:0 0 3px;font-size:12px;font-weight:700;color:#1E3A5F;">📌 Résumé</p>'
                f'<p style="margin:1px 0;font-size:11px;color:#374151;">🔴 <b>Point de vigilance :</b> {worst_sub} ({worst_sub_val:.1f}/100)</p>'
                f'<p style="margin:1px 0;font-size:11px;color:#374151;">🟢 <b>Point fort :</b> {best_sub} ({best_sub_val:.1f}/100)</p>'
            )
            if above_ref:
                sub_interp_html += f'<p style="margin:1px 0;font-size:11px;color:#374151;">📊 <b>{len(above_ref)} sous-domaine(s)</b> au-dessus de la moyenne entreprise ({ref_val:.1f}) : {", ".join(above_ref)}</p>'
            sub_interp_html += '</div>'

            st.markdown(sub_interp_html, unsafe_allow_html=True)

        elif sub_risk_vals:
            st.info("Ce domaine a moins de 3 sous-domaines disponibles pour le radar. Affichage en barres :")
            fig_bar = px.bar(
                x=sub_short_labels, y=sub_risk_vals,
                labels={"x": "Sous-domaine", "y": "Score risque (0-100)"},
                color=sub_risk_vals, color_continuous_scale=["#4ADE80", "#FACC15", "#FB923C", "#EF4444"],
                range_color=[0, 100],
            )
            fig_bar.update_layout(height=320, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Données insuffisantes pour ce domaine.")

with tab_analyse_simple:
    st.subheader("Statistiques univariees")
    analyse_df = filtered_df.copy() if "filtered_df" in locals() and not filtered_df.empty else df.copy()

    if analyse_df.empty:
        st.info("Aucune donnee disponible pour l'analyse univariee.")
    else:
        selected_col = st.selectbox("Variable", analyse_df.columns.tolist(), key="analyse_simple_variable")
        series_for_univariate = analyse_df[selected_col]
        recomputed_five = False

        if str(selected_col).endswith("_Categorie"):
            base_col = str(selected_col).rsplit("_Categorie", 1)[0]
            if base_col in analyse_df.columns:
                base_num = _to_numeric(analyse_df[base_col])
                if base_num.notna().sum() > 0:
                    series_for_univariate = _categorize_to_four_levels(base_num)
                    recomputed_five = True

        stats, freq = _get_univariate_stats(series_for_univariate, len(analyse_df), selected_col)
        left_col, right_col = st.columns([1, 1.4])

        with left_col:
            if recomputed_five:
                st.caption("Variable _Categorie recalculee en 4 niveaux: Tres faible, Faible, Fort, Tres fort.")
            with st.container(border=True):
                st.markdown("**Statistiques**")
                stats_df = pd.DataFrame(list(stats.items()), columns=["Mesure", "Valeur"])
                st.dataframe(_format_df_for_display(stats_df), use_container_width=True, height=260)
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("**Frequences detaillees**")
                st.dataframe(_format_df_for_display(freq), use_container_width=True, height=320)

        with right_col:
            temp_df = analyse_df.copy()
            temp_df[selected_col] = series_for_univariate
            fig_uni = _build_univariate_figure(temp_df, selected_col)
            png_bytes = _fig_to_png_bytes(fig_uni)
            if png_bytes is not None:
                safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(selected_col))
                st.download_button(
                    "PNG",
                    data=png_bytes,
                    file_name=f"{safe_name}.png",
                    mime="image/png",
                    key=f"dl_png_uni_{safe_name}",
                )
            st.pyplot(fig_uni, use_container_width=True)
            plt.close(fig_uni)

with tab_domaines_rps:
    st.subheader("Domaines et sous-domaines")
    socio_df = filtered_df.copy() if "filtered_df" in locals() else df.copy()
    score_df = filtered_scores.copy() if "filtered_scores" in locals() else df_scores.copy()
    common_index = socio_df.index.intersection(score_df.index)
    socio_df = socio_df.loc[common_index]
    score_df = score_df.loc[common_index]

    domain_cat_df, domain_map, missing_domains, domain_label_map = _build_rps_domain_categories(score_df)
    domain_choices = [group for group, cols in domain_map.items() if cols]
    if not domain_choices:
        st.warning("Aucun domaine exploitable detecte.")
        domain_choices = list(domain_map.keys()) if domain_map else []

    selected_group = st.selectbox("Groupe", domain_choices, key="domaines_rps_groupe") if domain_choices else None
    selected_cols = domain_map.get(selected_group, []) if selected_group else []

    if not selected_cols:
        st.warning("Aucun domaine construit pour ce groupe avec les colonnes actuelles.")
    else:
        fig_domain = _plot_domain_stacked_bar(
            domain_cat_df,
            selected_cols,
            f"Répartition des employés selon {selected_group}",
            domain_label_map,
        )
        if fig_domain is not None:
            png_bytes = _fig_to_png_bytes(fig_domain)
            if png_bytes is not None:
                group_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(selected_group))
                st.download_button(
                    "PNG",
                    data=png_bytes,
                    file_name=f"{group_name}.png",
                    mime="image/png",
                    key=f"dl_png_domain_{group_name}",
                )
            st.pyplot(fig_domain, use_container_width=True)
            plt.close(fig_domain)

    if missing_domains:
        with st.expander("Paires non construites (questions introuvables)"):
            st.dataframe(pd.DataFrame(missing_domains), use_container_width=True)

    st.markdown("### Domaines selon la démographie")
    socio_columns = _resolve_socio_columns(socio_df)
    domain_choices_cross = [group for group, cols in domain_map.items() if cols]

    if not domain_choices_cross or not socio_columns:
        st.info("Selection indisponible: groupe/sous-domaines/socio-vars insuffisants.")
    else:
        c1, c2, c3 = st.columns(3)
        grp_cross = c1.selectbox("Groupe (les domaines)", domain_choices_cross, key="domaines_rps_cross_group")
        socio_label = c2.selectbox(
            "Variable socio-demographique",
            ["Aucune"] + list(socio_columns.keys()),
            key="domaines_rps_cross_socio",
        )

        if socio_label == "Aucune":
            socio_modalities: list = []
            selected_modality = c3.selectbox("Modalite", ["Vue globale"], key="domaines_rps_cross_modalite")
            socio_col = None
        else:
            socio_col = socio_columns[socio_label]
            socio_modalities = sorted(socio_df[socio_col].dropna().astype(str).unique().tolist())
            selected_modality = c3.selectbox(
                "Modalite",
                ["Toutes"] + socio_modalities,
                key="domaines_rps_cross_modalite",
            )

        cross_cols = domain_map.get(grp_cross, [])
        if not cross_cols:
            st.warning("Aucun sous-domaine disponible pour ce groupe.")
        elif socio_col is None:
            st.info("Selectionnez une variable socio-demographique pour afficher le graphique.")
        else:
            if selected_modality == "Toutes":
                modalities_to_show = socio_modalities
            else:
                modalities_to_show = [selected_modality]

            if not modalities_to_show:
                st.warning("Aucune modalite disponible.")
            else:
                for modality in modalities_to_show:
                    if modality is None:
                        idx = socio_df.index
                        st.markdown("**Vue globale (aucun filtre socio-demographique)**")
                    else:
                        idx = socio_df[socio_df[socio_col].astype(str) == modality].index
                        st.markdown(f"**{socio_label} = {modality}**")

                    cat_subset = domain_cat_df.loc[domain_cat_df.index.intersection(idx)]
                    if cat_subset.empty:
                        continue

                    fig_cross = _plot_domain_stacked_bar(
                        cat_subset,
                        cross_cols,
                        f"Répartition des employés selon {grp_cross}",
                        domain_label_map,
                    )
                    if fig_cross is not None:
                        png_cross = _fig_to_png_bytes(fig_cross)
                        if png_cross is not None:
                            group_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(grp_cross))
                            socio_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(socio_label))
                            mod_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(modality if modality is not None else "Aucune"))
                            st.download_button(
                                "PNG",
                                data=png_cross,
                                file_name=f"{group_name}_{socio_name}_{mod_name}.png",
                                mime="image/png",
                                key=f"dl_png_domain_cross_{group_name}_{socio_name}_{mod_name}",
                            )
                        st.pyplot(fig_cross, use_container_width=True)
                        plt.close(fig_cross)

                    cross_table = _domain_distribution_table(cat_subset, cross_cols, domain_label_map)
                    if not cross_table.empty:
                        st.dataframe(_style_domain_table(cross_table), use_container_width=True)

with tab_croissement:
    st.subheader("Croisement socio-demographique selon l'outcome")
    socio_df = filtered_df.copy() if "filtered_df" in locals() else df.copy()
    score_df = filtered_scores.copy() if "filtered_scores" in locals() else df_scores.copy()
    common_index = socio_df.index.intersection(score_df.index)
    socio_df = socio_df.loc[common_index]
    score_df = score_df.loc[common_index]

    domain_cat_df, domain_map, _, domain_label_map = _build_rps_domain_categories(score_df)
    socio_columns = _resolve_socio_columns(socio_df)
    outcome_cols = [col for cols in domain_map.values() for col in cols if col in domain_cat_df.columns]

    if not socio_columns or not outcome_cols:
        st.warning("Variables insuffisantes pour l'analyse bivariee.")
    else:
        # Créer une liste combinée de toutes les variables disponibles
        all_vars = []
        var_info = {}
        
        # Ajouter les variables sociodémographiques
        for label, col in socio_columns.items():
            display_name = label
            all_vars.append(display_name)
            var_info[display_name] = {"type": "socio", "col": col, "label": label}
        
        # Ajouter les outcomes (sous-domaines RPS)
        for group, cols in domain_map.items():
            for col in cols:
                if col not in domain_cat_df.columns:
                    continue
                display_name = domain_label_map.get(col, col)
                # Éviter les doublons de noms (si un libellé RPS a le même nom qu'une variable socio)
                if display_name not in var_info:
                    all_vars.append(display_name)
                    var_info[display_name] = {
                        "type": "outcome", 
                        "col": col, 
                        "label": display_name,
                        "group": group
                    }
        
        # Trier alphabétiquement
        all_vars.sort()
        
        b1, b2 = st.columns(2)
        
        # Premier selectbox
        var1 = b1.selectbox("Variable 1", all_vars, key="croisement_var1")
        
        # Filtrer la liste pour le deuxième selectbox (exclure var1)
        var2_options = [v for v in all_vars if v != var1]
        
        # Deuxième selectbox avec les options filtrées
        var2 = b2.selectbox("Variable 2", var2_options, key="croisement_var2")
        
        # Récupérer les informations des variables sélectionnées
        var1_info = var_info[var1]
        var2_info = var_info[var2]
        
        # Déterminer automatiquement le rôle des variables
        # Si var1 est socio et var2 est outcome -> idéal
        # Si var1 est outcome et var2 est socio -> on les inverse
        if var1_info["type"] == "socio" and var2_info["type"] == "outcome":
            socio_label = var1
            socio_col = var1_info["col"]
            outcome_display = var2
            outcome_col = var2_info["col"]
        elif var1_info["type"] == "outcome" and var2_info["type"] == "socio":
            # Inverser pour avoir socio en X et outcome en Y
            socio_label = var2
            socio_col = var2_info["col"]
            outcome_display = var1
            outcome_col = var1_info["col"]
        elif var1_info["type"] == "socio" and var2_info["type"] == "socio":
            st.warning("⚠️ Vous avez sélectionné deux variables sociodémographiques. Le croisement montrera la répartition de la seconde selon la première.")
            socio_label = var1
            socio_col = var1_info["col"]
            outcome_display = var2
            # Pour deux variables socio, on utilise la première comme catégorie et la deuxième comme distribution
            temp_df = socio_df[[socio_col, var2_info["col"]]].dropna()
            if temp_df.empty:
                st.warning("Pas de données exploitables.")
                st.stop()
            
            # Créer le tableau croisé avec pourcentages en ligne
            ct = pd.crosstab(temp_df[socio_col], temp_df[var2_info["col"]], normalize="index").mul(100)
            
            # Créer un graphique avec les pourcentages dans les barres
            fig, ax = plt.subplots(figsize=(10, max(3.5, 0.6 * len(ct) + 1.5)))
            y = np.arange(len(ct))
            
            left = np.zeros(len(ct))
            colors = plt.cm.Set3(np.linspace(0, 1, len(ct.columns)))
            
            for i, (col_name, color) in enumerate(zip(ct.columns, colors)):
                values = ct[col_name].values
                bars = ax.barh(y, values, left=left, color=color, label=col_name)
                
                # Ajouter les pourcentages dans les barres
                for j, (bar, val) in enumerate(zip(bars, values)):
                    if val > 5:  # N'afficher que si le pourcentage est > 5% pour la lisibilité
                        width = bar.get_width()
                        x_pos = bar.get_x() + width/2
                        y_pos = bar.get_y() + bar.get_height()/2
                        ax.text(x_pos, y_pos, f'{val:.1f}%', 
                            ha='center', va='center', 
                            color='black', fontsize=9, fontweight='bold')
                
                left += values
            
            ax.set_yticks(y, ct.index.astype(str))
            ax.set_xlim(0, 100)
            ax.set_xticks(np.arange(0, 101, 10))
            ax.set_xlabel("Pourcentage (%)")
            ax.set_title(f"Répartition - {outcome_display} selon {socio_label}")
            
            # Légende en bas
            ax.legend(
                ncol=min(4, len(ct.columns)),
                bbox_to_anchor=(0.5, -0.15),
                loc="upper center",
                frameon=True,
                fontsize=8,
            )
            fig.subplots_adjust(bottom=0.2)
            fig.tight_layout()
            
            # Bouton de téléchargement PNG
            png_bytes = _fig_to_png_bytes(fig)
            if png_bytes is not None:
                socio_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(socio_label))
                out_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(outcome_display))
                st.download_button(
                    "📥 Télécharger PNG",
                    data=png_bytes,
                    file_name=f"{socio_name}_x_{out_name}.png",
                    mime="image/png",
                    key=f"dl_png_socio_socio_{socio_name}_{out_name}",
                )
            
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            
            # Afficher le tableau avec les pourcentages
            ct_display = ct.copy()
            ct_display["Total"] = ct_display.sum(axis=1)
            
            # Formater avec 1 décimale
            ct_display = ct_display.round(1)
            
            st.dataframe(ct_display, use_container_width=True)
            st.stop()        
        
        elif var1_info["type"] == "outcome" and var2_info["type"] == "outcome":
            st.warning("⚠️ Vous avez sélectionné deux variables RPS. Le croisement montrera la répartition de la seconde selon la première.")
            
            # Récupérer les colonnes correctes
            col1 = var1_info["col"]  # C'est déjà le nom de la colonne dans domain_cat_df
            col2 = var2_info["col"]  # C'est déjà le nom de la colonne dans domain_cat_df
            
            # Vérifier que les colonnes existent dans domain_cat_df
            if col1 not in domain_cat_df.columns or col2 not in domain_cat_df.columns:
                st.warning(f"Colonnes non trouvées: {col1} ou {col2}")
                st.stop()
            
            # Pour deux outcomes, on utilise directement les catégories
            # Pas besoin de recatégoriser car domain_cat_df contient déjà les catégories
            temp_df = pd.DataFrame({
                "cat": domain_cat_df[col1],  # Variable X (catégorisée)
                "outcome": domain_cat_df[col2]  # Variable Y (catégorisée)
            }).dropna()
            
            if temp_df.empty:
                st.warning("Pas de données exploitables pour ce croisement.")
                st.stop()
            
            # Créer le tableau croisé
            ct = pd.crosstab(temp_df["cat"], temp_df["outcome"], normalize="index").mul(100)
            ct = ct.reindex(columns=ORDER_LEVELS, fill_value=0)
            ct["Total"] = ct.sum(axis=1)
            
            # Créer le graphique
            fig_biv = _plot_bivariate_stacked(
                ct,
                f"Répartition - {var2} selon {var1}",
                subdomain_label=var2,
            )
            
            # Bouton de téléchargement
            png_bytes = _fig_to_png_bytes(fig_biv)
            if png_bytes is not None:
                out_name1 = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in var1)
                out_name2 = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in var2)
                st.download_button(
                    "📥 Télécharger PNG",
                    data=png_bytes,
                    file_name=f"{out_name1}_x_{out_name2}.png",
                    mime="image/png",
                    key=f"dl_png_outcome_outcome_{out_name1}_{out_name2}",
                )
            
            st.pyplot(fig_biv, use_container_width=True)
            plt.close(fig_biv)
            
            # Afficher le tableau
            st.dataframe(
                _style_bivariate_table(ct, subdomain_label=var2),
                use_container_width=True,
            )
            st.stop()
        # Cas standard : socio X outcome
        ct = _bivariate_table(socio_df[socio_col], domain_cat_df[outcome_col])
        if ct is None:
            st.warning("Pas de données exploitables pour ce croisement.")
        else:
            fig_biv = _plot_bivariate_stacked(
                ct,
                f"Répartition des employés - {socio_label} selon {outcome_display}",
                subdomain_label=outcome_display,
            )
            png_bytes = _fig_to_png_bytes(fig_biv)
            if png_bytes is not None:
                socio_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(socio_label))
                out_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(outcome_display))
                st.download_button(
                    "PNG",
                    data=png_bytes,
                    file_name=f"{socio_name}_x_{out_name}.png",
                    mime="image/png",
                    key=f"dl_png_biv_{socio_name}_{out_name}",
                )
            st.pyplot(fig_biv, use_container_width=True)
            plt.close(fig_biv)
            st.dataframe(
                _style_bivariate_table(ct, subdomain_label=outcome_display),
                use_container_width=True,
            )