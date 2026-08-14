import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.express as px
import traceback
import io
import os

# ==================================================
# CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Modèle Financier Immobilier",
    layout="wide"
)

st.title("🏢 Modèle Financier Immobilier")
st.markdown("Analyse de rentabilité immobilière")

# ==================================================
# FICHIER EXCEL
# ==================================================

excel_file_path = "Real_estate_app_project.xlsx"

if not os.path.exists(excel_file_path):
    st.error(
        f"Fichier introuvable : {excel_file_path}"
    )
    st.stop()

try:

    excel_file = pd.ExcelFile(excel_file_path)

    if "Hypothèses" in excel_file.sheet_names:
        sheet_name = "Hypothèses"
    elif "Hypotheses" in excel_file.sheet_names:
        sheet_name = "Hypotheses"
    else:
        st.error(
            f"Feuille Hypothèses introuvable.\n\n"
            f"Feuilles trouvées : {excel_file.sheet_names}"
        )
        st.stop()

    hypotheses_df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name
    )

    hypotheses_df.columns = [
        "Parameter",
        "Value"
    ]

    hypotheses_df = (
        hypotheses_df
        .dropna()
        .set_index("Parameter")
    )

except Exception as e:

    st.error("Erreur lors du chargement du fichier")

    st.code(traceback.format_exc())

    st.stop()

# ==================================================
# FONCTIONS
# ==================================================

def get_hypothesis(name):

    try:

        value = hypotheses_df.loc[name, "Value"]

        return float(value)

    except Exception:

        st.error(
            f"Paramètre absent : {name}"
        )

        st.stop()

# ==================================================
# HYPOTHESES
# ==================================================

prix_acquisition = get_hypothesis("Prix acquisition")
frais_acquisition = get_hypothesis("Frais acquisition %")
travaux = get_hypothesis("Travaux")

loyer_brut_an1 = get_hypothesis("Loyer brut An1")
croissance_loyers = get_hypothesis("Croissance loyers %")

vacance = get_hypothesis("Vacance %")
charges = get_hypothesis("Charges %")

dette_pct = get_hypothesis("Dette %")
taux_dette = get_hypothesis("Taux dette %")
duree_dette = int(get_hypothesis("Duree dette"))

horizon = int(get_hypothesis("Horizon"))

exit_cap_rate = get_hypothesis("Exit Cap Rate %")
frais_cession = get_hypothesis("Frais 
