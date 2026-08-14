import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.express as px
import io
import os
import traceback

# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Modèle Financier Immobilier",
    layout="wide"
)

st.title("🏢 Modèle Financier Immobilier")
st.markdown("Analyse de rentabilité immobilière")

# =====================================================
# CHARGEMENT DU FICHIER EXCEL
# =====================================================

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
            f"Feuille Hypothèses introuvable. Feuilles trouvées : {excel_file.sheet_names}"
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

# =====================================================
# FONCTIONS
# =====================================================

def get_hypothesis(name):

    try:
        return float(
            hypotheses_df.loc[name, "Value"]
        )

    except Exception:
        st.error(f"Paramètre absent : {name}")
        st.stop()

# =====================================================
# HYPOTHESES
# ===================
