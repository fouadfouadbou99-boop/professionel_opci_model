import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
from io import BytesIO

st.set_page_config(
    page_title="Modèle Immobilier OPCI",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Modèle Immobilier OPCI")

st.markdown(
    "Simulation simplifiée d'investissement immobilier OPCI."
)

# ==========================
# SIDEBAR
# ==========================

st.sidebar.header("Hypothèses")

prix_acquisition = st.sidebar.number_input(
    "Prix d'acquisition (MAD)",
    value=10000000.0,
    step=100000.0
)

loyer_annuel = st.sidebar.number_input(
    "Loyer brut année 1 (MAD)",
    value=120000.0,
    step=1000.0
)

croissance = st.sidebar.slider(
    "Croissance annuelle (%)",
    0.0,
    10.0,
    2.0
) / 100

vacance = st.sidebar.slider(
    "Taux de vacance (%)",
    0.0,
    20.0,
    5.0
) / 100

opex = st.sidebar.slider(
    "Charges exploitation (%)",
    0.0,
    50.0,
    20.0
) / 100

taux_actualisation = st.sidebar.slider(
    "Taux d'actualisation (%)",
    1.0,
    20.0,
    8.0
) / 100

exit_yield = st.sidebar.slider(
    "Exit Yield (%)",
    4.0,
    12.0,
    7.0
) / 100

horizon = st.sidebar.slider(
    "Horizon (années)",
    5,
    30,
    20
)

# ==========================
# CALCULS
# ==========================

data = []
cashflows = [-prix_acquisition]

dernier_noi = 0

for annee in range(1, horizon + 1):

    loyer_brut = loyer_annuel * ((1 + croissance) ** (annee - 1))

    loyer_net = loyer_brut * (1 - vacance)

    noi = loyer_net * (1 - opex)

    ffo = noi * 0.70

    affo = ffo * 0.95

    dernier_noi = noi

    cashflows.append(noi)

    data.append({
        "Année": annee,
        "Loyer Brut": round(loyer_brut, 2),
        "Loyer Net": round(loyer_net, 2),
        "NOI": round(noi, 2),
        "FFO": round(ffo, 2),
        "AFFO": round(affo, 2)
    })

# Valeur terminale

valeur_terminale = dernier_noi / exit_yield

cashflows[-1] += valeur_terminale

# KPI

van = npf.npv(
    taux_actualisation,
    cashflows
)

tri = npf.irr(
    cashflows
)

moic = (
    sum(cashflows[1:])
    / prix_acquisition
)

# ==========================
# DATAFRAMES
# ==========================

df_cashflow = pd.DataFrame(data)

df_hyp = pd.DataFrame({
    "Paramètre": [
        "Prix acquisition",
        "Loyer initial",
        "Croissance",
        "Vacance",
        "Opex",
        "Actualisation",
        "Exit Yield",
        "Horizon"
    ],
    "Valeur": [
        prix_acquisition,
        loyer_annuel,
        croissance,
        vacance,
        opex,
        taux_actualisation,
        exit_yield,
        horizon
    ]
})

df_acquisition = pd.DataFrame({
    "Elément": [
        "Prix acquisition"
    ],
    "Montant": [
        prix_acquisition
    ]
})

df_kpi = pd.DataFrame({
    "Indicateur": [
        "VAN",
        "TRI",
        "MOIC",
        "Valeur Terminale"
    ],
    "Valeur": [
        round(van, 0),
        round(tri * 100, 2),
        round(moic, 2),
        round(valeur_terminale, 0)
    ]
})

df_sensibilite = pd.DataFrame({
    "Croissance": [
        "0%",
        "2%",
        "4%"
    ],
    "TRI Estimatif": [
        round((tri - 0.02) * 100, 2),
        round(tri * 100, 2),
        round((tri + 0.02) * 100, 2)
    ]
})

# ==========================
# DASHBOARD
# ==========================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "VAN Projet",
    f"{van:,.0f} MAD"
)

c2.metric(
    "TRI",
    f"{tri:.2%}"
)

c3.metric(
    "MOIC",
    f"{moic:.2f}x"
)

c4.metric(
    "Valeur Terminale",
    f"{valeur_terminale:,.0f}"
)

st.subheader("Cash-Flows")

st.dataframe(
    df_cashflow,
    use_container_width=True
)

st.subheader("Evolution du NOI")

st.line_chart(
    df_cashflow.set_index("Année")["NOI"]
)

# ==========================
# EXPORT EXCEL
# ==========================

buffer = BytesIO()

with pd.ExcelWriter(
    buffer,
    engine="xlsxwriter"
) as writer:

    df_hyp.to_excel(
        writer,
        sheet_name="01_Hypotheses",
        index=False
    )

    df_acquisition.to_excel(
        writer,
        sheet_name="02_Acquisition",
        index=False
    )

    df_cashflow.to_excel(
        writer,
        sheet_name="03_Cashflow",
        index=False
    )

    df_kpi.to_excel(
        writer,
        sheet_name="04_KPI",
        index=False
    )

    df_sensibilite.to_excel(
        writer,
        sheet_name="05_Sensibilite",
        index=False
    )

buffer.seek(0)

st.download_button(
    label="📥 Télécharger le modèle Excel OPCI",
    data=buffer,
    file_name="Modele_OPCI.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
