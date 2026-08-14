import traceback
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import numpy_financial as npf
import io

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Modèle Financier Immobilier",
    layout="wide"
)

st.title("🏢 Modèle Financier Immobilier")
st.write("Projection financière, KPI et Dashboard")

EXCEL_FILE = "Real_estate_app_project.xlsx"

# --------------------------------------------------
# CHARGEMENT DU FICHIER
# --------------------------------------------------

try:

    excel_file = pd.ExcelFile(EXCEL_FILE)

    sheet_name = None

    if "Hypothèses" in excel_file.sheet_names:
        sheet_name = "Hypothèses"
    elif "Hypotheses" in excel_file.sheet_names:
        sheet_name = "Hypotheses"

    if sheet_name is None:
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

except Exception as e:
    st.error(f"Erreur chargement Excel : {e}")
    st.code(traceback.format_exc())
    st.stop()

# --------------------------------------------------
# FONCTIONS
# --------------------------------------------------

def get_hypothesis(name):

    try:
        value = hypotheses_df.loc[name, "Value"]
        return pd.to_numeric(value)

    except Exception:
        st.error(f"Paramètre manquant : {name}")
        st.stop()

# --------------------------------------------------
# HYPOTHESES
# --------------------------------------------------

prix_acquisition = get_hypothesis("Prix acquisition")
frais_acquisition = get_hypothesis("Frais acquisition %")
travaux = get_hypothesis("Travaux")

dette_pct = get_hypothesis("Dette %")
taux_dette = get_hypothesis("Taux dette %")
duree_dette = int(get_hypothesis("Duree dette"))

loyer_brut = get_hypothesis("Loyer brut An1")
croissance_loyers = get_hypothesis("Croissance loyers %")

vacance = get_hypothesis("Vacance %")
charges = get_hypothesis("Charges %")

horizon = int(get_hypothesis("Horizon"))

exit_yield = get_hypothesis("Exit Cap Rate %")
frais_cession = get_hypothesis("Frais cession %")

taux_actualisation = get_hypothesis("Taux actualisation %")

# --------------------------------------------------
# INVESTISSEMENT
# --------------------------------------------------

budget_total = (
    prix_acquisition *
    (1 + frais_acquisition)
    + travaux
)

montant_dette = budget_total * dette_pct
equity = budget_total - montant_dette

# --------------------------------------------------
# AMORTISSEMENT DETTE
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

schedule = []

for annee in range(1, duree_dette + 1):

    debut = solde

    interets_annuels = 0
    principal_annuel = 0

    for mois in range(12):

        if solde <= 0:
            break

        interet = solde * monthly_rate

        principal = mensualite - interet

        principal = min(principal, solde)

        solde -
