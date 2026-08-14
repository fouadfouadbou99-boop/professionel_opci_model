import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.express as px
import io
import os
import traceback

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Modèle Immobilier",
    layout="wide"
)

st.title("🏢 Modèle Financier Immobilier")

# --------------------------------------------------
# CHARGEMENT EXCEL
# --------------------------------------------------

excel_file_path = "Real_estate_app_project.xlsx"

if not os.path.exists(excel_file_path):
    st.error(f"Fichier introuvable : {excel_file_path}")
    st.stop()

try:

    excel_file = pd.ExcelFile(excel_file_path)

    if "Hypothèses" in excel_file.sheet_names:
        sheet_name = "Hypothèses"
    elif "Hypotheses" in excel_file.sheet_names:
        sheet_name = "Hypotheses"
    else:
        st.error(
            f"Feuille Hypothèses introuvable. "
            f"Feuilles disponibles : {excel_file.sheet_names}"
        )
        st.stop()

    hypotheses_df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name
    )

    hypotheses_df.columns = ["Parameter", "Value"]

    hypotheses_df = (
        hypotheses_df
        .dropna()
        .set_index("Parameter")
    )

except Exception:
    st.code(traceback.format_exc())
    st.stop()

# --------------------------------------------------
# FONCTION
# --------------------------------------------------

def get_hypothesis(name):

    try:
        return float(
            hypotheses_df.loc[name, "Value"]
        )

    except Exception:
        st.error(f"Paramètre absent : {name}")
        st.stop()

# --------------------------------------------------
# HYPOTHESES
# --------------------------------------------------

prix_acquisition = get_hypothesis("Prix acquisition")

frais_acquisition = get_hypothesis(
    "Frais acquisition %"
)

travaux = get_hypothesis("Travaux")

loyer_brut_an1 = get_hypothesis(
    "Loyer brut An1"
)

croissance_loyers = get_hypothesis(
    "Croissance loyers %"
)

vacance = get_hypothesis("Vacance %")

charges = get_hypothesis("Charges %")

dette_pct = get_hypothesis("Dette %")

taux_dette = get_hypothesis(
    "Taux dette %"
)

duree_dette = int(
    get_hypothesis("Duree dette")
)

horizon = int(
    get_hypothesis("Horizon")
)

exit_cap_rate = get_hypothesis(
    "Exit Cap Rate %"
)

frais_cession = get_hypothesis(
    "Frais cession %"
)

taux_actualisation = get_hypothesis(
    "Taux actualisation %"
)

# --------------------------------------------------
# ACQUISITION
# --------------------------------------------------

budget_total = (
    prix_acquisition
    * (1 + frais_acquisition)
    + travaux
)

montant_dette = (
    budget_total
    * dette_pct
)

equity = (
    budget_total
    - montant_dette
)

# --------------------------------------------------
# TABLEAU DE DETTE
# --------------------------------------------------

monthly_rate = taux_dette / 12

nper = duree_dette * 12

if monthly_rate > 0:

    mensualite = npf.pmt(
        monthly_rate,
        nper,
        -montant_dette
    )

else:

    mensualite = montant_dette / nper

solde = montant_dette

debt_rows = []

for annee in range(1, duree_dette + 1):

    debut = solde

    interets = 0
    principal = 0

    for m in range(12):

     if solde <= 0:
    break

if annee <= duree_dette:

    ligne = debt_df.loc[
        debt_df["Année"] == annee
    ]

    interets = ligne[
        "Intérêts"
    ].iloc[0]

    principal = ligne[
        "Principal"
    ].iloc[0]

else:

    interets = 0

    principal = 0
