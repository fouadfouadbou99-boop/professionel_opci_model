import streamlit as st
import pandas as pd
import numpy_financial as npf
from io import BytesIO

st.set_page_config(
    page_title="Modèle Immobilier OPCI",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Modèle Immobilier OPCI")

st.markdown(
    "Simulation d'investissement immobilier OPCI avec valorisation terminale."
)

# ==========================
# HYPOTHESES
# ==========================

st.sidebar.header("Hypothèses")

prix_acquisition = st.sidebar.number_input(
    "Prix acquisition (MAD)",
    value=10000000.0,
    step=100000.0
)

rendement_initial = st.sidebar.slider(
    "Rendement locatif initial (%)",
    1.0,
    15.0,
    8.0
) / 100

croissance = st.sidebar.slider(
    "Croissance annuelle loyers (%)",
    0.0,
    10.0,
    2.0
) / 100

vacance = st.sidebar.slider(
    "Vacance (%)",
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

loyer_annuel = prix_acquisition * rendement_initial

cashflows = [-prix_acquisition]

data = []

dernier_noi = 0

for annee in range(1, horizon + 1):

    loyer_brut = loyer_annuel * ((1 + croissance) ** (annee - 1))

    loyer_net = loyer_brut * (1 - vacance)

    noi = loyer_net * (1 - opex)

    ffo = noi

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

van = npf.npv(taux_actualisation, cashflows)

tri = npf.irr(cashflows)

moic = sum(cashflows[1:]) / prix_acquisition

# ==========================
# DATAFRAMES
# ==========================

df_cashflow = pd.DataFrame(data)

df_hyp = pd.DataFrame({
    "Paramètre": [
        "Prix acquisition",
        "Rendement initial",
        "Croissance",
        "Vacance",
        "OPEX",
        "Taux actualisation",
        "Exit Yield",
        "Horizon"
    ],
    "Valeur": [
        prix_acquisition,
        rendement_initial,
        croissance,
        vacance,
        opex,
        taux_actualisation,
        exit_yield,
        horizon
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
    f"{valeur_terminale:,.0f} MAD"
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

with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:

    df_hyp.to_excel(
        writer,
        sheet_name="01_Hypotheses",
        index=False
    )

    df_cashflow.to_excel(
        writer,
        sheet_name="02_Cashflow",
        index=False
    )

    df_kpi.to_excel(
        writer,
        sheet_name="03_KPI",
        index=False
    )

buffer.seek(0)

st.download_button(
    "📥 Télécharger le modèle Excel OPCI",
    data=buffer,
    file_name="Modele_OPCI.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
